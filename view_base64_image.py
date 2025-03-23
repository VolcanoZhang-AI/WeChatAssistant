#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
查看base64编码图像的工具，可以解码并显示base64图像
"""

import os
import sys
import base64
import io
from PIL import Image
import time

# 确保项目根目录在Python路径中
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def save_base64_image(base64_string, file_path=None):
    """
    保存base64编码的图像到文件并尝试显示
    
    Args:
        base64_string (str): base64编码的图像字符串
        file_path (str): 保存路径，如果为None则自动生成
    
    Returns:
        str: 保存的文件路径
    """
    try:
        # 解码base64字符串
        if "," in base64_string:
            # 处理可能带有头部的base64字符串，如: data:image/png;base64,xxxxx
            base64_string = base64_string.split(",", 1)[1]
        
        image_data = base64.b64decode(base64_string)
        
        # 如果未指定路径，生成一个带时间戳的文件名
        if file_path is None:
            screenshots_dir = os.path.join(project_root, "screenshots")
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(screenshots_dir, f"base64_image_{timestamp}.png")
        
        # 保存图像
        with open(file_path, "wb") as f:
            f.write(image_data)
            
        print(f"图像已保存到: {file_path}")
        
        # 尝试打开并显示图像（仅用于桌面环境）
        try:
            image = Image.open(io.BytesIO(image_data))
            image.show()
            print("图像已显示，您可以在弹出的窗口中查看")
        except Exception as e:
            print(f"无法显示图像: {e}")
            print(f"请直接打开保存的文件: {file_path}")
        
        return file_path
    except Exception as e:
        print(f"处理base64图像失败: {e}")
        return None

def main():
    """
    主函数，从文件读取base64字符串或请求用户粘贴
    """
    print("欢迎使用base64图像查看器")
    print("=" * 50)
    
    try:
        # 询问用户输入方式
        choice = input("请选择输入方式：\n1. 从文件读取\n2. 粘贴base64字符串\n请输入选项 (1/2): ")
        
        base64_string = ""
        
        if choice == "1":
            file_path = input("请输入包含base64字符串的文件路径: ")
            if not os.path.exists(file_path):
                print(f"错误：找不到文件 {file_path}")
                return
                
            with open(file_path, 'r') as f:
                base64_string = f.read().strip()
                
        elif choice == "2":
            print("请粘贴base64字符串 (输入完成后按Enter，然后输入END结束):")
            lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            base64_string = ''.join(lines)
        
        else:
            print("无效的选项，程序退出")
            return
        
        # 检查base64字符串是否有效
        if not base64_string:
            print("错误：base64字符串为空")
            return
            
        # 保存并显示图像
        save_base64_image(base64_string)
            
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main() 