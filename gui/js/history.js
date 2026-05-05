/**
 * history.js
 * Lógica da Aba "Histórico e Gestão"
 */
import { api } from './bridge.js';
import { showToast, formatCPF, applyHighlight, closeModal, promptAction, debounce } from './ui.js';

let state = {
    currentPage: 1,
    recordsPerPage: 10,
    totalRecords: 0,
    currentSortColumn: 'id',
    currentSortDir: 'DESC'
};

export function initHistoryView() {
    loadHistory();
    setupPagination();
    setupFilters();
    setupEditForm();
}

export async function updateDashboard() {
    const stats = await api.call('get_dashboard_stats');
    if (stats) {
        const updateEl = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.innerText = val || 0;
        };
        updateEl('stat-total', stats.total_terms);
        updateEl('stat-active', stats.active_devices);
        updateEl('stat-users', stats.active_users);
        updateEl('stat-finished', stats.finished_terms);
    }
}

export async function loadHistory() {
    const filters = {
        cpf: document.getElementById('search-cpf').value,
        imei: document.getElementById('search-imei').value,
        name: document.getElementById('search-name').value,
        status: document.getElementById('search-status').value,
        category: document.getElementById('search-category').value,
        filial: document.getElementById('search-filial').value
    };

    const tbody = document.getElementById('history-body');
    const loadingIndicator = document.getElementById('history-loading-indicator');
    const refreshBtn = document.getElementById('btn-refresh');

    try {
        if (loadingIndicator) loadingIndicator.style.display = 'block';
        tbody.classList.add('loading-state');

        // Proteção contra spam no botão de atualizar
        if (refreshBtn) {
            if (refreshBtn.disabled) return;
            refreshBtn.disabled = true;
            refreshBtn.innerText = '⏳...';
        }

        updateSortIcons();

        // Delay artificial (800ms) apenas se for uma carga manual ou inicial pesada
        await new Promise(resolve => setTimeout(resolve, 800));

        const result = await api.call('get_history', 
            filters.cpf, filters.imei, state.recordsPerPage, 
            (state.currentPage - 1) * state.recordsPerPage,
            state.currentSortColumn, state.currentSortDir,
            filters.name, filters.status, filters.category, filters.filial
        );

        tbody.innerHTML = '';
        tbody.classList.remove('loading-state');
        if (loadingIndicator) loadingIndicator.style.display = 'none';

        if (!result || !result.data || result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--text-muted);">Nenhum registro encontrado.</td></tr>';
            return;
        }

        state.totalRecords = result.total_records || 0;
        renderTableRows(result.data, filters);
        renderPagination();

    } catch (error) {
        console.error("Erro ao carregar histórico:", error);
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: red;">Erro ao carregar dados.</td></tr>';
    } finally {
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        tbody.classList.remove('loading-state');
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerText = 'Atualizar';
        }
    }
}

function renderTableRows(data, filters) {
    const tbody = document.getElementById('history-body');
    data.forEach(item => {
        const nomeStr = item.nome || "Não informado";
        const cpfStr = formatCPF(item.cpf) || "000.000.000-00";
        const imeiStr = item.imei || "S/N";
        const dataEntrega = item.data_entrega ? item.data_entrega.split('-').reverse().join('/') : '--/--/----';

        const highlightedName = applyHighlight(nomeStr, filters.name, false);
        const highlightedCPF = applyHighlight(cpfStr, filters.cpf, true);
        const highlightedIMEI = applyHighlight(imeiStr, filters.imei, true);

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <div class="clickable-name" style="font-weight: 600; color: var(--primary); cursor: pointer;" data-cpf="${item.cpf}" data-nome="${nomeStr}">
                    ${highlightedName} <span class="counter">${item.total_colaborador || 0}</span>
                </div>
                <div class="sub-info" style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">
                    CPF: ${highlightedCPF} | ${item.filial || ''}
                </div>
            </td>
            <td>
                <div class="clickable-device" style="font-weight: 600; color: var(--primary); cursor: pointer;" data-imei="${imeiStr}" data-name="${item.marca || ''} ${item.modelo || ''}">
                    ${item.marca || ''} ${item.modelo || ''} <span class="counter">${item.total_equipamento || 0}</span>
                </div>
                <div class="sub-info" style="font-size: 0.75rem; color: var(--text-muted);">IMEI: ${highlightedIMEI}</div>
            </td>
            <td>${dataEntrega}</td>
            <td><span class="badge ${item.status === 'Ativo' ? 'badge-active' : 'badge-finalized'}">${item.status}</span></td>
            <td>
                <div class="actions">
                    <button class="btn-icon btn-pdf" data-path="${item.caminho_pdf}"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><path d="M12 18v-6"/><path d="m9 15 3 3 3-3"/></svg></button>
                    ${item.status === 'Ativo' ? `
                        <button class="btn-icon btn-edit" data-item='${encodeURIComponent(JSON.stringify(item))}'><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg></button>
                        <button class="btn-icon btn-chip" data-id="${item.id}" data-chip="${item.chip || ''}"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg></button>
                        <button class="btn-icon btn-release" data-imei="${imeiStr}"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg></button>
                    ` : ''}
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });

    // Event Delegation para ações da tabela
    tbody.onclick = handleTableActions;
}

function handleTableActions(e) {
    const target = e.target.closest('[data-cpf], [data-imei], [data-path], [data-item], [data-id]');
    if (!target) return;

    if (target.dataset.cpf) openColaboradorDetails(target.dataset.cpf, target.dataset.nome);
    else if (target.dataset.imei && target.classList.contains('clickable-device')) openEquipamentoDetails(target.dataset.imei, target.dataset.name);
    else if (target.dataset.path) window.pywebview.api.open_pdf(target.dataset.path.replace(/\\/g, '/'));
    else if (target.dataset.item) openEditModal(target.dataset.item);
    else if (target.dataset.id && target.dataset.chip !== undefined) editChip(target.dataset.id, target.dataset.chip);
    else if (target.dataset.imei && target.classList.contains('btn-release')) releaseDevice(target.dataset.imei);
}

// --- DOSSIÊS ---
async function openColaboradorDetails(cpf, nome) {
    const history = await api.call('get_colaborador_history', cpf);
    renderTimeline(`Dossiê do Colaborador: ${nome}`, history, (item) => `
        <strong>${item.marca} ${item.modelo}</strong><br>
        <small>IMEI: ${item.imei}</small>
    `);
}

async function openEquipamentoDetails(imei, deviceName) {
    const history = await api.call('get_equipamento_history', imei);
    renderTimeline(`Dossiê do Ativo: ${deviceName}`, history, (item) => `
        <strong>Colaborador: ${item.nome}</strong><br>
        <small>CPF: ${formatCPF(item.cpf)}</small>
    `);
}

function renderTimeline(title, history, contentFn) {
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    if (modalTitle) modalTitle.innerText = title;

    let html = '<div class="timeline">';
    if (!history || history.length === 0) {
        html = '<p>Nenhum histórico encontrado.</p>';
    } else {
        history.forEach(item => {
            const isAtivo = item.status === 'Ativo';
            const dataEntrega = item.data_entrega.split('-').reverse().join('/');
            const dataBaixa = item.data_baixa ? item.data_baixa.split(' ')[0].split('-').reverse().join('/') : '';
            html += `
                <div class="timeline-item">
                    <div class="timeline-dot ${isAtivo ? '' : 'finalized'}"></div>
                    <div class="timeline-content">
                        <span class="timeline-date">${dataEntrega} ${isAtivo ? '(Atual)' : '(Encerrado em ' + dataBaixa + ')'}</span>
                        ${contentFn(item)}<br>
                        <small style="color: var(--text-muted);">${item.tecnico}</small>
                        <span class="badge ${isAtivo ? 'badge-active' : 'badge-finalized'}" style="margin-top: 8px;">${item.status}</span>
                    </div>
                </div>
            `;
        });
    }
    html += '</div>';
    if (modalBody) modalBody.innerHTML = html;
    document.getElementById('details-modal').classList.add('active');
}

// --- AÇÕES DIRETAS ---
function releaseDevice(imei) {
    promptAction('Devolver Equipamento', 'Condição de devolução:', '', 'Ex: perfeito estado...', async (cond) => {
        const res = await api.call('release_equipment', imei, { condicao: cond });
        if (res && res.success) {
            showToast('Equipamento devolvido!');
            loadHistory();
            updateDashboard();
        } else {
            showToast('Erro ao devolver equipamento: ' + (res.error || 'Erro desconhecido'), 'error');
        }
    });
}

function editChip(id, currentChip) {
    promptAction('Editar Chip', 'Novo número do chip:', currentChip, '(11) 99999-9999', async (novoChip) => {
        // Permitimos vazio caso queira remover o chip
        const res = await api.call('update_chip', id, novoChip);
        if (res && res.success) {
            showToast('Chip atualizado!');
            loadHistory();
        } else {
            showToast('Erro ao atualizar chip.', 'error');
        }
    });
}

// --- FILTROS E PAGINAÇÃO ---
function setupPagination() {
    const actions = {
        'first-page': () => { state.currentPage = 1; },
        'prev-page': () => { if (state.currentPage > 1) state.currentPage--; },
        'next-page': () => { if (state.currentPage < Math.ceil(state.totalRecords / state.recordsPerPage)) state.currentPage++; },
        'last-page': () => { state.currentPage = Math.ceil(state.totalRecords / state.recordsPerPage); }
    };
    Object.keys(actions).forEach(id => {
        const el = document.getElementById(id);
        if (el) el.onclick = () => { actions[id](); loadHistory(); };
    });
}

function setupFilters() {
    const debouncedLoad = debounce(loadHistory, 300);
    ['search-cpf', 'search-imei', 'search-name'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.oninput = (e) => {
            if (id === 'search-cpf') e.target.value = formatCPF(e.target.value);
            state.currentPage = 1;
            debouncedLoad();
        };
    });
    ['search-status', 'search-category', 'search-filial', 'btn-refresh'].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        if (id === 'btn-refresh') el.onclick = loadHistory;
        else el.onchange = () => { state.currentPage = 1; loadHistory(); };
    });
}

// --- EDIÇÃO COMPLETA ---
function setupEditForm() {
    const form = document.getElementById('edit-term-form');
    if (form) form.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        const btn = document.getElementById('save-edit-btn');
        btn.disabled = true;
        
        const res = await api.call('edit_term', parseInt(data.id), data);
        if (res && res.success) {
            showToast('Termo editado!');
            closeModal();
            loadHistory();
        } else {
            showToast('Erro ao editar: ' + (res.error || 'Erro desconhecido'), 'error');
        }
        btn.disabled = false;
    };
}

function openEditModal(itemB64) {
    const item = JSON.parse(decodeURIComponent(itemB64));
    document.getElementById('edit-termo-id').value = item.id;
    document.getElementById('edit-name').value = item.nome;
    document.getElementById('edit-cpf').value = formatCPF(item.cpf);
    document.getElementById('edit-cargo').value = item.cargo || '';
    document.getElementById('edit-filial').value = item.filial || '';
    document.getElementById('edit-brand').value = item.marca;
    document.getElementById('edit-model').value = item.modelo;
    document.getElementById('edit-imei').value = item.imei;
    document.getElementById('edit-chip').value = item.chip || '';
    document.getElementById('edit-value').value = item.valor;
    document.getElementById('edit-delivery-date').value = item.data_entrega;
    document.getElementById('edit-description').value = item.descricao || '';
    document.getElementById('edit-category').value = item.categoria || 'Celular';
    document.getElementById('edit-term-modal').classList.add('active');
}

function updateSortIcons() {
    ['colaborador', 'equipamento', 'entrega', 'status'].forEach(col => {
        const icon = document.getElementById(`sort-${col}`);
        if (icon) {
            if (state.currentSortColumn === col) {
                icon.innerText = state.currentSortDir === 'ASC' ? ' ▲' : ' ▼';
                icon.style.opacity = '1';
            } else {
                icon.innerText = ' ⇅';
                icon.style.opacity = '0.3';
            }
        }
    });
}

function renderPagination() {
    const totalPages = Math.ceil(state.totalRecords / state.recordsPerPage);
    const display = document.getElementById('page-display');
    if (display) display.innerText = `Página ${state.currentPage} de ${totalPages || 1} (${state.totalRecords} registros)`;
}
