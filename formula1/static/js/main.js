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
});
