import subprocess
import os

WRK_IMAGE = "williamyeh/wrk"
SERVER_URL = "http://host.docker.internal:5000/file"  
FILE_SIZES = [10, 50, 100, 200, 500, 1000]  
TEST_DURATION = "30s"  
THREADS = 12 
CONNECTIONS = 400  
OUTPUT_FILE = "wrk_results.txt" 

def run_wrk(file_size):
    """Executa o WRK para um tamanho de arquivo específico."""
    url = f"{SERVER_URL}/{file_size}"
    command = [
        "docker", "run", "--rm", WRK_IMAGE,
        f"-t{THREADS}", f"-c{CONNECTIONS}", f"-d{TEST_DURATION}", url
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

def main():
    """Executa os testes para diferentes tamanhos de arquivo e salva os resultados."""
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)  

    with open(OUTPUT_FILE, "w") as f:
        for size in FILE_SIZES:
            print(f"Executando teste para arquivo de {size} KB...")
            results = run_wrk(size)
            f.write(f"Resultados para {size} KB:\n")
            f.write(results + "\n")
            print(f"Teste para {size} KB concluído!")

    print(f"Testes completos! Resultados salvos em {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
