import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse

LATENCY_THRESHOLD_SECONDS = 1.5

# Lendo credenciais das variáveis de ambiente (Prática segura de DevSecOps)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    """Envia alerta via API do Telegram se as credenciais estiverem configuradas."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Notificação via Telegram ignorada (variáveis de ambiente não configuradas).")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=payload)
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                print("📱 Alerta enviado com sucesso para o Telegram!")
    except Exception as e:
        print(f"❌ Falha ao enviar alerta no Telegram: {e}")

def check_service(service):
    name = service["name"]
    url = service["url"]
    
    start_time = time.time()
    
    try:
        request = urllib.request.Request(
            url, 
            headers={"User-Agent": "HealthGuardian/1.0"}
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            status_code = response.getcode()
            
    except urllib.error.HTTPError as e:
        status_code = e.code
    except urllib.error.URLError:
        status_code = 0
    except Exception:
        status_code = 500

    elapsed_time_ms = round((time.time() - start_time) * 1000, 2)
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
    
    with open("services.json", "r", encoding="utf-8") as f:
        services = json.load(f)
    
    failed_services = []
    
    for service in services:
        result = check_service(service)
        status_icon = "✅" if result["healthy"] else "❌"
        print(f"{status_icon} [{result['name']}] Status: {result['status_code']} | Latência: {result['latency_ms']}ms")
        
        if not result["healthy"]:
            failed_services.append(result)

    # Se houver serviços com falha, envia alerta consolidado
    if failed_services:
        message = "🚨 *INCIDENTE DETECTADO - HEALTH GUARDIAN*\n\n"
        for item in failed_services:
            message += f"• *{item['name']}*\n  URL: `{item['url']}`\n  Status: `{item['status_code']}`\n\n"
        
        send_telegram_alert(message)

if __name__ == "__main__":
    main()