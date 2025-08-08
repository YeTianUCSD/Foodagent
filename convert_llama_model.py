#!/usr/bin/env python3
"""
转换 llama.cpp 格式的 .pth 模型为 HuggingFace 格式
"""

import os
import json
import torch
from transformers import LlamaTokenizer, LlamaForCausalLM
import argparse

def convert_llama_model(input_path, output_path):
    """
    将 llama.cpp 格式的模型转换为 HuggingFace 格式
    
    Args:
        input_path: 输入模型路径（包含 .pth 文件的目录）
        output_path: 输出模型路径
    """
    
    # 检查输入路径
    if not os.path.exists(input_path):
        raise ValueError(f"输入路径不存在: {input_path}")
    
    # 查找 .pth 文件
    pth_files = [f for f in os.listdir(input_path) if f.endswith('.pth')]
    if not pth_files:
        raise ValueError(f"在 {input_path} 中找不到 .pth 文件")
    
    # 读取 params.json
    params_file = os.path.join(input_path, 'params.json')
    if not os.path.exists(params_file):
        raise ValueError(f"找不到 params.json 文件: {params_file}")
    
    with open(params_file, 'r') as f:
        params = json.load(f)
    
    print(f"模型参数: {params}")
    
    # 创建输出目录
    os.makedirs(output_path, exist_ok=True)
    
    # 创建 config.json
    config = {
        "architectures": ["LlamaForCausalLM"],
        "model_type": "llama",
        "vocab_size": params.get('vocab_size', 32000),
        "hidden_size": params.get('dim', 4096),
        "intermediate_size": params.get('multiple_of', 256) * 4,
        "num_hidden_layers": params.get('n_layers', 32),
        "num_attention_heads": params.get('n_heads', 32),
        "num_key_value_heads": params.get('n_kv_heads', 32),
        "hidden_act": "silu",
        "max_position_embeddings": params.get('context_length', 2048),
        "rms_norm_eps": params.get('norm_eps', 1e-6),
        "rope_theta": params.get('rope_freq_base', 10000.0),
        "use_cache": True,
        "pad_token_id": None,
        "bos_token_id": 1,
        "eos_token_id": 2,
        "pretraining_tp": 1,
        "tie_word_embeddings": False,
        "rope_scaling": None,
    }
    
    with open(os.path.join(output_path, 'config.json'), 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"已创建 config.json")
    
    # 复制 tokenizer.model
    tokenizer_file = os.path.join(input_path, 'tokenizer.model')
    if os.path.exists(tokenizer_file):
        import shutil
        shutil.copy2(tokenizer_file, os.path.join(output_path, 'tokenizer.model'))
        print(f"已复制 tokenizer.model")
    
    # 创建 tokenizer.json（简化版本）
    tokenizer_config = {
        "version": "1.0",
        "truncation": None,
        "padding": None,
        "added_tokens": [],
        "normalizer": None,
        "pre_tokenizer": None,
        "post_processor": None,
        "decoder": None,
        "model": {
            "type": "BPE",
            "vocab": {},
            "merges": []
        }
    }
    
    with open(os.path.join(output_path, 'tokenizer.json'), 'w') as f:
        json.dump(tokenizer_config, f, indent=2)
    
    print(f"已创建 tokenizer.json")
    
    # 创建 special_tokens_map.json
    special_tokens = {
        "bos_token": "<s>",
        "eos_token": "</s>",
        "unk_token": "<unk>",
        "pad_token": None
    }
    
    with open(os.path.join(output_path, 'special_tokens_map.json'), 'w') as f:
        json.dump(special_tokens, f, indent=2)
    
    print(f"已创建 special_tokens_map.json")
    
    # 注意：实际的模型权重转换比较复杂，需要处理张量格式转换
    # 这里只是创建了基本的配置文件
    print(f"\n警告：这只是创建了配置文件。")
    print(f"要完整转换模型权重，你需要：")
    print(f"1. 使用 llama.cpp 的转换工具")
    print(f"2. 或者使用 HuggingFace 的转换脚本")
    print(f"\n建议使用官方转换工具：")
    print(f"git clone https://github.com/ggerganov/llama.cpp")
    print(f"cd llama.cpp")
    print(f"python convert.py {input_path} --outfile {output_path}/model.gguf")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="转换 llama.cpp 模型为 HuggingFace 格式")
    parser.add_argument("input_path", help="输入模型路径（包含 .pth 文件的目录）")
    parser.add_argument("output_path", help="输出模型路径")
    
    args = parser.parse_args()
    
    try:
        convert_llama_model(args.input_path, args.output_path)
        print(f"\n转换完成！输出路径: {args.output_path}")
    except Exception as e:
        print(f"转换失败: {e}") 