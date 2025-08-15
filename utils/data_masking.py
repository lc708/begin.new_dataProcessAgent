"""
数据脱敏工具
用于对敏感数据进行脱敏处理
"""
import re
import hashlib
import random
from typing import Any, Dict, List


def mask_data(value: Any, masking_type: str, masking_strategy: str = 'partial') -> str:
    """
    对数据进行脱敏处理
    
    Args:
        value: 要脱敏的值
        masking_type: 脱敏类型 ('phone', 'id_card', 'email', 'name', 'address')
        masking_strategy: 脱敏策略 ('partial', 'hash', 'random', 'remove')
        
    Returns:
        str: 脱敏后的值
    """
    if value is None or str(value).strip() == '':
        return str(value)
    
    value_str = str(value)
    
    # 根据脱敏类型和策略选择处理方法
    if masking_strategy == 'hash':
        return _hash_masking(value_str)
    elif masking_strategy == 'random':
        return _random_masking(value_str, masking_type)
    elif masking_strategy == 'remove':
        return _remove_masking()
    else:  # partial (默认)
        return _partial_masking(value_str, masking_type)


def batch_mask_column(series, masking_type: str, masking_strategy: str = 'partial'):
    """
    批量脱敏处理列数据
    
    Args:
        series: pandas Series对象
        masking_type: 脱敏类型
        masking_strategy: 脱敏策略
        
    Returns:
        pandas Series: 脱敏后的Series
    """
    return series.apply(lambda x: mask_data(x, masking_type, masking_strategy))


def _partial_masking(value: str, masking_type: str) -> str:
    """部分脱敏：保留部分字符，其余用*代替"""
    if masking_type == 'phone':
        return _mask_phone_partial(value)
    elif masking_type == 'id_card':
        return _mask_id_card_partial(value)
    elif masking_type == 'email':
        return _mask_email_partial(value)
    elif masking_type == 'name':
        return _mask_name_partial(value)
    elif masking_type == 'address':
        return _mask_address_partial(value)
    else:
        # 默认处理：保留前后各2个字符
        if len(value) <= 4:
            return '*' * len(value)
        return value[:2] + '*' * (len(value) - 4) + value[-2:]


def _hash_masking(value: str) -> str:
    """哈希脱敏：使用SHA256哈希"""
    return hashlib.sha256(value.encode('utf-8')).hexdigest()[:8]


def _random_masking(value: str, masking_type: str) -> str:
    """随机脱敏：生成随机但格式相似的数据"""
    if masking_type == 'phone':
        return _generate_random_phone()
    elif masking_type == 'id_card':
        return _generate_random_id_card()
    elif masking_type == 'email':
        return _generate_random_email()
    elif masking_type == 'name':
        return _generate_random_name()
    else:
        return _generate_random_string(len(value))


def _remove_masking() -> str:
    """删除脱敏：返回固定标记"""
    return '[已删除]'


def _mask_phone_partial(phone: str) -> str:
    """手机号部分脱敏：显示前3位和后4位"""
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    if len(cleaned) >= 11:
        return cleaned[:3] + '****' + cleaned[-4:]
    return '*' * len(cleaned)


def _mask_id_card_partial(id_card: str) -> str:
    """身份证部分脱敏：显示前6位和后4位"""
    cleaned = id_card.replace(' ', '')
    if len(cleaned) >= 18:
        return cleaned[:6] + '********' + cleaned[-4:]
    elif len(cleaned) >= 15:
        return cleaned[:6] + '*****' + cleaned[-4:]
    return '*' * len(cleaned)


def _mask_email_partial(email: str) -> str:
    """邮箱部分脱敏：保留用户名前2位和域名"""
    if '@' in email:
        username, domain = email.split('@', 1)
        if len(username) <= 2:
            masked_username = '*' * len(username)
        else:
            masked_username = username[:2] + '*' * (len(username) - 2)
        return f"{masked_username}@{domain}"
    return '*' * len(email)


def _mask_name_partial(name: str) -> str:
    """姓名部分脱敏：保留姓氏"""
    name = name.strip()
    if len(name) <= 1:
        return '*'
    elif len(name) == 2:
        return name[0] + '*'
    else:
        return name[0] + '*' * (len(name) - 1)


def _mask_address_partial(address: str) -> str:
    """地址部分脱敏：保留前面的行政区划，隐藏详细地址"""
    # 保留前面的省市区信息，隐藏详细地址
    if len(address) <= 10:
        return address[:len(address)//2] + '*' * (len(address) - len(address)//2)
    else:
        return address[:8] + '*' * (len(address) - 8)


def _generate_random_phone() -> str:
    """生成随机手机号"""
    prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                '150', '151', '152', '153', '155', '156', '157', '158', '159',
                '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
    prefix = random.choice(prefixes)
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return prefix + suffix


def _generate_random_id_card() -> str:
    """生成随机身份证号"""
    # 简单生成18位随机数字
    return ''.join([str(random.randint(0, 9)) for _ in range(17)]) + random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X'])


def _generate_random_email() -> str:
    """生成随机邮箱"""
    domains = ['example.com', 'test.com', 'demo.org', 'sample.net']
    username_length = random.randint(5, 10)
    username = ''.join([chr(random.randint(97, 122)) for _ in range(username_length)])
    domain = random.choice(domains)
    return f"{username}@{domain}"


def _generate_random_name() -> str:
    """生成随机中文姓名"""
    surnames = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴']
    given_names = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋']
    
    surname = random.choice(surnames)
    if random.choice([True, False]):  # 50%概率生成两字名
        given_name = random.choice(given_names)
    else:  # 50%概率生成三字名
        given_name = random.choice(given_names) + random.choice(given_names)
    
    return surname + given_name


def _generate_random_string(length: int) -> str:
    """生成随机字符串"""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join([random.choice(chars) for _ in range(length)])


def get_masking_preview(sample_values: List[str], masking_type: str, masking_strategy: str = 'partial') -> Dict[str, List[str]]:
    """
    获取脱敏预览结果
    
    Args:
        sample_values: 样本值列表
        masking_type: 脱敏类型
        masking_strategy: 脱敏策略
        
    Returns:
        Dict: 包含原值和脱敏后值的字典
    """
    preview_count = min(5, len(sample_values))
    sample_subset = sample_values[:preview_count]
    
    masked_values = [mask_data(val, masking_type, masking_strategy) for val in sample_subset]
    
    return {
        'original': sample_subset,
        'masked': masked_values
    }


if __name__ == "__main__":
    # 测试代码
    test_data = {
        'phone': ['13812345678', '15987654321'],
        'id_card': ['110101199001011234', '320123198506154321'],
        'email': ['user@example.com', 'test@gmail.com'],
        'name': ['张三', '李小明'],
        'address': ['北京市朝阳区建国路1号', '上海市浦东新区陆家嘴']
    }
    
    strategies = ['partial', 'hash', 'random', 'remove']
    
    for data_type, values in test_data.items():
        print(f"\n{data_type.upper()} 脱敏测试:")
        for strategy in strategies:
            print(f"  策略: {strategy}")
            for val in values:
                masked = mask_data(val, data_type, strategy)
                print(f"    {val} -> {masked}")
