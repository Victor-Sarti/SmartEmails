// Função para classificar o email
async function classifyEmail() {
    const emailText = document.getElementById('emailText').value.trim();
    if (!emailText) {
        alert('Por favor, cole o conteúdo do e-mail para análise.');
        return;
    }

    const classifyBtn = document.getElementById('classifyBtn');
    const originalText = classifyBtn.textContent;
    
    try {
        // Mostra o estado de carregamento
        classifyBtn.disabled = true;
        classifyBtn.innerHTML = '<span class="animate-spin mr-2">⏳</span> Analisando...';

        const response = await fetch('/classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email_text: emailText })
        });

        const result = await response.json();

        if (result.status === 'success') {
            // Atualiza a interface com os resultados
            document.getElementById('classification').textContent = result.classification;
            document.getElementById('confidence').textContent = `${(result.confidence * 100).toFixed(2)}%`;
            
            // Estiliza a classificação
            const classificationElement = document.getElementById('classification');
            if (result.classification === 'Produtivo') {
                classificationElement.className = 'px-2 py-1 rounded-full text-sm font-semibold bg-green-100 text-green-800';
            } else {
                classificationElement.className = 'px-2 py-1 rounded-full text-sm font-semibold bg-red-100 text-red-800';
            }

            // Mostra a seção de resultados e o botão de sugerir resposta
            document.getElementById('result').classList.remove('hidden');
            document.getElementById('suggestResponseBtn').classList.remove('hidden');
            
            // Armazena a resposta sugerida para uso posterior
            if (result.suggested_response) {
                document.getElementById('suggestedResponse').innerHTML = 
                    `<p class="text-gray-800">${result.suggested_response}</p>`;
            }
        } else {
            throw new Error(result.message || 'Erro ao classificar o e-mail');
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente.');
    } finally {
        // Restaura o botão
        classifyBtn.disabled = false;
        classifyBtn.textContent = originalText;
    }
}

// Função para sugerir resposta
async function suggestResponse() {
    const suggestBtn = document.getElementById('suggestResponseBtn');
    const originalText = suggestBtn.textContent;
    
    try {
        // Mostra o estado de carregamento
        suggestBtn.disabled = true;
        suggestBtn.innerHTML = '<span class="animate-spin mr-2">⏳</span> Gerando...';
        
        // Aqui você pode adicionar uma chamada para a API de geração de respostas
        // Por enquanto, apenas simulamos um atraso
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Simula uma resposta gerada (será substituído pela chamada real à API)
        const mockResponses = [
            "Agradeço pelo seu e-mail. Vou analisar e retornar em breve.",
            "Obrigado pelo contato. Estou verificando as informações solicitadas.",
            "Recebi sua mensagem e estou trabalhando nisso. Retorno em breve.",
            "Agradeço pelo envio. Vou analisar e te retorno o mais rápido possível."
        ];
        
        const randomResponse = mockResponses[Math.floor(Math.random() * mockResponses.length)];
        
        // Atualiza a resposta sugerida
        document.getElementById('suggestedResponse').innerHTML = 
            `<p class="text-gray-800">${randomResponse}</p>`;
        
    } catch (error) {
        console.error('Erro:', error);
        document.getElementById('suggestedResponse').innerHTML = 
            '<p class="text-red-500">Erro ao gerar resposta. Tente novamente mais tarde.</p>';
    } finally {
        // Restaura o botão
        suggestBtn.disabled = false;
        suggestBtn.textContent = originalText;
    }
}

// Adiciona suporte para pressionar Enter no textarea
document.getElementById('emailText').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.ctrlKey) {
        e.preventDefault();
        classifyEmail();
    }
});
