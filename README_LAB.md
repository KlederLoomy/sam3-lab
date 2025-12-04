# 🏢 SAM3 Lab - Detecção de Segurança Condominial

## 📋 Objetivo

Avaliar a aplicabilidade do modelo de IA **SAM 3** (Segment Anything Model 3) em cenários reais de detecção de elementos de vídeo para segurança condominial.

## 🎯 Cenários de Detecção

### ✅ Implementados
- **Pessoa Dormindo** - Detecta porteiro ou pessoas em posição de sono

### 🚧 Planejados
- **Criança na Piscina** - Detecta criança desacompanhada em área de piscina
- **Pessoa em Local Proibido** - Detecta pessoas em áreas restritas
- **Adulto com Nanismo** - Diferenciação entre criança e adulto com nanismo

## 🏗️ Arquitetura

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│ Câmera IP   │───▶│  RTSP Stream │───▶│  Frame Buffer   │
│  (RTSP)     │    │  Processor   │    │  (Ajustável)    │
└─────────────┘    └──────────────┘    └─────────────────┘
                                                │
                                                ▼
                   ┌─────────────────────────────────────┐
                   │         SAM3 Model                  │
                   │  (Text Prompt Detection)            │
                   └─────────────────────────────────────┘
                                                │
                                                ▼
                   ┌─────────────────────────────────────┐
                   │    Scenario Detectors               │
                   │  • Sleeping Person                  │
                   │  • Child in Pool (TODO)             │
                   │  • Restricted Area (TODO)           │
                   └─────────────────────────────────────┘
                                                │
                                                ▼
                   ┌─────────────────────────────────────┐
                   │      Webhook Sender                 │
                   │   (HTTP POST - 5W2H Format)         │
                   └─────────────────────────────────────┘
```

## 📁 Estrutura do Projeto

```
/workspace/sam3-lab/
├── repo/                              # Código principal
│   ├── main.py                        # Script principal
│   ├── config.yaml                    # Configurações
│   ├── rtsp_stream.py                 # Processador RTSP
│   ├── scenario_sleeping_detector.py  # Detector: Pessoa dormindo
│   ├── webhook_sender.py              # Envio de alertas
│   ├── test_sam3_model.py            # Teste do modelo
│   ├── check_hf_access.py            # Verificar acesso HuggingFace
│   └── (SAM3 original files...)
├── videos/                            # Vídeos de teste
├── logs/                              # Logs de alertas (JSON)
├── webhooks/                          # Dados de webhook
└── checkpoints/                       # Modelos SAM3 (auto-download)
```

## ⚙️ Requisitos

- **GPU**: RTX 4090 (24GB VRAM)
- **Python**: 3.12+
- **PyTorch**: 2.7+ com CUDA 12.6+
- **Sistema**: Ubuntu 22.04 (Runpod containerizado)

## 🚀 Instalação

### 1. Ambiente já está configurado no Runpod

### 2. Verificar instalação
```bash
cd /workspace/sam3-lab/repo
python test_sam3_model.py
```

### 3. Configurar webhook
Edite `config.yaml` e adicione sua URL de webhook:
```yaml
webhook:
  url: "https://seu-webhook.com/endpoint"
```

Você pode usar https://webhook.site para testes.

## 🎮 Como Usar

### Executar o sistema completo:
```bash
cd /workspace/sam3-lab/repo
python main.py
```

### Testar apenas o stream RTSP:
```bash
python rtsp_stream.py
```

### Testar apenas o webhook:
```bash
python webhook_sender.py
```

## 📊 Formato de Alerta (5W2H)

```json
{
  "what": "Pessoa dormindo detectada",
  "when": "2025-11-26T22:30:15.123456",
  "where": {
    "location": "Camera Feed",
    "bounding_box": [x1, y1, x2, y2],
    "orientation": "horizontal"
  },
  "who": "Sistema de Detecção SAM3",
  "why": "Pessoa em posição horizontal por mais de 10s",
  "how": {
    "method": "SAM3 Text Prompt Detection",
    "prompt_used": "person sleeping",
    "confidence_score": 0.87
  },
  "how_much": {
    "detection_count_in_period": 5,
    "persistence_seconds": 10
  },
  "metadata": {
    "alert_type": "sleeping_person",
    "severity": "medium",
    "requires_action": true
  }
}
```

## 🔧 Configuração

Edite `config.yaml` para ajustar:

- **FPS de processamento** (economizar recursos vs latência)
- **Thresholds de confiança** (precisão vs recall)
- **Tempo de persistência** (evitar falsos positivos)
- **URL do webhook**
- **Stream RTSP**

## 📈 Métricas de Performance

### Latência Objetivo
- **5-10 segundos** de delay aceitável

### Custo-Benefício
- Processar **1 frame/segundo** (configurável)
- Checar detecção a cada **2 segundos** (configurável)
- Cooldown de **30 segundos** após alerta

## 🔍 Status do Projeto

- ✅ Ambiente Runpod configurado
- ✅ SAM3 instalado e testado
- ✅ Stream RTSP implementado
- ✅ Detector "Pessoa Dormindo" implementado
- ✅ Webhook sender implementado
- ✅ Testes com câmera real Hikvision realizados
- 🔬 Debug e validação em andamento
- 🚧 Outros cenários em desenvolvimento

## 🧪 Descobertas Técnicas

### SAM3 Text Prompts - Limitações Identificadas

**Funciona:**
- ✅ "person" (98.3% confiança)
- ✅ "man" / "woman" (98%+ confiança)
- ✅ "chair" (92.5% confiança)
- ✅ "table", "computer" (alta confiança)

**Não funciona diretamente:**
- ❌ "sleeping person" (0 resultados)
- ❌ "person sleeping" (0 resultados)
- ❌ "person lying down" (0 resultados)

**Motivo:** SAM3 é treinado para **noun phrases simples** (objetos físicos), não para **estados/ações** (sleeping, running, etc). Para prompts complexos que exigem raciocínio, seria necessário o SAM3 Agent (MLLM).

### SAM3 Agent

O SAM3 Agent não é uma classe Python importável, mas sim um **notebook exemplo** (`examples/sam3_agent.ipynb`) que demonstra como usar um MLLM externo (vLLM ou API) para interpretar prompts complexos e chamar o SAM3.

**Complexidade:** Requer configuração de servidor MLLM adicional, o que adiciona overhead significativo.

**Decisão:** Não utilizaremos o Agent inicialmente. A abordagem de detectar "person" + análise temporal é mais simples e adequada.

## 🎯 Estratégia de Detecção Implementada

### Abordagem: Detecção de Pessoa + Persistência Temporal

1. **Detectar "person"** usando SAM3 (funciona com 98%+ confiança)
2. **Rastrear posição** da pessoa através de bounding boxes
3. **Calcular IoU** (Intersection over Union) entre detecções consecutivas
4. **Verificar persistência** - pessoa parada na mesma posição por X segundos
5. **Gerar alerta** quando critérios são atendidos

**Vantagens:**
- Usa apenas SAM3 base (sem dependências adicionais)
- Alta confiança de detecção (98%+)
- Funciona para pessoa dormindo em qualquer posição (sentada, deitada, etc)
- Configurável via `config.yaml`

## 📝 Próximos Passos

1. ⏳ Aguardar aprovação modelo SAM3 no HuggingFace
2. 🧪 Testar com stream real de câmera
3. 📊 Coletar métricas de performance (GPU, latência, precisão)
4. 💰 Calcular custo por hora de operação
5. 🎯 Implementar outros detectores (criança na piscina, etc)
6. 🔄 Otimizar FPS e intervalos baseado em resultados

## 🤝 Contribuindo

Este é um projeto de pesquisa/laboratório. 

## 📄 Licença

Segue a licença do SAM3 original.

## 🔗 Links

- Repositório SAM3 oficial: https://github.com/facebookresearch/sam3
- Fork do laboratório: https://github.com/KlederLoomy/sam3-lab
- HuggingFace SAM3: https://huggingface.co/facebook/sam3

---

**Desenvolvido com ❤️ para melhorar a segurança condominial através de IA**
