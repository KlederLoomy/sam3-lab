#!/usr/bin/env python3
"""
Detector de Teste: Cor Rosa
Detecta objetos rosas na imagem (teste simplificado)
"""

import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional

class PinkDetector:
    def __init__(
        self,
        area_threshold: int = 500,  # Área mínima em pixels
        persistence_seconds: int = 3,
        check_interval_seconds: int = 1
    ):
        """
        Detector simples de cor rosa para teste
        """
        self.area_threshold = area_threshold
        self.persistence_seconds = persistence_seconds
        self.check_interval = check_interval_seconds
        
        self.detections_history = []
        self.last_check_time = None
        self.alert_cooldown_until = None
        
    def should_check_frame(self, current_time: datetime) -> bool:
        """Verifica se deve processar o frame atual"""
        if self.last_check_time is None:
            return True
        
        elapsed = (current_time - self.last_check_time).total_seconds()
        return elapsed >= self.check_interval
    
    def detect_pink_object(
        self, 
        frame: np.ndarray, 
        timestamp: datetime
    ) -> Optional[Dict]:
        """
        Detecta objetos rosas no frame usando OpenCV
        """
        # Verificar intervalo
        if not self.should_check_frame(timestamp):
            return None
        
        self.last_check_time = timestamp
        
        # Verificar cooldown
        if self.alert_cooldown_until and timestamp < self.alert_cooldown_until:
            return None
        
        try:
            # Converter BGR para HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Definir range de rosa em HSV
            # Rosa: Hue ~300-330 (em OpenCV 0-180, então ~150-165)
            lower_pink = np.array([140, 50, 50])
            upper_pink = np.array([170, 255, 255])
            
            # Criar máscara
            mask = cv2.inRange(hsv, lower_pink, upper_pink)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            print(f"      🎨 Detectados {len(contours)} contornos rosas")
            
            # Verificar se há contornos grandes o suficiente
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                print(f"         Contorno {i}: área = {area:.0f} pixels")
                
                if area > self.area_threshold:
                    # Calcular bounding box
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    detection = {
                        "timestamp": timestamp,
                        "area": area,
                        "box": [x, y, x+w, y+h],
                        "score": min(area / 50000, 1.0)  # Normalizar score
                    }
                    
                    print(f"         ✓ ROSA DETECTADO! Área: {area:.0f}, Box: {detection['box']}")
                    
                    # Adicionar ao histórico
                    self._add_to_history(detection)
                    
                    # Verificar persistência
                    if self._check_persistence(timestamp):
                        alert = self._create_alert(detection, timestamp)
                        self.alert_cooldown_until = timestamp + timedelta(seconds=10)
                        return alert
            
            return None
            
        except Exception as e:
            print(f"❌ Erro na detecção de rosa: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _add_to_history(self, detection: Dict):
        """Adiciona detecção ao histórico"""
        self.detections_history.append(detection)
        
        # Manter apenas últimos 60 segundos
        cutoff_time = detection["timestamp"] - timedelta(seconds=60)
        self.detections_history = [
            d for d in self.detections_history 
            if d["timestamp"] > cutoff_time
        ]
        
        print(f"         Histórico: {len(self.detections_history)} detecções")
    
    def _check_persistence(self, current_time: datetime) -> bool:
        """Verifica se rosa está presente há tempo suficiente"""
        if len(self.detections_history) < 2:
            print(f"         Persistência: Muito poucas detecções ({len(self.detections_history)})")
            return False
        
        cutoff_time = current_time - timedelta(seconds=self.persistence_seconds)
        recent_detections = [
            d for d in self.detections_history 
            if d["timestamp"] > cutoff_time
        ]
        
        required = max(1, int((self.persistence_seconds / self.check_interval) * 0.7))
        has_persistence = len(recent_detections) >= required
        
        print(f"         Persistência: {len(recent_detections)}/{required} detecções necessárias")
        
        return has_persistence
    
    def _create_alert(self, detection: Dict, timestamp: datetime) -> Dict:
        """Cria alerta de objeto rosa detectado"""
        return {
            "what": "Objeto ROSA detectado (TESTE)",
            "when": timestamp.isoformat(),
            "where": {
                "location": "Camera Feed",
                "bounding_box": detection["box"],
                "area_pixels": detection["area"]
            },
            "who": "Sistema de Teste - Detector de Rosa",
            "why": f"Objeto rosa presente por mais de {self.persistence_seconds}s",
            "how": {
                "method": "OpenCV Color Detection (HSV)",
                "confidence_score": detection["score"],
                "area_threshold": self.area_threshold
            },
            "how_much": {
                "detection_count_in_period": len(self.detections_history),
                "persistence_seconds": self.persistence_seconds
            },
            "metadata": {
                "alert_type": "pink_object_test",
                "severity": "low",
                "requires_action": False
            }
        }


if __name__ == "__main__":
    print("Detector de Rosa - Teste")
    print("="*50)
    print("Este é um detector simplificado para validar o sistema")
    print("Mostre algo ROSA para a câmera!")
