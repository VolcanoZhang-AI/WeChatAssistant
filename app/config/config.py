#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# API配置
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "")

# 模型配置
QWEN_MAX_MODEL = "qwen-max"
QWEN_VL_MODEL = "qwen-vl-plus"

# 界面设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "微信自动化助手"

# 语音识别设置
SPEECH_LANG = "zh-CN"

# 其他通用设置
DEFAULT_TIMEOUT = 30  # 超时时间（秒）
DEFAULT_RETRY = 3  # 重试次数
OPERATION_DELAY = 0.5  # 操作之间的默认延迟（秒）

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = "wechat_assistant.log"

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WECHAT_GUIDE_PATH = os.path.join(BASE_DIR, "WeChat.md") 