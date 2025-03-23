#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyautogui
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

# 设置安全措施，避免失控（移动到屏幕角落会触发失败保护）
pyautogui.FAILSAFE = True
# 设置操作之间的延迟
pyautogui.PAUSE = 0.5

def perform_keyboard_action(action_type, value=None):
    """
    执行键盘操作
    
    Args:
        action_type (str): 键盘操作类型，如'press', 'hotkey', 'write'
        value (str或list): 按键或文本内容
    """
    logger.info(f"执行键盘操作: {action_type}, 值: {value}")
    try:
        if action_type == 'press':
            pyautogui.press(value)
            logger.info(f"已按下键: {value}")
            print(f"已按下键: {value}")
        
        elif action_type == 'hotkey':
            # value应该是一个按键列表，如['ctrl', 'f']
            if not isinstance(value, list):
                logger.warning(f"组合键值不是列表: {value}，尝试转换")
                if isinstance(value, str):
                    value = value.split('+')
                else:
                    logger.error(f"无法将 {value} 转换为组合键")
                    raise ValueError(f"组合键必须是列表或字符串，而不是 {type(value)}")
            
            pyautogui.hotkey(*value)
            logger.info(f"已执行组合键: {'+'.join(value)}")
            print(f"已执行组合键: {'+'.join(value)}")
        
        elif action_type == 'write':
            if value is None or value == "":
                logger.warning("尝试写入空文本")
            pyautogui.write(value)
            logger.info(f"已输入文本: {value}")
            print(f"已输入文本: {value}")
            
        elif action_type == 'keyDown':
            pyautogui.keyDown(value)
            logger.info(f"按住键: {value}")
            print(f"按住键: {value}")
            
        elif action_type == 'keyUp':
            pyautogui.keyUp(value)
            logger.info(f"释放键: {value}")
            print(f"释放键: {value}")
            
        else:
            logger.warning(f"未知的键盘操作类型: {action_type}")
            print(f"未知的键盘操作类型: {action_type}")
            
    except Exception as e:
        logger.error(f"键盘操作失败: {action_type}, {value}, 错误: {str(e)}")
        print(f"键盘操作失败: {e}")
        raise

def perform_mouse_action(action_type, x=None, y=None, clicks=1, button='left'):
    """
    执行鼠标操作
    
    Args:
        action_type (str): 鼠标操作类型，如'click', 'move', 'drag'
        x (int): x坐标
        y (int): y坐标
        clicks (int): 点击次数
        button (str): 鼠标按钮，'left', 'right', 'middle'
    """
    logger.info(f"执行鼠标操作: {action_type}, 位置: ({x}, {y}), 点击: {clicks}, 按钮: {button}")
    
    # 检查坐标有效性
    if (x is None or y is None) and action_type not in ['scroll']:
        logger.error(f"鼠标操作缺少坐标: x={x}, y={y}")
        raise ValueError("鼠标操作需要有效的x和y坐标")
        
    try:
        if action_type == 'click':
            # 检查坐标是否超出屏幕范围
            screen_width, screen_height = pyautogui.size()
            if x < 0 or x > screen_width or y < 0 or y > screen_height:
                logger.warning(f"点击坐标 ({x}, {y}) 可能超出屏幕范围 ({screen_width}x{screen_height})")
                
            pyautogui.click(x=x, y=y, clicks=clicks, button=button)
            logger.info(f"已在位置 ({x}, {y}) 点击 {button} 键 {clicks} 次")
            print(f"已在位置 ({x}, {y}) 点击 {button} 键 {clicks} 次")
            
        elif action_type == 'move':
            pyautogui.moveTo(x, y)
            logger.info(f"已移动鼠标到位置 ({x}, {y})")
            print(f"已移动鼠标到位置 ({x}, {y})")
            
        elif action_type == 'drag':
            # 需要起始位置和目标位置
            current_x, current_y = pyautogui.position()
            logger.debug(f"开始拖拽，当前位置: ({current_x}, {current_y}) 到目标位置: ({x}, {y})")
            pyautogui.dragTo(x, y, button=button)
            logger.info(f"已从 ({current_x}, {current_y}) 拖动到 ({x}, {y})")
            print(f"已从 ({current_x}, {current_y}) 拖动到 ({x}, {y})")
            
        elif action_type == 'scroll':
            # x表示滚动的单位
            pyautogui.scroll(x)
            logger.info(f"已滚动 {x} 单位")
            print(f"已滚动 {x} 单位")
            
        else:
            logger.warning(f"未知的鼠标操作类型: {action_type}")
            print(f"未知的鼠标操作类型: {action_type}")
            
    except Exception as e:
        logger.error(f"鼠标操作失败: {action_type}, 位置: ({x}, {y}), 错误: {str(e)}")
        print(f"鼠标操作失败: {e}")
        raise

def get_current_mouse_position():
    """
    获取当前鼠标位置
    
    Returns:
        tuple: (x, y) 坐标
    """
    try:
        x, y = pyautogui.position()
        logger.debug(f"当前鼠标位置: ({x}, {y})")
        return x, y
    except Exception as e:
        logger.error(f"获取鼠标位置失败: {str(e)}")
        raise

if __name__ == "__main__":
    # 等待3秒，让用户有时间调整窗口
    print("3秒后开始测试...")
    time.sleep(3)
    
    # 获取当前鼠标位置
    x, y = get_current_mouse_position()
    print(f"当前鼠标位置: ({x}, {y})")
    
    # 测试键盘操作
    perform_keyboard_action('hotkey', ['ctrl', 'a'])
    
    # 测试鼠标操作
    perform_mouse_action('move', x=100, y=100) 