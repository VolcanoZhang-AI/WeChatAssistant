#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信自动化助手启动脚本
"""

import os
import sys

# 确保项目根目录在Python路径中
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入并运行主程序
from app.main import main

if __name__ == "__main__":
    main() 