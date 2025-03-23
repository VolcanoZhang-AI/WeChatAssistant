#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pyautogui
import cv2
from PIL import Image
from PIL import ImageGrab  # 添加屏幕截图支持
import io
import base64
import time
import sys
import os

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.utils.logger import get_logger

# 获取日志记录器
logger = get_logger()

def capture_screen():
    """
    捕获当前屏幕内容
    
    Returns:
        bytes: 屏幕截图的二进制数据
    """
    logger.info("开始捕获屏幕内容")
    try:
        # 截取屏幕并转换为base64
        screenshot = ImageGrab.grab()
        logger.debug(f"屏幕截图尺寸: {screenshot.size}")
        
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        logger.info(f"屏幕捕获成功，图像大小: {len(img_base64)} 字符")
        return img_base64
    except Exception as e:
        logger.error(f"屏幕捕获失败: {str(e)}")
        raise Exception(f"屏幕捕获失败: {str(e)}")

def get_screen_capture():
    """
    获取当前屏幕截图，返回base64编码的图像数据
    
    Returns:
        str: base64编码的图像数据
    """
    return capture_screen()

def save_screen_capture(file_path="screenshot.png"):
    """
    保存屏幕截图到文件
    
    Args:
        file_path (str): 保存路径
    """
    logger.info(f"开始保存屏幕截图到: {file_path}")
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)
        logger.info(f"屏幕截图已保存: {file_path}")
        print(f"屏幕截图已保存到: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"保存屏幕截图失败: {str(e)}")
        print(f"保存截图失败: {str(e)}")
        return None

def get_screen_size():
    """
    获取屏幕尺寸
    
    Returns:
        tuple: 宽度和高度
    """
    try:
        width, height = pyautogui.size()
        logger.debug(f"获取屏幕尺寸: {width}x{height}")
        return width, height
    except Exception as e:
        logger.error(f"获取屏幕尺寸失败: {str(e)}")
        raise Exception(f"获取屏幕尺寸失败: {str(e)}")

if __name__ == "__main__":
    # 测试屏幕捕获功能
    image_data = capture_screen()
    print(f"捕获到屏幕图像，大小: {len(image_data)} 字节")
    
    # 保存示例
    save_screen_capture("test_screenshot.png")
    
    # 获取屏幕尺寸
    width, height = get_screen_size()
    print(f"屏幕尺寸: {width}x{height}") 