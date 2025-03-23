#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.utils.logger import get_logger

# 获取日志记录器
logger = get_logger()

def get_wechat_guide():
    """
    读取并解析微信操作指南文件
    
    Returns:
        dict: 包含微信操作指南的字典
    """
    logger.info("开始读取微信操作指南文件")
    guide_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'WeChat.md')
    
    if not os.path.exists(guide_path):
        logger.error(f"未找到微信操作指南文件: {guide_path}")
        print(f"警告: 未找到微信操作指南文件: {guide_path}")
        return {}
    
    try:
        with open(guide_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"成功读取微信操作指南文件: {guide_path}, 大小: {len(content)} 字节")
        
        # 解析指南内容为结构化数据
        guide = {}
        
        # 使用正则表达式提取标题和内容
        sections = re.split(r'#{1,5}\s+', content)
        section_titles = re.findall(r'#{1,5}\s+(.*)', content)
        
        for i, title in enumerate(section_titles):
            if i + 1 < len(sections):
                guide[title] = sections[i + 1].strip()
        
        logger.info(f"解析出 {len(guide)} 个指南部分: {', '.join(guide.keys())}")
        
        # 进一步结构化指南数据
        structured_guide = parse_structured_guide(guide)
        logger.info("指南结构化完成")
        
        return structured_guide
    except Exception as e:
        logger.error(f"读取或解析微信操作指南时出错: {str(e)}")
        print(f"解析微信操作指南出错: {str(e)}")
        return {}

def parse_structured_guide(guide):
    """
    进一步解析操作指南为结构化数据
    
    Args:
        guide (dict): 原始指南数据
        
    Returns:
        dict: 结构化的指南数据
    """
    logger.info("开始结构化解析操作指南")
    structured_guide = {
        'launch': {},
        'search': {},
        'chat': {}
    }
    
    try:
        # 解析启动微信的方法
        if '启动微信' in guide:
            logger.debug("解析'启动微信'部分")
            content = guide['启动微信']
            if '键盘启动' in content:
                keyboard_part = re.search(r'键盘启动[\s\S]*?(?=###|$)', content)
                if keyboard_part:
                    structured_guide['launch']['keyboard'] = keyboard_part.group().strip()
                    logger.debug("已解析键盘启动方法")
            
            if '鼠标启动' in content:
                mouse_part = re.search(r'鼠标启动[\s\S]*?(?=###|$)', content)
                if mouse_part:
                    structured_guide['launch']['mouse'] = mouse_part.group().strip()
                    logger.debug("已解析鼠标启动方法")
        else:
            logger.warning("未找到'启动微信'部分")
        
        # 解析搜索联系人的方法
        if '搜索联系人' in guide:
            logger.debug("解析'搜索联系人'部分")
            content = guide['搜索联系人']
            
            keyboard_part = re.search(r'键盘快捷搜索[\s\S]*?(?=###|$)', content)
            if keyboard_part:
                structured_guide['search']['keyboard'] = keyboard_part.group().strip()
                
                # 提取具体步骤
                steps = re.findall(r'(?<=\d\.\s).*', keyboard_part.group())
                structured_guide['search']['keyboard_steps'] = steps
                logger.debug(f"已解析键盘搜索步骤，共 {len(steps)} 步")
            
            mouse_part = re.search(r'鼠标配合键盘搜索[\s\S]*?(?=###|$)', content)
            if mouse_part:
                structured_guide['search']['mouse'] = mouse_part.group().strip()
                
                # 提取具体步骤
                steps = re.findall(r'(?<=\d\.\s).*', mouse_part.group())
                structured_guide['search']['mouse_steps'] = steps
                logger.debug(f"已解析鼠标搜索步骤，共 {len(steps)} 步")
        else:
            logger.warning("未找到'搜索联系人'部分")
        
        # 解析写入发送内容的方法
        if '写入发送内容' in guide:
            logger.debug("解析'写入发送内容'部分")
            content = guide['写入发送内容']
            steps = re.findall(r'(?<=\d\.\s).*', content)
            structured_guide['chat']['steps'] = steps
            logger.debug(f"已解析聊天步骤，共 {len(steps)} 步")
        else:
            logger.warning("未找到'写入发送内容'部分")
    except Exception as e:
        logger.error(f"结构化解析指南时出错: {str(e)}")
    
    # 检查解析结果完整性
    for section, content in structured_guide.items():
        if not content:
            logger.warning(f"指南部分 '{section}' 为空")
    
    return structured_guide

if __name__ == "__main__":
    # 测试解析功能
    guide = get_wechat_guide()
    print("解析结果:")
    import json
    print(json.dumps(guide, ensure_ascii=False, indent=2)) 