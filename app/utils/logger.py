#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import sys
from logging.handlers import RotatingFileHandler
import sys
import os

# 获取当前文件所在目录的父目录的父目录（项目根目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置日志级别（从环境变量或使用默认值）
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = "wechat_assistant.log"

# 创建日志目录
log_dir = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 日志文件路径
log_file_path = os.path.join(log_dir, LOG_FILE)

# 创建日志记录器
logger = logging.getLogger('wechat_assistant')

# 设置日志级别
log_level_map = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
logger.setLevel(log_level_map.get(LOG_LEVEL, logging.INFO))

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(log_level_map.get(LOG_LEVEL, logging.INFO))

# 创建文件处理器（滚动日志文件，最大5MB，保留5个备份）
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
)
file_handler.setLevel(log_level_map.get(LOG_LEVEL, logging.INFO))

# 创建日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

# 设置处理器格式
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def get_logger():
    """
    获取日志记录器
    
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logger 