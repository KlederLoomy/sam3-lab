#!/usr/bin/env python3
"""
Detector de Cenário: Pessoa Dormindo
Detecta quando uma pessoa está em posição de sono/deitada
"""

import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

class SleepingDetector:
    def __init__(
        self,
        sam3_processor,
        confidence_threshold: float = 0.3,
        persistence_seconds: int = 10,
        check_interval_seconds: int = 2
    ):
        """
        Args:
            sam3_processor: Instância do Sam3Processor
            confidence_threshold: Score mínimo para considerar detecção válida
            persistence_seconds: Tempo que pessoa deve ficar deitada para alertar
            check_interval_seconds: Intervalo entre verificações (economizar recursos)
        """
        self.processor = sam3_processor
        self.confidence_threshold = confidence_threshold
        self.persistence_seconds = persistence_seconds
        self.check_interval = check_interval_seconds
        
        # Prompts para detectar pessoa deitada/dormindo
        self.sleep_prompts = [
            "person sleeping",
            "person lying down",
            "person laying down"
        ]
        
        # Estado de rastreamento
        self.detections_history: List[Dict] = []
        self.last_check_time: Optional[datetime] = None
        self.alert_cooldown_until: Optional[datetime] = None
        
    def should_check_frame(self, current_time: datetime) -> bool:
        """Verifica se deve processar o frame atual (controle de intervalo)"""
        if self.last_check_time is None:
            return True
        
        elapsed = (current_time - self.last_check_time).total_seconds()
        return elapsed >= self.check_interval
    
    def detect_sleeping_person(
        self, 
        frame: np.ndarray, 
        timestamp: datetime
    ) -> Optional[Dict]:
        """
        Detecta pessoa dormindo no frame
        
        Returns:
            Dict com informações da detecção ou None se não detectou
        """
        # Verificar intervalo de checagem
        if not self.should_check_frame(timestamp):
            return None
        
        self.last_check_time = timestamp
        
        # Verificar cooldown de alerta
        if self.alert_cooldown_until and timestamp < self.alert_cooldown_until:
            return None
        
        # Processar frame com SAM3
        try:
            # Configurar imagem no processor
            from PIL import Image
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            inference_state = self.processor.set_image(pil_image)
            
            best_detection = None
            best_score = 0
            
            # Testar cada prompt
            for prompt in self.sleep_prompts:
                output = self.processor.set_text_prompt(
                    state=inference_state,
                    prompt=prompt
                )
                
                masks = output.get("masks", [])
                scores = output.get("scores", [])
                boxes = output.get("boxes", [])
                
                print(f"      🔍 Prompt: '{prompt}'")
                print(f"      📊 Masks: {len(masks)}, Scores: {len(scores)}, Boxes: {len(boxes)}")
                
                if len(scores) > 0:
                    print(f"      🎯 Scores encontrados:")
                    for idx, sc in enumerate(scores[:5]):  # Mostrar até 5
                        print(f"         [{idx}] Score: {sc:.4f}")
                
                # Verificar se encontrou algo com score aceitável
                for i, score in enumerate(scores):
                    if score > self.confidence_threshold and score > best_score:
                        best_score = score
                        best_detection = {
                            "prompt": prompt,
                            "score": float(score),
                            "box": boxes[i].tolist() if len(boxes) > i else None,
                            "mask_shape": masks[i].shape if len(masks) > i else None,
                            "timestamp": timestamp
                        }
            
            if best_detection:
                # Analisar orientação da bounding box
                if best_detection["box"]:
                    orientation = self._analyze_orientation(best_detection["box"])
                    best_detection["orientation"] = orientation
                
                # Adicionar ao histórico independente da orientação
                self._add_to_history(best_detection)
                
                # Verificar se persistiu tempo suficiente
                if self._check_persistence(timestamp):
                    alert = self._create_alert(best_detection, timestamp)
                    # Cooldown de 30 segundos após alerta
                    self.alert_cooldown_until = timestamp + timedelta(seconds=30)
                    return alert
            
            return None
            
        except Exception as e:
            print(f"Erro na detecção: {e}")
            return None
    
    def _analyze_orientation(self, box: List[float]) -> str:
        """
        Analisa se a bounding box está horizontal (deitado) ou vertical (em pé)
        
        Args:
            box: [x1, y1, x2, y2]
        """
        x1, y1, x2, y2 = box
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        aspect_ratio = width / height if height > 0 else 0
        
        # Se largura > altura, pessoa está deitada
        if aspect_ratio > 1.2:
            return "horizontal"
        else:
            return "vertical"
    
    def _add_to_history(self, detection: Dict):
        """Adiciona detecção ao histórico"""
        self.detections_history.append(detection)
        
        # Manter apenas últimos 60 segundos
        cutoff_time = detection["timestamp"] - timedelta(seconds=60)
        self.detections_history = [
            d for d in self.detections_history 
            if d["timestamp"] > cutoff_time
        ]
    
    def _check_persistence(self, current_time: datetime) -> bool:
        """
        Verifica se pessoa está deitada há tempo suficiente
        """
        if len(self.detections_history) < 2:
            return False
        
        # Verificar continuidade nos últimos N segundos
        cutoff_time = current_time - timedelta(seconds=self.persistence_seconds)
        recent_detections = [
            d for d in self.detections_history 
            if d["timestamp"] > cutoff_time
        ]
        
        # Se tem detecções suficientes no período
        return len(recent_detections) >= (self.persistence_seconds / self.check_interval) * 0.7
    
    def _create_alert(self, detection: Dict, timestamp: datetime) -> Dict:
        """
        Cria estrutura de alerta (5W2H)
        """
        return {
            "what": "Pessoa dormindo detectada",
            "when": timestamp.isoformat(),
            "where": {
                "location": "Camera Feed",
                "bounding_box": detection["box"],
                "orientation": detection["orientation"]
            },
            "who": "Sistema de Detecção SAM3",
            "why": f"Pessoa em posição horizontal por mais de {self.persistence_seconds}s",
            "how": {
                "method": "SAM3 Text Prompt Detection",
                "prompt_used": detection["prompt"],
                "confidence_score": detection["score"]
            },
            "how_much": {
                "detection_count_in_period": len(self.detections_history),
                "persistence_seconds": self.persistence_seconds
            },
            "metadata": {
                "alert_type": "sleeping_person",
                "severity": "medium",
                "requires_action": True
            }
        }


# Teste do detector
if __name__ == "__main__":
    print("Detector de Pessoa Dormindo")
    print("="*50)
    print("\nEste módulo será usado quando o modelo SAM3 estiver disponível")
    print("\nConfiguração:")
    print("- Threshold de confiança: 0.3")
    print("- Tempo de persistência: 10 segundos")
    print("- Intervalo de checagem: 2 segundos")
    print("\nPrompts utilizados:")
    detector = SleepingDetector(None)
    for prompt in detector.sleep_prompts:
        print(f"  - {prompt}")
