# 微信自动化助手

基于Python和千问大模型的微信自动化助手，可以通过语音或文字指令自动完成微信操作。

## 功能特点

- 使用千问-max进行文本推理，分析用户指令并规划操作步骤
- 使用千问-vl-plus进行多模态分析，理解屏幕内容并执行精确操作
- 支持语音和文字输入指令
- 自动化执行微信常见操作，如启动微信、搜索联系人、发送消息等
- 基于WeChat.md操作指南，深度理解微信操作流程
- 完善的日志记录系统，便于调试和追踪问题

## 系统架构

该系统的工作流程如下：

1. **语音/文字输入** - 用户通过语音或文字输入任务指令
2. **大模型分析** - 使用千问-max模型分析指令，规划具体步骤
3. **获取当前界面** - 捕获当前屏幕内容
4. **界面分析** - 使用千问-vl-plus模型分析界面，找出操作元素
5. **规划键盘鼠标操作** - 根据分析结果规划具体的键盘鼠标操作步骤
6. **执行操作** - 自动执行规划的操作步骤
7. **循环机制** - 根据用户反馈决定是否继续下一轮操作

## 安装与配置

### 环境要求

- Python 3.8+
- 依赖包见requirements.txt
- 千问API密钥

### 安装步骤

1. 克隆仓库到本地
```bash
git clone https://github.com/yourusername/WeChatAssistant.git
cd WeChatAssistant
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
创建.env文件，添加以下内容：
```
QWEN_API_KEY=你的千问API密钥
LOG_LEVEL=INFO  # 可选：DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 使用方法

1. 启动助手（从项目根目录运行）
```bash
python run.py
```

2. 输入指令

输入您想要执行的操作指令，例如：
- "打开微信并搜索联系人张三"
- "发送消息'你好，周末有空吗？'"

3. 查看日志

运行日志保存在 `logs/wechat_assistant.log` 文件中，可以帮助您追踪程序执行情况和调试问题。日志级别可通过环境变量 `LOG_LEVEL` 设置。

## 日志记录系统

系统内置完善的日志记录功能，记录程序运行的各个阶段：

- **ERROR**: 记录操作失败、API调用错误等关键问题
- **WARNING**: 记录潜在问题或非关键错误
- **INFO**: 记录正常操作流程和状态变化
- **DEBUG**: 记录详细调试信息，如API请求和响应

日志同时输出到控制台和日志文件，便于实时查看和后期分析。

## 故障排除

### 导入错误

如果遇到 `ModuleNotFoundError: No module named 'app'` 之类的导入错误，请确保：

1. 从项目根目录运行 `python run.py`，而不是直接运行app目录下的文件
2. 如果仍有问题，可以尝试设置PYTHONPATH环境变量：
   ```bash
   # Windows
   set PYTHONPATH=%PYTHONPATH%;你的项目根目录路径
   
   # Linux/Mac
   export PYTHONPATH=$PYTHONPATH:你的项目根目录路径
   ```

## 注意事项

- 首次运行时可能需要授予屏幕截图和键盘鼠标控制权限
- 执行过程中请勿移动鼠标或使用键盘，以免干扰自动化操作
- 本工具仅供学习和个人使用，请勿用于商业或非法用途

## 开源许可

MIT License 