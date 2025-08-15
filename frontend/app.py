"""
数据处理Agent的Streamlit前端界面
提供用户友好的数据上传、配置、处理和结果展示功能
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import base64
import json
import time
import io
import sys
import os
from typing import Dict, Any, Optional

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import process_dataframe, validate_data_only
from utils.config_validator import get_default_config, get_config_template


# 页面配置
st.set_page_config(
    page_title="数据处理Agent",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.section-header {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2e7d32;
    margin-top: 2rem;
    margin-bottom: 1rem;
}
.metric-card {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.success-message {
    background-color: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #c3e6cb;
}
.error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #f5c6cb;
}
.sidebar-radio {
    margin-bottom: 0.5rem;
}
.sidebar-radio > div {
    background-color: #f8f9fa;
    padding: 0.5rem;
    border-radius: 0.5rem;
    margin-bottom: 0.3rem;
}
.sidebar-radio > div:hover {
    background-color: #e9ecef;
    transition: background-color 0.2s;
}
.guide-text {
    font-size: 0.85rem;
    line-height: 1.4;
    color: #666;
}
.github-button {
    background-color: #24292e !important;
    color: white !important;
    padding: 8px 16px;
    border-radius: 6px;
    text-decoration: none !important;
    display: inline-block;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    transition: all 0.2s ease;
    border: none;
}
.github-button:hover {
    background-color: #0366d6 !important;
    color: white !important;
    text-decoration: none !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)


def main():
    """主应用函数"""
    
    # 标题和GitHub链接
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<h1 class="main-header">🔄 数据处理Agent</h1>', unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="text-align: right; margin-top: 20px;">
            <a href="https://github.com/lc708/begin.new_dataProcessAgent" target="_blank" class="github-button">
                📁 GitHub源码
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("基于MACore框架的智能数据标准化和预处理Agent - powered by [begin.new](https://www.begin.new/)")
    
    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 功能导航")
        st.markdown("---")
        
        # 使用单选按钮替代下拉框，直接显示所有页面
        page_options = [
            "🔄 数据上传与处理",
            "⚙️ 配置管理", 
            "📋 处理历史",
            "💻 系统状态"
        ]
        
        page_display = st.radio(
            "请选择功能模块：",
            page_options,
            index=0,
            label_visibility="collapsed"
        )
        
        # 去掉图标，只保留文字用于后续匹配
        page = page_display.split(" ", 1)[1] if " " in page_display else page_display
        
        st.markdown("---")
        
        # 添加一些辅助信息
        st.markdown("### 📚 快速指南")
        st.markdown('<div class="guide-text">', unsafe_allow_html=True)
        st.markdown("""
        **🔄 数据处理**  
        上传文件，配置处理选项，查看结果
        
        **⚙️ 配置管理**  
        管理默认配置和自定义模板
        
        **📋 处理历史**  
        查看历史任务和结果
        
        **💻 系统状态**  
        监控系统运行状态
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 添加版本信息
        st.markdown("---")
        st.markdown("**版本信息**")
        st.caption("🔧 MACore Framework")
        st.caption("🚀 FastAPI + Streamlit")
        st.caption("🤖 AI-Powered Processing")
    
    # 路由到不同页面
    if page == "数据上传与处理":
        data_processing_page()
    elif page == "配置管理":
        config_management_page()
    elif page == "处理历史":
        processing_history_page()
    elif page == "系统状态":
        system_status_page()


def data_processing_page():
    """数据上传与处理页面"""
    st.markdown('<h2 class="section-header">📁 数据上传与处理</h2>', unsafe_allow_html=True)
    
    # 创建两列布局
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. 数据上传")
        
        # 文件上传
        uploaded_file = st.file_uploader(
            "选择数据文件",
            type=['csv', 'xlsx', 'xls', 'json'],
            help="支持CSV、Excel和JSON格式的数据文件"
        )
        
        if uploaded_file is not None:
            # 显示文件信息
            st.success(f"已上传文件: {uploaded_file.name}")
            
            # 读取并预览数据
            try:
                df = load_data(uploaded_file)
                
                st.subheader("📊 数据预览")
                
                # 基本信息
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.metric("行数", len(df))
                with col_info2:
                    st.metric("列数", len(df.columns))
                with col_info3:
                    st.metric("缺失值", df.isnull().sum().sum())
                
                # 数据预览表格
                st.dataframe(df.head(10), use_container_width=True)
                
                # 数据质量快速检查
                if st.button("🔍 数据质量检查", type="secondary"):
                    with st.spinner("正在检查数据质量..."):
                        validation_result = validate_data_only(df)
                        
                        if validation_result['success']:
                            st.success("数据质量检查完成！")
                            
                            errors = validation_result.get('validation_errors', [])
                            warnings = validation_result.get('validation_warnings', [])
                            
                            if errors:
                                st.error(f"发现 {len(errors)} 个错误:")
                                for error in errors:
                                    st.write(f"❌ {error}")
                            
                            if warnings:
                                st.warning(f"发现 {len(warnings)} 个警告:")
                                for warning in warnings:
                                    st.write(f"⚠️ {warning}")
                            
                            if not errors and not warnings:
                                st.success("✅ 数据质量良好，可以进行处理")
                        else:
                            st.error(f"数据质量检查失败: {validation_result.get('error', '未知错误')}")
                
            except Exception as e:
                st.error(f"数据加载失败: {str(e)}")
                uploaded_file = None
    
    with col2:
        st.subheader("2. 处理配置")
        
        # 配置选项
        use_default_config = st.checkbox("使用默认配置", value=True)
        
        if use_default_config:
            config = get_default_config()
            st.info("使用系统默认配置")
            
            # 为默认配置也显示配置说明
            show_config_explanation = st.checkbox("💡 查看配置说明", value=False, help="了解默认配置的具体功能")
            if show_config_explanation:
                display_config_explanation(config)
        else:
            st.subheader("自定义配置")
            config = configure_processing_options()
        
        # 显示当前配置
        with st.expander("查看当前配置", expanded=False):
            st.json(config)
    
    # 处理按钮和结果
    st.markdown('<h3 class="section-header">🚀 开始处理</h3>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        if st.button("开始数据处理", type="primary", use_container_width=True):
            process_data_workflow(df, config, uploaded_file.name)
    else:
        st.info("请先上传数据文件")


def get_config_explanations() -> Dict[str, Dict[str, str]]:
    """获取配置参数的详细解释"""
    return {
        "standardization": {
            "title": "📋 表结构标准化",
            "description": "统一数据表的结构格式，提高数据质量和一致性",
            "enable_column_rename": "启用列名标准化：将列名转换为统一格式（如snake_case），便于程序处理",
            "naming_convention": "列名命名规范：\n• snake_case: user_name\n• camelCase: userName\n• PascalCase: UserName",
            "remove_duplicate_columns": "移除重复列：自动删除内容完全相同的重复列，节省存储空间",
            "remove_empty_columns": "移除空列：删除完全没有数据的列，清理无用字段",
            "auto_detect_types": "自动类型检测：智能识别每列的最佳数据类型（数值、文本、日期等）",
            "custom_type_mapping": "自定义类型映射：为特定列指定数据类型，覆盖自动检测结果"
        },
        "missing_handling": {
            "title": "🔧 缺失值处理",
            "description": "智能填充或处理数据中的空值，提高数据完整性",
            "default_strategy": "默认填充策略：\n• mean: 用平均值填充\n• median: 用中位数填充\n• mode: 用众数填充\n• forward_fill: 用前一个值填充\n• backward_fill: 用后一个值填充\n• drop: 删除含空值的行",
            "column_strategies": "列特定策略：为不同列设置不同的填充策略",
            "custom_fill_values": "自定义填充值：为特定列指定固定的填充值",
            "missing_threshold": "缺失率阈值：当列的缺失率超过此值时，直接删除该列（0.9 = 90%）"
        },
        "masking_rules": {
            "title": "🛡️ 数据脱敏规则",
            "description": "自动识别和保护敏感信息，确保数据隐私安全",
            "enable_auto_detection": "启用智能检测：使用AI和规则自动识别手机号、邮箱、姓名等敏感字段",
            "default_strategy": "默认脱敏策略：\n• partial: 部分遮掩(138****5678)\n• hash: 哈希替换(a1b2c3d4)\n• random: 随机替换\n• remove: 完全删除",
            "column_rules": "列特定规则：为特定列设置专门的脱敏策略",
            "sensitivity_threshold": "敏感度阈值：AI判断字段敏感性的置信度阈值（0.7 = 70%）"
        },
        "feature_extraction": {
            "title": "🎯 特征提取",
            "description": "从原始数据中提取有用的统计和计算特征，丰富数据维度",
            "enable_extraction": "启用特征提取：是否执行特征工程步骤（默认关闭）",
            "extract_numeric_stats": "数值特征：提取统计指标（绝对值、是否为空等）",
            "extract_text_features": "文本特征：提取文本长度、词数、是否为空等特征",
            "extract_datetime_features": "时间特征：提取年、月、星期几等时间相关特征",
            "custom_features": "自定义特征：添加业务相关的特殊特征提取规则"
        }
    }


def display_config_explanation(config: Dict[str, Any]):
    """显示配置解释和操作总览"""
    explanations = get_config_explanations()
    
    # 配置参数说明
    st.markdown("### ⚙️ 当前配置解释")
    
    # 表结构标准化
    with st.expander("📋 表结构标准化", expanded=False):
        st.info(explanations['standardization']['description'])
        if config['standardization']['enable_column_rename']:
            st.markdown(f"✅ **列名标准化**: {config['standardization']['naming_convention']}")
        if config['standardization']['auto_detect_types']:
            st.markdown("✅ **自动类型检测**: 优化数据类型，节省内存")
    
    # 缺失值处理
    with st.expander("🔧 缺失值处理", expanded=False):
        st.info(explanations['missing_handling']['description'])
        st.markdown(f"✅ **默认策略**: {config['missing_handling']['default_strategy']}")
        st.markdown(f"✅ **缺失率阈值**: {config['missing_handling']['missing_threshold']:.0%} (超过此值删除列)")
    
    # 数据脱敏
    with st.expander("🛡️ 数据脱敏规则", expanded=True):
        st.info(explanations['masking_rules']['description'])
        if config['masking_rules']['enable_auto_detection']:
            st.markdown("✅ **AI智能检测**: 自动识别敏感字段")
            st.markdown(f"✅ **敏感度阈值**: {config['masking_rules']['sensitivity_threshold']:.1f}")
            st.markdown(f"✅ **脱敏策略**: {config['masking_rules']['default_strategy']}")
            
            # 敏感度调整建议
            st.markdown("**💡 调整脱敏字段数量：**")
            current_threshold = config['masking_rules']['sensitivity_threshold']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if current_threshold <= 0.6:
                    st.success("🔒 **高安全**: 更多字段被保护")
                else:
                    st.markdown("🔒 **高安全**: 阈值 ≤ 0.6")
            
            with col2:
                if 0.6 < current_threshold <= 0.8:
                    st.success("⚖️ **平衡模式**: 当前设置")
                else:
                    st.markdown("⚖️ **平衡模式**: 阈值 0.6-0.8")
            
            with col3:
                if current_threshold > 0.8:
                    st.success("📊 **重可用性**: 较少字段被脱敏")
                else:
                    st.markdown("📊 **重可用性**: 阈值 > 0.8")
        else:
            st.markdown("❌ **自动检测已关闭**: 仅处理明确指定的敏感字段")
    
    # 特征提取
    with st.expander("🎯 特征提取", expanded=False):
        st.info(explanations['feature_extraction']['description'])
        if config['feature_extraction']['enable_extraction']:
            st.markdown("✅ **特征提取已启用**")
            features = []
            if config['feature_extraction']['extract_numeric_stats']:
                features.append("数值统计特征")
            if config['feature_extraction']['extract_text_features']:
                features.append("文本长度特征")
            if config['feature_extraction']['extract_datetime_features']:
                features.append("时间相关特征")
            if features:
                st.markdown(f"• {', '.join(features)}")
        else:
            st.markdown("❌ **特征提取已关闭**")
    
    # 操作总览
    st.markdown("---")
    st.markdown("### 📋 处理流程预览")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**将要执行的操作：**")
        operations = []
        
        operations.append("🔍 数据验证和质量检查")
        if config['standardization']['enable_column_rename']:
            operations.append(f"📋 列名标准化 ({config['standardization']['naming_convention']})")
        if config['standardization']['auto_detect_types']:
            operations.append("🔧 自动数据类型优化")
        
        operations.append(f"🛠️ 缺失值填充 ({config['missing_handling']['default_strategy']})")
        
        if config['masking_rules']['enable_auto_detection']:
            operations.append("🤖 AI智能敏感字段检测")
            operations.append(f"🛡️ 数据脱敏 ({config['masking_rules']['default_strategy']})")
        
        if config['feature_extraction']['enable_extraction']:
            operations.append("🎯 特征工程")
        
        operations.append("📊 生成质量报告")
        
        for op in operations:
            st.markdown(f"• {op}")
    
    with col2:
        st.markdown("**预期效果：**")
        effects = [
            "数据格式统一标准化",
            "缺失值得到妥善处理", 
            "数据完整性显著提高"
        ]
        
        if config['masking_rules']['enable_auto_detection']:
            effects.extend([
                "敏感信息自动识别保护",
                "数据隐私安全合规"
            ])
        
        if config['feature_extraction']['enable_extraction']:
            effects.append("增加有价值的计算特征")
        
        effects.append("获得详细的质量分析报告")
        
        for effect in effects:
            st.markdown(f"• {effect}")


def configure_processing_options() -> Dict[str, Any]:
    """配置处理选项"""
    config = get_default_config()
    
    # 显示配置说明开关
    show_help = st.checkbox("💡 显示配置说明", value=False, help="显示每个配置项的详细说明")
    explanations = get_config_explanations() if show_help else {}
    
    # 表结构标准化配置
    st.subheader("📋 表结构标准化")
    if show_help and 'standardization' in explanations:
        st.info(explanations['standardization']['description'])
    
    config['standardization']['enable_column_rename'] = st.checkbox(
        "启用列名标准化", 
        value=config['standardization']['enable_column_rename'],
        help=explanations.get('standardization', {}).get('enable_column_rename', '')
    )
    
    if config['standardization']['enable_column_rename']:
        config['standardization']['naming_convention'] = st.selectbox(
            "列名命名约定",
            ["snake_case", "camelCase", "PascalCase"],
            index=0,
            help=explanations.get('standardization', {}).get('naming_convention', '')
        )
    
    config['standardization']['auto_detect_types'] = st.checkbox(
        "自动检测数据类型",
        value=config['standardization']['auto_detect_types'],
        help=explanations.get('standardization', {}).get('auto_detect_types', '')
    )
    
    # 缺失值处理配置
    st.subheader("🔧 缺失值处理")
    if show_help and 'missing_handling' in explanations:
        st.info(explanations['missing_handling']['description'])
    
    config['missing_handling']['default_strategy'] = st.selectbox(
        "默认填充策略",
        ["mean", "median", "mode", "forward_fill", "backward_fill", "drop"],
        index=0,
        help=explanations.get('missing_handling', {}).get('default_strategy', '')
    )
    
    config['missing_handling']['missing_threshold'] = st.slider(
        "缺失率阈值（超过此值删除列）",
        0.0, 1.0, 
        value=config['missing_handling']['missing_threshold'],
        step=0.1,
        help=explanations.get('missing_handling', {}).get('missing_threshold', '')
    )
    
    # 数据脱敏配置
    st.subheader("🔒 数据脱敏")
    if show_help and 'masking_rules' in explanations:
        st.info(explanations['masking_rules']['description'])
    
    config['masking_rules']['enable_auto_detection'] = st.checkbox(
        "启用敏感字段自动检测",
        value=config['masking_rules']['enable_auto_detection'],
        help=explanations.get('masking_rules', {}).get('enable_auto_detection', '')
    )
    
    if config['masking_rules']['enable_auto_detection']:
        config['masking_rules']['sensitivity_threshold'] = st.slider(
            "敏感性检测阈值",
            0.0, 1.0,
            value=config['masking_rules']['sensitivity_threshold'],
            step=0.1,
            help=explanations.get('masking_rules', {}).get('sensitivity_threshold', '')
        )
        
        # 显示LLM调用说明
        if show_help:
            st.markdown("**🤖 AI智能检测说明**：")
            st.markdown("当启用自动检测时，系统会：")
            st.markdown("1. 首先使用规则检测（基于列名和数据格式）")
            st.markdown("2. 对不确定的字段调用LLM进行智能分析")
            st.markdown("3. 结合两种方法的结果做最终决策")
    
    config['masking_rules']['default_strategy'] = st.selectbox(
        "默认脱敏策略",
        ["partial", "hash", "random", "remove"],
        index=0,
        help=explanations.get('masking_rules', {}).get('default_strategy', '')
    )
    
    # 特征提取配置
    st.subheader("🎯 特征提取")
    if show_help and 'feature_extraction' in explanations:
        st.info(explanations['feature_extraction']['description'])
    
    config['feature_extraction']['enable_extraction'] = st.checkbox(
        "启用特征提取",
        value=config['feature_extraction']['enable_extraction'],
        help=explanations.get('feature_extraction', {}).get('enable_extraction', '')
    )
    
    if config['feature_extraction']['enable_extraction']:
        config['feature_extraction']['extract_numeric_stats'] = st.checkbox(
            "提取数值统计特征",
            value=config['feature_extraction']['extract_numeric_stats'],
            help=explanations.get('feature_extraction', {}).get('extract_numeric_stats', '')
        )
        
        config['feature_extraction']['extract_text_features'] = st.checkbox(
            "提取文本特征",
            value=config['feature_extraction']['extract_text_features'],
            help=explanations.get('feature_extraction', {}).get('extract_text_features', '')
        )
        
        config['feature_extraction']['extract_datetime_features'] = st.checkbox(
            "提取时间特征",
            value=config['feature_extraction']['extract_datetime_features'],
            help=explanations.get('feature_extraction', {}).get('extract_datetime_features', '')
        )
    
    # 配置总览
    if show_help:
        st.markdown("---")
        st.subheader("📋 当前配置总览")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**将要执行的操作：**")
            operations = []
            
            # 表结构标准化
            if config['standardization']['enable_column_rename']:
                operations.append(f"📋 列名标准化 ({config['standardization']['naming_convention']})")
            if config['standardization']['auto_detect_types']:
                operations.append("🔍 自动数据类型检测")
            
            # 缺失值处理
            operations.append(f"🔧 缺失值填充 ({config['missing_handling']['default_strategy']})")
            if config['missing_handling']['missing_threshold'] < 1.0:
                operations.append(f"🗑️ 删除高缺失率列 (>{config['missing_handling']['missing_threshold']:.0%})")
            
            # 数据脱敏
            if config['masking_rules']['enable_auto_detection']:
                operations.append("🛡️ AI智能敏感字段检测")
                operations.append(f"🔒 数据脱敏 ({config['masking_rules']['default_strategy']})")
            
            # 特征提取
            if config['feature_extraction']['enable_extraction']:
                operations.append("🎯 特征工程")
            
            operations.append("📊 生成质量报告")
            
            for op in operations:
                st.markdown(f"• {op}")
        
        with col2:
            st.markdown("**预期效果：**")
            effects = []
            
            if config['standardization']['enable_column_rename']:
                effects.append("列名格式统一，便于程序处理")
            if config['standardization']['auto_detect_types']:
                effects.append("数据类型优化，节省内存")
            
            effects.append("缺失值减少，数据完整性提高")
            
            if config['masking_rules']['enable_auto_detection']:
                effects.append("敏感信息自动识别和保护")
                effects.append("数据隐私安全得到保障")
            
            if config['feature_extraction']['enable_extraction']:
                effects.append("增加有用的计算特征")
            
            effects.append("获得详细的数据质量分析")
            
            for effect in effects:
                st.markdown(f"• {effect}")
    
    return config


def process_data_workflow(df: pd.DataFrame, config: Dict[str, Any], filename: str):
    """处理数据工作流"""
    # 创建处理进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("正在初始化处理流程...")
        progress_bar.progress(10)
        
        # 处理数据
        status_text.text("正在处理数据...")
        progress_bar.progress(50)
        
        result = process_dataframe(df, config, file_info={'filename': filename})
        
        progress_bar.progress(100)
        
        if result['success']:
            status_text.text("处理完成！")
            
            # 显示处理结果
            display_processing_results(result)
            
            # 保存结果到session state
            st.session_state['last_result'] = result
            
        else:
            st.error(f"处理失败: {result['error']}")
            
            # 显示处理日志
            if 'processing_log' in result:
                st.subheader("处理日志")
                for log_entry in result['processing_log']:
                    if log_entry.get('status') == 'failed':
                        st.error(f"❌ {log_entry.get('message', '未知错误')}")
                    else:
                        st.info(f"ℹ️ {log_entry.get('message', '步骤完成')}")
        
    except Exception as e:
        st.error(f"处理异常: {str(e)}")
    finally:
        progress_bar.empty()
        status_text.empty()


def display_processing_results(result: Dict[str, Any]):
    """显示处理结果"""
    st.markdown('<h3 class="section-header">📊 处理结果</h3>', unsafe_allow_html=True)
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["处理后数据", "质量报告", "脱敏信息", "处理日志", "数据导出"])
    
    with tab1:
        st.subheader("处理后数据")
        processed_data = result.get('processed_data')
        
        if processed_data is not None:
            # 检查数据格式并转换为DataFrame
            if isinstance(processed_data, dict) and 'data' in processed_data:
                # 从API返回的字典格式重建DataFrame
                processed_df = pd.DataFrame(processed_data['data'])
                shape = processed_data.get('shape', (len(processed_df), len(processed_df.columns)))
            elif isinstance(processed_data, pd.DataFrame):
                # 直接是DataFrame
                processed_df = processed_data
                shape = processed_df.shape
            else:
                st.error("未知的数据格式")
                return
            
            # 数据统计
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("行数", shape[0])
            with col2:
                st.metric("列数", shape[1])
            with col3:
                st.metric("缺失值", processed_df.isnull().sum().sum())
            with col4:
                st.metric("内存使用", f"{processed_df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            
            # 数据预览
            st.dataframe(processed_df, use_container_width=True)
        else:
            st.warning("没有处理后的数据")
    
    with tab2:
        st.subheader("数据质量报告")
        
        # 显示文本报告
        text_report = result.get('text_report', '')
        if text_report:
            st.text_area("质量报告", text_report, height=300)
        
        # 显示质量指标图表
        quality_report = result.get('quality_report', {})
        if quality_report:
            display_quality_charts(quality_report)
    
    with tab3:
        st.subheader("数据脱敏信息")
        masked_columns = result.get('masked_columns', [])
        
        if masked_columns:
            st.success(f"成功脱敏 {len(masked_columns)} 个敏感字段")
            
            for masked_col in masked_columns:
                with st.expander(f"字段: {masked_col['column']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**敏感类型**: {masked_col['type']}")
                        st.write(f"**脱敏策略**: {masked_col['strategy']}")
                    
                    with col2:
                        preview = masked_col.get('preview', {})
                        if preview:
                            st.write("**脱敏预览**:")
                            for orig, masked in zip(preview.get('original', []), preview.get('masked', [])):
                                st.write(f"{orig} → {masked}")
        else:
            st.info("未检测到需要脱敏的敏感字段")
    
    with tab4:
        st.subheader("处理日志")
        processing_log = result.get('processing_log', [])
        
        for log_entry in processing_log:
            status = log_entry.get('status', 'unknown')
            message = log_entry.get('message', '无消息')
            
            if status == 'success':
                st.success(f"✅ {message}")
            elif status == 'failed':
                st.error(f"❌ {message}")
            else:
                st.info(f"ℹ️ {message}")
    
    with tab5:
        st.subheader("数据导出")
        processed_data = result.get('processed_data')
        
        if processed_data is not None:
            # 检查数据格式并转换为DataFrame
            if isinstance(processed_data, dict) and 'data' in processed_data:
                # 从API返回的字典格式重建DataFrame
                processed_df = pd.DataFrame(processed_data['data'])
            elif isinstance(processed_data, pd.DataFrame):
                # 直接是DataFrame
                processed_df = processed_data
            else:
                st.error("未知的数据格式，无法导出")
                return
            
            # 导出格式选择
            export_format = st.selectbox("选择导出格式", ["CSV", "Excel", "JSON"])
            
            # 直接显示下载按钮，不使用中间按钮
            st.markdown("### 📥 下载处理后数据")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if export_format == "CSV":
                    csv_data = processed_df.to_csv(index=False)
                    st.download_button(
                        label="📄 下载CSV文件",
                        data=csv_data,
                        file_name="processed_data.csv",
                        mime="text/csv",
                        type="primary"
                    )
            
            with col2:
                if export_format == "Excel":
                    buffer = io.BytesIO()
                    processed_df.to_excel(buffer, index=False)
                    st.download_button(
                        label="📊 下载Excel文件",
                        data=buffer.getvalue(),
                        file_name="processed_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary"
                    )
            
            with col3:
                if export_format == "JSON":
                    json_data = processed_df.to_json(orient='records', force_ascii=False)
                    st.download_button(
                        label="📋 下载JSON文件",
                        data=json_data,
                        file_name="processed_data.json",
                        mime="application/json",
                        type="primary"
                    )
        else:
            st.warning("没有可导出的数据")


def display_quality_charts(quality_report: Dict[str, Any]):
    """显示质量指标图表"""
    # 质量得分对比
    scores = quality_report.get('data_quality_score', {})
    if scores:
        # 创建得分对比图
        metrics = ['completeness', 'consistency', 'overall']
        original_scores = [scores.get(metric, {}).get('original', 0) for metric in metrics]
        processed_scores = [scores.get(metric, {}).get('processed', 0) for metric in metrics]
        
        fig = go.Figure(data=[
            go.Bar(name='处理前', x=metrics, y=original_scores),
            go.Bar(name='处理后', x=metrics, y=processed_scores)
        ])
        
        fig.update_layout(
            title='数据质量得分对比',
            xaxis_title='质量指标',
            yaxis_title='得分 (%)',
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 缺失数据分析
    missing_data = quality_report.get('missing_data', {})
    if missing_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "缺失值减少",
                f"{missing_data.get('improvement', {}).get('missing_reduction', 0)} 个",
                delta=f"{missing_data.get('improvement', {}).get('rate_improvement', 0):.2f}%"
            )
        
        with col2:
            original_rate = missing_data.get('original', {}).get('missing_rate', 0)
            processed_rate = missing_data.get('processed', {}).get('missing_rate', 0)
            st.metric(
                "缺失率",
                f"{processed_rate:.2f}%",
                delta=f"{processed_rate - original_rate:.2f}%"
            )





def config_management_page():
    """配置管理页面"""
    st.markdown('<h2 class="section-header">⚙️ 配置管理</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("默认配置")
        default_config = get_default_config()
        st.json(default_config)
        
        if st.button("应用默认配置"):
            st.session_state['current_config'] = default_config
            st.success("已应用默认配置")
    
    with col2:
        st.subheader("配置模板")
        template = get_config_template()
        st.text_area("YAML配置模板", template, height=400)
        
        if st.button("复制模板"):
            st.success("配置模板已复制到剪贴板")


def processing_history_page():
    """处理历史页面"""
    st.markdown('<h2 class="section-header">📝 处理历史</h2>', unsafe_allow_html=True)
    
    # 显示最近的处理结果
    if 'last_result' in st.session_state:
        st.subheader("最近的处理结果")
        result = st.session_state['last_result']
        
        # 基本信息
        processing_summary = result.get('processing_summary', {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("处理步骤", processing_summary.get('total_steps', 0))
        with col2:
            st.metric("成功步骤", processing_summary.get('successful_steps', 0))
        with col3:
            st.metric("脱敏字段", processing_summary.get('masked_columns_count', 0))
        with col4:
            st.metric("提取特征", processing_summary.get('extracted_features_count', 0))
        
        # 处理时间线
        st.subheader("处理时间线")
        timeline = processing_summary.get('processing_timeline', [])
        for i, step in enumerate(timeline):
            status = step.get('status', 'unknown')
            message = step.get('message', '无消息')
            
            if status == 'success':
                st.success(f"步骤 {i+1}: {message}")
            elif status == 'failed':
                st.error(f"步骤 {i+1}: {message}")
            else:
                st.info(f"步骤 {i+1}: {message}")
    else:
        st.info("暂无处理历史记录")


def system_status_page():
    """系统状态页面"""
    st.markdown('<h2 class="section-header">🖥️ 系统状态</h2>', unsafe_allow_html=True)
    
    # 系统信息
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Python版本", f"{sys.version_info.major}.{sys.version_info.minor}")
    
    with col2:
        st.metric("Streamlit版本", st.__version__)
    
    with col3:
        st.metric("Pandas版本", pd.__version__)
    
    # 功能状态检查
    st.subheader("功能状态检查")
    
    # 检查各个模块
    modules_status = check_modules_status()
    
    for module_name, status in modules_status.items():
        if status:
            st.success(f"✅ {module_name}: 正常")
        else:
            st.error(f"❌ {module_name}: 异常")


def check_modules_status() -> Dict[str, bool]:
    """检查模块状态"""
    status = {}
    
    try:
        from utils.call_llm import call_llm
        status["LLM调用模块"] = True
    except Exception:
        status["LLM调用模块"] = False
    
    try:
        from utils.data_type_detector import detect_data_type
        status["数据类型检测模块"] = True
    except Exception:
        status["数据类型检测模块"] = False
    
    try:
        from utils.sensitive_detector import detect_sensitive_field
        status["敏感字段检测模块"] = True
    except Exception:
        status["敏感字段检测模块"] = False
    
    try:
        from utils.data_masking import mask_data
        status["数据脱敏模块"] = True
    except Exception:
        status["数据脱敏模块"] = False
    
    try:
        from utils.quality_metrics import calculate_quality_metrics
        status["质量指标模块"] = True
    except Exception:
        status["质量指标模块"] = False
    
    try:
        from utils.config_validator import validate_config
        status["配置验证模块"] = True
    except Exception:
        status["配置验证模块"] = False
    
    return status


def load_data(uploaded_file) -> pd.DataFrame:
    """加载上传的数据文件"""
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.json'):
            return pd.read_json(uploaded_file)
        else:
            raise ValueError(f"不支持的文件格式: {uploaded_file.name}")
    except Exception as e:
        raise Exception(f"文件加载失败: {str(e)}")


if __name__ == "__main__":
    main()
