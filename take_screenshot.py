#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单的屏幕截图工具，用于获取当前屏幕内容
"""

import os
import sys
import time

# 确保项目根目录在Python路径中
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.utils.screen_capture import capture_screen, save_screen_capture
from app.utils.logger import get_logger

def take_and_save_screenshot():
    """获取截图并保存到文件"""
    logger = get_logger()
    
    try:
        print("正在获取屏幕截图...")
        
        # 创建screenshots目录
        screenshots_dir = os.path.join(project_root, "screenshots")
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        
        # 生成带时间戳的文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")
        
        # 方法1：使用pyautogui直接保存截图
        saved_path = save_screen_capture(screenshot_path)
        
        print(f"屏幕截图已保存到: {saved_path}")
        print(f"您可以在 {screenshots_dir} 目录中查看所有截图")
        
        return saved_path
    except Exception as e:
        print(f"截图失败: {e}")
        return None

if __name__ == "__main__":
    take_and_save_screenshot() 