/**
 * generate.js
 * Lógica da Aba "Novo Termo"
 */
import { api } from './bridge.js';
import { showToast, formatCPF, confirmAction, promptAction } from './ui.js';

export function initGenerateView() {
    const termForm = document.getElementById('term-form');
    if (termForm) termForm.addEventListener('submit', handleFormSubmit);

    const cpfInput = document.getElementById('cpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', (e) => e.target.value = formatCPF(e.target.value));
        cpfInput.addEventListener('blur', handleCPFBlur);
    }

    const imeiInput = document.getElementById('imei');
    if (imeiInput) {
        imeiInput.addEventListener('input', handleIMEIInput);
        imeiInput.addEventListener('blur', handleIMEIBlur);
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById('generate-btn');
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    btn.disabled = true;
    btn.innerHTML = '<span>⏳ Gerando...</span>';

    try {
        const result = await api.call('generate_term', data);
        if (result.success) {
            showToast('Termo gerado com sucesso!');
            e.target.reset();
            document.getElementById('delivery-date').valueAsDate = new Date();
            // Dispara evento para atualizar outras abas se necessário
            window.dispatchEvent(new CustomEvent('term-created'));
        } else {
            showToast('Erro ao gerar termo: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Falha de comunicação com o sistema.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><path d="M12 18v-6"/><path d="m9 15 3 3 3-3"/></svg>
            Gerar Termo de Responsabilidade
        `;
    }
}

async function handleCPFBlur(e) {
    const cpfVal = e.target.value.trim();
    if (cpfVal.length === 14) {
        const result = await api.call('get_colaborador_by_cpf', cpfVal);
        if (result && result.success) {
            document.getElementById('name').value = result.nome || '';
            document.getElementById('cargo').value = result.cargo || '';
            showToast('Dados do colaborador carregados.', 'info');
        }
    }
}

function handleIMEIInput(e) {
    const category = document.getElementById('category').value;
    if (category === 'Celular' || category === 'Tablet') {
        let val = e.target.value.replace(/\D/g, '');
        if (val.length > 15) val = val.substring(0, 15);
        e.target.value = val;
    }
    document.getElementById('generate-btn').disabled = false;
    e.target.style.borderColor = '';
}

async function handleIMEIBlur(e) {
    const imeiVal = e.target.value.trim();
    const category = document.getElementById('category').value;
    if (!imeiVal) return;

    if ((category === 'Celular' || category === 'Tablet') && imeiVal.length < 15) {
        showToast('IMEI inválido! Deve conter 15 dígitos.', 'error');
        document.getElementById('generate-btn').disabled = true;
        e.target.style.borderColor = 'red';
        return;
    }

    const result = await api.call('check_imei_active', imeiVal);
    if (result && result.equipamento) {
        document.getElementById('brand').value = result.equipamento.marca || '';
        document.getElementById('model').value = result.equipamento.modelo || '';
        document.getElementById('value').value = result.equipamento.valor || '';
    }

    if (result && result.active) {
        document.getElementById('generate-btn').disabled = true;
        e.target.style.borderColor = 'red';
        confirmAction(
            `Atenção: O equipamento está com <b>${result.nome}</b>. Deseja dar baixa para prosseguir?`,
            () => {
                promptAction('Baixa de Equipamento', 'Condição de devolução:', '', 'Ex: perfeito estado...', async (cond) => {
                    if (cond) {
                        const res = await api.call('release_equipment', imeiVal, { condicao: cond });
                        if (res.success) {
                            showToast('Liberado! Pode prosseguir.', 'success');
                            document.getElementById('generate-btn').disabled = false;
                            e.target.style.borderColor = '#10b981';
                        }
                    }
                });
            }
        );
    }
}
