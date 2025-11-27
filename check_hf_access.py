#!/usr/bin/env python3
"""Verifica se o acesso ao SAM3 foi aprovado"""

from huggingface_hub import HfApi
import sys

try:
    api = HfApi()
    model_info = api.model_info("facebook/sam3")
    print("✅ ACESSO APROVADO! Você pode baixar o modelo SAM3.")
    print("\nExecute agora:")
    print("  python test_sam3_model.py")
    sys.exit(0)
except Exception as e:
    print("⏳ Acesso ainda não aprovado.")
    print(f"Erro: {e}")
    print("\nVerifique em: https://huggingface.co/facebook/sam3")
    sys.exit(1)
