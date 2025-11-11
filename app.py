import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from dotenv import load_dotenv

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

@app.route('/processar', methods=['POST'])
@app.route('/processar/<int:preview>', methods=['POST'])
def processar_email(preview=0):
    """
    Rota para processar o email enviado via formulário.
    Aceita tanto texto direto quanto upload de arquivo.
    """
    email_content = ""
    
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
                email_content = read_pdf_file(filepath)
            else:  # .txt
                email_content = read_txt_file(filepath)
                
            # Remove o arquivo após a leitura
            try:
                os.remove(filepath)
            except:
                pass
    else:
        # Se não foi enviado arquivo, verifica se há texto direto
        email_content = request.form.get('texto_email', '').strip()
    
    if not email_content:
        flash('Por favor, insira um texto ou envie um arquivo.', 'error')
        return redirect(url_for('index'))
    
    # Se for uma pré-visualização (AJAX), retorna JSON
    if preview:
        return jsonify({
            'status': 'success',
            'content': email_content[:500] + '...' if len(email_content) > 500 else email_content
        })
    
    # Senão, renderiza a página de resultado
    return render_template('resultado.html', conteudo=email_content)

if __name__ == '__main__':
    # Garante que a pasta de uploads existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)
