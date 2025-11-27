#!/usr/bin/env python3
"""Teste de carregamento do modelo SAM3"""

print("Tentando carregar modelo SAM3...")

try:
    from sam3.model_builder import build_sam3_image_model
    from sam3.model.sam3_image_processor import Sam3Processor
    
    print("✓ Imports OK")
    print("Baixando modelo (pode demorar 5-10 minutos)...")
    
    model = build_sam3_image_model()
    print("✓ Modelo carregado!")
    
    processor = Sam3Processor(model)
    print("✓ Processor inicializado!")
    
    print("\n✅ SAM3 pronto para uso!")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    print("\nSe o erro for sobre acesso ao HuggingFace:")
    print("- Verifique se sua solicitação foi aprovada em:")
    print("  https://huggingface.co/facebook/sam3")
