"""
数据处理Agent的主程序
提供数据处理的主要入口函数
"""
import os
import dotenv

# 确保环境变量在应用启动时加载
dotenv.load_dotenv('.env')       # 先加载默认环境变量
dotenv.load_dotenv('.env.local') # 再加载本地环境变量（会覆盖同名变量）

import pandas as pd
import io
import base64
import logging
from typing import Dict, Any, Optional
from flow import create_data_processing_flow, create_simple_data_processing_flow
from utils.config_validator import get_default_config, validate_config


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_data_from_file(file_path: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    从文件处理数据
    
    Args:
        file_path: 数据文件路径
        config: 处理配置
        
    Returns:
        Dict: 处理结果
    """
    # 读取文件
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path}")
    except Exception as e:
        return {'success': False, 'error': f"文件读取失败: {str(e)}"}
    
    # 处理数据
    return process_dataframe(df, config, file_info={'filename': file_path})


def process_data_from_content(file_content: bytes, filename: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    从文件内容处理数据
    
    Args:
        file_content: 文件内容
        filename: 文件名
        config: 处理配置
        
    Returns:
        Dict: 处理结果
    """
    # 读取文件内容
    try:
        file_like = io.BytesIO(file_content)
        
        if filename.endswith('.csv'):
            df = pd.read_csv(file_like)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_like)
        elif filename.endswith('.json'):
            df = pd.read_json(file_like)
        else:
            raise ValueError(f"不支持的文件格式: {filename}")
    except Exception as e:
        return {'success': False, 'error': f"文件解析失败: {str(e)}"}
    
    # 处理数据
    return process_dataframe(df, config, file_info={'filename': filename})


def process_dataframe(df: pd.DataFrame, config: Optional[Dict[str, Any]] = None, 
                     file_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    处理DataFrame数据
    
    Args:
        df: 要处理的DataFrame
        config: 处理配置
        file_info: 文件信息
        
    Returns:
        Dict: 处理结果
    """
    try:
        # 使用默认配置或验证用户配置
        if config is None:
            config = get_default_config()
        else:
            is_valid, errors = validate_config(config)
            if not is_valid:
                return {'success': False, 'error': f"配置验证失败: {errors}"}
        
        # 准备共享存储
        shared = {
            'input_data': {
                'raw_df': df.copy(),
                'file_info': file_info or {},
                'validation_errors': []
            },
            'config': config,
            'processing_results': {
                'processing_log': []
            }
        }
        
        # 选择处理流程
        enable_feature_extraction = config.get('feature_extraction', {}).get('enable_extraction', False)
        
        if enable_feature_extraction:
            flow = create_data_processing_flow()
        else:
            flow = create_simple_data_processing_flow()
        
        logger.info(f"开始数据处理，数据形状: {df.shape}")
        
        # 执行流程
        flow.run(shared)
        
        # 检查处理结果
        processing_log = shared.get('processing_results', {}).get('processing_log', [])
        failed_steps = [log for log in processing_log if log.get('status') == 'failed']
        
        if failed_steps:
            error_messages = [step.get('message', '未知错误') for step in failed_steps]
            return {
                'success': False, 
                'error': f"处理失败: {'; '.join(error_messages)}",
                'processing_log': processing_log
            }
        
        # 返回成功结果
        result = {
            'success': True,
            'processed_data': shared.get('processing_results', {}).get('processed_df'),
            'quality_report': shared.get('processing_results', {}).get('quality_report'),
            'text_report': shared.get('processing_results', {}).get('text_report'),
            'processing_summary': shared.get('processing_results', {}).get('processing_summary'),
            'masked_columns': shared.get('processing_results', {}).get('masked_columns', []),
            'extracted_features': shared.get('processing_results', {}).get('extracted_features', []),
            'processing_log': processing_log
        }
        
        logger.info("数据处理完成")
        return result
        
    except Exception as e:
        logger.error(f"数据处理失败: {str(e)}")
        return {'success': False, 'error': f"处理异常: {str(e)}"}


def validate_data_only(df: pd.DataFrame) -> Dict[str, Any]:
    """
    仅验证数据质量，不进行处理
    
    Args:
        df: 要验证的DataFrame
        
    Returns:
        Dict: 验证结果
    """
    try:
        from flow import create_validation_only_flow
        
        shared = {
            'input_data': {
                'raw_df': df.copy(),
                'file_info': {},
                'validation_errors': []
            },
            'processing_results': {
                'processing_log': []
            }
        }
        
        validation_flow = create_validation_only_flow()
        validation_flow.run(shared)
        
        return {
            'success': True,
            'validation_errors': shared.get('input_data', {}).get('validation_errors', []),
            'validation_warnings': shared.get('input_data', {}).get('validation_warnings', []),
            'basic_stats': shared.get('input_data', {}).get('basic_stats', {}),
            'processing_log': shared.get('processing_results', {}).get('processing_log', [])
        }
        
    except Exception as e:
        return {'success': False, 'error': f"验证失败: {str(e)}"}


def export_processed_data(processed_df: pd.DataFrame, format: str = 'csv') -> bytes:
    """
    导出处理后的数据
    
    Args:
        processed_df: 处理后的DataFrame
        format: 导出格式 ('csv', 'xlsx', 'json')
        
    Returns:
        bytes: 文件内容
    """
    buffer = io.BytesIO()
    
    if format == 'csv':
        processed_df.to_csv(buffer, index=False, encoding='utf-8-sig')
    elif format == 'xlsx':
        processed_df.to_excel(buffer, index=False)
    elif format == 'json':
        processed_df.to_json(buffer, orient='records', force_ascii=False)
    else:
        raise ValueError(f"不支持的导出格式: {format}")
    
    return buffer.getvalue()


# 示例主函数
def main():
    """示例主函数，演示如何使用数据处理功能"""
    # 创建示例数据
    sample_data = {
        'user_id': [1, 2, 3, 4, 5],
        'User Name': ['张三', '李四', '王五', '赵六', '孙七'],
        'Age': [25, None, 35, 40, 45],
        'Phone': ['13812345678', '15987654321', None, '18611112222', '13755555555'],
        'Email': ['zhangsan@example.com', 'lisi@test.com', 'wangwu@demo.org', None, 'sunqi@sample.net'],
        'Salary': [5000.5, 6000.0, None, 8000.0, 7500.5]
    }
    
    df = pd.DataFrame(sample_data)
    print("原始数据:")
    print(df)
    print()
    
    # 使用默认配置处理数据
    result = process_dataframe(df)
    
    if result['success']:
        print("处理成功!")
        print("\n处理后数据:")
        print(result['processed_data'])
        
        print(f"\n质量报告:")
        print(result['text_report'])
        
        print(f"\n脱敏字段: {len(result['masked_columns'])} 个")
        for masked_col in result['masked_columns']:
            print(f"  - {masked_col['column']}: {masked_col['type']} ({masked_col['strategy']})")
        
    else:
        print(f"处理失败: {result['error']}")


if __name__ == "__main__":
    main()