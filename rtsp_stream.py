#!/usr/bin/env python3
"""
Captura e processa stream RTSP
"""

import cv2
import time
from datetime import datetime

class RTSPStream:
    def __init__(self, rtsp_url, fps_target=1):
        """
        Args:
            rtsp_url: URL do stream RTSP
            fps_target: Quantos frames por segundo processar (1 = 1 frame/seg)
        """
        self.rtsp_url = rtsp_url
        self.fps_target = fps_target
        self.cap = None
        
    def connect(self):
        """Conecta ao stream RTSP"""
        print(f"Conectando a {self.rtsp_url}...")
        self.cap = cv2.VideoCapture(self.rtsp_url)
        
        if not self.cap.isOpened():
            raise Exception("Não foi possível conectar ao stream RTSP")
        
        print("✓ Conectado com sucesso!")
        return True
    
    def get_frame(self):
        """Captura um frame"""
        if self.cap is None:
            raise Exception("Stream não conectado. Execute connect() primeiro.")
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        return frame
    
    def process_stream(self, callback, max_frames=None):
        """
        Processa stream continuamente
        
        Args:
            callback: Função que recebe (frame, timestamp) para processar
            max_frames: Limite de frames (None = infinito)
        """
        frame_interval = 1.0 / self.fps_target
        frame_count = 0
        
        print(f"Processando stream a {self.fps_target} FPS...")
        
        try:
            while True:
                start_time = time.time()
                
                frame = self.get_frame()
                if frame is None:
                    print("Stream encerrado ou erro na captura")
                    break
                
                timestamp = datetime.now()
                
                # Chamar callback de processamento
                callback(frame, timestamp)
                
                frame_count += 1
                if max_frames and frame_count >= max_frames:
                    print(f"Limite de {max_frames} frames atingido")
                    break
                
                # Controlar FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\nProcessamento interrompido pelo usuário")
        finally:
            self.disconnect()
    
    def disconnect(self):
        """Desconecta do stream"""
        if self.cap:
            self.cap.release()
            print("✓ Stream desconectado")

# Exemplo de uso
if __name__ == "__main__":
    # Stream de teste público
    test_url = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4"
    
    def process_frame(frame, timestamp):
        print(f"Frame capturado em {timestamp.strftime('%H:%M:%S')} - Shape: {frame.shape}")
    
    stream = RTSPStream(test_url, fps_target=1)
    stream.connect()
    stream.process_stream(process_frame, max_frames=5)
