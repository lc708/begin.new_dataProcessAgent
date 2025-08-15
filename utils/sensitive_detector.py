"""
敏感字段检测工具
用于识别DataFrame中的敏感信息字段
"""
import re
import pandas as pd
from typing import List, Tuple, Dict, Any


def _safe_to_string(value) -> str:
    """
    安全地将任意类型转换为字符串
    
    Args:
        value: 任意类型的值
        
    Returns:
        str: 转换后的字符串
    """
    if value is None:
        return ''
    
    try:
        if isinstance(value, (int, float)):
            # 对于数值类型，确保大整数精度不丢失
            if isinstance(value, float) and value.is_integer():
                return str(int(value))
            return str(value)
        else:
            return str(value)
    except (ValueError, TypeError):
        return str(value)


def detect_sensitive_field(column_name: str, sample_values: List[str], max_samples: int = 20) -> str:
    """
    检测字段是否包含敏感信息
    
    Args:
        column_name: 列名
        sample_values: 样本值列表
        max_samples: 最大样本数量
        
    Returns:
        str: 敏感信息类型 ('phone', 'id_card', 'email', 'name', 'address', 'none')
    """
    # 限制样本数量以提高性能
    sample_values = sample_values[:max_samples] if sample_values else []
    
    # 基于列名的检测
    column_type = _detect_by_column_name(column_name)
    if column_type != 'none':
        # 验证样本值是否符合预期格式
        if _validate_field_type(sample_values, column_type):
            return column_type
    
    # 基于样本值的检测
    value_type = _detect_by_sample_values(sample_values)
    return value_type


def get_sensitivity_score(column_name: str, sample_values: List[str]) -> float:
    """
    计算字段的敏感性得分
    
    Args:
        column_name: 列名
        sample_values: 样本值列表
        
    Returns:
        float: 敏感性得分 (0-1之间，1表示最敏感)
    """
    sensitive_type = detect_sensitive_field(column_name, sample_values)
    
    # 敏感性等级评分
    sensitivity_scores = {
        'id_card': 1.0,    # 身份证号最敏感
        'phone': 0.9,      # 手机号高敏感
        'email': 0.8,      # 邮箱较敏感
        'name': 0.7,       # 姓名中等敏感
        'address': 0.6,    # 地址较低敏感
        'none': 0.0        # 非敏感
    }
    
    return sensitivity_scores.get(sensitive_type, 0.0)


def _detect_by_column_name(column_name: str) -> str:
    """基于列名检测敏感字段类型"""
    name_lower = column_name.lower()
    
    # 手机号相关
    phone_patterns = [
        'phone', 'mobile', 'tel', 'telephone', '手机', '电话', '联系方式',
        'cell', 'contact_phone', 'phone_number'
    ]
    if any(pattern in name_lower for pattern in phone_patterns):
        return 'phone'
    
    # 身份证相关
    id_patterns = [
        'id_card', 'identity', 'id_number', '身份证', 'citizen_id',
        'national_id', 'card_no', 'id_no'
    ]
    if any(pattern in name_lower for pattern in id_patterns):
        return 'id_card'
    
    # 邮箱相关
    email_patterns = [
        'email', 'mail', 'e_mail', '邮箱', '邮件', 'email_address'
    ]
    if any(pattern in name_lower for pattern in email_patterns):
        return 'email'
    
    # 姓名相关
    name_patterns = [
        'name', 'username', 'real_name', '姓名', '用户名', 'full_name',
        'first_name', 'last_name', '真实姓名'
    ]
    if any(pattern in name_lower for pattern in name_patterns):
        return 'name'
    
    # 地址相关
    address_patterns = [
        'address', 'addr', 'location', '地址', '住址', 'home_address',
        'work_address', '详细地址'
    ]
    if any(pattern in name_lower for pattern in address_patterns):
        return 'address'
    
    return 'none'


def _detect_by_sample_values(sample_values: List[str]) -> str:
    """基于样本值检测敏感字段类型"""
    if not sample_values:
        return 'none'
    
    # 计算各种模式的匹配率
    total_samples = len(sample_values)
    
    # 手机号检测
    phone_matches = sum(1 for val in sample_values if _is_phone_number(val))
    if phone_matches / total_samples > 0.7:  # 70%以上匹配
        return 'phone'
    
    # 身份证检测
    id_matches = sum(1 for val in sample_values if _is_id_card(val))
    if id_matches / total_samples > 0.7:
        return 'id_card'
    
    # 邮箱检测
    email_matches = sum(1 for val in sample_values if _is_email(val))
    if email_matches / total_samples > 0.7:
        return 'email'
    
    # 中文姓名检测
    name_matches = sum(1 for val in sample_values if _is_chinese_name(val))
    if name_matches / total_samples > 0.7:
        return 'name'
    
    return 'none'


def _validate_field_type(sample_values: List[str], field_type: str) -> bool:
    """验证样本值是否符合指定的字段类型"""
    if not sample_values:
        return True
    
    validation_functions = {
        'phone': _is_phone_number,
        'id_card': _is_id_card,
        'email': _is_email,
        'name': _is_chinese_name,
        'address': lambda x: len(_safe_to_string(x)) > 5  # 地址通常较长
    }
    
    if field_type not in validation_functions:
        return True
    
    validator = validation_functions[field_type]
    valid_count = sum(1 for val in sample_values if validator(val))
    
    # 至少50%的样本值符合格式
    return valid_count / len(sample_values) >= 0.5


def _is_phone_number(value) -> bool:
    """检测是否为手机号"""
    # 安全转换为字符串
    value_str = _safe_to_string(value)
    if not value_str:
        return False
    
    # 清理空格和特殊字符
    cleaned = re.sub(r'[\s\-\(\)\+]', '', value_str)
    
    # 中国手机号格式 (11位数字，以1开头)
    china_mobile = re.match(r'^1[3-9]\d{9}$', cleaned)
    
    # 国际格式 (+86开头或86开头)
    china_international = re.match(r'^(\+?86)?1[3-9]\d{9}$', cleaned)
    
    # 美国手机号格式 (10位数字，可能有前缀1)
    us_mobile = re.match(r'^1?[2-9]\d{2}[2-9]\d{2}\d{4}$', cleaned)
    
    # 国际通用格式 (7-15位数字)
    international_general = re.match(r'^\d{7,15}$', cleaned) and len(cleaned) >= 7
    
    # 包含分机号的格式 (x后跟数字)
    cleaned_for_extension = value_str.replace(' ', '').replace('-', '')
    with_extension = re.search(r'\d{7,15}x\d+', cleaned_for_extension)
    
    return bool(china_mobile or china_international or us_mobile or 
                (international_general and len(cleaned) >= 10) or with_extension)


def _is_id_card(value) -> bool:
    """检测是否为身份证号"""
    # 安全转换为字符串
    value_str = _safe_to_string(value)
    if not value_str:
        return False
    
    # 清理空格并转大写
    cleaned = value_str.replace(' ', '').upper()
    
    # 18位身份证号格式
    if len(cleaned) == 18:
        # 前17位为数字，最后一位为数字或X
        pattern = re.match(r'^\d{17}[\dX]$', cleaned)
        return bool(pattern)
    
    # 15位身份证号格式（旧版）
    elif len(cleaned) == 15:
        pattern = re.match(r'^\d{15}$', cleaned)
        return bool(pattern)
    
    return False


def _is_email(value) -> bool:
    """检测是否为邮箱地址"""
    # 安全转换为字符串
    value_str = _safe_to_string(value)
    if not value_str:
        return False
    
    pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    return bool(pattern.match(value_str))


def _is_chinese_name(value) -> bool:
    """检测是否为中文姓名"""
    # 安全转换为字符串
    value_str = _safe_to_string(value)
    if not value_str:
        return False
    
    # 2-4个中文字符组成的姓名
    pattern = re.compile(r'^[\u4e00-\u9fa5]{2,4}$')
    return bool(pattern.match(value_str.strip()))


if __name__ == "__main__":
    # 测试代码
    test_cases = [
        ("手机号", ["13812345678", "15987654321", "18611112222"]),
        ("身份证", ["110101199001011234", "320123198506154321"]),
        ("邮箱", ["user@example.com", "test@gmail.com", "admin@company.org"]),
        ("姓名", ["张三", "李四", "王小明"]),
        ("地址", ["北京市朝阳区建国路1号", "上海市浦东新区陆家嘴"]),
        ("普通数据", ["123", "456", "789"])
    ]
    
    for field_name, samples in test_cases:
        sensitive_type = detect_sensitive_field(field_name, samples)
        score = get_sensitivity_score(field_name, samples)
        print(f"字段: {field_name}")
        print(f"  检测类型: {sensitive_type}")
        print(f"  敏感性得分: {score:.2f}")
        print()
