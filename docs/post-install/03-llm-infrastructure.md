# Local LLM Infrastructure & Framework Architecture

This guide details the deployment, hardware profiling, and optimization of local Large Language Model (LLM) engines on Arch Linux / Garuda workstations, covering discrete GPU acceleration (Desktop), unified memory APU compute (Laptop), and alternative open-source fine-tuning and inference ecosystems.

---

## 1. Hardware-Specific Ollama Deployment

Ollama serves as the core local inference daemon, exposing both native endpoints (`/api/generate`, `/api/chat`) and OpenAI-compatible endpoints (`/v1`).

Configuration templates are stored in [`configs/llm/`](../../configs/llm).

---

### Profile 1: Desktop High-Performance dGPU (Garuda - AMD Radeon RX 9070 XT)

On desktop systems with high-end discrete GPUs, Ollama utilizes dedicated VRAM and accelerated compute shaders.

#### 1. Systemd Environment Files
Create `/etc/ollama.conf`:
```ini
OLLAMA_HOST="http://0.0.0.0:11434"
OLLAMA_KEEP_ALIVE="5m"
OLLAMA_LOAD_TIMEOUT="5m"
OLLAMA_CONTEXT_LENGTH=4096
OLLAMA_MAX_LOADED_MODELS=0
OLLAMA_GPU_OVERHEAD=0
OLLAMA_MAX_QUEUE=512
OLLAMA_NUM_PARALLEL=1
OLLAMA_NOHISTORY=false
OLLAMA_NOPRUNE=false
OLLAMA_FLASH_ATTENTION=true
OLLAMA_SCHED_SPREAD=false
OLLAMA_DEBUG=0
```

Create `/etc/ollama-vulkan.conf`:
```ini
OLLAMA_VULKAN=1
```

#### 2. Systemd Service Override (`/etc/systemd/system/ollama.service.d/override.conf`)
```ini
[Service]
EnvironmentFile=-/etc/ollama.conf
EnvironmentFile=-/etc/ollama-vulkan.conf
Environment="OLLAMA_HOST=0.0.0.0" "OLLAMA_ORIGINS=*"
```

---

### Profile 2: Laptop APU iGPU (Framework 13 - AMD Radeon 780M / Ryzen 7840U)

On AMD APUs sharing Unified Memory Architecture (UMA) system RAM, Ollama requires specific flags to properly allocate system memory and prevent shader freezes on RDNA3 iGPUs.

#### Systemd Drop-in Override (`/etc/systemd/system/ollama.service.d/override.conf`)
```ini
[Service]
# Force Vulkan acceleration
Environment="OLLAMA_VULKAN=1"

# CRITICAL: Map exclusively to the first Vulkan device (0). Specifying non-existent devices causes core dumps.
Environment="OLLAMA_VULKAN_DEVICE=0"

# Force memory allocation on UMA shared system memory
Environment="OLLAMA_INTEGRATED_GPU=1"

# CRITICAL: Disable Flash Attention to prevent compute shader freezes on RDNA3 APUs
Environment="OLLAMA_FLASH_ATTENTION=0"

# Network binding
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_ORIGINS=*"
```

---

### Profile 3: CPU-Only Fallback

When operating without GPU compute support or troubleshooting driver lockups:

```ini
[Service]
Environment="OLLAMA_VULKAN=0"
Environment="OLLAMA_VULKAN_DEVICE="
Environment="OLLAMA_RUNNER=cpu"
Environment="OLLAMA_HOST=127.0.0.1:11434"
```

---

### Applying and Verifying Service
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama.service

# Verify initialization logs
journalctl -u ollama.service -b -n 40
```

---

## 2. LLM Framework Ecosystem & Alternatives

Beyond standard Ollama serving, local development workflows often incorporate specialized engines for fine-tuning, high-throughput batching, and IDE integrations:

```text
┌──────────────────────────────────────────────────────────────────┐
│                   Local LLM & AI Ecosystem                       │
├─────────────────┬─────────────────┬──────────────────────────────┤
│ Inference / API │ Fine-Tuning     │ Developer Clients            │
├─────────────────┼─────────────────┼──────────────────────────────┤
│ • Ollama        │ • Unsloth       │ • Continue.dev (IDE Autocomp)│
│ • llama.cpp     │ • Axolotl       │ • Aider (CLI Git Pair-Prog)  │
│ • vLLM          │ • Torchtune     │ • Open WebUI (Self-hosted)   │
│ • LiteLLM Proxy │ • HuggingFace   │ • Antigravity Agent Proxy    │
└─────────────────┴─────────────────┴──────────────────────────────┘
```

---

### 2.1 Unsloth Framework Overview
[Unsloth](https://github.com/unslothai/unsloth) is an open-source, ultra-fast LLM fine-tuning and inference engine designed to optimize memory bandwidth and training throughput.

* **Architecture & Mechanics**:
  - Replaces slow PyTorch backpropagation and attention kernels with custom, handwritten **Triton GPU kernels**.
  - Retains 100% mathematical accuracy (no approximation error compared to standard PyTorch implementations).
* **Key Advantages**:
  - **2x to 5x faster training speeds** compared to HuggingFace TRL / DeepSpeed.
  - **70% to 80% VRAM memory reduction**, enabling QLoRA fine-tuning of 7B/14B/32B models on consumer GPUs (e.g., 8GB - 24GB VRAM).
* **Export Pipeline to Ollama**:
  After fine-tuning a model with Unsloth in Python, models can be directly quantized and exported to GGUF:
  ```python
  # Save directly to GGUF format (e.g. 4-bit Q4_K_M quantization)
  model.save_pretrained_gguf("custom_model", tokenizer, quantization_method="q4_k_m")
  ```
  Then imported into Ollama via a `Modelfile`:
  ```dockerfile
  FROM ./custom_model-unsloth.Q4_K_M.gguf
  PARAMETER temperature 0.7
  ```
  ```bash
  ollama create custom-model -f Modelfile
  ```

---

### 2.2 `llama.cpp`
The core C/C++ foundation powering Ollama:
* Enables standalone CLI inference, quantized model conversion (`GGUF`), and direct Vulkan/ROCm/CUDA bindings with zero external dependencies.
* Useful for manual quantization experiments (`llama-quantize`) and edge hardware deployments.

---

### 2.3 `vLLM`
A production-grade, high-throughput distributed serving engine:
* Implements **PagedAttention** (virtual memory management for KV cache), dramatically increasing concurrency and batch processing efficiency.
* Ideal for multi-user internal API clusters and microservice deployments.

---

### 2.4 IDE & Agent Integrations

1. **Continue.dev (VS Code / Antigravity IDE)**:
   - Connects to Ollama's local endpoint (`http://localhost:11434`) for tab-autocomplete and sidebar code editing.
   - Recommended split model configuration:
     - Autocomplete: `qwen2.5-coder:1.5b` or `deepseek-coder:1.3b` (Ultra-low latency).
     - Inline Chat: `qwen2.5-coder:14b` or `qwen2.5-coder:32b` (Contextual reasoning).

2. **Aider (`aider-chat`)**:
   - Terminal-based Git pair programmer that edits source files directly via git diff blocks.
   - Run directly against local Ollama:
     ```bash
     aider --model ollama/qwen2.5-coder:14b
     ```

3. **LiteLLM Proxy**:
   - Lightweight OpenAI-compatible proxy server for unified routing, load-balancing, and rate-limiting across multiple local Ollama nodes and external frontier APIs.
