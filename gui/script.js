// Global State
let currentPage = 1;

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('delivery-date').valueAsDate = new Date();
    setupTabs();
    document.getElementById('mock-btn').addEventListener('click', fillMock);
    
    // Close Modal Events
    document.querySelector('.close-modal').addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target.id === 'details-modal') closeModal();
    });

    loadHistory();
    
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) { currentPage--; loadHistory(); }
    });
    document.getElementById('next-page').addEventListener('click', () => {
        currentPage++; loadHistory();
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
            document.getElementById(tabId).classList.add('active');
            if (tabId === 'history-view') {
                currentPage = 1;
                loadHistory();
                updateDashboard();
            }
        });
    });
}

// Dashboards
async function updateDashboard() {
    if (window.pywebview && window.pywebview.api) {
        const stats = await window.pywebview.api.get_dashboard_stats();
        document.getElementById('stat-active-users').innerText = stats.active_users;
        document.getElementById('stat-active-devices').innerText = stats.active_devices;
        document.getElementById('stat-total-terms').innerText = stats.total_terms;
    }
}

// Modais (Visão 360)
async function openColaboradorDetails(cpf, nome) {
    if (window.pywebview && window.pywebview.api) {
        const history = await window.pywebview.api.get_colaborador_history(cpf);
        document.getElementById('modal-title').innerText = `Dossiê: ${nome}`;
        let html = `<h4>Histórico de Equipamentos Vinculados:</h4><br>`;
        
        history.forEach(item => {
            html += `
                <div class="detail-row">
                    <div>
                        <strong>${item.marca} ${item.modelo}</strong><br>
                        <small>${item.imei}</small>
                    </div>
                    <div style="text-align: right;">
                        <span class="badge ${item.status === 'Ativo' ? 'badge-active' : 'badge-finalized'}">${item.status}</span><br>
                        <small>${item.data_entrega}</small>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('modal-body').innerHTML = html || '<p>Nenhum histórico encontrado.</p>';
        document.getElementById('details-modal').classList.add('active');
    }
}

async function openEquipamentoDetails(imei, deviceName) {
    if (window.pywebview && window.pywebview.api) {
        const history = await window.pywebview.api.get_equipamento_history(imei);
        document.getElementById('modal-title').innerText = `Ciclo de Vida: ${deviceName}`;
        let html = `<h4>Colaboradores que já utilizaram este item:</h4><br>`;
        
        history.forEach(item => {
            html += `
                <div class="detail-row">
                    <div>
                        <strong>${item.nome}</strong><br>
                        <small>CPF: ${item.cpf}</small>
                    </div>
                    <div style="text-align: right;">
                        <span class="badge ${item.status === 'Ativo' ? 'badge-active' : 'badge-finalized'}">${item.status}</span><br>
                        <small>Entregue em: ${item.data_entrega}</small>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('modal-body').innerHTML = html || '<p>Nenhum histórico encontrado.</p>';
        document.getElementById('details-modal').classList.add('active');
    }
}

function closeModal() {
    document.getElementById('details-modal').classList.remove('active');
}

// Load and Render History
async function loadHistory() {
    const cpf = document.getElementById('search-cpf').value;
    const imei = document.getElementById('search-imei').value;
    const tbody = document.getElementById('history-body');
    const pageDisplay = document.getElementById('page-display');

    if (window.pywebview && window.pywebview.api) {
        const history = await window.pywebview.api.get_history(cpf, imei, currentPage);
        tbody.innerHTML = '';
        pageDisplay.innerText = `Página ${currentPage}`;

        history.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <div style="font-weight: 600; color: var(--primary); cursor: pointer;" 
                         onclick="openColaboradorDetails('${item.cpf}', '${item.nome}')" title="Ver Dossiê">${item.nome}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">
                        ${item.cpf} <span class="counter" title="Total de termos vinculados">${item.total_colaborador}</span>
                    </div>
                </td>
                <td>
                    <div style="font-weight: 600; cursor: pointer; color: var(--primary);" 
                         onclick="openEquipamentoDetails('${item.imei}', '${item.marca} ${item.modelo}')" title="Ver Ciclo de Vida">${item.marca} ${item.modelo}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">
                        ${item.imei} <span class="counter" title="Total de vezes emprestado">${item.total_equipamento}</span>
                    </div>
                </td>
                <td style="font-size: 0.9rem;">${item.data_entrega}</td>
                <td>
                    <span class="badge ${item.status === 'Ativo' ? 'badge-active' : 'badge-finalized'}">${item.status}</span>
                </td>
                <td>
                    <div class="actions">
                        <button class="btn-icon" onclick="openPdf('${item.caminho_pdf.replace(/\\/g, '/')}')" title="Ver PDF">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><path d="M12 18v-6"/><path d="m9 15 3 3 3-3"/></svg>
                        </button>
                        ${item.status === 'Ativo' ? `
                            <button class="btn-icon" onclick="releaseDevice('${item.imei}')" title="Dar Baixa" style="color: var(--danger-color);">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                            </button>
                        ` : ''}
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
        document.getElementById('prev-page').disabled = (currentPage === 1);
        document.getElementById('next-page').style.visibility = (history.length < 10) ? 'hidden' : 'visible';
    }
}

async function openPdf(path) {
    if (window.pywebview && window.pywebview.api) {
        const result = await window.pywebview.api.open_pdf(path);
        if (!result.success) alert(result.error);
    }
}

async function releaseDevice(imei) {
    if (confirm(`Deseja dar baixa no equipamento Serial/IMEI ${imei}?`)) {
        const result = await window.pywebview.api.release_equipment(imei);
        if (result.success) {
            loadHistory();
            updateDashboard();
        } else {
            alert('Erro ao dar baixa.');
        }
    }
}

function fillMock() {
    document.getElementById('technician').value = 'Pedro Henrique';
    document.getElementById('name').value = 'Christian Sales Rodrigues';
    document.getElementById('cpf').value = '887.264.363-53';
    document.getElementById('brand').value = 'Samsung';
    document.getElementById('model').value = 'Galaxy A02s';
    document.getElementById('imei').value = '357268116377427';
    document.getElementById('value').value = '800';
    document.getElementById('description').value = 'Aparelho em excelente estado.\nAcompanha Carregador e Capinha.';
}
