# 数据处理Agent - 环境设置指南

本文档详细说明如何正确设置Python虚拟环境并安装项目依赖。

## 📋 前置要求

- Python 3.8 或更高版本
- pip 包管理器
- 命令行终端（Terminal/Command Prompt）

## 🐍 虚拟环境设置

### 为什么使用虚拟环境？

虚拟环境的优势：
- ✅ **隔离依赖**：避免不同项目之间的包版本冲突
- ✅ **环境一致性**：确保开发和生产环境的一致性
- ✅ **便于管理**：可以轻松删除和重建环境
- ✅ **系统保护**：不会影响系统全局的Python环境

### 步骤1：创建虚拟环境

```bash
# 进入项目目录
cd bpapp_004_dataprocessing

# 创建名为 venv 的虚拟环境
python -m venv venv
```

### 步骤2：激活虚拟环境

#### Windows系统
```cmd
# Command Prompt
venv\Scripts\activate

# PowerShell
venv\Scripts\Activate.ps1
```

#### macOS/Linux系统
```bash
source venv/bin/activate
```

### 步骤3：验证虚拟环境

激活成功后，命令行提示符前应该显示 `(venv)`：

```bash
(venv) $ python --version
(venv) $ which python  # macOS/Linux
(venv) $ where python  # Windows
```

### 步骤4：升级pip（推荐）

```bash
(venv) $ python -m pip install --upgrade pip
```

### 步骤5：安装项目依赖

```bash
(venv) $ pip install -r requirements.txt
```

### 步骤6：验证安装

**快速验证**：
```bash
(venv) $ python -c "import streamlit, fastapi, pandas, numpy; print('✅ 所有依赖安装成功！')"
```

**完整验证**（推荐）：
```bash
(venv) $ python test_installation.py
```

这个测试脚本会检查：
- ✅ 所有依赖模块是否正确安装
- ✅ 项目自定义模块是否可以导入
- ✅ 基本功能是否正常工作
- ✅ 环境配置是否正确

## 🔧 环境配置

### 配置环境变量

1. **复制环境变量模板**
```bash
cp env.template .env
```

2. **编辑 .env 文件**
```bash
# 使用你喜欢的编辑器
nano .env  # Linux/macOS
notepad .env  # Windows
```

3. **添加必要的API密钥**
```bash
# OpenAI API密钥（用于智能脱敏功能）
OPENAI_API_KEY=your_openai_api_key_here

# 其他可选配置
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4
```

## 🚀 启动应用

### 启动后端服务

```bash
(venv) $ python run_backend.py
```

成功启动后会看到：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 启动前端界面（新开终端）

```bash
# 新开一个终端窗口
cd bpapp_004_dataprocessing

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 启动前端
(venv) $ python run_frontend.py
```

成功启动后会看到：
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

## 🛠️ 常见问题解决

### 问题1：python命令找不到

**解决方案**：
```bash
# 尝试使用 python3
python3 -m venv venv

# 或者指定完整路径
/usr/bin/python3 -m venv venv
```

### 问题2：pip安装失败

**解决方案**：
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 问题3：权限错误（Windows）

**解决方案**：
```powershell
# 以管理员身份运行PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题4：虚拟环境激活失败

**解决方案**：
```bash
# 检查虚拟环境是否创建成功
ls venv/  # macOS/Linux
dir venv\  # Windows

# 重新创建虚拟环境
rm -rf venv  # macOS/Linux
python -m venv venv
```

### 问题5：依赖安装冲突

**解决方案**：
```bash
# 清理pip缓存
pip cache purge

# 重新安装
pip install --no-cache-dir -r requirements.txt

# 或者逐个安装核心依赖
pip install streamlit fastapi pandas numpy
```

## 📦 虚拟环境管理

### 导出当前环境依赖

```bash
(venv) $ pip freeze > requirements_freeze.txt
```

### 停用虚拟环境

```bash
(venv) $ deactivate
```

### 删除虚拟环境

```bash
# 停用环境后删除文件夹
rm -rf venv  # macOS/Linux
# 或手动删除 venv 文件夹  # Windows
```

### 重建虚拟环境

```bash
# 删除旧环境
rm -rf venv

# 创建新环境
python -m venv venv

# 激活环境
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 💡 最佳实践

1. **始终使用虚拟环境**：每个Python项目都应该有独立的虚拟环境
2. **定期更新依赖**：定期检查和更新项目依赖到最新版本
3. **备份环境配置**：使用`requirements.txt`记录精确的依赖版本
4. **环境变量安全**：不要将包含敏感信息的`.env`文件提交到版本控制
5. **文档化配置**：记录所有必要的环境变量和配置步骤

## 🔍 环境验证清单

安装完成后，请检查以下项目：

- [ ] Python虚拟环境已创建并激活
- [ ] 所有依赖包已成功安装
- [ ] 环境变量已正确配置
- [ ] 后端服务可以正常启动（http://localhost:8000）
- [ ] 前端界面可以正常访问（http://localhost:8501）
- [ ] 可以成功上传和处理测试数据文件

如果所有项目都已完成，恭喜您！环境已成功设置，可以开始使用数据处理Agent了！ 🎉

---

如有其他问题，请参考 [README.md](README.md) 或提交 Issue。
