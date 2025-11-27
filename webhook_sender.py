#!/usr/bin/env python3
"""
Webhook Sender - Envia alertas via HTTP POST
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional
import time

class WebhookSender:
    def __init__(
        self,
        webhook_url: str,
        timeout_seconds: int = 10,
        retry_attempts: int = 3,
        retry_delay: int = 2
    ):
        """
        Args:
            webhook_url: URL do endpoint webhook
            timeout_seconds: Timeout da requisição HTTP
            retry_attempts: Número de tentativas em caso de falha
            retry_delay: Delay entre tentativas (segundos)
        """
        self.webhook_url = webhook_url
        self.timeout = timeout_seconds
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
    def send_alert(self, alert_data: Dict) -> bool:
        """
        Envia alerta para o webhook
        
        Args:
            alert_data: Dicionário com dados do alerta (formato 5W2H)
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        # Adicionar metadata de envio
        payload = {
            **alert_data,
            "sent_at": datetime.now().isoformat(),
            "sender": "SAM3-Lab"
        }
        
        for attempt in range(1, self.retry_attempts + 1):
            try:
                print(f"Enviando alerta (tentativa {attempt}/{self.retry_attempts})...")
                
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 201, 202]:
                    print(f"✓ Alerta enviado com sucesso! Status: {response.status_code}")
                    return True
                else:
                    print(f"✗ Webhook retornou status: {response.status_code}")
                    print(f"  Resposta: {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                print(f"✗ Timeout na tentativa {attempt}")
            except requests.exceptions.ConnectionError:
                print(f"✗ Erro de conexão na tentativa {attempt}")
            except Exception as e:
                print(f"✗ Erro inesperado: {e}")
            
            # Aguardar antes de tentar novamente
            if attempt < self.retry_attempts:
                print(f"  Aguardando {self.retry_delay}s antes de tentar novamente...")
                time.sleep(self.retry_delay)
        
        print(f"✗ Falha ao enviar alerta após {self.retry_attempts} tentativas")
        return False
    
    def test_connection(self) -> bool:
        """Testa se o webhook está acessível"""
        test_payload = {
            "test": True,
            "message": "Teste de conexão do SAM3-Lab",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            print(f"Testando conexão com {self.webhook_url}...")
            response = requests.post(
                self.webhook_url,
                json=test_payload,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201, 202]:
                print(f"✓ Webhook acessível! Status: {response.status_code}")
                return True
            else:
                print(f"✗ Webhook retornou status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Erro ao testar webhook: {e}")
            return False


# Teste
if __name__ == "__main__":
    print("Webhook Sender - Teste")
    print("="*50)
    
    # Exemplo com webhook de teste (webhook.site)
    # Você pode gerar um em: https://webhook.site
    test_url = "https://hook.us1.make.com/miyytagdrn6qhkhydykfq9ggrra1uvrd"
    
    sender = WebhookSender(test_url)
    
    # Teste de conexão
    sender.test_connection()
    
    # Exemplo de alerta
    example_alert = {
        "what": "Teste de alerta",
        "when": datetime.now().isoformat(),
        "where": {"location": "Test Camera"},
        "who": "Sistema de Teste",
        "why": "Validação do webhook",
        "how": {"method": "Manual test"},
        "how_much": {"count": 1}
    }
    
    sender.send_alert(example_alert)
