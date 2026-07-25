import json
import time
import urllib.request
import urllib.error

# Configuração do limite aceitável de latência (em segundos)
LATENCY_THRESHOLD_SECONDS = 1.5

def check_service(service):
    name = service["name"]
    url = service["url"]
    
    start_time = time.time()
    
    try:
        # Faz a requisição HTTP GET usando a biblioteca nativa do Python
        request = urllib.request.Request(
            url, 
            headers={"User-Agent": "HealthGuardian/1.0"}
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            status_code = response.getcode()
            
    except urllib.error.HTTPError as e:
        status_code = e.code
    except urllib.error.URLError:
        status_code = 0  # 0 indica falha total de conexão / DNS
    except Exception:
        status_code = 500

    # Calcula o tempo total de resposta em milissegundos
    elapsed_time_ms = round((time.time() - start_time) * 1000, 2)
    
    # Avalia se a resposta foi de sucesso (200-299)
    is_healthy = 200 <= status_code < 300
    
    return {
        "name": name,
        "url": url,
        "status_code": status_code,
        "latency_ms": elapsed_time_ms,
        "healthy": is_healthy
    }

def main():
    print("🔍 Iniciando verificação de saúde das aplicações...\n")
    
    # Carrega a lista de serviços a partir do arquivo JSON
    with open("services.json", "r", encoding="utf-8") as f:
        services = json.load(f)
    
    results = []
    
    for service in services:
        result = check_service(service)
        results.append(result)
        
        status_icon = "✅" if result["healthy"] else "❌"
        print(f"{status_icon} [{result['name']}] Status: {result['status_code']} | Latência: {result['latency_ms']}ms")

if __name__ == "__main__":
    main()