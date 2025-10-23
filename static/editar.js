const form = document.getElementById('form-edicao');
const userId = document.getElementById('user-id').textContent;
const statusMessage = document.createElement('p');

form.addEventListener('submit', function(event) {
    event.preventDefault();

    const token = localStorage.getItem('access_token'); 
    
    if (!token) {
        alert('Erro: Token de autenticação não encontrado. Redirecionando para o login.');
        window.location.href = '/login'; 
        return;
    }

    const novosDados = {
        nome: document.getElementById('nome').value,
        email: document.getElementById('email').value,
        idade: document.getElementById('idade').value,
    };
    
    const senha = document.getElementById('senha').value;
    if (senha) {
        novosDados.senha = senha;
    }

    fetch(`/usuarios/${userId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(novosDados),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(errorData.message || 'Erro desconhecido ao atualizar');
            });
        }
        return response.json();
    })
    .then(data => {
        statusMessage.textContent = data.message;
        statusMessage.style.color = 'green';
        
        if (!form.contains(statusMessage)) {
             form.appendChild(statusMessage);
        }
    })
    .catch(error => {
        statusMessage.textContent = error.message;
        statusMessage.style.color = 'red';

        if (!form.contains(statusMessage)) {
             form.appendChild(statusMessage);
        }
        
        console.error('Erro:', error);
    });
});