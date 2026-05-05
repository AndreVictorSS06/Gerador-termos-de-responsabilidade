/**
 * ui.js
 * Utilitários de Interface, Toasts, Modais e Máscaras
 */

export function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerText = message;
    container.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

export function formatCPF(value) {
    if (!value) return "";
    const cleanValue = String(value).replace(/\D/g, "");
    return cleanValue
        .replace(/(\d{3})(\d)/, "$1.$2")
        .replace(/(\d{3})(\d)/, "$1.$2")
        .replace(/(\d{3})(\d{1,2})$/, "$1-$2")
        .substring(0, 14);
}

export function applyHighlight(text, searchTerm, isNumeric = true) {
    if (!searchTerm || !text) return text;
    let cleanSearch = isNumeric ? searchTerm.replace(/\D/g, "") : searchTerm;
    if (!cleanSearch) return text;

    try {
        const escapedSearch = cleanSearch.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escapedSearch})`, "gi");
        return String(text).replace(regex, "<mark>$1</mark>");
    } catch (e) {
        return text;
    }
}

export function closeModal() {
    const detailsModal = document.getElementById('details-modal');
    const editModal = document.getElementById('edit-term-modal');
    if (detailsModal) detailsModal.classList.remove('active');
    if (editModal) editModal.classList.remove('active');
}

export function confirmAction(message, callback) {
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');
    const modal = document.getElementById('details-modal');
    
    if (title) title.innerText = 'Confirmação';
    if (body) {
        body.innerHTML = `
            <p style="margin-bottom: 20px;">${message}</p>
            <div class="modal-footer">
                <button class="btn-secondary" id="confirm-cancel">Cancelar</button>
                <button class="btn-primary" id="confirm-yes">Confirmar</button>
            </div>
        `;
    }
    if (modal) modal.classList.add('active');

    document.getElementById('confirm-cancel').onclick = closeModal;
    document.getElementById('confirm-yes').onclick = () => {
        callback();
        closeModal();
    };
}

export function promptAction(titleText, message, defaultValue, placeholder, callback) {
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');
    const modal = document.getElementById('details-modal');

    if (title) title.innerText = titleText;
    if (body) {
        body.innerHTML = `
            <div style="margin-bottom: 20px;">
                <p style="margin-bottom: 10px; color: var(--text-muted);">${message}</p>
                <input type="text" id="prompt-input" value="${defaultValue || ''}" placeholder="${placeholder || ''}" 
                    style="width: 100%; padding: 0.85rem; border: 1.5px solid var(--border-color); border-radius: 10px; font-size: 1rem; outline: none;">
            </div>
            <div class="modal-footer" style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem;">
                <button class="btn-secondary" id="prompt-cancel">Cancelar</button>
                <button class="btn-primary" id="prompt-confirm" style="min-width: 120px; padding: 0.65rem 1.5rem;">Confirmar</button>
            </div>
        `;
    }
    if (modal) modal.classList.add('active');
    
    const input = document.getElementById('prompt-input');
    if (input) {
        setTimeout(() => { input.focus(); input.select(); }, 100);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') document.getElementById('prompt-confirm').click();
        });
    }

    document.getElementById('prompt-cancel').onclick = () => closeModal();
    document.getElementById('prompt-confirm').onclick = () => {
        const val = document.getElementById('prompt-input').value;
        callback(val);
        closeModal();
    };
}

export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
