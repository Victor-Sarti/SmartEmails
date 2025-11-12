# Email Classifier

Aplicação web para classificação automática de e-mails como "Produtivo" ou "Improdutivo" com geração de respostas automáticas.

## 🚀 Funcionalidades

- Classificação de e-mails em categorias (Produtivo/Improdutivo)
- Geração automática de respostas
- Interface web intuitiva
- Análise de confiança da classificação
- Respostas personalizáveis

## 🛠️ Estrutura do Projeto

```
email_classifier/
├── config/                  # Arquivos de configuração
├── models/                  # Modelos de machine learning
├── services/                # Lógica de negócios e serviços
├── static/                  # Arquivos estáticos (CSS, JS, imagens)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/               # Templates HTML
├── utils/                   # Utilitários e funções auxiliares
├── .env.example             # Exemplo de variáveis de ambiente
├── app.py                   # Aplicação Flask principal
├── requirements.txt          # Dependências do projeto
└── README.md                # Documentação
```

## 🚀 Como Executar

1. **Clonar o repositório**
   ```bash
   git clone <repositorio>
   cd email_classifier
   ```

2. **Criar e ativar um ambiente virtual (recomendado)**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # No Windows
   source venv/bin/activate  # No Linux/Mac
   ```

3. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variáveis de ambiente**
   - Copie o arquivo `.env.example` para `.env`
   - Preencha as variáveis necessárias

5. **Baixar modelos do spaCy (se necessário)**
   ```bash
   python -m spacy download pt_core_news_sm
   ```

6. **Iniciar a aplicação**
   ```bash
   python app.py
   ```

7. **Acessar no navegador**

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript, TailwindCSS
- **Processamento de Linguagem Natural**: spaCy, NLTK, Transformers
- **Machine Learning**: scikit-learn, PyTorch
- **Geração de Respostas**: OpenAI API (opcional)

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

Desenvolvido com ❤️ por Victor Sarti
