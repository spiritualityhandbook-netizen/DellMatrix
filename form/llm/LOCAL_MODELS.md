# Local open-source models → Dell Matrix

Run models **on her PC** (no cloud required for this path).

## Why Ollama

Easiest local stack on Windows: download models, serve at `http://127.0.0.1:11434`, OpenAI-style API. Dell Matrix talks to it as provider `ollama` / `local`.

Alternatives: **LM Studio**, **llama.cpp**, **GPT4All** — same idea (local weights); Ollama is what the bridge auto-detects.

## Install (Windows)

1. Install from https://ollama.com (Windows installer).
2. Open PowerShell:

```powershell
ollama serve
# new window:
ollama pull llama3.2
# or stronger if she has GPU/RAM:
ollama pull qwen2.5:7b
ollama pull qwen2.5-coder:7b
```

## Pick a model by hardware

| Hardware (rough) | Start with | Notes |
|------------------|------------|--------|
| 8–16 GB RAM, weak/no GPU | `llama3.2` (3B) or `phi3` | Fast, lighter quality |
| 16 GB + decent GPU | `qwen2.5:7b` / `llama3.1:8b` | Good daily driver |
| Coding focus | `qwen2.5-coder:7b` | Terminal + scripts |
| 24 GB+ VRAM | `qwen3-coder` class / larger Qwen | Heavier; check Ollama library tags |

Tags change; run `ollama list` and `ollama pull <name>` from [Ollama library](https://ollama.com/library).

Community 2026 pattern: **Qwen** family strong for code; smaller **Llama/Gemma/Phi** for chat on limited boxes. Bigger is not always better if it swaps to disk.

## Link into her matrix

```powershell
cd $env:USERPROFILE\Documents\DellMatrix

# optional default model
$env:OLLAMA_MODEL = "qwen2.5:7b"
$env:OLLAMA_HOST = "http://127.0.0.1:11434"

python -m form.llm.cli --detect
python -m form.llm.cli --provider ollama "Summarize a cautious paper-trading plan"
python -m form.llm.cli --matrix --owner Sister --provider ollama
```

## Daily offline chain

```powershell
python -m form.trading.cli --owner Sister daily
python -m form.llm.cli --matrix --owner Sister --provider ollama "Daily brief; not advice"
```

## Local vs cloud

| | Local (Ollama) | Cloud (Gemini/Grok/Claude) |
|--|----------------|----------------------------|
| Privacy | Weights + data stay on PC | Leaves machine |
| Cost | Electricity | API usage |
| Quality | Depends on size/VRAM | Often stronger |
| Internet | Only to *download* model once | Every call |

She can use **both**: local default, cloud when keys exist (`--all`).

## Not financial advice

Local models can still be wrong about markets. Paper trade first.
