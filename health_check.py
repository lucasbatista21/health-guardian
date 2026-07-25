import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone, timedelta

LATENCY_THRESHOLD_SECONDS = 1.5

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

def generate_html_dashboard(results):
    """Gera uma pagina de status HTML estatica com os resultados."""
    brt_timezone = timezone(timedelta(hours=-3))
    now_brt = datetime.now(brt_timezone).strftime("%d/%m/%Y às %H:%M:%S (Horário de Brasília)")
    
    cards_html = ""
    for r in results:
        status_badge = '<span style="background-color: #2da44e; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.85em;">ONLINE</span>' if r["healthy"] else '<span style="background-color: #cf222e; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.85em;">OFFLINE</span>'
        
        cards_html += f"""
        <div style="border: 1px solid #d0d7de; border-radius: 6px; padding: 16px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0 0 6px 0; font-size: 1.1em;">{r['name']}</h3>
                <p style="margin: 0; font-size: 0.85em; color: #57606a;">{r['url']}</p>
            </div>
            <div style="text-align: right;">
                <div style="margin-bottom: 6px;">{status_badge}</div>
                <small style="color: #57606a;">Status: {r['status_code']} | Latência: {r['latency_ms']}ms</small>
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health Guardian - Status Page</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f6f8fa; color: #24292f; margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 650px; margin: 0 auto; background: white; border: 1px solid #d0d7de; border-radius: 8px; padding: 24px; box-shadow: 0 3px 6px rgba(140,149,159,0.15); }}
        h1 {{ font-size: 1.5em; margin-top: 0; border-bottom: 1px solid #d0d7de; padding-bottom: 12px; }}
        .footer {{ font-size: 0.8em; color: #57606a; margin-top: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Health Guardian Status Page</h1>
        <div style="margin-top: 20px;">
            {cards_html}
        </div>
        <div class="footer">
            Última verificação automatizada em: <strong>{now_brt}</strong><br>
            Powered by GitHub Actions & Python
        </div>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("📄 Dashboard 'index.html' gerado com sucesso!")

def main():
    print("🔍 Iniciando verificação de saúde das aplicações...\n")
    
    with open("services.json", "r", encoding="utf-8") as f:
        services = json.load(f)
    
    results = []
    failed_services = []
    
    for service in services:
        result = check_service(service)
        results.append(result)
        
        status_icon = "✅" if result["healthy"] else "❌"
        print(f"{status_icon} [{result['name']}] Status: {result['status_code']} | Latência: {result['latency_ms']}ms")
        
        if not result["healthy"]:
            failed_services.append(result)

    # Gerar o arquivo HTML estatico
    generate_html_dashboard(results)

    # Se houver serviços com falha, envia alerta
    if failed_services:
        message = "🚨 *INCIDENTE DETECTADO - HEALTH GUARDIAN*\n\n"
        for item in failed_services:
            message += f"• *{item['name']}*\n  URL: `{item['url']}`\n  Status: `{item['status_code']}`\n\n"
        
        send_telegram_alert(message)

if __name__ == "__main__":
    main()