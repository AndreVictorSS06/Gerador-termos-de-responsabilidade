/**
 * app.js
 * Ponto de entrada da aplicação (Main Orchestrator)
 */
import { initGenerateView } from './generate.js';
import { initHistoryView, updateDashboard, loadHistory } from './history.js';
import { loadLogs } from './logs.js';
import { closeModal } from './ui.js';

document.addEventListener('DOMContentLoaded', () => {
    // Inicialização Geral
    const deliveryDateInput = document.getElementById('delivery-date');
    if (deliveryDateInput) deliveryDateInput.valueAsDate = new Date();

    // Inicializa Views
    initGenerateView();
    initHistoryView();
    setupTabs();
    
    // Global Modal Listeners
    setupGlobalListeners();

    // Listener para quando um termo é criado (atualiza outras abas)
    window.addEventListener('term-created', () => {
        updateDashboard();
        loadHistory();
    });
});

function setupTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            const content = document.getElementById(tabId);
            if (content) content.classList.add('active');

            // Lógica específica ao trocar de aba
            if (tabId === 'history-view') {
                updateDashboard();
                loadHistory();
            } else if (tabId === 'logs-view') {
                loadLogs();
            }
        });
    });
}

function setupGlobalListeners() {
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.onclick = closeModal;
    });

    window.onclick = (e) => {
        if (e.target.id === 'details-modal' || e.target.id === 'edit-term-modal') {
            closeModal();
        }
    };
}
