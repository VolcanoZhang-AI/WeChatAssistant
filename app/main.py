#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import sys
import base64
from datetime import datetime
import traceback

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app.utils.voice_recognition import recognize_speech
from app.utils.screen_capture import capture_screen, save_screen_capture, get_screen_capture
from app.utils.input_control import perform_keyboard_action, perform_mouse_action
from app.models.qwen_interface import analyze_text, analyze_image, multi_round_image_analysis
from app.utils.wechat_guide_parser import get_wechat_guide
from app.utils.logger import get_logger
from app.controllers.action_executor import execute_action
import pyautogui

# 获取日志记录器
logger = get_logger()

# 设置PyAutoGUI安全参数
pyautogui.PAUSE = 1  # 每次操作之间暂停1秒
pyautogui.FAILSAFE = True  # 保持故障安全机制开启

def save_base64_image(base64_string, file_path="screenshot.png"):
    """
    保存base64编码的图像到文件
    
    Args:
        base64_string (str): base64编码的图像字符串
        file_path (str): 保存路径
    """
    try:
        image_data = base64.b64decode(base64_string)
        with open(file_path, "wb") as f:
            f.write(image_data)
        logger.info(f"截图已保存到: {file_path}")
        print(f"截图已保存到: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存截图失败: {str(e)}")
        print(f"保存截图失败: {str(e)}")
        return False

def get_screenshot(screenshots_dir):
    """
    获取当前屏幕截图并保存
    
    Args:
        screenshots_dir (str): 保存截图的目录
    
    Returns:
        tuple: (base64编码的截图数据, 截图文件路径)
    """
    logger.info("开始获取屏幕截图")
    print("获取当前界面...")
    
    try:
        img_base64 = capture_screen()
        logger.debug(f"截图成功，图像大小: {len(img_base64)} 字符")
        
        # 保存截图到文件，方便查看
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")
        save_base64_image(img_base64, screenshot_path)
        return img_base64, screenshot_path
    except Exception as e:
        logger.error(f"截图失败: {str(e)}")
        print(f"截图失败: {str(e)}")
        return None, None

def safe_execute_action(action, task_context=None):
    """
    安全地执行操作，包含错误处理和重试机制
    
    Args:
        action (dict): 包含操作细节的字典
        task_context (dict): 任务上下文
        
    Returns:
        bool: 操作是否成功
    """
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        try:
            logger.info(f"尝试执行操作 (尝试 {attempts+1}/{max_attempts}): {action['description']}")
            print(f"执行操作: {action['description']}")
            
            # 添加小延迟
            time.sleep(0.5)
            
            # 检查是否为返回桌面的快捷操作
            if action.get('action') == 'hotkey' and action.get('value') == 'win+d':
                logger.info("执行返回桌面操作 (Win+D)")
                pyautogui.hotkey('win', 'd')
                time.sleep(1)  # 等待动画完成
                return True
                
            # 普通操作执行
            execute_action(action)
            logger.info(f"操作执行完成: {action['description']}")
            print(f"操作执行完成")
            
            # 等待操作结果显示
            time.sleep(1.5)
            return True
            
        except Exception as e:
            attempts += 1
            error_msg = str(e)
            logger.error(f"执行操作失败 (尝试 {attempts}/{max_attempts}): {error_msg}")
            
            # 检查是否是PyAutoGUI的FAILSAFE错误
            if "PyAutoGUI fail-safe triggered" in error_msg:
                logger.warning("检测到PyAutoGUI安全机制触发，尝试恢复鼠标位置")
                try:
                    # 将鼠标移动到屏幕中心，避免触发FAILSAFE
                    screen_width, screen_height = pyautogui.size()
                    pyautogui.moveTo(screen_width/2, screen_height/2, duration=0.5)
                    print("已将鼠标移回屏幕中心")
                except Exception as move_err:
                    logger.error(f"移动鼠标失败: {str(move_err)}")
            
            # 如果还有尝试次数，等待后重试
            if attempts < max_attempts:
                wait_time = attempts * 1.5  # 逐渐增加等待时间
                logger.info(f"等待 {wait_time} 秒后重试")
                print(f"操作失败，等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"执行操作失败: {error_msg}")
                print("已达到最大重试次数，跳过此操作")
                
                # 如果是涉及返回桌面的操作且重试失败，尝试不同的方法
                if action.get('action') == 'hotkey' and ('win' in str(action.get('value', ''))):
                    print("尝试使用替代方法显示桌面...")
                    try:
                        # 尝试使用Win+M最小化所有窗口
                        pyautogui.hotkey('win', 'm')
                        return True
                    except Exception as alt_err:
                        logger.error(f"替代方法也失败: {str(alt_err)}")
                
                return False
    
    return False

# 添加处理桌面场景判断
def is_desktop_task(task):
    """
    判断任务是否需要从桌面开始
    
    Args:
        task (str): 任务描述
        
    Returns:
        bool: 是否需要从桌面开始
    """
    desktop_keywords = [
        '打开', '启动', '运行', '开始', '执行', '从桌面', 
        '桌面图标', '桌面快捷方式', '程序', '应用', '在桌面'
    ]
    
    task = task.lower()  # 转换为小写进行比较
    
    # 如果任务包含这些关键词，可能需要从桌面开始
    return any(keyword in task for keyword in desktop_keywords)

def main():
    """
    微信助手主程序，控制整个流程
    """
    logger.info("微信自动化助手启动")
    print("欢迎使用微信自动化助手")
    
    # 创建截图保存目录
    screenshots_dir = os.path.join(parent_dir, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    
    task_completed = False
    
    while not task_completed:
        # 1. 获取用户输入（语音或文字）
        user_input = input("请输入您的指令（输入'exit'退出）: ")
        logger.info(f"用户输入: {user_input}")
        
        if user_input.lower() == 'exit':
            logger.info("用户选择退出程序")
            task_completed = True
            continue
        
        # 2. 确定操作类型
        print("请选择操作方式:")
        print("1. 键盘操作")
        print("2. 鼠标操作")
        print("3. 混合操作 (默认)")
        operation_choice = input("请选择 (1/2/3): ").strip()
        
        if operation_choice == '1':
            operation_type = "keyboard"
        elif operation_choice == '2':
            operation_type = "mouse"
        else:
            operation_type = "mixed"
        
        print(f"已选择: {operation_type} 操作方式")
        
        try:
            # 3. 初始化任务上下文
            task_context = {
                "task": user_input,
                "operation_type": operation_type,
                "method": operation_type,
                "instruction": user_input,
                "steps_executed": 0,
                "last_action": {},
                "context": "",
                "status": "进行中"
            }
            
            # 4. 初始文本分析
            logger.info(f"开始分析用户输入: {user_input}")
            print("正在分析您的指令...")
            text_analysis = analyze_text(user_input)
            
            if "error" in text_analysis:
                logger.error(f"文本分析失败: {text_analysis['error']}")
                print(f"分析指令时出错: {text_analysis['error']}")
                continue
            
            # 更新任务上下文
            task_context["task"] = text_analysis.get("task", user_input)
            task_context["context"] = text_analysis.get("context", "")
            
            logger.info(f"文本分析完成: {task_context['task']}")
            print(f"任务: {task_context['task']}")
            
            # 5. 开始执行循环
            max_steps = 15  # 最大步骤数，防止无限循环
            step_count = 0
            
            while step_count < max_steps and task_context["status"] == "进行中":
                # 5.1 获取当前屏幕截图
                print("\n第 " + str(step_count + 1) + " 轮循环")
                print("获取当前界面...")
                img_base64, screenshot_path = get_screenshot(screenshots_dir)
                if not img_base64:
                    print("无法获取屏幕截图，操作中止")
                    break
                
                print(f"已获取屏幕截图: {screenshot_path}")
                
                # 5.2 使用多轮对话分析当前屏幕，规划下一步操作
                print("使用多轮对话分析当前界面...")
                image_analysis = multi_round_image_analysis(img_base64, task_context)
                
                if "error" in image_analysis:
                    logger.error(f"图像多轮分析失败: {image_analysis['error']}")
                    print(f"分析界面时出错: {image_analysis['error']}")
                    # 当多轮分析失败时，尝试使用单轮分析作为备选
                    print("尝试使用单轮分析作为备选...")
                    image_analysis = analyze_image(img_base64, task_context)
                    if "error" in image_analysis:
                        print(f"备选分析也失败: {image_analysis['error']}")
                        break
                
                # 显示多轮对话分析结果
                print("\n------ 多轮对话分析结果 ------")
                
                # 显示当前场景
                current_scene = image_analysis.get("current_scene", "未提供场景描述")
                print(f"当前场景: {current_scene}")
                
                # 显示环境状态
                env_ready = image_analysis.get("environment_ready", False)
                print(f"环境就绪状态: {'✓' if env_ready else '✗'}")
                if not env_ready:
                    print("注意: 当前环境尚未准备好执行任务，需要先进行环境准备")
                
                # 显示目标元素
                target_elements = image_analysis.get("target_elements", [])
                if target_elements:
                    print(f"任务目标元素: {', '.join(target_elements)}")
                
                # 显示找到的元素
                elements_found = image_analysis.get("elements_found", [])
                if elements_found:
                    print("找到的元素:")
                    for element in elements_found:
                        print(f"  - {element.get('element', '未命名元素')} 位置:({element.get('x', 0)}, {element.get('y', 0)})")
                
                # 显示未找到的元素
                elements_not_found = image_analysis.get("elements_not_found", [])
                if elements_not_found:
                    print(f"未找到的元素: {', '.join(elements_not_found)}")
                
                # 显示分析推理
                reasoning = image_analysis.get("reasoning", "")
                if reasoning:
                    print(f"分析推理: {reasoning}")
                
                # 显示预期下一场景
                next_scene = image_analysis.get("next_expected_scene", "")
                if next_scene:
                    print(f"预期下一场景: {next_scene}")
                
                print("---------------------------\n")
                
                # 更新任务状态
                task_context["status"] = image_analysis.get("status", "进行中")
                
                # 打印更多任务状态信息，方便调试
                print(f"当前任务状态: {task_context['status']}")
                print(f"已执行步骤数: {task_context['steps_executed']}")
                if task_context["status"] == "已完成":
                    print("大模型判断任务已完成!")
                    
                    # 对于特定任务，额外验证任务是否真的完成
                    if "打开" in task_context["task"] and task_context["steps_executed"] == 0:
                        print("警告: 对于'打开应用'任务，如果没有执行任何步骤就判断为完成，这可能是错误的")
                        print("继续执行任务...")
                        task_context["status"] = "进行中"
                
                # 检查任务是否完成
                if task_context["status"] == "已完成":
                    print("任务已完成!")
                    break
                
                # 检查环境状态
                env_ready = image_analysis.get("environment_ready", False)
                if not env_ready:
                    print("当前环境不适合执行任务，尝试返回桌面...")
                    # 尝试返回桌面
                    return_desktop_action = {
                        "description": "返回Windows桌面",
                        "type": "keyboard",
                        "action": "hotkey",
                        "value": "win+d",
                        "delay": 1.0
                    }
                    
                    if safe_execute_action(return_desktop_action, task_context):
                        # 更新任务上下文
                        task_context["steps_executed"] += 1
                        task_context["last_action"] = return_desktop_action
                        print("已返回桌面")
                        # 跳过本轮剩余部分，进入下一轮循环
                        continue
                    else:
                        print("无法返回桌面，操作可能受限")
                        print("是否仍要继续？")
                        retry = input("输入'y'继续，其他退出: ").lower()
                        if retry != 'y':
                            break
                
                # 获取下一步操作
                steps = image_analysis.get("steps", [])
                if not steps:
                    logger.warning("未找到下一步操作")
                    
                    # 检查是否需要从桌面开始
                    if is_desktop_task(task_context.get("task", "")) and task_context["steps_executed"] == 0:
                        print("当前任务可能需要从桌面开始，尝试返回桌面...")
                        return_desktop_action = {
                            "description": "返回Windows桌面",
                            "type": "keyboard",
                            "action": "hotkey",
                            "value": "win+d",
                            "delay": 1.0
                        }
                        
                        if safe_execute_action(return_desktop_action, task_context):
                            # 更新任务上下文
                            task_context["steps_executed"] += 1
                            task_context["last_action"] = return_desktop_action
                            print("已返回桌面")
                            # 跳过本轮剩余部分，进入下一轮循环
                            continue
                        else:
                            print("无法返回桌面")
                    
                    print("分析结果中没有找到可执行的操作")
                    print("是否继续尝试？")
                    retry = input("输入'y'继续，其他退出: ").lower()
                    if retry == 'y':
                        continue
                    else:
                        break
                
                # 5.3 只执行下一步操作
                next_action = steps[0]
                
                # 执行操作
                if safe_execute_action(next_action, task_context):
                    # 更新任务上下文
                    task_context["steps_executed"] += 1
                    task_context["last_action"] = next_action
                    print(f"操作成功: {next_action['description']}")
                else:
                    print(f"操作失败: {next_action['description']}")
                    print("是否继续任务？")
                    retry = input("输入'y'继续，其他退出: ").lower()
                    if retry != 'y':
                        break
                
                # 增加步骤计数
                step_count += 1
                
                # 每3步询问用户是否继续
                if step_count % 3 == 0 and step_count < max_steps:
                    print(f"已执行{step_count}步操作，是否继续？")
                    continue_task = input("输入'y'继续，其他退出: ").lower()
                    if continue_task != 'y':
                        print("用户选择停止操作")
                        break
            
            # 任务结束
            if step_count >= max_steps and task_context["status"] == "进行中":
                print(f"已达到最大步骤数 {max_steps}，操作停止")
            
            print(f"操作流程结束，共执行了 {task_context['steps_executed']} 步操作")
            
        except Exception as e:
            logger.error(f"执行过程中发生错误: {str(e)}")
            print(f"执行过程中发生错误: {str(e)}")
            traceback.print_exc()  # 打印完整的错误堆栈
        
        # 询问是否继续新任务
        print("是否继续执行新的任务？")
        continue_input = input("输入'y'继续，其他退出: ").lower()
        if continue_input != 'y':
            logger.info("用户选择结束操作")
            task_completed = True
        else:
            logger.info("用户选择继续新任务")
    
    logger.info("微信自动化助手退出")

if __name__ == "__main__":
    main() 