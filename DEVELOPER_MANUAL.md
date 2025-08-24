# Manual do Desenvolvedor ShortGPT

## Índice
1. [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
2. [Fluxo de Geração de Vídeo](#fluxo-de-geração-de-vídeo)
3. [Sistema de Engines](#sistema-de-engines)
4. [Sistema de Editing Steps](#sistema-de-editing-steps)
5. [Core Editing Engine](#core-editing-engine)
6. [Sistema de Flows](#sistema-de-flows)
7. [Templates e Prompts](#templates-e-prompts)
8. [Pontos de Extensão](#pontos-de-extensão)
9. [Exemplos Práticos](#exemplos-práticos)
10. [Referência Rápida](#referência-rápida)

---

## Visão Geral da Arquitetura

O ShortGPT é um framework para automação de geração de vídeos curtos que segue uma arquitetura modular e extensível:

```
┌─────────────────┐
│   Interface     │  (Gradio UI)
│   runShortGPT.py│
└────────┬────────┘
         │
┌────────▼────────┐
│   UI Tabs       │  (ui_tab_short_automation.py)
│                 │
└────────┬────────┘
         │
┌────────▼────────┐
│  Content Engine │  (ContentShortEngine, FactsShortEngine, RedditShortEngine)
│                 │
└────────┬────────┘
         │
┌────────▼────────┐
│ Editing Engine  │  (EditingEngine + EditingSteps)
│                 │
└────────┬────────┘
         │
┌────────▼────────┐
│ Core Editing    │  (CoreEditingEngine)
│    Engine       │
└─────────────────┘
```

### Componentes Principais:

1. **Interface (Gradio)**: Ponto de entrada para usuários
2. **Content Engines**: Orquestram o processo de geração de conteúdo
3. **Editing Engine**: Constrói o schema JSON de edição
4. **Core Editing Engine**: Renderiza o vídeo final usando MoviePy

---

## Fluxo de Geração de Vídeo

### 1. Início do Processo

**Arquivo**: `runShortGPT.py`
```python
app = ShortGptUI(colab=False)
app.launch()  # Inicia servidor Gradio na porta 31415
```

### 2. Interface Gradio

**Arquivo**: `gui/ui_tab_short_automation.py`

Quando o usuário clica em "Create Shorts":
```python
def create_short(self, numShorts, short_type, ...):
    # 1. Valida parâmetros
    # 2. Cria instância do Engine apropriado
    shortEngine = self.create_short_engine(short_type=short_type, ...)
    
    # 3. Executa o processo de geração
    for step_num, step_info in shortEngine.makeContent():
        # Processa cada step sequencialmente
```

### 3. Execução dos Steps

O método `makeContent()` (em `abstract_content_engine.py:63`) executa cada step definido no `stepDict`:

```python
def makeContent(self):
    while (not self.isShortDone()):
        currentStep = self._db_last_completed_step + 1
        self.stepDict[currentStep]()  # Executa o step
        self._db_last_completed_step = currentStep
```

---

## Sistema de Engines

### Hierarquia de Classes

```
AbstractContentEngine
    └── ContentShortEngine
            ├── FactsShortEngine
            └── RedditShortEngine
```

### ContentShortEngine Steps

**Arquivo**: `shortGPT/engine/content_short_engine.py:33`

```python
self.stepDict = {
    1:  self._generateScript,          # Gera o roteiro usando GPT
    2:  self._generateTempAudio,       # Sintetiza voz (TTS)
    3:  self._speedUpAudio,            # Acelera áudio se necessário
    4:  self._timeCaptions,            # Gera legendas temporizadas (Whisper)
    5:  self._generateImageSearchTerms, # GPT gera termos de busca para imagens
    6:  self._generateImageUrls,       # Busca URLs de imagens (Pexels API)
    7:  self._chooseBackgroundMusic,   # Seleciona música de fundo
    8:  self._chooseBackgroundVideo,   # Seleciona vídeo de fundo
    9:  self._prepareBackgroundAssets, # Prepara e corta assets
    10: self._prepareCustomAssets,     # Assets customizados (override)
    11: self._editAndRenderShort,      # Renderiza vídeo final
    12: self._addYoutubeMetadata       # Gera título e descrição
}
```

### Persistência de Estado

O sistema usa TinyDB para persistir o estado entre execuções. Propriedades com prefixo `_db_` são automaticamente salvadas:

```python
# abstract_content_engine.py:29
def __setattr__(self, name, value):
    if name.startswith('_db_'):
        db_path = name[4:]  # remove '_db_' prefix
        self.dataManager.save(db_path, value)
```

---

## Sistema de Editing Steps

### Estrutura JSON dos Editing Steps

**Localização**: `shortGPT/editing_framework/editing_steps/`

Cada editing step é um arquivo JSON que define uma operação de edição:

#### Exemplo: `make_caption.json`
```json
{
  "caption": {
    "type": "text",
    "z": 4,  // Ordem de camada (z-index)
    "inputs": {
      "parameters": ["text"],
      "actions": ["set_time_start", "set_time_end"]
    },
    "parameters": {
      "text": null,
      "font_size": 80,
      "font": "fonts/LuckiestGuy-Regular.ttf",
      "color": "white",
      "stroke_width": 3,
      "stroke_color": "black"
    },
    "actions": [
      {"type": "set_time_start", "param": null},
      {"type": "set_time_end", "param": null},
      {"type": "screen_position", "param": {"pos": "center"}}
    ]
  }
}
```

### EditingSteps Disponíveis

| EditingStep | Arquivo JSON | Descrição |
|------------|--------------|-----------|
| CROP_1920x1080 | crop_1920x1080_to_short.json | Corta vídeo para formato vertical |
| ADD_CAPTION_SHORT | make_caption.json | Adiciona legendas |
| ADD_WATERMARK | show_watermark.json | Adiciona marca d'água |
| ADD_SUBSCRIBE_ANIMATION | subscribe_animation.json | Animação de inscrição |
| SHOW_IMAGE | show_top_image.json | Mostra imagem temporizada |
| ADD_VOICEOVER_AUDIO | add_voiceover.json | Adiciona narração |
| ADD_BACKGROUND_MUSIC | background_music.json | Música de fundo com loop |
| ADD_REDDIT_IMAGE | show_reddit_image.json | Imagem específica do Reddit |

---

## Core Editing Engine

**Arquivo**: `shortGPT/editing_framework/core_editing_engine.py`

O Core Editing Engine é responsável por processar o schema JSON e renderizar o vídeo final usando MoviePy.

### Processo de Renderização

```python
def generate_video(self, schema, output_file, logger=None):
    # 1. Ordena assets por z-index
    visual_assets = dict(sorted(schema['visual_assets'].items(), 
                               key=lambda item: item[1]['z']))
    audio_assets = dict(sorted(schema['audio_assets'].items(), 
                              key=lambda item: item[1]['z']))
    
    # 2. Processa cada asset visual
    for asset_key in visual_assets:
        asset = visual_assets[asset_key]
        if asset['type'] == 'video':
            clip = self.process_video_asset(asset)
        elif asset['type'] == 'image':
            clip = self.process_image_asset(asset)
        elif asset['type'] == 'text':
            clip = self.process_text_asset(asset)
    
    # 3. Processa assets de áudio
    for asset_key in audio_assets:
        audio_clip = self.process_audio_asset(asset)
    
    # 4. Compõe e renderiza
    video = CompositeVideoClip(visual_clips)
    if audio_clips:
        audio = CompositeAudioClip(audio_clips)
        video = video.with_audio(audio)
    
    video.write_videofile(output_file)
```

### Actions Disponíveis

**Actions Comuns**:
- `set_time_start`: Define tempo inicial
- `set_time_end`: Define tempo final
- `subclip`: Corta trecho do clip

**Actions Visuais**:
- `resize`: Redimensiona
- `crop`: Recorta
- `screen_position`: Posiciona na tela
- `green_screen`: Remove fundo verde
- `normalize_image`: Normaliza cores

**Actions de Áudio**:
- `normalize_music`: Normaliza volume
- `loop_background_music`: Loop com duração específica
- `volume_percentage`: Ajusta volume percentual

---

## Sistema de Flows

**Localização**: `shortGPT/editing_framework/flows/`

Flows são templates JSON pré-configurados para operações complexas.

### Exemplo: `build_reddit_image.json`

```json
{
  "inputs": {
    "username_text": "visual_assets/username_txt/parameters/text",
    "ncomments_text": "visual_assets/ncomments_txt/parameters/text",
    "nupvote_text": "visual_assets/nupvote_txt/parameters/text",
    "question_text": "visual_assets/question_txt/parameters/text"
  },
  "visual_assets": {
    "white_reddit_template_image": {
      "type": "image",
      "z": 0,
      "parameters": {
        "url": "public/white_reddit_template.png"
      }
    },
    "username_txt": {
      "type": "text",
      "z": 1,
      "parameters": {
        "text": null,
        "font_size": 32,
        "font": "fonts/Roboto-Bold.ttf"
      }
    }
    // ... outros elementos
  }
}
```

### Uso de Flows

```python
imageEditingEngine = EditingEngine()
imageEditingEngine.ingestFlow(Flow.WHITE_REDDIT_IMAGE_FLOW, {
    "username_text": header,
    "ncomments_text": n_comments,
    "nupvote_text": n_upvotes,
    "question_text": title
})
imageEditingEngine.renderImage("output.png")
```

---

## Templates e Prompts

**Localização**: `shortGPT/prompt_templates/`

Sistema de templates YAML para prompts do GPT com variáveis substituíveis.

### Estrutura de Template

```yaml
system_prompt: >
  Você é um especialista em conteúdo...
  
chat_prompt: >
  <<VARIABLE_NAME>>
```

### Uso de Templates

```python
# shortGPT/gpt/facts_gpt.py
def generateFacts(facts_type):
    chat, system = gpt_utils.load_local_yaml_prompt(
        'prompt_templates/facts_generator.yaml')
    chat = chat.replace("<<FACTS_TYPE>>", facts_type)
    result = gpt_utils.llm_completion(chat_prompt=chat, 
                                    system=system, temp=1.3)
    return result
```

---

## Pontos de Extensão

### 1. Adicionar Novo Editing Step

**Passo 1**: Criar arquivo JSON em `shortGPT/editing_framework/editing_steps/`

```json
{
  "my_custom_effect": {
    "type": "text",
    "z": 5,
    "inputs": {
      "parameters": ["custom_param"],
      "actions": ["custom_action"]
    },
    "parameters": {
      "custom_param": null
    },
    "actions": [
      {"type": "custom_action", "param": null}
    ]
  }
}
```

**Passo 2**: Adicionar enum em `editing_engine.py:17`

```python
class EditingStep(Enum):
    # ... steps existentes
    MY_CUSTOM_EFFECT = "my_custom_effect.json"
```

**Passo 3**: Implementar processamento de actions em `core_editing_engine.py`

```python
def process_common_visual_actions(self, clip, actions):
    for action in actions:
        if action['type'] == 'custom_action':
            # Implementar lógica customizada
            clip = clip.with_effects([custom_effect()])
```

### 2. Criar Novo Engine

**Passo 1**: Herdar de `ContentShortEngine` ou `AbstractContentEngine`

```python
from shortGPT.engine.content_short_engine import ContentShortEngine

class CustomShortEngine(ContentShortEngine):
    def __init__(self, voiceModule, **kwargs):
        super().__init__(short_type="custom_shorts", **kwargs)
        
    def _generateScript(self):
        """Override para geração customizada de script"""
        self._db_script = self.custom_script_generation()
    
    def custom_script_generation(self):
        # Lógica customizada
        return "Script gerado"
```

**Passo 2**: Adicionar na UI (`ui_tab_short_automation.py:155`)

```python
def create_short_engine(self, short_type, ...):
    # ... engines existentes
    if short_type == "Custom shorts":
        return CustomShortEngine(voice_module, ...)
```

### 3. Adicionar Novo Flow

Criar arquivo JSON em `shortGPT/editing_framework/flows/` com estrutura:

```json
{
  "inputs": {
    "param1": "path/to/parameter/in/schema"
  },
  "visual_assets": {
    // Definição de assets
  },
  "audio_assets": {
    // Definição de áudio
  }
}
```

---

## Exemplos Práticos

### Exemplo 1: Gerando um Facts Short

```python
from shortGPT.engine.facts_short_engine import FactsShortEngine
from shortGPT.audio.edge_voice_module import EdgeTTSVoiceModule
from shortGPT.config.languages import Language, EDGE_TTS_VOICENAME_MAPPING

# Configurar voz
language = Language.ENGLISH
voice_module = EdgeTTSVoiceModule(
    EDGE_TTS_VOICENAME_MAPPING[language]['male'])

# Criar engine
engine = FactsShortEngine(
    voiceModule=voice_module,
    facts_type="Scientific Facts",
    background_video_name="background_video_1",
    background_music_name="background_music_1",
    num_images=10,
    watermark="MyChannel",
    language=language
)

# Gerar conteúdo
for step_num, step_info in engine.makeContent():
    print(f"Step {step_num}: {step_info}")

# Obter vídeo final
video_path = engine.get_video_output_path()
```

### Exemplo 2: Criando Schema de Edição Customizado

```python
from shortGPT.editing_framework.editing_engine import EditingEngine, EditingStep

editor = EditingEngine()

# Adicionar narração
editor.addEditingStep(EditingStep.ADD_VOICEOVER_AUDIO, {
    'url': 'path/to/voiceover.mp3'
})

# Adicionar música de fundo
editor.addEditingStep(EditingStep.ADD_BACKGROUND_MUSIC, {
    'url': 'path/to/music.mp3',
    'loop_background_music': 60,  # 60 segundos
    'volume_percentage': 0.15
})

# Adicionar vídeo de fundo cortado
editor.addEditingStep(EditingStep.CROP_1920x1080, {
    'url': 'path/to/background.mp4'
})

# Adicionar legendas
captions = [
    ((0, 2), "Hello world"),
    ((2, 4), "This is a test"),
]
for timing, text in captions:
    editor.addEditingStep(EditingStep.ADD_CAPTION_SHORT, {
        'text': text,
        'set_time_start': timing[0],
        'set_time_end': timing[1]
    })

# Renderizar
editor.renderVideo("output.mp4")
```

### Exemplo 3: Usando Flow para Reddit Image

```python
from shortGPT.editing_framework.editing_engine import EditingEngine, Flow

# Criar engine de edição
editor = EditingEngine()

# Usar flow pré-configurado
editor.ingestFlow(Flow.WHITE_REDDIT_IMAGE_FLOW, {
    "username_text": "u/johndoe",
    "ncomments_text": "1.2k comments",
    "nupvote_text": "5.6k",
    "question_text": "What's the weirdest thing that happened to you?"
})

# Renderizar imagem
editor.renderImage("reddit_post.png")
```

---

## Referência Rápida

### Estrutura de Diretórios

```
shortGPT/
├── engine/                      # Content Engines
│   ├── abstract_content_engine.py
│   ├── content_short_engine.py
│   ├── facts_short_engine.py
│   └── reddit_short_engine.py
│
├── editing_framework/           # Sistema de Edição
│   ├── core_editing_engine.py  # Renderização MoviePy
│   ├── editing_engine.py       # Construtor de Schema
│   ├── editing_steps/          # Steps JSON
│   └── flows/                  # Templates de Flow
│
├── gpt/                        # Integração LLM
│   ├── gpt_utils.py           # Utilitários
│   ├── facts_gpt.py           # Geração de facts
│   └── reddit_gpt.py          # Geração Reddit
│
├── prompt_templates/           # Templates YAML
│
├── audio/                      # Síntese de voz
│   ├── voice_module.py        # Interface base
│   ├── edge_voice_module.py   # EdgeTTS
│   └── eleven_voice_module.py # ElevenLabs
│
└── database/                   # Persistência
    ├── content_database.py
    └── content_data_manager.py
```

### Comandos Úteis

```bash
# Executar aplicação
python runShortGPT.py

# Porta padrão
http://localhost:31415

# Diretório de saída
videos/

# Assets temporários
.editing_assets/{content_type}_assets/{id}/
```

### Variáveis de Ambiente Necessárias

```bash
GEMINI_API_KEY=      # LLM principal
OPENAI_API_KEY=      # LLM fallback
ELEVENLABS_API_KEY=  # TTS premium (opcional)
PEXELS_API_KEY=      # API de imagens stock
```

### Fluxo de Dados

1. **UI** → Coleta parâmetros do usuário
2. **Engine** → Orquestra o processo de geração
3. **GPT** → Gera conteúdo (script, títulos, etc)
4. **TTS** → Sintetiza voz
5. **Whisper** → Gera legendas temporizadas
6. **EditingEngine** → Constrói schema JSON
7. **CoreEditingEngine** → Renderiza com MoviePy
8. **Output** → Vídeo final em `videos/`

---

## Conclusão

O ShortGPT utiliza uma arquitetura modular onde:

1. **Engines** orquestram o processo de geração através de steps sequenciais
2. **EditingSteps** são operações atômicas definidas em JSON
3. **CoreEditingEngine** processa o schema JSON e renderiza com MoviePy
4. **Flows** são templates reutilizáveis para operações complexas
5. **Sistema de persistência** mantém estado entre execuções

Para estender o sistema:
- Adicione novos EditingSteps criando JSONs
- Crie novos Engines herdando de AbstractContentEngine
- Implemente novos Flows para operações complexas
- Adicione novos templates de prompt em YAML

O sistema é projetado para ser extensível e modular, permitindo fácil adição de novos tipos de conteúdo e efeitos de edição.