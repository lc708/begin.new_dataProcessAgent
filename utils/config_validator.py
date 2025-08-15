"""
配置验证工具
用于验证用户配置的有效性
"""
import yaml
import json
from typing import Dict, Any, Tuple, List
from pydantic import BaseModel, ValidationError, validator
from enum import Enum


class NamingConvention(str, Enum):
    """列名命名约定"""
    SNAKE_CASE = "snake_case"
    CAMEL_CASE = "camelCase"
    PASCAL_CASE = "PascalCase"


class MissingStrategy(str, Enum):
    """缺失值处理策略"""
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    FORWARD_FILL = "forward_fill"
    BACKWARD_FILL = "backward_fill"
    DROP = "drop"
    CUSTOM = "custom"


class MaskingStrategy(str, Enum):
    """脱敏策略"""
    PARTIAL = "partial"
    HASH = "hash"
    RANDOM = "random"
    REMOVE = "remove"


class SensitiveType(str, Enum):
    """敏感信息类型"""
    PHONE = "phone"
    ID_CARD = "id_card"
    EMAIL = "email"
    NAME = "name"
    ADDRESS = "address"


class StandardizationConfig(BaseModel):
    """表结构标准化配置"""
    enable_column_rename: bool = True
    naming_convention: NamingConvention = NamingConvention.SNAKE_CASE
    remove_duplicate_columns: bool = True
    remove_empty_columns: bool = True
    auto_detect_types: bool = True
    custom_type_mapping: Dict[str, str] = {}
    
    @validator('custom_type_mapping')
    def validate_type_mapping(cls, v):
        valid_types = {'numeric', 'datetime', 'categorical', 'text', 'boolean'}
        for column, dtype in v.items():
            if dtype not in valid_types:
                raise ValueError(f"Invalid data type '{dtype}' for column '{column}'. Valid types: {valid_types}")
        return v


class MissingHandlingConfig(BaseModel):
    """缺失值处理配置"""
    default_strategy: MissingStrategy = MissingStrategy.MEAN
    column_strategies: Dict[str, MissingStrategy] = {}
    custom_fill_values: Dict[str, Any] = {}
    missing_threshold: float = 0.9  # 缺失率阈值，超过则删除列
    
    @validator('missing_threshold')
    def validate_threshold(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("missing_threshold must be between 0 and 1")
        return v


class MaskingRuleConfig(BaseModel):
    """脱敏规则配置"""
    enable_auto_detection: bool = True
    default_strategy: MaskingStrategy = MaskingStrategy.PARTIAL
    column_rules: Dict[str, Dict[str, Any]] = {}
    sensitivity_threshold: float = 0.7
    
    @validator('sensitivity_threshold')
    def validate_sensitivity_threshold(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("sensitivity_threshold must be between 0 and 1")
        return v
    
    @validator('column_rules')
    def validate_column_rules(cls, v):
        for column, rule in v.items():
            if 'type' in rule and rule['type'] not in [e.value for e in SensitiveType]:
                raise ValueError(f"Invalid sensitive type '{rule['type']}' for column '{column}'")
            if 'strategy' in rule and rule['strategy'] not in [e.value for e in MaskingStrategy]:
                raise ValueError(f"Invalid masking strategy '{rule['strategy']}' for column '{column}'")
        return v


class FeatureExtractionConfig(BaseModel):
    """特征提取配置"""
    enable_extraction: bool = False
    extract_numeric_stats: bool = True
    extract_text_features: bool = True
    extract_datetime_features: bool = True
    custom_features: List[str] = []


class DataProcessingConfig(BaseModel):
    """完整的数据处理配置"""
    standardization: StandardizationConfig = StandardizationConfig()
    missing_handling: MissingHandlingConfig = MissingHandlingConfig()
    masking_rules: MaskingRuleConfig = MaskingRuleConfig()
    feature_extraction: FeatureExtractionConfig = FeatureExtractionConfig()


def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    验证配置的有效性
    
    Args:
        config: 配置字典
        
    Returns:
        Tuple[bool, List[str]]: (是否有效, 错误信息列表)
    """
    errors = []
    
    try:
        # 使用Pydantic模型验证
        DataProcessingConfig(**config)
        return True, []
    except ValidationError as e:
        for error in e.errors():
            field = " -> ".join(str(x) for x in error['loc'])
            message = error['msg']
            errors.append(f"字段 '{field}': {message}")
        return False, errors
    except Exception as e:
        errors.append(f"配置验证失败: {str(e)}")
        return False, errors


def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置
    
    Returns:
        Dict: 默认配置字典
    """
    default_config = DataProcessingConfig()
    return default_config.dict()


def load_config_from_file(file_path: str) -> Tuple[Dict[str, Any], List[str]]:
    """
    从文件加载配置
    
    Args:
        file_path: 配置文件路径
        
    Returns:
        Tuple[Dict, List[str]]: (配置字典, 错误信息列表)
    """
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                config = yaml.safe_load(f)
            elif file_path.endswith('.json'):
                config = json.load(f)
            else:
                errors.append("不支持的文件格式，请使用 .yaml, .yml 或 .json 文件")
                return {}, errors
        
        # 验证加载的配置
        is_valid, validation_errors = validate_config(config)
        if not is_valid:
            errors.extend(validation_errors)
        
        return config, errors
        
    except FileNotFoundError:
        errors.append(f"配置文件未找到: {file_path}")
        return {}, errors
    except yaml.YAMLError as e:
        errors.append(f"YAML格式错误: {str(e)}")
        return {}, errors
    except json.JSONDecodeError as e:
        errors.append(f"JSON格式错误: {str(e)}")
        return {}, errors
    except Exception as e:
        errors.append(f"读取配置文件失败: {str(e)}")
        return {}, errors


def save_config_to_file(config: Dict[str, Any], file_path: str) -> List[str]:
    """
    保存配置到文件
    
    Args:
        config: 配置字典
        file_path: 保存路径
        
    Returns:
        List[str]: 错误信息列表
    """
    errors = []
    
    try:
        # 先验证配置
        is_valid, validation_errors = validate_config(config)
        if not is_valid:
            errors.extend(validation_errors)
            return errors
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            elif file_path.endswith('.json'):
                json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                errors.append("不支持的文件格式，请使用 .yaml, .yml 或 .json 文件")
        
        return errors
        
    except Exception as e:
        errors.append(f"保存配置文件失败: {str(e)}")
        return errors


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并配置（覆盖配置会覆盖基础配置）
    
    Args:
        base_config: 基础配置
        override_config: 覆盖配置
        
    Returns:
        Dict: 合并后的配置
    """
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged


def get_config_template() -> str:
    """
    获取配置文件模板
    
    Returns:
        str: YAML格式的配置模板
    """
    template = """
# 数据处理配置文件模板

standardization:
  enable_column_rename: true
  naming_convention: "snake_case"  # snake_case, camelCase, PascalCase
  remove_duplicate_columns: true
  remove_empty_columns: true
  auto_detect_types: true
  custom_type_mapping: {}  # 自定义类型映射，如 {"column_name": "numeric"}

missing_handling:
  default_strategy: "mean"  # mean, median, mode, forward_fill, backward_fill, drop, custom
  column_strategies: {}     # 针对特定列的策略，如 {"age": "median", "name": "mode"}
  custom_fill_values: {}    # 自定义填充值，如 {"status": "unknown"}
  missing_threshold: 0.9    # 缺失率阈值，超过则删除列

masking_rules:
  enable_auto_detection: true
  default_strategy: "partial"  # partial, hash, random, remove
  column_rules: {}             # 针对特定列的规则
  sensitivity_threshold: 0.7   # 敏感性检测阈值

feature_extraction:
  enable_extraction: false
  extract_numeric_stats: true
  extract_text_features: true
  extract_datetime_features: true
  custom_features: []

# 示例配置：
# masking_rules:
#   column_rules:
#     "phone":
#       type: "phone"
#       strategy: "partial"
#     "email":
#       type: "email"
#       strategy: "hash"
"""
    return template.strip()


if __name__ == "__main__":
    # 测试代码
    print("=== 配置验证测试 ===")
    
    # 测试默认配置
    default_config = get_default_config()
    is_valid, errors = validate_config(default_config)
    print(f"默认配置验证: {'通过' if is_valid else '失败'}")
    if errors:
        for error in errors:
            print(f"  错误: {error}")
    
    # 测试无效配置
    invalid_config = {
        "standardization": {
            "naming_convention": "invalid_convention"
        },
        "missing_handling": {
            "missing_threshold": 1.5  # 超出范围
        }
    }
    
    is_valid, errors = validate_config(invalid_config)
    print(f"\n无效配置验证: {'通过' if is_valid else '失败'}")
    if errors:
        for error in errors:
            print(f"  错误: {error}")
    
    # 输出配置模板
    print(f"\n=== 配置文件模板 ===")
    print(get_config_template())
