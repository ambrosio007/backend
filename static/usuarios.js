        function excluirUsuario(id, cpf) {
            if (confirm(`Tem certeza que deseja excluir este usuário com o CPF ${cpf}?`)) {
                fetch(`/usuarios/${id}`, {
                    method: 'DELETE',
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