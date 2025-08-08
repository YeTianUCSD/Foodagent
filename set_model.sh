#!/bin/bash

# 设置不同模型的脚本

echo "选择要使用的模型："
echo "1. DialoGPT-large (推荐，效果较好)"
echo "2. DialoGPT-medium (较小，加载快)"
echo "3. GPT-2 (最小，加载最快)"
echo "4. 自定义模型路径"

read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        export LLAMA_MODEL_PATH="microsoft/DialoGPT-large"
        echo "已设置为 DialoGPT-large"
        ;;
    2)
        export LLAMA_MODEL_PATH="microsoft/DialoGPT-medium"
        echo "已设置为 DialoGPT-medium"
        ;;
    3)
        export LLAMA_MODEL_PATH="gpt2"
        echo "已设置为 GPT-2"
        ;;
    4)
        read -p "请输入模型路径: " custom_path
        export LLAMA_MODEL_PATH="$custom_path"
        echo "已设置为自定义路径: $custom_path"
        ;;
    *)
        echo "无效选择，使用默认模型"
        export LLAMA_MODEL_PATH="microsoft/DialoGPT-large"
        ;;
esac

echo "环境变量已设置。现在可以运行: python run.py" 