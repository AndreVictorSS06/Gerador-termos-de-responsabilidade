import webview
import os
import sys
from app.bridge import Bridge

# Configuração de ambiente
DEBUG = True # Mudar para False em produção

def main():
    # Define o diretório base para encontrar os arquivos da GUI
    # Define diretórios (estáticos vs persistentes)
    if getattr(sys, 'frozen', False):
        gui_base = sys._MEIPASS
        data_base = os.path.dirname(sys.executable)
    else:
        gui_base = os.path.dirname(os.path.abspath(__file__))
        data_base = gui_base

    gui_dir = os.path.join(gui_base, 'gui')
    index_path = os.path.join(gui_dir, 'index.html')

    # Garantir estrutura de pastas persistentes
    for folder in ["data/termos/novos", "data/termos/editados", "data/assets"]:
        os.makedirs(os.path.join(data_base, folder), exist_ok=True)
    
    # Inicializa a Ponte (Controller)
    api = Bridge()

    # Cria a janela principal
    window = webview.create_window(
        title='STRS - Sistema de Termos de Responsabilidade Serrana',
        url=index_path,
        js_api=api,
        width=1100,
        height=850,
        resizable=True,
        min_size=(800, 600)
    )

    api.set_window(window)
    
    # Inicia a aplicação
    webview.start(debug=DEBUG, private_mode=True)

if __name__ == '__main__':
    main()
