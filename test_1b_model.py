#!/usr/bin/env python3
"""
测试 1B 模型
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

def test_1b_model():
    model_path = os.path.expanduser("~/models/Llama3.2-1B-Instruct-hf")
    
    print(f"模型路径: {model_path}")
    print(f"路径存在: {os.path.exists(model_path)}")
    
    print("加载 tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True, trust_remote_code=True)
    
    print("加载模型...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用设备: {device}")
    
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    model.eval()
    
    # 测试简单的 prompt
    test_prompt = "Hello, how are you?"
    print(f"测试 prompt: {test_prompt}")
    
    # 编码并移动到正确的设备
    inputs = tokenizer(test_prompt, return_tensors="pt", add_special_tokens=True)
    if device == "cuda":
        inputs = {k: v.to(device) for k, v in inputs.items()}
    print(f"输入 tokens: {inputs['input_ids']}")
    
    # 生成
    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=50,
            temperature=0.7,
            top_p=0.9,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            repetition_penalty=1.1,
        )
    
    # 解码
    full_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    print(f"完整输出: {full_text}")
    
    # 只取新生成的部分
    prompt_tokens = len(inputs['input_ids'][0])
    new_tokens = output_ids[0][prompt_tokens:]
    new_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
    print(f"新生成部分: {new_text}")
    
    # 检查特殊 token
    print(f"BOS token ID: {tokenizer.bos_token_id}")
    print(f"EOS token ID: {tokenizer.eos_token_id}")
    print(f"PAD token ID: {tokenizer.pad_token_id}")
    
    # 检查词汇表大小
    print(f"词汇表大小: {tokenizer.vocab_size}")

if __name__ == "__main__":
    test_1b_model() 