import os
import re
import string
import torch
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax

# Inicializa o lematizador
lemmatizer = WordNetLemmatizer()

# Carrega o modelo e tokenizador do Hugging Face
MODEL_NAME = "distilbert-base-uncased"
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    # Definir os rótulos das classes (ajuste conforme necessário)
    CLASS_LABELS = ["Improdutivo", "Produtivo"]
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    tokenizer = None
    model = None
    CLASS_LABELS = ["Improdutivo", "Produtivo"]  # Rótulos padrão

# Obtém as stopwords em português
try:
    stop_words = set(stopwords.words('portuguese'))
    # Adiciona algumas palavras específicas que são comuns em e-mails
    custom_stopwords = {'para', 'com', 'por', 'pelo', 'pela', 'nos', 'nas', 'esse', 'essa', 'isso',
                       'desse', 'dessa', 'disso', 'neste', 'nesta', 'nisto', 'muito', 'muita',
                       'muitos', 'muitas', 'também', 'pois', 'quando', 'como', 'assim', 'então',
                       'só', 'já', 'aqui', 'lá', 'onde', 'quem', 'qual', 'quais', 'cujo', 'cuja',
                       'cujos', 'cujas', 'meu', 'minha', 'teu', 'tua', 'seu', 'sua', 'nosso',
                       'nossa', 'deles', 'delas', 'isto', 'isso', 'aquilo', 'este', 'esta', 'esse'}
    stop_words.update(custom_stopwords)
except:
    # Se não conseguir carregar as stopwords em português, usa as em inglês como fallback
    stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """
    Pré-processa o texto do e-mail:
    1. Converte para minúsculas
    2. Remove pontuações e caracteres especiais
    3. Remove números
    4. Remove stopwords
    5. Aplica lematização
    6. Remove palavras muito curtas
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Converte para minúsculas
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove endereços de e-mail
    text = re.sub(r'\S*@\S*\s?', '', text)
    
    # Remove números e caracteres especiais, mantendo acentuação
    text = re.sub(r'[^\w\sáàâãéèêíïóôõöúçñ]', ' ', text)
    
    # Remove números
    text = re.sub(r'\d+', '', text)
    
    # Tokenização
    tokens = word_tokenize(text, language='portuguese')
    
    # Remove stopwords e aplica lematização
    processed_tokens = []
    for token in tokens:
        if token not in stop_words and len(token) > 2:  # Remove palavras muito curtas
            # Lematização
            lemma = lemmatizer.lemmatize(token)
            processed_tokens.append(lemma)
    
    # Junta os tokens novamente em um texto
    return ' '.join(processed_tokens)

# Carrega as variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Configurações
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Garante que a pasta de uploads existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_txt_file(file_path):
    """Lê o conteúdo de um arquivo de texto."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo de texto: {str(e)}")

def read_pdf_file(file_path):
    """Lê o conteúdo de um arquivo PDF."""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo PDF: {str(e)}")

@app.route('/')
def index():
    """Rota principal que exibe o formulário de upload."""
    return render_template('upload.html')

def classificar_texto(texto):
    """
    Classifica o texto usando o modelo pré-treinado.
    Retorna um dicionário com a categoria e a confiança.
    """
    if not texto or not model or not tokenizer:
        return {
            "categoria": "Erro",
            "confianca": 0.0,
            "erro": "Modelo não carregado corretamente"
        }
    
    try:
        # Tokeniza o texto
        inputs = tokenizer(texto, return_tensors="pt", truncation=True, max_length=512)
        
        # Faz a previsão
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Obtém as probabilidades
        probs = softmax(outputs.logits, dim=1)
        
        # Pega a classe com maior probabilidade
        pred_class = torch.argmax(probs, dim=1).item()
        confidence = probs[0][pred_class].item() * 100  # Convertendo para porcentagem
        
        return {
            "categoria": CLASS_LABELS[pred_class],
            "confianca": round(confidence, 2),
            "erro": None
        }
    except Exception as e:
        return {
            "categoria": "Erro",
            "confianca": 0.0,
            "erro": str(e)
        }

@app.route('/processar', methods=['POST'])
@app.route('/processar/<int:preview>', methods=['POST'])
def processar_email(preview=0):
    """
    Rota para processar o email enviado via formulário.
    Aceita tanto texto direto quanto upload de arquivo.
    """
    email_content = ""
    original_content = ""
    
    # Verifica se foi enviado um arquivo
    if 'arquivo' in request.files:
        file = request.files['arquivo']
        
        # Se o usuário não selecionou um arquivo, o navegador pode
        # enviar uma parte vazia sem nome de arquivo
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Lê o conteúdo do arquivo com base na extensão
            if filename.lower().endswith('.pdf'):
                original_content = read_pdf_file(filepath)
            else:  # .txt
                original_content = read_txt_file(filepath)
                
            # Remove o arquivo após a leitura
            try:
                os.remove(filepath)
            except:
                pass
    else:
        # Se não foi enviado arquivo, verifica se há texto direto
        original_content = request.form.get('texto_email', '').strip()
    
    if not original_content:
        flash('Por favor, insira um texto ou envie um arquivo.', 'error')
        return redirect(url_for('index'))
    
    # Aplica o pré-processamento ao texto
    email_content = preprocess_text(original_content)
    
    # Classifica o texto original (não processado)
    classificacao = classificar_texto(original_content)
    
    # Se for uma pré-visualização (AJAX), retorna JSON
    if preview:
        return jsonify({
            'status': 'success',
            'original': original_content[:500] + '...' if len(original_content) > 500 else original_content,
            'processed': email_content[:500] + '...' if len(email_content) > 500 else email_content,
            'classificacao': classificacao
        })
    
    # Senão, renderiza a página de resultado com todas as informações
    return render_template('resultado.html', 
                         original=original_content,
                         processado=email_content,
                         classificacao=classificacao)

if __name__ == '__main__':
    # Garante que a pasta de uploads existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)
