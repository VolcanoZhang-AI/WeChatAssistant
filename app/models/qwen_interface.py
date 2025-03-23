#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import base64
import requests
import re
from PIL import Image
from io import BytesIO
import time
from openai import OpenAI
import sys
import os

# 将项目根目录添加到Python路径以解决导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.utils.logger import get_logger

# 获取日志记录器
logger = get_logger()

# 从环境变量或配置文件获取API密钥
API_KEY = os.environ.get("QWEN_API_KEY", "QWEN_API_KEY")

# 千问 API 的基础 URL
QWEN_MAX_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
QWEN_VL_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

def analyze_text(user_input, wechat_guide=None):
    """
    使用千问-max模型分析文本指令，规划操作步骤
    
    Args:
        user_input (str): 用户输入的指令
        wechat_guide (dict): 微信操作指南
        
    Returns:
        dict: 分析结果，包含操作步骤
    """
    logger.info(f"开始分析文本指令: {user_input}")
    if not API_KEY:
        logger.error("QWEN_API_KEY 环境变量未设置")
        raise ValueError("QWEN_API_KEY 环境变量未设置")
    
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务的base_url
    )
    
    # 构建提示内容
    guide_content = ""
    if wechat_guide:
        guide_content = "微信操作指南:\n" + json.dumps(wechat_guide, ensure_ascii=False, indent=2)
        logger.debug("已添加微信操作指南到提示中")
    
    prompt = f"""
作为自动化助手，请分析以下用户指令，并生成详细的键盘鼠标操作步骤。
请参考提供的微信操作指南，并输出一个JSON格式的操作计划。

用户指令: {user_input}

{guide_content}

请输出包含以下字段的JSON：
{{
  "task": "任务描述",
  "operation_type": "launch/search/chat/other",
  "method": "keyboard/mouse/mixed",
  "steps": [
    {{
      "description": "步骤描述",
      "type": "keyboard/mouse",
      "action": "press/hotkey/write/click/move/drag/scroll",
      "value": "按键名或文本内容",
      "x": X坐标,
      "y": Y坐标,
      "delay": 延迟秒数
    }}
  ]
}}

只需输出JSON，不要有其他内容。
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen-max",
        "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的自动化助手，专门规划详细的键盘鼠标操作步骤。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
        ],
        "parameters": {}
    }
    
    try:
        logger.info("发送请求到千问-max模型")
        try:
            completion = client.chat.completions.create(
                model="qwen-max",  
                messages=[
                    {'role': 'system', 'content': '你是一个专业的自动化助手，专门规划详细的键盘鼠标操作步骤。你需要给出详细的键盘鼠标操作步骤，包括按键名、坐标、动作、延迟等。'},
                    {'role': 'user', 'content': prompt}],
                extra_body={
                    "enable_search": False
                }
            )
            logger.info("成功收到千问-max模型响应")
            content = completion.choices[0].message.content
        except Exception as api_error:
            logger.error(f"API调用失败: {str(api_error)}")
            return {"error": f"API调用失败: {str(api_error)}"}
            
        # 尝试解析JSON内容
        try:
            # 查找JSON内容（可能被包裹在代码块中）
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```|(\{[\s\S]*\})', content)
            if json_match:
                json_str = json_match.group(1) or json_match.group(2)
                result = json.loads(json_str)
                logger.info(f"成功解析JSON响应: {result.get('task', '未知任务')}")
                return result
            else:
                result = json.loads(content)
                logger.info(f"成功解析JSON响应: {result.get('task', '未知任务')}")
                return result
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"JSON解析错误: {str(e)}")
            logger.debug(f"原始响应内容: {content}")
            # 返回包含原始回复的简单格式
            return {"error": "解析失败", "raw_content": content}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"API请求错误: {str(e)}")
        return {"error": str(e)}

def analyze_image(image_data, task_context):
    """
    使用千问-vl-plus模型分析屏幕截图，基于任务上下文规划下一步操作
    
    Args:
        image_data (bytes): 屏幕截图的base64数据
        task_context (dict): 任务上下文，包含任务信息、已执行步骤等
        
    Returns:
        dict: 包含下一步操作的计划
    """
    logger.info("开始分析屏幕截图")
    if not API_KEY:
        logger.error("QWEN_API_KEY 环境变量未设置")
        raise ValueError("QWEN_API_KEY 环境变量未设置")

    client = OpenAI(
        api_key=API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    # 构建更详细的提示，包含任务上下文信息
    prompt = f"""
请分析这张屏幕截图，根据当前任务目标有针对性地寻找并识别关键元素，然后规划下一步操作。

当前任务上下文:
- 任务: {task_context.get('task', '未知任务')}
- 操作类型: {task_context.get('operation_type', 'unknown')}
- 方法: {task_context.get('method', 'mixed')}
- 已执行步骤数: {task_context.get('steps_executed', 0)}
- 用户原始指令: {task_context.get('instruction', '')}
- 上一步操作: {json.dumps(task_context.get('last_action', {}), ensure_ascii=False)}
- 附加说明: {task_context.get('context', '')}

针对性分析指南:
1. 首先明确当前任务需要寻找的特定元素（如图标、按钮、输入框、特定文本等）
2. 仔细分析图像中是否存在这些目标元素，给出具体坐标位置
3. 如果找到目标元素，提供精确的操作方法（点击、输入等）
4. 如果未找到目标元素，分析可能的原因并提供获取该元素的具体操作步骤
5. 提供操作理由，说明为什么这是最佳的下一步操作

例如：
- 如果任务是"打开微信"，应首先寻找微信图标，若找到则点击，若未找到则提供搜索微信或打开开始菜单的操作
- 如果任务是"发消息给联系人"，应首先确认是否已在微信界面，然后寻找联系人列表、搜索框等

请生成一个包含以下内容的JSON：
{{
  "task": "当前任务描述",
  "target_elements": ["目标元素1", "目标元素2"], // 当前任务需要寻找的关键元素
  "status": "进行中/已完成/需要用户确认/失败",
  "elements_found": [
    {{
      "element": "已找到的元素描述",
      "x": X坐标,
      "y": Y坐标,
      "confidence": 置信度
    }}
  ],
  "elements_not_found": ["未找到的元素1", "未找到的元素2"], // 需要但未找到的元素
  "steps": [
    {{
      "description": "下一步操作的详细描述，说明为什么需要这个操作",
      "type": "keyboard/mouse",
      "action": "press/hotkey/write/click/move/drag/scroll",
      "value": "按键名或文本内容",
      "x": X坐标,
      "y": Y坐标,
      "delay": 延迟秒数
    }}
  ],
  "reasoning": "分析逻辑和操作理由，说明为什么这是最佳的下一步操作"
}}

只需输出JSON，不要有其他内容。确保你的分析和操作建议非常针对性，直接服务于当前任务目标。
"""
    
    try:
        logger.info("发送请求到千问-vl-plus模型")
        try:
            completion = client.chat.completions.create(
                model="qwen-vl-plus",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的自动化助手，负责分析屏幕截图。输入是一张截图，输出是界面分析内容。当前界面是什么？\
                            当前界面有什么？界面有哪些button，有什么功能？以左上角为0，其xy坐标是多少？有哪些窗口，有什么功能？"

                    },
                    {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", 
                            "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                    ]
                    }
                ]
            )
            logger.info("成功收到千问-vl-plus模型响应")
            result = completion.choices[0].message.content
        except Exception as api_error:
            logger.error(f"VL模型API调用失败: {str(api_error)}")
            return {"error": f"VL模型API调用失败: {str(api_error)}"}
        
        # 尝试解析JSON内容
        try:
            # 查找JSON内容（可能被包裹在代码块中）
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```|(\{[\s\S]*\})', result)
            if json_match:
                json_str = json_match.group(1) or json_match.group(2)
                parsed_result = json.loads(json_str)
                
                # 检查解析结果是否为字典类型
                if not isinstance(parsed_result, dict):
                    logger.warning(f"解析结果不是字典类型，而是 {type(parsed_result)}，尝试转换")
                    
                    # 如果是列表类型，尝试转换为字典
                    if isinstance(parsed_result, list):
                        # 如果列表中有字典，使用第一个字典
                        dict_items = [item for item in parsed_result if isinstance(item, dict)]
                        if dict_items:
                            parsed_result = dict_items[0]
                            logger.info("成功从列表中提取字典")
                        else:
                            # 如果列表中没有字典，创建一个包含列表的字典
                            parsed_result = {
                                "task": "从列表转换的任务",
                                "status": "进行中",
                                "elements_found": [],
                                "steps": parsed_result if parsed_result else [],
                                "reasoning": "自动从列表转换"
                            }
                            logger.info("将列表转换为字典格式")
                
                # 确保结果包含必要的键
                if "steps" not in parsed_result:
                    parsed_result["steps"] = []
                if "task" not in parsed_result:
                    parsed_result["task"] = "未指定任务"
                if "elements_found" not in parsed_result:
                    parsed_result["elements_found"] = []
                if "status" not in parsed_result:
                    parsed_result["status"] = "进行中"
                if "reasoning" not in parsed_result:
                    parsed_result["reasoning"] = "未提供推理过程"
                if "target_elements" not in parsed_result:
                    parsed_result["target_elements"] = []
                if "elements_not_found" not in parsed_result:
                    parsed_result["elements_not_found"] = []
                
                # 检查任务是否已完成
                if "任务已完成" in result:
                    # 额外判断：如果是第一次分析屏幕（steps_executed为0）且返回"任务已完成"，通常是错误的
                    steps_executed = task_context.get('steps_executed', 0)
                    if steps_executed > 0:
                        parsed_result["status"] = "已完成"
                        logger.info("检测到任务已完成的信息，执行步骤数大于0，确认任务已完成")
                    else:
                        # 如果尚未执行任何步骤，则不应直接判定为任务完成
                        logger.warning("任务刚开始（未执行任何步骤）就检测到'任务已完成'信息，这可能是错误判断")
                        parsed_result["status"] = "进行中"
                elif parsed_result.get("status") == "已完成":
                    # 如果模型返回的状态为"已完成"，同样进行验证
                    steps_executed = task_context.get('steps_executed', 0)
                    if steps_executed > 0:
                        logger.info("模型返回的状态为'已完成'，且执行步骤数大于0，确认任务已完成")
                    else:
                        # 如果尚未执行任何步骤，则不应直接判定为任务完成
                        logger.warning("任务刚开始（未执行任何步骤）就收到'已完成'状态，这可能是错误判断")
                        parsed_result["status"] = "进行中"
                
                # 添加原始回复内容，以便检查是否包含"任务已完成"等信息
                parsed_result["raw_content"] = result
                
                logger.info(f"成功解析图像分析JSON: 状态={parsed_result['status']}, 找到 {len(parsed_result.get('elements_found', []))} 个元素，{len(parsed_result.get('steps', []))} 个操作步骤")
                logger.debug(f"推理过程: {parsed_result.get('reasoning', '无')}")
                return parsed_result
            else:
                # 尝试直接解析JSON
                try:
                    parsed_result = json.loads(result)
                    
                    # 检查和处理与上面相同的逻辑
                    if not isinstance(parsed_result, dict):
                        logger.warning(f"解析结果不是字典类型，而是 {type(parsed_result)}，尝试转换")
                        
                        if isinstance(parsed_result, list):
                            dict_items = [item for item in parsed_result if isinstance(item, dict)]
                            if dict_items:
                                parsed_result = dict_items[0]
                                logger.info("成功从列表中提取字典")
                            else:
                                parsed_result = {
                                    "task": "从列表转换的任务",
                                    "status": "进行中",
                                    "elements_found": [],
                                    "steps": parsed_result if parsed_result else [],
                                    "reasoning": "自动从列表转换"
                                }
                                logger.info("将列表转换为字典格式")
                    
                    # 确保结果包含必要的键
                    if "steps" not in parsed_result:
                        parsed_result["steps"] = []
                    if "task" not in parsed_result:
                        parsed_result["task"] = "未指定任务"
                    if "elements_found" not in parsed_result:
                        parsed_result["elements_found"] = []
                    if "status" not in parsed_result:
                        parsed_result["status"] = "进行中"
                    if "reasoning" not in parsed_result:
                        parsed_result["reasoning"] = "未提供推理过程"
                    if "target_elements" not in parsed_result:
                        parsed_result["target_elements"] = []
                    if "elements_not_found" not in parsed_result:
                        parsed_result["elements_not_found"] = []
                    
                    # 检查任务是否已完成
                    if "任务已完成" in result:
                        # 额外判断：如果是第一次分析屏幕（steps_executed为0）且返回"任务已完成"，通常是错误的
                        steps_executed = task_context.get('steps_executed', 0)
                        if steps_executed > 0:
                            parsed_result["status"] = "已完成"
                            logger.info("检测到任务已完成的信息，执行步骤数大于0，确认任务已完成")
                        else:
                            # 如果尚未执行任何步骤，则不应直接判定为任务完成
                            logger.warning("任务刚开始（未执行任何步骤）就检测到'任务已完成'信息，这可能是错误判断")
                            parsed_result["status"] = "进行中"
                    elif parsed_result.get("status") == "已完成":
                        # 如果模型返回的状态为"已完成"，同样进行验证
                        steps_executed = task_context.get('steps_executed', 0)
                        if steps_executed > 0:
                            logger.info("模型返回的状态为'已完成'，且执行步骤数大于0，确认任务已完成")
                        else:
                            # 如果尚未执行任何步骤，则不应直接判定为任务完成
                            logger.warning("任务刚开始（未执行任何步骤）就收到'已完成'状态，这可能是错误判断")
                            parsed_result["status"] = "进行中"
                    
                    # 添加原始回复内容
                    parsed_result["raw_content"] = result
                    
                    logger.info(f"成功解析图像分析JSON: 状态={parsed_result['status']}, 找到 {len(parsed_result.get('elements_found', []))} 个元素，{len(parsed_result.get('steps', []))} 个操作步骤")
                    logger.debug(f"推理过程: {parsed_result.get('reasoning', '无')}")
                    return parsed_result
                except json.JSONDecodeError:
                    # 如果直接解析失败，尝试提取任何类似JSON的部分
                    logger.warning("直接解析JSON失败，尝试提取任何类似JSON的部分")
                    
                    # 检查是否包含任务完成的提示
                    task_completed = "任务已完成" in result
                    # 额外判断：需要考虑已执行的步骤数
                    steps_executed = task_context.get('steps_executed', 0)
                    status = "已完成" if (task_completed and steps_executed > 0) else "需要用户确认"
                    if task_completed and steps_executed == 0:
                        logger.warning("任务刚开始（未执行任何步骤）就检测到'任务已完成'信息，这可能是错误判断")
                    
                    fallback_result = {
                        "error": "解析失败，未找到有效JSON",
                        "raw_content": result,
                        "task": "未能解析的任务",
                        "status": status,
                        "elements_found": [],
                        "steps": [],
                        "reasoning": "无法解析模型回复为有效JSON"
                    }
                    return fallback_result
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"JSON解析错误: {str(e)}")
            logger.debug(f"原始响应内容: {result}")
            
            # 检查是否包含任务完成的提示
            task_completed = "任务已完成" in result
            # 额外判断：需要考虑已执行的步骤数
            steps_executed = task_context.get('steps_executed', 0)
            status = "已完成" if (task_completed and steps_executed > 0) else "需要用户确认"
            if task_completed and steps_executed == 0:
                logger.warning("任务刚开始（未执行任何步骤）就检测到'任务已完成'信息，这可能是错误判断")
            
            # 返回包含原始回复的简单格式，同时确保包含必要的键
            return {
                "error": f"解析失败: {str(e)}", 
                "raw_content": result,
                "task": "解析失败的任务",
                "status": status,
                "elements_found": [],
                "steps": [],
                "reasoning": f"解析失败: {str(e)}"
            }
            
    except Exception as e:
        logger.error(f"图像分析过程中发生错误: {str(e)}")
        return {
            "error": str(e),
            "task": "出错的任务",
            "status": "失败",
            "elements_found": [],
            "steps": [],
            "reasoning": f"发生错误: {str(e)}"
        }

def multi_round_image_analysis(image_data, task_context):
    """
    通过多轮对话与大模型分析图像，更准确地识别元素和确定操作
    
    Args:
        image_data (bytes): 屏幕截图的base64数据
        task_context (dict): 任务上下文，包含任务信息、已执行步骤等
        
    Returns:
        dict: 包含下一步操作的计划
    """
    logger.info("开始多轮对话图像分析")
    if not API_KEY:
        logger.error("QWEN_API_KEY 环境变量未设置")
        raise ValueError("QWEN_API_KEY 环境变量未设置")

    client = OpenAI(
        api_key=API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    # 第一轮：场景识别 - 确定当前屏幕环境
    prompt_scene = f"""
首先识别当前屏幕场景。请详细分析这个屏幕截图，回答以下问题：
1. 当前是否在Windows桌面？如果不是，当前环境是什么？
2. 是否可以看到以下任何界面元素：开始菜单、任务栏、桌面图标、应用窗口？
3. 当前屏幕最主要/最突出的应用或界面是什么？

请仅回答上述问题，简明扼要地描述您在图像中看到的内容。
"""
    
    try:
        logger.info("第一轮对话：场景识别")
        scene_response = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_scene},
                    {"type": "image_url", 
                        "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                ]
            }]
        )
        scene_result = scene_response.choices[0].message.content
        logger.info(f"场景识别结果: {scene_result}")
        
        # 第二轮：目标元素识别 - 寻找任务相关的特定元素
        prompt_elements = f"""
基于任务要求，请识别屏幕上的特定元素。

任务信息: {task_context.get('task', '未知任务')}

当前场景描述: {scene_result}

请回答以下问题：
1. 根据任务"{task_context.get('task', '未知任务')}"，我们需要寻找哪些特定元素？请列出完成任务所需的关键元素。
2. 这些元素在当前屏幕上是否可见？对于每个元素，给出以下信息：
   a. 元素名称
   b. 是否可见
   c. 如果可见，它的大致位置坐标(x,y)
3. 如果关键元素不可见，需要执行什么操作才能看到它们？

请详细且具体地回答，这将帮助确定下一步操作。
"""
        
        logger.info("第二轮对话：目标元素识别")
        elements_response = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_scene},
                        {"type": "image_url", 
                            "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                    ]
                },
                {
                    "role": "assistant",
                    "content": scene_result
                },
                {
                    "role": "user",
                    "content": prompt_elements
                }
            ]
        )
        elements_result = elements_response.choices[0].message.content
        logger.info(f"目标元素识别结果: {elements_result}")
        
        # 第三轮：行动规划 - 基于前两轮对话确定下一步操作
        prompt_action = f"""
基于当前场景和目标元素分析，请规划下一步具体操作。

任务信息: {task_context.get('task', '未知任务')}
已执行步骤数: {task_context.get('steps_executed', 0)}
上一步操作: {json.dumps(task_context.get('last_action', {}), ensure_ascii=False)}

当前场景: {scene_result}

目标元素分析: {elements_result}

考虑到当前环境和任务目标，请规划一个具体的操作步骤，确保操作安全且有效。特别注意：
1. 如果当前不在Windows桌面，且任务需要从桌面开始，请先提供返回桌面的操作（如使用Win+D快捷键）
2. 如果需要点击元素，请确保元素在当前屏幕可见，并提供准确的坐标
3. 对于不可见的元素，请提供合适的操作序列来访问它们
4. 考虑任务上下文和已执行步骤，避免重复操作

操作类型必须是以下之一：
- 键盘操作: type为"keyboard"，action为"press"/"hotkey"/"write"
- 鼠标操作: type为"mouse"，action为"click"/"move"/"drag"/"scroll"
不要使用其他类型的操作，如check_environment等，因为程序无法执行它们。

请生成一个标准JSON格式的操作计划，包含以下内容：
{{
  "task": "当前任务描述",
  "current_scene": "当前场景描述",
  "target_elements": ["目标元素1", "目标元素2"],
  "status": "进行中/已完成/需要用户确认/失败",
  "environment_ready": true/false,  // 当前环境是否已准备好执行任务
  "elements_found": [
    {{
      "element": "已找到的元素描述",
      "x": X坐标,
      "y": Y坐标,
      "confidence": 置信度
    }}
  ],
  "elements_not_found": ["未找到的元素1", "未找到的元素2"],
  "steps": [
    {{
      "description": "下一步操作的详细描述",
      "type": "keyboard/mouse",  // 只能是这两种类型
      "action": "press/hotkey/write/click/move/drag/scroll",  // 只能是这些操作
      "value": "按键名或文本内容",
      "x": X坐标,
      "y": Y坐标,
      "delay": 延迟秒数
    }}
  ],
  "reasoning": "分析逻辑和操作理由",
  "next_expected_scene": "执行操作后预期的场景"
}}

只需输出JSON，不要有其他内容。确保JSON格式正确，且操作步骤非常具体和精确。
"""
        
        logger.info("第三轮对话：行动规划")
        action_response = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_scene},
                        {"type": "image_url", 
                            "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                    ]
                },
                {
                    "role": "assistant",
                    "content": scene_result
                },
                {
                    "role": "user",
                    "content": prompt_elements
                },
                {
                    "role": "assistant",
                    "content": elements_result
                },
                {
                    "role": "user",
                    "content": prompt_action
                }
            ]
        )
        action_result = action_response.choices[0].message.content
        logger.info(f"行动规划结果: {action_result}")
        
        # 解析最终的JSON结果
        try:
            # 查找JSON内容（可能被包裹在代码块中）
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```|(\{[\s\S]*\})', action_result)
            if json_match:
                json_str = json_match.group(1) or json_match.group(2)
                parsed_result = json.loads(json_str)
            else:
                parsed_result = json.loads(action_result)
            
            # 确保结果包含必要的键
            if "steps" not in parsed_result:
                parsed_result["steps"] = []
            if "task" not in parsed_result:
                parsed_result["task"] = task_context.get("task", "未指定任务")
            if "elements_found" not in parsed_result:
                parsed_result["elements_found"] = []
            if "status" not in parsed_result:
                parsed_result["status"] = "进行中"
            if "reasoning" not in parsed_result:
                parsed_result["reasoning"] = "未提供推理过程"
            if "target_elements" not in parsed_result:
                parsed_result["target_elements"] = []
            if "elements_not_found" not in parsed_result:
                parsed_result["elements_not_found"] = []
            if "current_scene" not in parsed_result:
                parsed_result["current_scene"] = scene_result
            if "environment_ready" not in parsed_result:
                parsed_result["environment_ready"] = True
            if "next_expected_scene" not in parsed_result:
                parsed_result["next_expected_scene"] = "未指定"
            
            # 检查任务是否已完成
            if "任务已完成" in action_result:
                steps_executed = task_context.get('steps_executed', 0)
                if steps_executed > 0:
                    parsed_result["status"] = "已完成"
                    logger.info("多轮分析检测到任务已完成，且执行步骤大于0")
                else:
                    logger.warning("任务未执行任何步骤就被判断为完成，可能有误")
                    parsed_result["status"] = "进行中"
            
            # 添加对话历史到结果中
            parsed_result["conversation_history"] = {
                "scene_analysis": scene_result,
                "elements_analysis": elements_result,
                "action_planning": action_result
            }
            
            logger.info("多轮对话图像分析完成")
            return parsed_result
            
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"解析多轮对话结果时出错: {str(e)}")
            # 构建一个基本的返回结构
            return {
                "error": f"解析多轮对话结果失败: {str(e)}",
                "conversation_history": {
                    "scene_analysis": scene_result,
                    "elements_analysis": elements_result,
                    "action_planning": action_result
                },
                "task": task_context.get("task", "未知任务"),
                "status": "需要用户确认",
                "elements_found": [],
                "elements_not_found": [],
                "steps": [],
                "reasoning": "解析失败，请检查原始对话结果"
            }
        
    except Exception as e:
        logger.error(f"多轮对话图像分析过程中发生错误: {str(e)}")
        return {
            "error": str(e),
            "task": task_context.get("task", "出错的任务"),
            "status": "失败",
            "elements_found": [],
            "elements_not_found": [],
            "steps": [],
            "reasoning": f"多轮对话过程中发生错误: {str(e)}"
        }

if __name__ == "__main__":
    # 测试文本分析
    sample_input = "打开微信并搜索联系人张三"
    result = analyze_text(sample_input, {})
    print("文本分析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2)) 