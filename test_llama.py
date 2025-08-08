#!/usr/bin/env python3
"""
测试 DialoGPT 模型
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def test_llama_model():
    model_path = "microsoft/DialoGPT-large"
    
    print("加载 tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True, trust_remote_code=True)
    
    print("加载模型...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
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

if __name__ == "__main__":
    test_llama_model() 