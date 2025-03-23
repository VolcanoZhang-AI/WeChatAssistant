#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信自动化助手测试脚本 - 用于验证修复的问题
"""

import os
import sys
import time

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.controllers.action_executor import execute_action
from app.utils.logger import get_logger

# 获取日志记录器
logger = get_logger()

def test_check_environment():
    """测试环境检查操作是否能被正确处理"""
    print("\n=== 测试环境检查操作处理 ===")
    
    # 创建一个check_environment操作
    check_action = {
        "description": "检测当前是否处于Windows桌面",
        "type": "check_environment",
        "action": "check",
        "value": "desktop"
    }
    
    print(f"执行操作: {check_action['description']}")
    result = execute_action(check_action)
    
    if result:
        print("✓ 成功: 环境检查操作被正确处理")
    else:
        print("✗ 失败: 环境检查操作未被正确处理")
    
    return result

def test_return_to_desktop():
    """测试返回桌面操作是否能被正确执行"""
    print("\n=== 测试返回桌面操作 ===")
    
    # 创建一个返回桌面的操作
    desktop_action = {
        "description": "返回Windows桌面",
        "type": "keyboard",
        "action": "hotkey",
        "value": "win+d",
        "delay": 1.0
    }
    
    print(f"执行操作: {desktop_action['description']}")
    result = execute_action(desktop_action)
    
    if result:
        print("✓ 成功: 返回桌面操作被正确执行")
    else:
        print("✗ 失败: 返回桌面操作未被正确执行")
    
    return result

def test_desktop_task_detection():
    """测试桌面任务检测功能"""
    print("\n=== 测试桌面任务检测 ===")
    
    # 导入is_desktop_task函数
    sys.path.insert(0, os.path.join(current_dir, "app"))
    from main import is_desktop_task
    
    # 测试用例
    test_cases = [
        ("打开微信", True),
        ("启动Chrome浏览器", True),
        ("在桌面上查找文件", True),
        ("发送消息给张三", False),
        ("关闭当前窗口", False)
    ]
    
    all_passed = True
    
    for task, expected in test_cases:
        result = is_desktop_task(task)
        if result == expected:
            print(f"✓ 成功: '{task}' 检测为{result}，符合预期")
        else:
            print(f"✗ 失败: '{task}' 检测为{result}，预期为{expected}")
            all_passed = False
    
    if all_passed:
        print("所有桌面任务检测用例通过")
    else:
        print("部分桌面任务检测用例失败")
    
    return all_passed

def run_all_tests():
    """运行所有测试"""
    print("开始测试微信自动化助手修复...")
    
    test_results = {
        "环境检查操作处理": test_check_environment(),
        "返回桌面操作": test_return_to_desktop(),
        "桌面任务检测": test_desktop_task_detection()
    }
    
    print("\n=== 测试结果汇总 ===")
    all_passed = True
    for test_name, result in test_results.items():
        status = "通过" if result else "失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✓ 所有测试通过! 修复成功!")
    else:
        print("\n✗ 部分测试失败，修复不完全")

if __name__ == "__main__":
    run_all_tests() 