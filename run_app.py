import streamlit.web.cli as stcli
import os
import sys

def resolve_path(path):
    """Obtiene la ruta absoluta para recursos"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

if __name__ == "__main__":
    # Ruta al script principal de Streamlit
    script_path = resolve_path("App.py")
    
    # Cambiar al directorio del script para que las rutas relativas funcionen
    os.chdir(os.path.dirname(script_path))
    
    # Configurar argumentos para simular 'streamlit run App.py'
    sys.argv = [
        "streamlit",
        "run",
        script_path,
        "--global.developmentMode=false",
        "--server.port=8501",
        "--server.address=localhost",
        "--server.headless=true",
    ]
    
    # Ejecutar Streamlit
    sys.exit(stcli.main())
