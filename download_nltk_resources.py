import nltk

def download_nltk_resources():
    try:
        # Baixa as stopwords
        nltk.download('stopwords', quiet=True)
        # Baixa o tokenizador
        nltk.download('punkt', quiet=True)
        # Baixa o lematizador
        nltk.download('wordnet', quiet=True)
        print("Recursos do NLTK baixados com sucesso!")
    except Exception as e:
        print(f"Erro ao baixar recursos do NLTK: {e}")

if __name__ == "__main__":
    download_nltk_resources()
