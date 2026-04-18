document.getElementById('term-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    console.log('Sending data to Python:', data);

    // Call the Python API
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.generate_term(data).then(response => {
            if (response.success) {
                alert('Termo gerado com sucesso! ' + (response.message || ''));
            } else {
                alert('Erro ao gerar termo: ' + response.error);
            }
        });
    } else {
        console.error('pywebview API not available');
        alert('Erro: Conexão com o sistema não estabelecida.');
    }
});

// Simple CPF mask (optional enhancement)
document.getElementById('cpf').addEventListener('input', function (e) {
    let x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,3})(\d{0,2})/);
    e.target.value = !x[2] ? x[1] : x[1] + '.' + x[2] + (x[3] ? '.' + x[3] : '') + (x[4] ? '-' + x[4] : '');
});

// Mock Data Filler
document.getElementById('mock-btn').addEventListener('click', function() {
    const testData = {
        'name': 'Christian Sales Rodrigues',
        'cpf': '887.264.363-53',
        'brand': 'Samsung',
        'model': 'Galaxy A02s',
        'imei': '357268116377427',
        'value': '850,00',
        'description': 'Aparelho em perfeito estado, acompanha carregador original e capa de proteção preta.'
    };

    for (const [key, value] of Object.entries(testData)) {
        const input = document.getElementById(key);
        if (input) input.value = value;
    }
    
    // Set a return date for test (1 year from now)
    const returnDate = new Date();
    returnDate.setFullYear(returnDate.getFullYear() + 1);
    document.getElementById('return-date').valueAsDate = returnDate;
});

// Set default delivery date to today
document.getElementById('delivery-date').valueAsDate = new Date();
