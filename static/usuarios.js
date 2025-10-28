function excluirUsuario(id, cpf) {

    const token = localStorage.getItem('access_token'); 

    if (!token) {
        alert('Erro: Token de autenticação não encontrado. Redirecionando para o login.');
        window.location.href = '/login'; 
        return;
    }

    if (confirm(`Tem certeza que deseja excluir este usuário com o CPF ${cpf}?`)) {
        fetch(`/usuarios/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}` 
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || 'Erro desconhecido');
                });
            }
            return response.json();
        })
        .then(data => {
            alert(data.message);
            const linha = document.getElementById('linha-' + id);
            if (linha) {
                linha.remove();
            }
        })
        .catch(error => {
            alert(`Erro ao excluir usuário: ${error.message}`);
        });
    }
}

function carregarPaginaEdicao(userId) {
    const token = localStorage.getItem('access_token'); 

    if (!token) {
        alert('Erro: Token de autenticação não encontrado. Redirecionando para o login.');
        window.location.href = '/login'; 
        return;
    }

    const url = `/editar-usuario/${userId}`;

    // Esta função é a mesma lógica de 'loadProtectedPage' que você usou no login
    fetch(url, { 
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}` 
        }
    })
    .then(response => {
        if (response.status === 401 || response.status === 403) {
            localStorage.removeItem('access_token');
            // Redireciona para o login se a sessão expirar ou for negada
            window.location.href = '/login'; 
            return;
        }
        return response.text();
    })
    .then(html => {
        if (html) {
            // Substitui o conteúdo da página com o HTML de edição
            document.documentElement.innerHTML = html;
            // Atualiza a URL do navegador
            history.pushState({}, '', url);

            // ⚠️ IMPORTANTE: Você precisará carregar o editar.js aqui também,
            // assim como fez com o usuarios.js no login.html!
            // Exemplo:
            const script = document.createElement('script');
            script.src = '/static/editar.js'; 
            document.body.appendChild(script);
        }
    })
    .catch(error => {
        console.error("Erro ao carregar página de edição:", error);
        alert("Erro ao carregar a página de edição.");
    });
}

function fazerLogout() {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        // Se já não houver token, apenas redireciona para o login
        window.location.href = '/login'; 
        return;
    }

    // 1. Envia a requisição POST para a rota de logout (protegida)
    fetch('/logout', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}` 
        }
    })
    .then(response => {
        // O servidor deve revogar o token, mesmo que a resposta seja um erro HTTP (exceto 401/403)
        // No entanto, o importante é revogar localmente
        if (response.ok || response.status === 200) {
            return response.json();
        } else {
            // Se falhar (ex: token expirado - 401), tratamos abaixo, mas limpamos o local storage de qualquer forma
             return response.json().then(errorData => {
                 console.warn("Aviso: Falha na revogação no servidor, mas o token local será limpo.", errorData.message);
                 // Não lançamos erro aqui para garantir o logout local.
             });
        }
    })
    .catch(error => {
        console.error("Erro de rede/revogação:", error);
    })
    .finally(() => {
        // 2. Limpa o token do armazenamento local (ESSENCIAL)
        localStorage.removeItem('access_token');
        
        // 3. Redireciona para a página de login
        window.location.href = '/login';
    });
}