#!/usr/bin/env python3
"""
Teste SAM3 - Exemplo Oficial Simplificado
Testa SAM3 com frame real da câmera para debug
"""

import torch
from PIL import Image
import cv2
from sam3.model_builder import build_sam3_image_model
from sam3.model.sam3_image_processor import Sam3Processor

print("="*70)
print("  TESTE SAM3 - Exemplo Oficial")
print("="*70)

# Carregar modelo
print("\n1. Carregando modelo...")
model = build_sam3_image_model()
processor = Sam3Processor(model)
print("✓ Modelo carregado")

# Capturar frame da câmera
print("\n2. Capturando frame da câmera RTSP...")
rtsp_url = "rtsp://admin:t86kxyJQN7WYr3W@201.16.120.51:555/Streaming/Channels/101"
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("✗ Erro ao conectar na câmera!")
    exit(1)

ret, frame = cap.read()
cap.release()

if not ret:
    print("✗ Erro ao capturar frame!")
    exit(1)

print(f"✓ Frame capturado: {frame.shape}")

# Converter para PIL
pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
print(f"✓ Convertido para PIL: {pil_image.size}")

# Processar com SAM3
print("\n3. Processando com SAM3...")
inference_state = processor.set_image(pil_image)
print("✓ Imagem configurada no processor")

# Testar vários prompts
test_prompts = [
    "person",
    "sleeping person",
    "person sleeping",
    "human",
    "man",
    "woman",
    "chair",
    "table",
    "computer"
]

print("\n4. Testando prompts:\n")
for prompt in test_prompts:
    print(f"   Prompt: '{prompt}'")
    output = processor.set_text_prompt(state=inference_state, prompt=prompt)
    
    masks = output.get("masks", [])
    boxes = output.get("boxes", [])
    scores = output.get("scores", [])
    
    print(f"   → Masks: {len(masks)}, Boxes: {len(boxes)}, Scores: {len(scores)}")
    
    if len(scores) > 0:
        print(f"   → Scores: {[f'{s:.3f}' for s in scores[:3]]}")
        print(f"   ✓ ENCONTROU ALGO!")
    else:
        print(f"   ✗ Nada encontrado")
    print()

print("="*70)
print("\nSe NENHUM prompt encontrou nada:")
print("1. Verifique se há alguma pessoa/objeto na frente da câmera")
print("2. Teste com notebook oficial: examples/sam3_image_predictor_example.ipynb")
print("3. Verifique se o modelo foi baixado corretamente")
print("="*70)
