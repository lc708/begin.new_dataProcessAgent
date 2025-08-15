#!/usr/bin/env python3
"""
测试安装是否正确的快速验证脚本
"""
import sys

def test_imports():
    """测试所有必要的模块是否可以正常导入"""
    print("🧪 测试模块导入...")
    
    try:
        import pandas as pd
        print("✅ pandas导入成功")
    except ImportError as e:
        print(f"❌ pandas导入失败: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy导入成功")
    except ImportError as e:
        print(f"❌ numpy导入失败: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ streamlit导入成功")
    except ImportError as e:
        print(f"❌ streamlit导入失败: {e}")
        return False
    
    try:
        import fastapi
        print("✅ fastapi导入成功")
    except ImportError as e:
        print(f"❌ fastapi导入失败: {e}")
        return False
    
    try:
        import plotly
        print("✅ plotly导入成功")
    except ImportError as e:
        print(f"❌ plotly导入失败: {e}")
        return False
    
    try:
        import pydantic
        print("✅ pydantic导入成功")
    except ImportError as e:
        print(f"❌ pydantic导入失败: {e}")
        return False
    
    return True


def test_project_modules():
    """测试项目自定义模块是否可以正常导入"""
    print("\n🔧 测试项目模块...")
    
    try:
        from macore import Node, Flow
        print("✅ MACore框架导入成功")
    except ImportError as e:
        print(f"❌ MACore框架导入失败: {e}")
        return False
    
    try:
        from utils.call_llm import call_llm
        print("✅ LLM调用模块导入成功")
    except ImportError as e:
        print(f"❌ LLM调用模块导入失败: {e}")
        return False
    
    try:
        from utils.data_type_detector import detect_data_type
        print("✅ 数据类型检测模块导入成功")
    except ImportError as e:
        print(f"❌ 数据类型检测模块导入失败: {e}")
        return False
    
    try:
        from utils.sensitive_detector import detect_sensitive_field
        print("✅ 敏感字段检测模块导入成功")
    except ImportError as e:
        print(f"❌ 敏感字段检测模块导入失败: {e}")
        return False
    
    try:
        from utils.data_masking import mask_data
        print("✅ 数据脱敏模块导入成功")
    except ImportError as e:
        print(f"❌ 数据脱敏模块导入失败: {e}")
        return False
    
    try:
        from utils.quality_metrics import calculate_quality_metrics
        print("✅ 质量指标模块导入成功")
    except ImportError as e:
        print(f"❌ 质量指标模块导入失败: {e}")
        return False
    
    try:
        from utils.config_validator import validate_config
        print("✅ 配置验证模块导入成功")
    except ImportError as e:
        print(f"❌ 配置验证模块导入失败: {e}")
        return False
    
    try:
        from nodes import (
            DataValidationNode,
            TableStandardizationNode,
            MissingDataHandlingNode,
            DataMaskingAgentNode,
            FeatureExtractionNode,
            QualityReportNode
        )
        print("✅ 所有处理节点导入成功")
    except ImportError as e:
        print(f"❌ 处理节点导入失败: {e}")
        return False
    
    try:
        from flow import create_data_processing_flow
        print("✅ 数据处理流程导入成功")
    except ImportError as e:
        print(f"❌ 数据处理流程导入失败: {e}")
        return False
    
    return True


def test_basic_functionality():
    """测试基本功能是否正常工作"""
    print("\n⚙️ 测试基本功能...")
    
    try:
        import pandas as pd
        from utils.config_validator import get_default_config
        
        # 测试默认配置获取
        config = get_default_config()
        print("✅ 默认配置获取成功")
        
        # 测试DataFrame创建
        test_data = {'a': [1, 2, 3], 'b': ['x', 'y', 'z']}
        df = pd.DataFrame(test_data)
        print("✅ DataFrame创建成功")
        
        # 测试数据类型检测
        from utils.data_type_detector import detect_data_type
        data_type = detect_data_type(df['a'])
        print(f"✅ 数据类型检测成功: {data_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False


def check_environment():
    """检查环境配置"""
    print("\n🌍 检查环境配置...")
    
    print(f"Python版本: {sys.version}")
    
    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 运行在虚拟环境中")
    else:
        print("⚠️ 未检测到虚拟环境，建议使用虚拟环境")
    
    # 检查环境变量文件
    import os
    if os.path.exists('.env'):
        print("✅ 环境变量文件 .env 存在")
    else:
        print("⚠️ 环境变量文件 .env 不存在，某些功能可能无法正常工作")
        if os.path.exists('env.template'):
            print("💡 提示: 请复制 env.template 为 .env 并配置API密钥")


def main():
    """主测试函数"""
    print("🚀 数据处理Agent - 安装验证测试")
    print("=" * 50)
    
    # 检查环境
    check_environment()
    
    # 测试模块导入
    if not test_imports():
        print("\n❌ 依赖模块导入测试失败，请检查安装")
        return False
    
    # 测试项目模块
    if not test_project_modules():
        print("\n❌ 项目模块导入测试失败，请检查代码")
        return False
    
    # 测试基本功能
    if not test_basic_functionality():
        print("\n❌ 基本功能测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！安装成功！")
    print("\n📚 后续步骤:")
    print("1. 启动后端服务: python run_backend.py")
    print("2. 启动前端界面: python run_frontend.py")
    print("3. 访问前端界面: http://localhost:8501")
    print("4. 访问API文档: http://localhost:8000/docs")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
