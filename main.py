import webview
import os
import sys
from app.bridge import Bridge

def main():
    # Define o diretório base para encontrar os arquivos da GUI
    if getattr(sys, 'frozen', False):
        # Se rodando via executável (PyInstaller)
        base_dir = sys._MEIPASS
    else:
        # Se rodando via script normal
        base_dir = os.path.dirname(os.path.abspath(__file__))

    gui_dir = os.path.join(base_dir, 'gui')
    index_path = os.path.join(gui_dir, 'index.html')

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
    # debug=True habilita o Inspecionar Elemento (F12)
    webview.start(debug=True)

if __name__ == '__main__':
    main()
