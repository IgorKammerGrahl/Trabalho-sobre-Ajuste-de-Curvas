from flask import Flask, request, send_file, jsonify
import json
import os
from datetime import datetime
import random
import time
import logging

app = Flask(__name__)

# Configurações
LOG_DIR = "/app/logs"
FILES_DIR = "files"
LOG_FILE = os.path.join(LOG_DIR, "server_logs.json")
REQUEST_TIMEOUT = 3  # segundos

# Inicialização segura de diretórios
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "server.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Dados em memória para performance
request_logs = []

def save_server_logs():
    """Salva logs formatados em arquivo com tratamento de erros"""
    try:
        with open(LOG_FILE, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "requests": request_logs
            }, f, indent=4)
    except Exception as e:
        logger.error(f"Falha ao salvar logs: {str(e)}")

def generate_dummy_file(size_kb):
    """Gera arquivo dummy otimizado com tamanho variável"""
    try:
        varied_size = max(1, int(size_kb * (1 + random.uniform(-0.1, 0.1))))
        file_path = os.path.join(FILES_DIR, f"{varied_size}kb.dat")
        
        if not os.path.exists(file_path):
            start_gen = time.time()
            with open(file_path, 'wb') as f:
                f.write(os.urandom(varied_size * 1024))  # Gera bytes aleatórios
            logger.info(f"Arquivo {file_path} gerado em {time.time()-start_gen:.2f}s")
            
        return file_path, varied_size
        
    except Exception as e:
        logger.error(f"Erro na geração de arquivo: {str(e)}")
        raise

@app.route('/health')
def health_check():
    """Endpoint de verificação de saúde do servidor"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "requests_processed": len(request_logs)
    }), 200

@app.route('/file/<int:size_kb>', methods=['GET'])
def handle_file_request(size_kb):
    """Processa requisições de arquivo com logging detalhado"""
    start_time = time.time()
    client_ip = request.remote_addr
    log_data = {
        "client_ip": client_ip,
        "requested_size": size_kb,
        "timestamp": datetime.now().isoformat(),
        "status": "failed"
    }

    try:
        # Gera arquivo dinâmico
        file_path, actual_size = generate_dummy_file(size_kb)
        
        # Log de sucesso
        log_data.update({
            "status": "success",
            "actual_size_kb": actual_size,
            "response_time": time.time() - start_time,
            "file_path": file_path
        })
        
        # Adiciona à lista de logs
        request_logs.append(log_data)
        
        # Envia arquivo com timeout
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"file_{actual_size}kb.dat",
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Erro na requisição: {str(e)}")
        log_data["error"] = str(e)
        request_logs.append(log_data)
        return jsonify({"error": "Erro interno do servidor"}), 500
        
    finally:
        save_server_logs()

def clean_old_files():
    """Limpeza periódica de arquivos gerados"""
    try:
        for filename in os.listdir(FILES_DIR):
            file_path = os.path.join(FILES_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"Arquivo removido: {file_path}")
    except Exception as e:
        logger.error(f"Erro na limpeza de arquivos: {str(e)}")

if __name__ == "__main__":
    clean_old_files()
    try:
        logger.info("Iniciando servidor...")
        app.run(
            host="0.0.0.0",
            port=5000,
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        logger.critical(f"Falha crítica no servidor: {str(e)}")
        raise