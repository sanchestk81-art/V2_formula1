// Interações JavaScript para o portal de Fórmula 1
document.addEventListener('DOMContentLoaded', () => {
    // 1. Fechar mensagens de alerta flash
    const closeButtons = document.querySelectorAll('.alert-close');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const alert = button.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 250);
            }
        });
    });

    // Auto-remover alertas de sucesso após 6 segundos
    const successAlerts = document.querySelectorAll('.alert-success');
    successAlerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 6000);
    });

    // 2. Menu Mobile Toggle (Hamburger)
    const mobileToggle = document.getElementById('mobileMenuToggle');
    const siteNav = document.getElementById('siteNav');

    if (mobileToggle && siteNav) {
        mobileToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            mobileToggle.classList.toggle('open');
            siteNav.classList.toggle('open');
        });

        // Fecha ao clicar fora
        document.addEventListener('click', (e) => {
            if (!siteNav.contains(e.target) && !mobileToggle.contains(e.target)) {
                mobileToggle.classList.remove('open');
                siteNav.classList.remove('open');
            }
        });
    }

    // 3. Dropdown 'Mais' com suporte a clique e touch
    const dropdownTrigger = document.getElementById('dropdownTrigger');
    const dropdownMenu = document.getElementById('dropdownMenu');

    if (dropdownTrigger && dropdownMenu) {
        dropdownTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });

        // Fecha o dropdown se clicar fora
        document.addEventListener('click', (e) => {
            if (!dropdownMenu.contains(e.target) && e.target !== dropdownTrigger) {
                dropdownMenu.classList.remove('show');
            }
        });
    }

    // 4. Exclusão Suave via AJAX sem Atualizar a Página (Requisito 1)
    inicializarExclusaoAjax();
});

// ==============================================================================
// SISTEMA DE NOTIFICAÇÃO TOAST VISUAL
// ==============================================================================
function mostrarToast(mensagem, tipo = 'sucesso') {
    let toast = document.getElementById('f1ToastFeedback');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'f1ToastFeedback';
        toast.className = 'f1-toast';
        document.body.appendChild(toast);
    }

    toast.className = `f1-toast ${tipo === 'erro' ? 'toast-error' : ''}`;
    toast.innerHTML = `<span>${tipo === 'erro' ? '⚠️' : '✅'}</span> <span>${mensagem}</span>`;
    
    // Animação de entrada
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    clearTimeout(toast.tempoSumir);
    toast.tempoSumir = setTimeout(() => {
        toast.classList.remove('show');
    }, 3800);
}

// ==============================================================================
// INTERCEPTADOR GLOBAL DE EXCLUSÃO (SEM RELOAD)
// ==============================================================================
function inicializarExclusaoAjax() {
    document.addEventListener('submit', function (e) {
        const form = e.target;
        if (!form || !form.action) return;

        // Verifica se é uma ação de exclusão
        const isDeleteAction = form.action.includes('/excluir/') || form.classList.contains('form-excluir-ajax');
        if (!isDeleteAction) return;

        e.preventDefault();

        // Confirmação com o usuário
        const msgConfirmacao = form.getAttribute('data-confirm') || 'Deseja realmente excluir este item permanentemente?';
        if (!confirm(msgConfirmacao)) {
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]') || form.querySelector('.btn-danger');
        let textoOriginal = '';
        if (submitBtn) {
            textoOriginal = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '⏳ Excluindo...';
        }

        // Localiza o card ou linha a ser removida
        const containerItem = form.closest('.card') || form.closest('tr') || form.closest('.admin-item-row');

        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Falha ao processar a exclusão no servidor.');
            }
            return response.json().catch(() => ({ success: true, message: 'Item excluído com sucesso!' }));
        })
        .then(data => {
            mostrarToast(data.message || 'Item excluído com sucesso!', 'sucesso');

            if (containerItem) {
                containerItem.classList.add('item-deleting');
                setTimeout(() => {
                    containerItem.remove();
                    // Atualiza contadores visuais se existirem
                    atualizarContadoresAposExclusao();
                }, 380);
            }
        })
        .catch(err => {
            console.error('Erro na exclusão AJAX:', err);
            mostrarToast('Erro ao excluir item: ' + err.message, 'erro');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = textoOriginal;
            }
        });
    });
}

function atualizarContadoresAposExclusao() {
    // Atualiza contadores dentro de cabeçalhos de anos no admin
    document.querySelectorAll('.admin-year-accordion').forEach(acc => {
        const itensRestantes = acc.querySelectorAll('.admin-item-row, .card:not(.admin-year-accordion)').length;
        const badgeContador = acc.querySelector('.year-count-badge');
        if (badgeContador) {
            badgeContador.textContent = `${itensRestantes} corrida${itensRestantes === 1 ? '' : 's'}`;
        }
    });
}
