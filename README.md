# 数据处理Agent - MACore项目

基于MACore框架的智能数据标准化和预处理系统，采用前后端分离架构，专注于数据质量提升和敏感信息保护。

## 🚀 项目特色

- **智能数据处理**：自动化数据标准化、缺失值处理、类型转换
- **AI驱动脱敏**：使用LLM智能识别敏感字段，自动执行数据脱敏
- **全流程可视化**：Streamlit前端界面，直观展示处理过程和结果
- **企业级API**：FastAPI后端服务，支持异步处理和状态跟踪
- **配置化管理**：灵活的配置系统，支持自定义处理策略
- **质量报告**：详细的数据质量分析和处理前后对比

## 🏗️ 系统架构

```
数据处理Agent
├── 前端界面 (Streamlit)
│   ├── 数据上传与预览
│   ├── 配置管理
│   ├── 处理结果展示
│   └── 质量报告可视化
├── 后端API (FastAPI)
│   ├── 数据处理接口
│   ├── 状态查询接口
│   ├── 配置验证接口
│   └── 数据导出接口
└── 处理引擎 (MACore)
    ├── 数据验证节点
    ├── 表结构标准化节点
    ├── 缺失值处理节点
    ├── 智能脱敏Agent节点
    ├── 特征提取节点
    └── 质量报告节点
```

## 📋 核心功能

### 1. 数据标准化
- ✅ 列名格式统一 (snake_case/camelCase/PascalCase)
- ✅ 数据类型自动检测和转换
- ✅ 重复列和空列自动清理
- ✅ 自定义类型映射规则

### 2. 缺失值处理
- ✅ 多种填充策略 (均值/中位数/众数/前向填充/后向填充)
- ✅ 按列自定义处理策略
- ✅ 缺失率阈值控制
- ✅ 自定义填充值设置

### 3. 智能数据脱敏
- 🤖 **AI识别敏感字段**：手机号、身份证、邮箱、姓名、地址
- 🔒 **多种脱敏策略**：部分脱敏、哈希脱敏、随机脱敏、删除脱敏
- ⚙️ **配置化规则**：支持自定义脱敏规则和策略
- 👁️ **脱敏预览**：处理前后数据对比展示

### 4. 数据质量分析
- 📊 **质量指标计算**：完整性、一致性、整体质量得分
- 📈 **质量改善跟踪**：处理前后质量对比
- 📝 **详细报告生成**：文本和图表形式的质量报告
- 🔍 **异常数据识别**：自动标记潜在问题

### 5. 特征提取（可选）
- 🔢 **数值特征**：统计特征、空值标记、绝对值等
- 📝 **文本特征**：长度、词数、空值标记等
- 📅 **时间特征**：年、月、星期等时间维度

## 🛠️ 技术栈

### 后端技术
- **框架**：MACore (工作流编排) + FastAPI (API服务)
- **数据处理**：Pandas + NumPy
- **配置管理**：Pydantic + PyYAML
- **AI集成**：OpenAI API (敏感字段识别)

### 前端技术
- **框架**：Streamlit
- **可视化**：Plotly
- **数据展示**：Pandas DataFrame组件

### 支持格式
- **输入**：CSV、Excel (.xlsx/.xls)、JSON
- **输出**：CSV、Excel、JSON

## 📦 本地开发环境设置

### 环境要求
- Python 3.8+
- pip 包管理器

### 快速启动

1. **克隆项目**
```bash
git clone <project-url>
cd bpapp_004_dataprocessing
```

2. **创建并激活Python虚拟环境** ⚠️ **重要步骤**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. **安装依赖**
```bash
# 确保虚拟环境已激活（命令行前应显示 (venv)）
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp env.template .env
# 编辑 .env 文件，添加必要的API密钥
```

5. **启动后端服务**
```bash
python run_backend.py
# 后端服务将在 http://localhost:8000 启动
```

6. **启动前端界面**（新开终端窗口）
```bash
# 确保激活虚拟环境
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

python run_frontend.py
# 前端界面将在 http://localhost:8501 启动
```

### 验证安装
```bash
# 快速验证
python -c "import streamlit, fastapi, pandas, numpy; print('✅ 所有依赖安装成功！')"

# 检查API健康状态
curl http://localhost:8000/health
```

## 🚢 生产环境部署 (Railway)

### 🏗️ 部署架构
项目使用Nginx + Supervisor架构，实现前后端统一部署：

```
Railway容器
├── Nginx (动态端口) - 反向代理
│   ├── / → Streamlit前端界面
│   ├── /api/ → FastAPI后端API
│   ├── /docs → API文档
│   └── /health → 健康检查
├── FastAPI后端 (localhost:8000)
└── Streamlit前端 (localhost:8501)
```

### 📁 部署文件说明
- `railway.json` - Railway平台配置
- `Dockerfile` - Docker构建配置（包含Nginx+Supervisor）
- `nginx.conf` - Nginx反向代理配置
- `supervisord.conf` - 进程管理配置
- `start_with_nginx.sh` - 启动脚本

### 🚀 Railway部署步骤

1. **连接GitHub仓库**
   - 登录 [Railway](https://railway.app)
   - 点击 "New Project" → "Deploy from GitHub repo"
   - 选择您的项目仓库

2. **配置环境变量**
   
   在Railway项目设置 → Variables 中**只需添加**以下核心变量：
   ```bash
   # 🔑 LLM配置（必需）
   OPENAI_API_KEY=sk-your-openai-api-key-here
   LLM_PROVIDER=openai
   OPENAI_MODEL=gpt-4o
   
   # 🌐 应用配置（必需）
   RAILWAY_ENVIRONMENT=production
   BASE_URL=https://app-dataprocessing.begin.new
   
   # 🛠 系统配置（推荐）
   PYTHONPATH=/app
   PYTHONUNBUFFERED=1
   LOG_LEVEL=INFO
   TZ=Asia/Shanghai
   ```
   
   **注意**：不需要配置端口相关变量，Nginx会自动处理端口路由。

3. **配置自定义域名**
   - 进入项目 → Settings → Networking
   - 添加自定义域名: `app-dataprocessing.begin.new`

4. **部署验证**
   - 检查构建日志确认Nginx+Supervisor启动成功
   - 访问前端界面: `https://app-dataprocessing.begin.new/`
   - 访问API文档: `https://app-dataprocessing.begin.new/docs`
   - 访问健康检查: `https://app-dataprocessing.begin.new/health`

### 🔧 部署故障排除

**构建失败**
- 检查 `requirements.txt` 依赖版本
- 确认Dockerfile中的系统依赖安装是否成功
- 查看构建日志中的具体错误信息

**服务启动失败**
- 检查Supervisor日志：查看后端、前端、Nginx是否正常启动
- 验证环境变量设置完整性（特别是OPENAI_API_KEY）
- 确认端口配置：Railway会自动分配PORT给Nginx

**访问问题**
- 健康检查失败：访问 `/health` 端点检查后端状态
- 前端无法访问：检查Supervisor中的frontend进程状态
- API调用失败：验证 `/docs` 页面是否可以访问

**功能异常**
- LLM调用失败：检查API密钥有效性和配额限制
- 文件上传问题：确认前后端通信正常
- 数据处理错误：查看后端API日志

**日志查看**
- Railway Dashboard → Deployments → Logs
- 关键日志标识：`[nginx]`, `[backend]`, `[frontend]`, `[supervisor]`

## 🎯 使用指南

### 基础使用流程

1. **访问前端界面**：打开应用地址
2. **上传数据文件**：支持拖拽上传CSV/Excel/JSON文件
3. **数据质量检查**：快速检查数据基本质量
4. **配置处理参数**：选择默认配置或自定义配置
5. **执行数据处理**：一键启动数据处理流程
6. **查看处理结果**：多维度展示处理结果和质量报告
7. **导出处理数据**：下载处理后的清洁数据

### 脱敏参数调整

如果脱敏字段太多，可以调整 **敏感度阈值**：

| 阈值设置 | 脱敏字段数量 | 适用场景 |
|---------|-------------|---------|
| 0.5-0.6 | 很多字段 | 高安全要求 |
| 0.7 (默认) | 中等字段 | 平衡安全性和可用性 |
| 0.8-0.9 | 较少字段 | 注重数据可用性 |

**调整方法**：
1. 取消勾选 "使用默认配置"
2. 在 "数据脱敏" 部分调整 "敏感性检测阈值" 滑块
3. 向右调高阈值减少脱敏字段，向左调低阈值增加脱敏字段

### API使用示例

```python
import requests
import base64

# 1. 上传文件进行处理
with open('data.csv', 'rb') as f:
    file_content = base64.b64encode(f.read()).decode()

response = requests.post('http://localhost:8000/api/v1/process-data', 
    json={
        'file_data': file_content,
        'filename': 'data.csv',
        'config': None  # 使用默认配置
    }
)

job_id = response.json()['job_id']

# 2. 查询处理状态
status_response = requests.get(f'http://localhost:8000/api/v1/processing-status/{job_id}')
result = status_response.json()

# 3. 导出处理后数据
if result['status'] == 'completed':
    export_response = requests.post(f'http://localhost:8000/api/v1/export-data/{job_id}?format=csv')
    with open('processed_data.csv', 'wb') as f:
        f.write(export_response.content)
```

### 配置文件示例

```yaml
# config/custom_config.yaml
standardization:
  enable_column_rename: true
  naming_convention: "snake_case"
  auto_detect_types: true

missing_handling:
  default_strategy: "mean"
  missing_threshold: 0.8
  column_strategies:
    age: "median"
    name: "mode"

masking_rules:
  enable_auto_detection: true
  sensitivity_threshold: 0.7  # 调整此值控制脱敏严格程度
  column_rules:
    phone:
      type: "phone"
      strategy: "partial"
    email:
      type: "email"
      strategy: "hash"
```

## 📊 处理示例

### 输入数据
```csv
user_id,User Name,Age,Phone,Email,Salary
1,张三,25,13812345678,zhangsan@example.com,5000.5
2,李四,,15987654321,lisi@test.com,6000.0
3,王五,35,,wangwu@demo.org,
4,赵六,40,18611112222,,8000.0
```

### 处理后数据
```csv
user_id,user_name,age,phone,email,salary
1,张*,25,138****5678,zha****@example.com,5000.5
2,李*,32.5,159****4321,lis****@test.com,6000.0
3,王*,35,139****0000,wan****@demo.org,6500.0
4,赵*,40,186****2222,[已脱敏],8000.0
```

### 处理摘要
- ✅ 列名标准化：User Name → user_name
- ✅ 缺失值填充：Age列使用均值填充，Salary列使用均值填充
- 🔒 敏感字段脱敏：姓名、手机号、邮箱自动脱敏
- 📊 质量得分提升：76% → 95%

## 🧪 开发和测试

### 虚拟环境管理
```bash
# 停用虚拟环境
deactivate

# 重新激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 删除虚拟环境（如需重新创建）
rm -rf venv  # Linux/macOS
# 或手动删除 venv 文件夹  # Windows
```

### 开发环境验证
```bash
# 运行示例数据处理
python main.py

# 验证API文档
# 访问 http://localhost:8000/docs
```

### 常见问题

**Q: 虚拟环境激活失败？**
```bash
# Windows PowerShell权限问题
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 重新创建虚拟环境
rm -rf venv
python -m venv venv
```

**Q: 依赖安装失败？**
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**Q: 如何添加新的脱敏策略？**

在 `utils/data_masking.py` 中添加新的脱敏函数，并在配置验证器中更新策略枚举。

**Q: 如何自定义质量指标？**

在 `utils/quality_metrics.py` 中添加新的质量计算函数，并更新报告生成逻辑。

## 💡 技术特色

### LLM调用说明
系统仅在 **数据脱敏Agent节点** 中调用LLM，用于：
- 智能识别可能的敏感字段
- 对规则难以判断的字段进行智能分析
- 提供字段敏感性评分

### 处理流程
1. 🔍 数据验证和质量检查
2. 📋 表结构标准化
3. 🛠️ 缺失值智能填充  
4. 🤖 AI敏感字段检测 ← **LLM调用点**
5. 🛡️ 数据脱敏处理
6. 🎯 特征工程（可选）
7. 📊 质量报告生成

## 📚 API文档

### 🌐 访问方式

#### **生产环境** (Railway)
- **API文档**: `https://app-dataprocessing.begin.new/docs`
- **健康检查**: `https://app-dataprocessing.begin.new/health`  
- **前端界面**: `https://app-dataprocessing.begin.new/`

#### **本地开发环境**
- **API文档**: `http://localhost:8000/docs`
- **健康检查**: `http://localhost:8000/health`
- **前端界面**: `http://localhost:8501`

### 🔌 核心接口
- `POST /api/v1/process-data` - 数据处理主接口
- `GET /api/v1/processing-status/{job_id}` - 处理状态查询
- `POST /api/v1/validate-config` - 配置验证
- `GET /api/v1/default-config` - 获取默认配置
- `POST /api/v1/export-data/{job_id}` - 数据导出接口
- `GET /health` - 健康检查端点

### 🏗️ 架构说明
- **生产环境**: Nginx反向代理，所有请求通过统一域名访问
- **本地环境**: 前后端独立运行在不同端口

---

**让数据处理变得简单、安全、智能！** 🚀

**部署完成后访问：https://app-dataprocessing.begin.new** 🌐