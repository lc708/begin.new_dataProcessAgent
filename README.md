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

## 📦 安装和部署

### 环境要求
- Python 3.8+
- pip 包管理器

### 快速启动

1. **克隆项目**
```bash
git clone <project-url>
cd bpapp_004_dataprocessing
```

2. **创建并激活Python虚拟环境**
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
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp env.template .env
# 编辑 .env 文件，添加必要的API密钥（如OPENAI_API_KEY等）
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

## 🎯 使用指南

### 基础使用流程

1. **访问前端界面**：打开 http://localhost:8501
2. **上传数据文件**：支持拖拽上传CSV/Excel/JSON文件
3. **数据质量检查**：快速检查数据基本质量
4. **配置处理参数**：选择默认配置或自定义配置
5. **执行数据处理**：一键启动数据处理流程
6. **查看处理结果**：多维度展示处理结果和质量报告
7. **导出处理数据**：下载处理后的清洁数据

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
  sensitivity_threshold: 0.7
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

## 🧪 测试和开发

### 运行示例
```bash
# 确保已激活虚拟环境
python main.py  # 运行示例数据处理
```

### 开发环境设置
```bash
# 1. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 2. 安装开发依赖
pip install -r requirements.txt

# 3. 设置环境变量
cp env.template .env
# 编辑 .env 文件，添加你的API密钥

# 4. 验证安装
python -c "import streamlit, fastapi, pandas; print('安装成功！')"
```

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

## 📚 开发文档

详细的开发文档请参考：
- [设计文档](docs/design.md) - 系统架构和技术设计
- [开发记录](docs/detail_note.md) - 详细的开发过程记录
- [API文档](http://localhost:8000/docs) - 后端API接口文档

## 💡 常见问题

### Q: 如何添加新的脱敏策略？
A: 在 `utils/data_masking.py` 中添加新的脱敏函数，并在配置验证器中更新策略枚举。

### Q: 如何集成新的数据源？
A: 在 `main.py` 中添加新的数据读取函数，支持新的文件格式或数据库连接。

### Q: 如何自定义质量指标？
A: 在 `utils/quality_metrics.py` 中添加新的质量计算函数，并更新报告生成逻辑。

---

**让数据处理变得简单、安全、智能！** 🚀