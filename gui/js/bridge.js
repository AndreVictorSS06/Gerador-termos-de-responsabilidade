/**
 * bridge.js
 * Centraliza a comunicação com a API Python do PyWebView
 */

export const api = {
    async call(method, ...args) {
        if (window.pywebview && window.pywebview.api && window.pywebview.api[method]) {
            try {
                // Delay de segurança global (300ms) para suavizar a interface e proteger o banco
                const delay = new Promise(resolve => setTimeout(resolve, 300));
                
                const [result] = await Promise.all([
                    window.pywebview.api[method](...args),
                    delay
                ]);
                
                return result;
            } catch (error) {
                console.error(`Erro na chamada API [${method}]:`, error);
                throw error;
            }
        }
        console.warn(`API PyWebView não disponível ou método [${method}] não encontrado.`);
        return null;
    }
};
