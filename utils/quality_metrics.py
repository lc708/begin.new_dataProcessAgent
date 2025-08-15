"""
数据质量指标计算工具
用于生成数据处理前后的质量报告
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple


def _safe_column_intersection(df1_columns, df2_columns):
    """安全地计算两个列集合的交集，处理不可哈希类型"""
    try:
        return set(df1_columns) & set(df2_columns)
    except TypeError:
        # 如果列名包含不可哈希类型，使用列表推导式
        return [col for col in df1_columns if col in df2_columns]


def _safe_column_difference(df1_columns, df2_columns):
    """安全地计算两个列集合的差集，处理不可哈希类型"""
    try:
        return list(set(df1_columns) - set(df2_columns))
    except TypeError:
        # 如果列名包含不可哈希类型，使用列表推导式
        return [col for col in df1_columns if col not in df2_columns]


def calculate_quality_metrics(original_df: pd.DataFrame, processed_df: pd.DataFrame) -> Dict[str, Any]:
    """
    计算数据质量指标
    
    Args:
        original_df: 原始DataFrame
        processed_df: 处理后的DataFrame
        
    Returns:
        Dict: 质量指标报告
    """
    metrics = {
        'basic_info': _get_basic_info(original_df, processed_df),
        'missing_data': _analyze_missing_data(original_df, processed_df),
        'data_types': _analyze_data_types(original_df, processed_df),
        'data_distribution': _analyze_data_distribution(original_df, processed_df),
        'data_quality_score': _calculate_quality_score(original_df, processed_df),
        'processing_summary': _get_processing_summary(original_df, processed_df)
    }
    
    return metrics


def _get_basic_info(original_df: pd.DataFrame, processed_df: pd.DataFrame) -> Dict[str, Any]:
    """获取基本信息对比"""
    return {
        'original': {
            'rows': len(original_df),
            'columns': len(original_df.columns),
            'memory_usage': original_df.memory_usage(deep=True).sum(),
            'column_names': list(original_df.columns)
        },
        'processed': {
            'rows': len(processed_df),
            'columns': len(processed_df.columns),
            'memory_usage': processed_df.memory_usage(deep=True).sum(),
            'column_names': list(processed_df.columns)
        }
    }


def _analyze_missing_data(original_df: pd.DataFrame, processed_df: pd.DataFrame) -> Dict[str, Any]:
    """分析缺失数据情况"""
    original_missing = original_df.isnull().sum()
    processed_missing = processed_df.isnull().sum()
    
    # 计算缺失率
    original_missing_rate = (original_missing / len(original_df) * 100).round(2)
    processed_missing_rate = (processed_missing / len(processed_df) * 100).round(2)
    
    return {
        'original': {
            'total_missing': original_missing.sum(),
            'missing_rate': (original_missing.sum() / (len(original_df) * len(original_df.columns)) * 100).round(2),
            'by_column': original_missing_rate.to_dict()
        },
        'processed': {
            'total_missing': processed_missing.sum(),
            'missing_rate': (processed_missing.sum() / (len(processed_df) * len(processed_df.columns)) * 100).round(2),
            'by_column': processed_missing_rate.to_dict()
        },
        'improvement': {
            'missing_reduction': original_missing.sum() - processed_missing.sum(),
            'rate_improvement': (original_missing.sum() / (len(original_df) * len(original_df.columns)) * 100 - 
                               processed_missing.sum() / (len(processed_df) * len(processed_df.columns)) * 100).round(2)
        }
    }


def _analyze_data_types(original_df: pd.DataFrame, processed_df: pd.DataFrame) -> Dict[str, Any]:
    """分析数据类型变化"""
    original_types = original_df.dtypes.value_counts().to_dict()
    processed_types = processed_df.dtypes.value_counts().to_dict()
    
    # 转换类型名称为字符串
    original_types = {str(k): v for k, v in original_types.items()}
    processed_types = {str(k): v for k, v in processed_types.items()}
    
    return {
        'original': original_types,
        'processed': processed_types,
        'changes': _get_type_changes(original_df, processed_df)
    }


def _get_type_changes(original_df: pd.DataFrame, processed_df: pd.DataFrame) -> List[Dict[str, str]]:
    """获取数据类型变化详情"""
    changes = []
    
    # 安全地找到共同的列，避免不可哈希类型问题
    common_columns = _safe_column_intersection(original_df.columns, processed_df.columns)
    
    for col in common_columns:
        original_type = str(original_df[col].dtype)
        processed_type = str(processed_df[col].dtype)
        
        if original_type != processed_type:
            changes.append({
                'column': col,
                'from': original_type,
                'to': processed_type
            })
    
    return changes


def _analyze_data_distribution(original_df: pd.DataFrame, processed_df: pd.DataFrame) -> Dict[str, Any]:
    """分析数据分布变化"""
    analysis = {}
    
    # 找到共同的数值列
    original_numeric = original_df.select_dtypes(include=[np.number])
    processed_numeric = processed_df.select_dtypes(include=[np.number])
    
    # 安全地找到共同的数值列，避免不可哈希类型问题
    common_numeric_cols = _safe_column_intersection(original_numeric.columns, processed_numeric.columns)
    
    for col in common_numeric_cols:
        analysis[col] = {
            'original': {
                'mean': round(original_numeric[col].mean(), 2) if not original_numeric[col].empty else None,
                'std': round(original_numeric[col].std(), 2) if not original_numeric[col].empty else None,
                'min': round(original_numeric[col].min(), 2) if not original_numeric[col].empty else None,
                'max': round(original_numeric[col].max(), 2) if not original_numeric[col].empty else None,
                'unique_count': original_numeric[col].nunique()
            },
            'processed': {
                'mean': round(processed_numeric[col].mean(), 2) if not processed_numeric[col].empty else None,
                'std': round(processed_numeric[col].std(), 2) if not processed_numeric[col].empty else None,
                'min': round(processed_numeric[col].min(), 2) if not processed_numeric[col].empty else None,
                'max': round(processed_numeric[col].max(), 2) if not processed_numeric[col].empty else None,
                'unique_count': processed_numeric[col].nunique()
            }
        }
    
    return analysis


def _calculate_quality_score(original_df: pd.DataFrame, processed_df: pd.DataFrame) -> Dict[str, float]:
    """计算数据质量得分"""
    scores = {}
    
    # 完整性得分 (基于缺失值)
    original_completeness = 1 - (original_df.isnull().sum().sum() / (len(original_df) * len(original_df.columns)))
    processed_completeness = 1 - (processed_df.isnull().sum().sum() / (len(processed_df) * len(processed_df.columns)))
    
    scores['completeness'] = {
        'original': round(original_completeness * 100, 2),
        'processed': round(processed_completeness * 100, 2),
        'improvement': round((processed_completeness - original_completeness) * 100, 2)
    }
    
    # 一致性得分 (基于数据类型标准化)
    original_type_consistency = _calculate_type_consistency(original_df)
    processed_type_consistency = _calculate_type_consistency(processed_df)
    
    scores['consistency'] = {
        'original': round(original_type_consistency * 100, 2),
        'processed': round(processed_type_consistency * 100, 2),
        'improvement': round((processed_type_consistency - original_type_consistency) * 100, 2)
    }
    
    # 整体质量得分
    original_overall = (original_completeness * 0.6 + original_type_consistency * 0.4)
    processed_overall = (processed_completeness * 0.6 + processed_type_consistency * 0.4)
    
    scores['overall'] = {
        'original': round(original_overall * 100, 2),
        'processed': round(processed_overall * 100, 2),
        'improvement': round((processed_overall - original_overall) * 100, 2)
    }
    
    return scores


def _calculate_type_consistency(df: pd.DataFrame) -> float:
    """计算数据类型一致性得分"""
    if df.empty:
        return 0.0
    
    consistent_columns = 0
    total_columns = len(df.columns)
    
    for col in df.columns:
        # 检查列中数据类型的一致性
        try:
            non_null_series = df[col].dropna()
            if len(non_null_series) == 0:
                consistent_columns += 0.5  # 空列给予中等分数
                continue
            
            # 尝试推断最佳数据类型
            if pd.api.types.is_numeric_dtype(non_null_series):
                consistent_columns += 1
            elif pd.api.types.is_datetime64_any_dtype(non_null_series):
                consistent_columns += 1
            elif pd.api.types.is_bool_dtype(non_null_series):
                consistent_columns += 1
            else:
                # 对于对象类型，检查是否应该是其他类型
                if _should_be_numeric(non_null_series):
                    consistent_columns += 0.3
                elif _should_be_datetime(non_null_series):
                    consistent_columns += 0.3
                else:
                    consistent_columns += 0.8  # 文本类型通常是合理的
        except Exception:
            consistent_columns += 0.5
    
    return consistent_columns / total_columns if total_columns > 0 else 0.0


def _should_be_numeric(series: pd.Series) -> bool:
    """检查序列是否应该是数值类型"""
    try:
        pd.to_numeric(series.head(10), errors='raise')
        return True
    except (ValueError, TypeError):
        return False


def _should_be_datetime(series: pd.Series) -> bool:
    """检查序列是否应该是日期时间类型"""
    try:
        pd.to_datetime(series.head(10), errors='raise')
        return True
    except (ValueError, TypeError):
        return False


def _get_processing_summary(original_df: pd.DataFrame, processed_df: pd.DataFrame) -> Dict[str, Any]:
    """获取处理总结"""
    # 安全地处理列名，避免不可哈希类型的问题
    new_columns = _safe_column_difference(processed_df.columns, original_df.columns)
    removed_columns = _safe_column_difference(original_df.columns, processed_df.columns)
    
    return {
        'rows_added': len(processed_df) - len(original_df),
        'columns_added': len(processed_df.columns) - len(original_df.columns),
        'new_columns': new_columns,
        'removed_columns': removed_columns,
        'memory_change': processed_df.memory_usage(deep=True).sum() - original_df.memory_usage(deep=True).sum()
    }


def generate_quality_report_text(metrics: Dict[str, Any]) -> str:
    """生成文本格式的质量报告"""
    report = []
    
    # 基本信息
    basic = metrics['basic_info']
    report.append("=== 数据质量报告 ===\n")
    report.append("基本信息对比:")
    report.append(f"  行数: {basic['original']['rows']} → {basic['processed']['rows']}")
    report.append(f"  列数: {basic['original']['columns']} → {basic['processed']['columns']}")
    
    # 质量得分
    scores = metrics['data_quality_score']
    report.append(f"\n质量得分:")
    report.append(f"  完整性: {scores['completeness']['original']}% → {scores['completeness']['processed']}%")
    report.append(f"  一致性: {scores['consistency']['original']}% → {scores['consistency']['processed']}%")
    report.append(f"  整体质量: {scores['overall']['original']}% → {scores['overall']['processed']}%")
    
    # 缺失数据改善
    missing = metrics['missing_data']
    report.append(f"\n缺失数据改善:")
    report.append(f"  缺失值减少: {missing['improvement']['missing_reduction']} 个")
    report.append(f"  缺失率改善: {missing['improvement']['rate_improvement']:.2f}%")
    
    return "\n".join(report)


if __name__ == "__main__":
    # 测试代码
    # 创建测试数据
    original_data = {
        'name': ['张三', None, '李四', '王五'],
        'age': ['25', '30', None, '35'],
        'phone': ['13812345678', '15987654321', None, '18611112222'],
        'score': [85.5, None, 92.0, 78.5]
    }
    
    processed_data = {
        'name': ['张*', '[已脱敏]', '李*', '王*'],
        'age': [25, 30, 32, 35],  # 缺失值已填充，类型已转换
        'phone': ['138****5678', '159****4321', '139****0000', '186****2222'],
        'score': [85.5, 87.0, 92.0, 78.5]  # 缺失值已填充
    }
    
    original_df = pd.DataFrame(original_data)
    processed_df = pd.DataFrame(processed_data)
    
    print("原始数据:")
    print(original_df)
    print(f"\n数据类型: {original_df.dtypes.to_dict()}")
    
    print("\n处理后数据:")
    print(processed_df)
    print(f"\n数据类型: {processed_df.dtypes.to_dict()}")
    
    # 计算质量指标
    metrics = calculate_quality_metrics(original_df, processed_df)
    
    # 生成报告
    report = generate_quality_report_text(metrics)
    print(f"\n{report}")
