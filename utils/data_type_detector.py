"""
数据类型检测工具
用于自动检测DataFrame列的数据类型并进行智能转换
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, Any


def detect_data_type(column: pd.Series) -> str:
    """
    检测pandas列的数据类型
    
    Args:
        column: pandas Series对象
        
    Returns:
        str: 检测到的数据类型 ('numeric', 'datetime', 'categorical', 'text', 'boolean')
    """
    # 去除空值进行检测
    non_null_values = column.dropna()
    
    if len(non_null_values) == 0:
        return 'text'  # 全为空值，默认为文本类型
    
    # 检测布尔类型
    if _is_boolean_column(non_null_values):
        return 'boolean'
    
    # 检测数值类型
    if _is_numeric_column(non_null_values):
        return 'numeric'
    
    # 检测日期时间类型
    if _is_datetime_column(non_null_values):
        return 'datetime'
    
    # 检测分类类型
    if _is_categorical_column(non_null_values):
        return 'categorical'
    
    # 默认为文本类型
    return 'text'


def convert_column_type(column: pd.Series, target_type: str) -> pd.Series:
    """
    将列转换为指定的数据类型
    
    Args:
        column: 要转换的列
        target_type: 目标类型
        
    Returns:
        pd.Series: 转换后的列
    """
    try:
        if target_type == 'numeric':
            return pd.to_numeric(column, errors='coerce')
        elif target_type == 'datetime':
            return pd.to_datetime(column, errors='coerce')
        elif target_type == 'boolean':
            return column.astype('boolean')
        elif target_type == 'categorical':
            return column.astype('category')
        else:  # text
            return column.astype('string')
    except Exception:
        # 转换失败，返回原列
        return column


def standardize_column_names(df: pd.DataFrame, naming_convention: str = 'snake_case') -> pd.DataFrame:
    """
    标准化列名格式
    
    Args:
        df: DataFrame
        naming_convention: 命名约定 ('snake_case', 'camelCase', 'PascalCase')
        
    Returns:
        pd.DataFrame: 列名标准化后的DataFrame
    """
    df_copy = df.copy()
    
    if naming_convention == 'snake_case':
        df_copy.columns = [_to_snake_case(col) for col in df_copy.columns]
    elif naming_convention == 'camelCase':
        df_copy.columns = [_to_camel_case(col) for col in df_copy.columns]
    elif naming_convention == 'PascalCase':
        df_copy.columns = [_to_pascal_case(col) for col in df_copy.columns]
    
    return df_copy


def _is_boolean_column(series: pd.Series) -> bool:
    """检测是否为布尔类型列"""
    unique_values = set(str(v).lower() for v in series.unique())
    # 使用列表而不是集合来避免不可哈希类型错误
    boolean_patterns = [
        {'true', 'false'},
        {'yes', 'no'},
        {'y', 'n'},
        {'1', '0'},
        {'是', '否'}
    ]
    return any(unique_values.issubset(pattern) for pattern in boolean_patterns)


def _is_numeric_column(series: pd.Series) -> bool:
    """检测是否为数值类型列"""
    try:
        pd.to_numeric(series, errors='raise')
        return True
    except (ValueError, TypeError):
        return False


def _is_datetime_column(series: pd.Series) -> bool:
    """检测是否为日期时间类型列"""
    if len(series) == 0:
        return False
    
    # 尝试转换前几个值
    sample_size = min(10, len(series))
    sample_values = series.head(sample_size)
    
    try:
        pd.to_datetime(sample_values, errors='raise')
        return True
    except (ValueError, TypeError):
        return False


def _is_categorical_column(series: pd.Series) -> bool:
    """检测是否为分类类型列"""
    # 如果唯一值数量相对较少，可能是分类数据
    unique_ratio = len(series.unique()) / len(series)
    return unique_ratio < 0.1 and len(series.unique()) < 50


def _to_snake_case(name: str) -> str:
    """转换为snake_case"""
    # 处理空格和特殊字符
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', '_', name)
    # 处理驼峰命名
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def _to_camel_case(name: str) -> str:
    """转换为camelCase"""
    # 先转换为snake_case，然后转换为camelCase
    snake_name = _to_snake_case(name)
    components = snake_name.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def _to_pascal_case(name: str) -> str:
    """转换为PascalCase"""
    snake_name = _to_snake_case(name)
    components = snake_name.split('_')
    return ''.join(word.capitalize() for word in components)


if __name__ == "__main__":
    # 测试代码
    test_data = {
        'user_id': [1, 2, 3, 4, 5],
        'User Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [25, 30, 35, 40, 45],
        'IsActive': ['True', 'False', 'True', 'True', 'False'],
        'Created Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']
    }
    
    df = pd.DataFrame(test_data)
    print("原始数据:")
    print(df.dtypes)
    
    # 测试数据类型检测
    for col in df.columns:
        detected_type = detect_data_type(df[col])
        print(f"列 '{col}' 检测类型: {detected_type}")
    
    # 测试列名标准化
    standardized_df = standardize_column_names(df, 'snake_case')
    print("\n标准化后的列名:")
    print(list(standardized_df.columns))
