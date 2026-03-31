import streamlit.web.cli as stcli
import os, sys, logging

# Configurar logs en un archivo temporal para depurar el EXE
log_path = os.path.join(os.environ.get('TEMP', '.'), 'astor_exe_debug.log')
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def resolve_path(path):
    # PyInstaller extrae archivos a _MEIPASS
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.normpath(os.path.join(base_path, path))

if __name__ == "__main__":
    try:
        logging.info("Iniciando AstorSimulador...")
        
        script_path = resolve_path("Astor.py")
        logging.info(f"Ruta del script resuelta: {script_path}")
        
        if not os.path.exists(script_path):
            logging.error(f"ERROR: No se encontró Astor.py en {script_path}")
            sys.exit(1)

        # Cambiar al directorio del script
        os.chdir(os.path.dirname(script_path))
        logging.info(f"Directorio de trabajo: {os.getcwd()}")
        
        # Argumentos para Streamlit
        sys.argv = [
            "streamlit",
            "run",
            script_path,
            "--global.developmentMode=false",
            "--server.port=8501",
            "--server.address=localhost",
            "--server.headless=false",
        ]
        
        logging.info("Ejecutando stcli.main()...")
        sys.exit(stcli.main())
        
    except Exception as e:
        logging.exception("Falla crítica en run_app.py")
        with open("error_critico_astor.txt", "w") as f:
            f.write(str(e))
        sys.exit(1)
