# LlamaLLM 使用指南

## 当前状态

你的本地模型 `~/models/Llama3.1-8B-Instruct` 是 `.pth` 格式（llama.cpp 格式），需要转换为 HuggingFace 格式才能使用。

## 临时解决方案

### 1. 使用开源模型（推荐）

运行以下命令选择模型：

```bash
conda activate cha
source set_model.sh
python run.py
```

可选择的模型：
- **DialoGPT-large**: 效果最好，但加载较慢
- **DialoGPT-medium**: 平衡效果和速度
- **GPT-2**: 最小最快，但效果一般

### 2. 手动设置环境变量

```bash
# 使用 DialoGPT-large
export LLAMA_MODEL_PATH="microsoft/DialoGPT-large"
python run.py

# 使用其他模型
export LLAMA_MODEL_PATH="gpt2"
python run.py
```

## 转换你的本地模型

要将你的 `~/models/Llama3.1-8B-Instruct` 转换为可用格式，需要：

### 方法1：转换为 HuggingFace 格式

1. 下载 llama.cpp：
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
```

2. 转换模型：
```bash
python convert.py ~/models/Llama3.1-8B-Instruct --outfile ~/models/Llama3.1-8B-Instruct-hf
```

3. 使用转换后的模型：
```bash
export LLAMA_MODEL_PATH="~/models/Llama3.1-8B-Instruct-hf"
python run.py
```

### 方法2：使用预转换的模型

你也可以下载已经转换好的 Llama-3-Instruct 模型：

```bash
# 使用 HuggingFace 上的开源 Llama-3-Instruct 模型
export LLAMA_MODEL_PATH="meta-llama/Llama-3-8B-Instruct"  # 需要 HuggingFace 访问权限
# 或者
export LLAMA_MODEL_PATH="NousResearch/Llama-3-8B-Instruct"  # 开源版本
```

## 模型效果对比

| 模型 | 效果 | 加载速度 | 内存占用 | 推荐度 |
|------|------|----------|----------|--------|
| DialoGPT-large | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| DialoGPT-medium | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| GPT-2 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Llama-3-Instruct | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## 注意事项

1. **首次加载**：模型首次加载时会下载，需要网络连接
2. **内存要求**：大模型需要更多内存，建议至少 8GB RAM
3. **GPU 加速**：如果有 CUDA GPU，会自动使用 GPU 加速
4. **模型缓存**：下载的模型会缓存在 `~/.cache/huggingface/` 目录

## 故障排除

### 问题1：模型下载失败
```bash
# 设置镜像源
export HF_ENDPOINT=https://hf-mirror.com
```

### 问题2：内存不足
```bash
# 使用较小的模型
export LLAMA_MODEL_PATH="gpt2"
```

### 问题3：CUDA 错误
```bash
# 强制使用 CPU
export CUDA_VISIBLE_DEVICES=""
``` 