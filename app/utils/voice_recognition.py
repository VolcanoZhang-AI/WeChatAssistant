#!/usr/bin/env python
# -*- coding: utf-8 -*-

import speech_recognition as sr
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

def recognize_speech():
    """
    使用麦克风录制语音并转换为文本
    
    Returns:
        str: 识别出的文本
    """
    logger.info("启动语音识别")
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            logger.info("开始录音，等待用户说话...")
            print("请说话...")
            # 调整麦克风适应环境噪声
            recognizer.adjust_for_ambient_noise(source)
            logger.debug("已完成环境噪声调整")
            # 录制音频
            audio = recognizer.listen(source)
            logger.info("录音完成，开始识别")
            
        try:
            # 使用Google语音识别API (也可以替换为其他API)
            print("正在识别...")
            text = recognizer.recognize_google(audio, language='zh-CN')
            logger.info(f"语音识别成功: {text}")
            print(f"识别结果: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("无法识别语音内容")
            print("无法识别语音")
            return ""
        except sr.RequestError as e:
            logger.error(f"语音识别服务请求失败: {str(e)}")
            print(f"语音识别服务出错: {e}")
            return ""
    except Exception as e:
        logger.error(f"语音识别过程中发生错误: {str(e)}")
        print(f"语音识别错误: {e}")
        return ""

if __name__ == "__main__":
    # 测试语音识别功能
    result = recognize_speech()
    print(f"识别结果: {result}") 