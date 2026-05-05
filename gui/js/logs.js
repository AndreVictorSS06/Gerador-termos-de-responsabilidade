/**
 * logs.js
 * Lógica da Aba "Auditoria"
 */
import { api } from './bridge.js';

export async function loadLogs() {
    const tbody = document.getElementById('logs-body');
    const refreshBtn = document.getElementById('btn-refresh-logs');
    if (!tbody) return;

    // Prevenção de "porrada no banco": desabilita o botão temporariamente
    if (refreshBtn) {
        if (refreshBtn.disabled) return; // Já está carregando
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<span>⏳ Atualizando...</span>';
        
        // Garante que o listener de clique esteja configurado (apenas uma vez)
        if (!refreshBtn.dataset.listener) {
            refreshBtn.onclick = loadLogs;
            refreshBtn.dataset.listener = 'true';
        }
    }

    try {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:2rem;">Carregando logs...</td></tr>';
        
        // Pequeno delay artificial (800ms) para evitar spam e suavizar a UI
        await new Promise(resolve => setTimeout(resolve, 800));
        
        const logs = await api.call('get_logs');
        
        tbody.innerHTML = '';
        if (!logs || logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:2rem;">Nenhum log registrado.</td></tr>';
            return;
        }

        logs.forEach(log => {
            const tr = document.createElement('tr');
            const dataFormatada = log.criado_em.split('.')[0].replace(' ', ' às ');
            
            let actionClass = 'log-badge';
            const action = log.acao.toLowerCase();
            if (action.includes('criacao')) actionClass += ' log-criacao';
            else if (action.includes('edicao_completa')) actionClass += ' log-edicao_completa';
            else if (action.includes('edicao')) actionClass += ' log-edicao';
            else if (action.includes('devolucao')) actionClass += ' log-devolucao';
            else if (action.includes('chip')) actionClass += ' log-edicao_chip';

            tr.innerHTML = `
                <td class="log-time">${dataFormatada}</td>
                <td class="log-user">${log.usuario}</td>
                <td><span class="${actionClass}">${log.acao}</span></td>
                <td><small>${log.entidade} #${log.entidade_id}</small></td>
                <td style="font-size: 0.85rem; max-width: 300px;">${log.detalhes}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:red; padding:2rem;">Erro ao carregar logs.</td></tr>';
    } finally {
        // Reabilita o botão após a conclusão
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
                Atualizar Logs
            `;
        }
    }
}
