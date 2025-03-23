"""
操作执行器 - 用于执行大模型分析结果中规划的操作
"""
import os
import time
import sys
import pyautogui

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from app.utils.logger import get_logger

# 获取日志记录器
logger = get_logger()

# 安全设置，防止鼠标移动到屏幕角落时出错
pyautogui.FAILSAFE = True

def execute_action(action):
    """
    执行一个操作（键盘或鼠标）
    
    Args:
        action (dict): 包含操作细节的字典
        
    Returns:
        bool: 操作是否成功
    """
    logger.info(f"执行操作: {action.get('description', '未描述')}")
    
    action_type = action.get('type', '').lower()
    action_name = action.get('action', '').lower()
    
    # 1. 键盘操作
    if action_type == 'keyboard':
        # 根据操作名称执行对应的键盘操作
        if action_name == 'press':
            # 按单个键
            key = action.get('value', '')
            if not key:
                logger.error("按键操作缺少'value'字段")
                return False
            delay = action.get('delay', 0.1)
            logger.info(f"按键: {key}, 延迟: {delay}")
            return perform_keyboard_action('press', key=key, delay=delay)
            
        elif action_name == 'hotkey':
            # 按组合键
            keys = action.get('value', '').split('+')
            if not keys or len(keys) < 2:
                logger.error("组合键操作值无效，格式应为'key1+key2'")
                return False
            delay = action.get('delay', 0.1)
            logger.info(f"组合键: {'+'.join(keys)}, 延迟: {delay}")
            return perform_keyboard_action('hotkey', keys=keys, delay=delay)
            
        elif action_name == 'write':
            # 输入文本
            text = action.get('value', '')
            if not text:
                logger.error("文本输入操作缺少'value'字段")
                return False
            delay = action.get('delay', 0.05)
            logger.info(f"输入文本: {text}, 延迟: {delay}")
            return perform_keyboard_action('write', text=text, delay=delay)
            
        else:
            logger.error(f"未知的键盘操作: {action_name}")
            return False
            
    # 2. 鼠标操作
    elif action_type == 'mouse':
        # 获取坐标
        x = action.get('x')
        y = action.get('y')
        
        # 根据操作名称执行对应的鼠标操作
        if action_name == 'click':
            # 鼠标点击
            if x is None or y is None:
                logger.error("点击操作缺少坐标")
                return False
            button = action.get('value', 'left')  # 默认左键点击
            delay = action.get('delay', 0.1)
            logger.info(f"点击: ({x}, {y}), 按钮: {button}, 延迟: {delay}")
            return perform_mouse_action('click', x=x, y=y, button=button, delay=delay)
            
        elif action_name == 'move':
            # 鼠标移动
            if x is None or y is None:
                logger.error("移动操作缺少坐标")
                return False
            delay = action.get('delay', 0.2)
            logger.info(f"移动到: ({x}, {y}), 延迟: {delay}")
            return perform_mouse_action('move', x=x, y=y, delay=delay)
            
        elif action_name == 'drag':
            # 鼠标拖动
            if x is None or y is None:
                logger.error("拖动操作缺少坐标")
                return False
            # 获取拖动终点
            end_x = action.get('end_x')
            end_y = action.get('end_y')
            if end_x is None or end_y is None:
                logger.error("拖动操作缺少终点坐标")
                return False
            button = action.get('value', 'left')  # 默认左键拖动
            delay = action.get('delay', 0.5)
            logger.info(f"拖动: 从({x}, {y})到({end_x}, {end_y}), 按钮: {button}, 延迟: {delay}")
            return perform_mouse_action('drag', x=x, y=y, end_x=end_x, end_y=end_y, button=button, delay=delay)
            
        elif action_name == 'scroll':
            # 鼠标滚动
            amount = action.get('value')
            if amount is None:
                logger.error("滚动操作缺少'value'字段")
                return False
            try:
                amount = int(amount)
            except ValueError:
                logger.error(f"滚动量值无效: {amount}")
                return False
            delay = action.get('delay', 0.2)
            logger.info(f"滚动: {amount}, 延迟: {delay}")
            return perform_mouse_action('scroll', amount=amount, delay=delay)
            
        else:
            logger.error(f"未知的鼠标操作: {action_name}")
            return False
    
    # 3. 环境检查操作（新增）
    elif action_type == 'check_environment':
        logger.info(f"执行环境检查: {action.get('description', '未描述的环境检查')}")
        
        # 这里实际上我们不需要做任何实际操作，只是将环境检查信息记录下来
        # 因为环境检查是在多轮对话分析中通过图像分析完成的，而不是通过实际的键盘鼠标操作
        
        # 可以在此处添加一些额外的环境验证逻辑，如果需要的话
        # 例如：检查特定进程是否运行，检查网络连接等
        
        # 简单地返回成功，表示我们已经注意到了环境状态
        logger.info("环境检查完成")
        return True
    
    # 4. 未知操作类型
    else:
        logger.warning(f"未知的操作类型: {action_type}")
        return False

def perform_keyboard_action(method, **kwargs):
    try:
        if method == 'press':
            key = kwargs['key']
            delay = kwargs['delay']
            pyautogui.press(key)
            logger.info(f"按下按键: {key}")
            time.sleep(delay)
            return True
        elif method == 'hotkey':
            keys = kwargs['keys']
            delay = kwargs['delay']
            pyautogui.hotkey(*keys)
            logger.info(f"按下组合键: {'+'.join(keys)}")
            time.sleep(delay)
            return True
        elif method == 'write':
            text = kwargs['text']
            delay = kwargs['delay']
            pyautogui.write(text, interval=0.05)
            logger.info(f"输入文本: {text}")
            time.sleep(delay)
            return True
        else:
            logger.warning(f"未知的键盘操作方法: {method}")
            return False
    except Exception as e:
        logger.error(f"执行键盘操作时出错: {str(e)}")
        return False

def perform_mouse_action(method, **kwargs):
    try:
        if method == 'click':
            x = kwargs['x']
            y = kwargs['y']
            button = kwargs['button']
            delay = kwargs['delay']
            pyautogui.moveTo(x, y, duration=0.2)
            time.sleep(0.1)
            if button == 'right':
                pyautogui.rightClick()
                logger.info(f"右键点击: ({x}, {y})")
            elif button == 'double':
                pyautogui.doubleClick()
                logger.info(f"双击: ({x}, {y})")
            else:
                pyautogui.click()
                logger.info(f"点击: ({x}, {y})")
            time.sleep(delay)
            return True
        elif method == 'move':
            x = kwargs['x']
            y = kwargs['y']
            delay = kwargs['delay']
            pyautogui.moveTo(x, y, duration=0.2)
            logger.info(f"移动鼠标到: ({x}, {y})")
            time.sleep(delay)
            return True
        elif method == 'drag':
            x = kwargs['x']
            y = kwargs['y']
            end_x = kwargs['end_x']
            end_y = kwargs['end_y']
            button = kwargs['button']
            delay = kwargs['delay']
            pyautogui.moveTo(x, y, duration=0.2)
            time.sleep(0.1)
            pyautogui.dragTo(end_x, end_y, duration=0.5, button=button)
            logger.info(f"拖动: 从({x}, {y})到({end_x}, {end_y})")
            time.sleep(delay)
            return True
        elif method == 'scroll':
            amount = kwargs['amount']
            delay = kwargs['delay']
            pyautogui.scroll(amount)
            direction = "向下" if amount < 0 else "向上"
            logger.info(f"滚动: {direction} ({abs(amount)})")
            time.sleep(delay)
            return True
        else:
            logger.warning(f"未知的鼠标操作方法: {method}")
            return False
    except Exception as e:
        logger.error(f"执行鼠标操作时出错: {str(e)}")
        return False 