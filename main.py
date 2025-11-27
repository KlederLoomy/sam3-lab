#!/usr/bin/env python3
"""
SAM3 Lab - Script Principal
Integra stream RTSP + SAM3 + Detectores + Webhook
"""

import yaml
import sys
import signal
from datetime import datetime
from pathlib import Path

# Imports dos módulos do lab
from rtsp_stream import RTSPStream
from scenario_sleeping_detector import SleepingDetector
from webhook_sender import WebhookSender

# Flag para shutdown gracioso
shutdown_requested = False

def signal_handler(signum, frame):
    """Handler para Ctrl+C"""
    global shutdown_requested
    print("\n\n🛑 Shutdown solicitado...")
    shutdown_requested = True

def load_config(config_path: str = "config.yaml"):
    """Carrega configurações do YAML"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    print("="*70)
    print("  SAM3 LAB - Sistema de Detecção para Segurança Condominial")
    print("="*70)
    
    # Configurar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Carregar configurações
    print("\n📋 Carregando configurações...")
    try:
        config = load_config()
        print("✓ Configurações carregadas")
    except Exception as e:
        print(f"✗ Erro ao carregar config.yaml: {e}")
        return 1
    
    # Inicializar SAM3
    print("\n🤖 Inicializando SAM3...")
    try:
        from sam3.model_builder import build_sam3_image_model
        from sam3.model.sam3_image_processor import Sam3Processor
        
        print("  Carregando modelo (pode demorar alguns minutos)...")
        model = build_sam3_image_model()
        processor = Sam3Processor(model)
        print("✓ SAM3 inicializado")
    except Exception as e:
        print(f"✗ Erro ao inicializar SAM3: {e}")
        print("\n💡 Dica: Verifique se:")
        print("  1. Seu acesso ao HuggingFace foi aprovado")
        print("  2. Você está autenticado (huggingface-cli login)")
        return 1
    
    # Inicializar detectores
    print("\n🔍 Inicializando detectores...")
    detectors = []
    
    if config['sleeping_detector']['enabled']:
        sleeping_det = SleepingDetector(
            sam3_processor=processor,
            confidence_threshold=config['sleeping_detector']['confidence_threshold'],
            persistence_seconds=config['sleeping_detector']['persistence_seconds'],
            check_interval_seconds=config['sleeping_detector']['check_interval_seconds']
        )
        detectors.append(('sleeping', sleeping_det))
        print("✓ Detector de pessoa dormindo ativado")
    
    if not detectors:
        print("✗ Nenhum detector ativado! Verifique config.yaml")
        return 1
    
    # Inicializar webhook
    print("\n📡 Configurando webhook...")
    webhook = WebhookSender(
        webhook_url=config['webhook']['url'],
        timeout_seconds=config['webhook']['timeout'],
        retry_attempts=config['webhook']['retry_attempts'],
        retry_delay=config['webhook']['retry_delay']
    )
    
    if not webhook.test_connection():
        print("⚠️  Webhook não acessível, mas continuando...")
    
    # Inicializar stream RTSP
    print("\n📹 Conectando ao stream RTSP...")
    stream = RTSPStream(
        rtsp_url=config['rtsp']['url'],
        fps_target=config['rtsp']['fps_target']
    )
    
    try:
        stream.connect()
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        return 1
    
    # Callback de processamento de frame
    def process_frame(frame, timestamp):
        global shutdown_requested
        
        if shutdown_requested:
            return
        
        print(f"\n⏰ {timestamp.strftime('%H:%M:%S')} - Processando frame...")
        
        # Executar cada detector
        for detector_name, detector in detectors:
            try:
                if detector_name == 'sleeping':
                    alert = detector.detect_sleeping_person(frame, timestamp)
                    
                    if alert:
                        print(f"\n🚨 ALERTA: {alert['what']}")
                        print(f"   Confiança: {alert['how']['confidence_score']:.2f}")
                        
                        # Enviar para webhook
                        webhook.send_alert(alert)
                        
                        # Salvar log local
                        log_path = Path(config['logging']['log_dir'])
                        log_path.mkdir(exist_ok=True)
                        
                        log_file = log_path / f"alert_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
                        import json
                        with open(log_file, 'w') as f:
                            json.dump(alert, f, indent=2)
                        print(f"   Log salvo: {log_file}")
                
            except Exception as e:
                print(f"✗ Erro no detector {detector_name}: {e}")
    
    # Iniciar processamento
    print("\n" + "="*70)
    print("🚀 SISTEMA ATIVO - Monitorando stream...")
    print("   Pressione Ctrl+C para parar")
    print("="*70)
    
    try:
        stream.process_stream(process_frame)
    except Exception as e:
        print(f"\n✗ Erro no processamento: {e}")
        return 1
    finally:
        print("\n✓ Sistema encerrado")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
