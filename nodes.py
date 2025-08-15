"""
数据处理Agent的MACore节点实现
包含数据验证、标准化、缺失值处理、脱敏、特征提取和质量报告生成
"""
import pandas as pd
import logging
from typing import Dict, Any, List
from macore import Node
from utils.call_llm import call_llm
from utils.data_type_detector import detect_data_type, convert_column_type, standardize_column_names
from utils.sensitive_detector import detect_sensitive_field, get_sensitivity_score
from utils.data_masking import mask_data, batch_mask_column, get_masking_preview
from utils.quality_metrics import calculate_quality_metrics, generate_quality_report_text
from utils.config_validator import validate_config, get_default_config


class DataValidationNode(Node):
    """数据验证节点：验证输入数据的格式、大小和基本质量要求"""
    
    def prep(self, shared):
        """准备阶段：读取原始数据和文件信息"""
        return {
            'raw_df': shared.get('input_data', {}).get('raw_df'),
            'file_info': shared.get('input_data', {}).get('file_info', {})
        }
    
    def exec(self, prep_data):
        """执行阶段：执行数据格式验证、大小检查、基本质量检查"""
        errors = []
        raw_df = prep_data.get('raw_df')
        file_info = prep_data.get('file_info', {})
        
        # 检查DataFrame是否存在
        if raw_df is None:
            errors.append("数据为空")
            return {'valid': False, 'errors': errors}
        
        # 检查是否为空DataFrame
        if raw_df.empty:
            errors.append("数据文件为空")
            return {'valid': False, 'errors': errors}
        
        # 检查数据大小限制 (默认100万行)
        max_rows = 1000000
        if len(raw_df) > max_rows:
            errors.append(f"数据行数超出限制：{len(raw_df)} > {max_rows}")
        
        # 检查列数限制 (默认1000列)
        max_columns = 1000
        if len(raw_df.columns) > max_columns:
            errors.append(f"数据列数超出限制：{len(raw_df.columns)} > {max_columns}")
        
        # 检查重复列名
        duplicate_columns = raw_df.columns[raw_df.columns.duplicated()].tolist()
        if duplicate_columns:
            errors.append(f"存在重复列名：{duplicate_columns}")
        
        # 检查全空列
        empty_columns = raw_df.columns[raw_df.isnull().all()].tolist()
        if empty_columns:
            logging.warning(f"发现全空列：{empty_columns}")
        
        # 基本质量检查
        total_cells = len(raw_df) * len(raw_df.columns)
        missing_cells = raw_df.isnull().sum().sum()
        missing_rate = missing_cells / total_cells if total_cells > 0 else 0
        
        if missing_rate > 0.8:  # 缺失率超过80%
            errors.append(f"数据质量过低，缺失率：{missing_rate:.2%}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': [f"全空列：{empty_columns}"] if empty_columns else [],
            'stats': {
                'rows': len(raw_df),
                'columns': len(raw_df.columns),
                'missing_rate': missing_rate
            }
        }
    
    def post(self, shared, prep_res, exec_res):
        """后处理阶段：将验证结果写入共享存储"""
        if 'input_data' not in shared:
            shared['input_data'] = {}
        
        shared['input_data']['validation_errors'] = exec_res.get('errors', [])
        shared['input_data']['validation_warnings'] = exec_res.get('warnings', [])
        shared['input_data']['basic_stats'] = exec_res.get('stats', {})
        
        # 记录处理日志
        if 'processing_results' not in shared:
            shared['processing_results'] = {'processing_log': []}
        
        shared['processing_results']['processing_log'].append({
            'step': 'data_validation',
            'status': 'success' if exec_res['valid'] else 'failed',
            'message': f"数据验证{'通过' if exec_res['valid'] else '失败'}",
            'details': exec_res
        })
        
        return 'valid' if exec_res['valid'] else 'invalid'


class TableStandardizationNode(Node):
    """表结构标准化节点：执行表结构标准化，包括列名格式化和数据类型转换"""
    
    def prep(self, shared):
        """准备阶段：读取原始DataFrame和标准化配置"""
        raw_df = shared.get('input_data', {}).get('raw_df')
        config = shared.get('config', {}).get('standardization', {})
        
        return {'df': raw_df.copy() if raw_df is not None else None, 'config': config}
    
    def exec(self, prep_data):
        """执行阶段：调用数据类型检测工具，执行列名标准化和类型转换"""
        df = prep_data.get('df')
        config = prep_data.get('config', {})
        
        if df is None:
            raise ValueError("没有可处理的数据")
        
        changes_log = []
        
        # 1. 移除重复列
        if config.get('remove_duplicate_columns', True):
            duplicate_cols = df.columns[df.columns.duplicated()].tolist()
            if duplicate_cols:
                df = df.loc[:, ~df.columns.duplicated()]
                changes_log.append(f"移除重复列：{duplicate_cols}")
        
        # 2. 移除全空列
        if config.get('remove_empty_columns', True):
            empty_cols = df.columns[df.isnull().all()].tolist()
            if empty_cols:
                df = df.drop(columns=empty_cols)
                changes_log.append(f"移除全空列：{empty_cols}")
        
        # 3. 标准化列名
        if config.get('enable_column_rename', True):
            original_columns = df.columns.tolist()
            naming_convention = config.get('naming_convention', 'snake_case')
            df = standardize_column_names(df, naming_convention)
            
            column_mapping = dict(zip(original_columns, df.columns.tolist()))
            renamed_cols = {k: v for k, v in column_mapping.items() if k != v}
            if renamed_cols:
                changes_log.append(f"列名标准化：{renamed_cols}")
        
        # 4. 自动检测和转换数据类型
        if config.get('auto_detect_types', True):
            type_changes = {}
            for col in df.columns:
                original_type = str(df[col].dtype)
                detected_type = detect_data_type(df[col])
                
                # 只转换明显需要转换的类型
                if detected_type in ['numeric', 'datetime', 'boolean'] and original_type == 'object':
                    df[col] = convert_column_type(df[col], detected_type)
                    new_type = str(df[col].dtype)
                    if new_type != original_type:
                        type_changes[col] = {'from': original_type, 'to': new_type}
            
            if type_changes:
                changes_log.append(f"数据类型转换：{type_changes}")
        
        # 5. 应用自定义类型映射
        custom_mapping = config.get('custom_type_mapping', {})
        for col, target_type in custom_mapping.items():
            if col in df.columns:
                original_type = str(df[col].dtype)
                df[col] = convert_column_type(df[col], target_type)
                new_type = str(df[col].dtype)
                if new_type != original_type:
                    changes_log.append(f"自定义类型转换 {col}: {original_type} -> {new_type}")
        
        return {'standardized_df': df, 'changes': changes_log}
    
    def post(self, shared, prep_res, exec_res):
        """后处理阶段：将标准化后的DataFrame写入共享存储"""
        if 'processing_results' not in shared:
            shared['processing_results'] = {}
        
        shared['processing_results']['standardized_df'] = exec_res['standardized_df']
        
        # 计算一致性改进
        try:
            from utils.quality_metrics import _calculate_type_consistency
            original_df = shared.get('input_data', {}).get('raw_df')
            processed_df = exec_res['processed_df']
            
            if original_df is not None and processed_df is not None:
                original_consistency = _calculate_type_consistency(original_df) * 100
                processed_consistency = _calculate_type_consistency(processed_df) * 100
                consistency_improvement = processed_consistency - original_consistency
                
                message = f'表结构标准化完成，数据一致性从 {original_consistency:.1f}% 提升到 {processed_consistency:.1f}%'
                if consistency_improvement > 0:
                    message += f' (提升 {consistency_improvement:.1f}%)'
            else:
                message = '表结构标准化完成'
        except Exception:
            message = '表结构标准化完成'
        
        # 记录处理日志
        shared['processing_results']['processing_log'].append({
            'step': 'table_standardization',
            'status': 'success',
            'message': message,
            'details': {'changes': exec_res['changes']}
        })
        
        return 'default'


class MissingDataHandlingNode(Node):
    """缺失数据处理节点：根据配置策略处理缺失数据"""
    
    def prep(self, shared):
        """准备阶段：读取标准化后的DataFrame和缺失值处理配置"""
        df = shared.get('processing_results', {}).get('standardized_df')
        config = shared.get('config', {}).get('missing_handling', {})
        
        return {'df': df.copy() if df is not None else None, 'config': config}
    
    def exec(self, prep_data):
        """执行阶段：根据数据类型和配置策略填充缺失值"""
        df = prep_data.get('df')
        config = prep_data.get('config', {})
        
        if df is None:
            raise ValueError("没有可处理的数据")
        
        changes_log = []
        original_missing = df.isnull().sum().sum()
        
        # 1. 删除缺失率过高的列
        missing_threshold = config.get('missing_threshold', 0.9)
        high_missing_cols = []
        for col in df.columns:
            missing_rate = df[col].isnull().sum() / len(df)
            if missing_rate > missing_threshold:
                high_missing_cols.append(col)
        
        if high_missing_cols:
            df = df.drop(columns=high_missing_cols)
            changes_log.append(f"删除高缺失率列：{high_missing_cols}")
        
        # 2. 处理剩余缺失值
        default_strategy = config.get('default_strategy', 'mean')
        column_strategies = config.get('column_strategies', {})
        custom_fill_values = config.get('custom_fill_values', {})
        
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                strategy = column_strategies.get(col, default_strategy)
                
                if col in custom_fill_values:
                    # 使用自定义填充值
                    fill_value = custom_fill_values[col]
                    df[col] = df[col].fillna(fill_value)
                    changes_log.append(f"列 {col} 使用自定义值填充：{fill_value}")
                
                elif strategy == 'mean' and pd.api.types.is_numeric_dtype(df[col]):
                    fill_value = df[col].mean()
                    df[col] = df[col].fillna(fill_value)
                    changes_log.append(f"列 {col} 使用均值填充：{fill_value:.2f}")
                
                elif strategy == 'median' and pd.api.types.is_numeric_dtype(df[col]):
                    fill_value = df[col].median()
                    df[col] = df[col].fillna(fill_value)
                    changes_log.append(f"列 {col} 使用中位数填充：{fill_value}")
                
                elif strategy == 'mode':
                    mode_values = df[col].mode()
                    if len(mode_values) > 0:
                        fill_value = mode_values[0]
                        df[col] = df[col].fillna(fill_value)
                        changes_log.append(f"列 {col} 使用众数填充：{fill_value}")
                
                elif strategy == 'forward_fill':
                    df[col] = df[col].ffill()
                    changes_log.append(f"列 {col} 使用前向填充")
                
                elif strategy == 'backward_fill':
                    df[col] = df[col].bfill()
                    changes_log.append(f"列 {col} 使用后向填充")
                
                elif strategy == 'drop':
                    # 删除包含缺失值的行
                    before_rows = len(df)
                    df = df.dropna(subset=[col])
                    after_rows = len(df)
                    if before_rows != after_rows:
                        changes_log.append(f"因列 {col} 缺失值删除 {before_rows - after_rows} 行")
        
        final_missing = df.isnull().sum().sum()
        missing_reduction = original_missing - final_missing
        
        return {
            'processed_df': df,
            'changes': changes_log,
            'missing_reduction': missing_reduction
        }
    
    def post(self, shared, prep_res, exec_res):
        """后处理阶段：更新DataFrame到共享存储"""
        shared['processing_results']['standardized_df'] = exec_res['processed_df']
        
        # 记录处理日志
        shared['processing_results']['processing_log'].append({
            'step': 'missing_data_handling',
            'status': 'success',
            'message': f'缺失值处理完成，减少缺失值 {exec_res["missing_reduction"]} 个',
            'details': {'changes': exec_res['changes']}
        })
        
        return 'default'


class DataMaskingAgentNode(Node):
    """数据脱敏Agent节点：智能识别敏感字段并执行脱敏处理"""
    
    def prep(self, shared):
        """准备阶段：读取当前DataFrame和脱敏规则配置"""
        df = shared.get('processing_results', {}).get('standardized_df')
        config = shared.get('config', {}).get('masking_rules', {})
        
        return {'df': df.copy() if df is not None else None, 'config': config}
    
    def exec(self, prep_data):
        """执行阶段：使用LLM分析字段特征，识别敏感信息，执行脱敏操作"""
        df = prep_data.get('df')
        config = prep_data.get('config', {})
        
        if df is None:
            raise ValueError("没有可处理的数据")
        
        changes_log = []
        masked_columns = []
        
        enable_auto_detection = config.get('enable_auto_detection', True)
        sensitivity_threshold = config.get('sensitivity_threshold', 0.7)
        default_strategy = config.get('default_strategy', 'partial')
        column_rules = config.get('column_rules', {})
        
        # 处理每一列
        for col in df.columns:
            should_mask = False
            masking_type = None
            masking_strategy = default_strategy
            
            # 1. 检查是否有明确的列规则
            if col in column_rules:
                rule = column_rules[col]
                should_mask = True
                masking_type = rule.get('type', 'text')
                masking_strategy = rule.get('strategy', default_strategy)
                changes_log.append(f"列 {col} 使用预设规则：{rule}")
            
            # 2. 自动检测敏感字段
            elif enable_auto_detection:
                # 获取样本值用于检测
                sample_values = df[col].dropna().astype(str).head(20).tolist()
                
                if sample_values:
                    # 使用LLM进行智能分析
                    llm_analysis = self._analyze_column_with_llm(col, sample_values)
                    
                    # 结合规则检测
                    detected_type = detect_sensitive_field(col, sample_values)
                    sensitivity_score = get_sensitivity_score(col, sample_values)
                    
                    if sensitivity_score >= sensitivity_threshold or llm_analysis.get('is_sensitive', False):
                        should_mask = True
                        masking_type = detected_type if detected_type != 'none' else llm_analysis.get('suggested_type', 'text')
                        
                        changes_log.append(
                            f"列 {col} 自动检测为敏感字段：类型={masking_type}, "
                            f"得分={sensitivity_score:.2f}, LLM建议={llm_analysis}"
                        )
            
            # 3. 执行脱敏处理
            if should_mask:
                try:
                    original_sample = df[col].dropna().head(3).tolist()
                    df[col] = batch_mask_column(df[col], masking_type, masking_strategy)
                    masked_sample = df[col].dropna().head(3).tolist()
                    
                    masked_columns.append({
                        'column': col,
                        'type': masking_type,
                        'strategy': masking_strategy,
                        'preview': {
                            'original': original_sample,
                            'masked': masked_sample
                        }
                    })
                    
                    changes_log.append(f"列 {col} 脱敏完成：{masking_type} -> {masking_strategy}")
                    
                except Exception as e:
                    changes_log.append(f"列 {col} 脱敏失败：{str(e)}")
        
        return {
            'masked_df': df,
            'masked_columns': masked_columns,
            'changes': changes_log
        }
    
    def _analyze_column_with_llm(self, column_name: str, sample_values: List[str]) -> Dict[str, Any]:
        """使用LLM分析列的敏感性"""
        try:
            # 限制样本数量和长度以控制prompt大小
            limited_samples = sample_values[:5]
            limited_samples = [str(val)[:50] for val in limited_samples]
            
            prompt = f"""
分析以下数据列是否包含敏感信息：

列名：{column_name}
样本值：{limited_samples}

请判断：
1. 这个列是否包含敏感信息？
2. 如果是敏感信息，属于什么类型？(phone/id_card/email/name/address/other)
3. 建议的脱敏策略？(partial/hash/random/remove)

请以JSON格式回复：
{{
    "is_sensitive": true/false,
    "confidence": 0-1,
    "suggested_type": "类型",
    "suggested_strategy": "策略",
    "reasoning": "判断理由"
}}
"""
            
            response = call_llm(prompt)
            
            # 简单解析LLM响应
            try:
                import json
                # 尝试提取JSON部分
                if '{' in response and '}' in response:
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except:
                pass
            
            # 如果JSON解析失败，返回保守的结果
            return {
                "is_sensitive": False,
                "confidence": 0.5,
                "suggested_type": "text",
                "suggested_strategy": "partial",
                "reasoning": "LLM分析失败，采用保守策略"
            }
            
        except Exception as e:
            logging.warning(f"LLM分析列 {column_name} 失败：{str(e)}")
            return {
                "is_sensitive": False,
                "confidence": 0.0,
                "suggested_type": "text",
                "suggested_strategy": "partial",
                "reasoning": f"分析出错：{str(e)}"
            }
    
    def post(self, shared, prep_res, exec_res):
        """后处理阶段：将脱敏后的DataFrame写入共享存储"""
        shared['processing_results']['processed_df'] = exec_res['masked_df']
        shared['processing_results']['masked_columns'] = exec_res['masked_columns']
        
        # 记录处理日志
        shared['processing_results']['processing_log'].append({
            'step': 'data_masking',
            'status': 'success',
            'message': f'数据脱敏完成，处理 {len(exec_res["masked_columns"])} 个敏感字段',
            'details': {'changes': exec_res['changes'], 'masked_columns': exec_res['masked_columns']}
        })
        
        return 'default'


class FeatureExtractionNode(Node):
    """特征提取节点：提取基础统计特征和文本特征"""
    
    def prep(self, shared):
        """准备阶段：读取处理后的DataFrame和特征提取配置"""
        df = shared.get('processing_results', {}).get('processed_df')
        config = shared.get('config', {}).get('feature_extraction', {})
        
        return {'df': df.copy() if df is not None else None, 'config': config}
    
    def exec(self, prep_data):
        """执行阶段：根据数据类型提取相应特征"""
        df = prep_data.get('df')
        config = prep_data.get('config', {})
        
        if df is None or not config.get('enable_extraction', False):
            return {'features_df': df, 'extracted_features': []}
        
        extracted_features = []
        features_df = df.copy()
        
        # 数值特征提取
        if config.get('extract_numeric_stats', True):
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                if df[col].notna().sum() > 0:  # 有非空值
                    # 添加统计特征
                    features_df[f'{col}_is_null'] = df[col].isnull().astype(int)
                    features_df[f'{col}_abs'] = df[col].abs()
                    
                    extracted_features.append(f'{col}_is_null')
                    extracted_features.append(f'{col}_abs')
        
        # 文本特征提取
        if config.get('extract_text_features', True):
            text_cols = df.select_dtypes(include=['object', 'string']).columns
            for col in text_cols:
                if df[col].notna().sum() > 0:
                    # 文本长度特征
                    features_df[f'{col}_length'] = df[col].astype(str).str.len()
                    features_df[f'{col}_word_count'] = df[col].astype(str).str.split().str.len()
                    features_df[f'{col}_is_empty'] = (df[col].astype(str).str.strip() == '').astype(int)
                    
                    extracted_features.extend([
                        f'{col}_length',
                        f'{col}_word_count',
                        f'{col}_is_empty'
                    ])
        
        # 时间特征提取
        if config.get('extract_datetime_features', True):
            datetime_cols = df.select_dtypes(include=['datetime64']).columns
            for col in datetime_cols:
                if df[col].notna().sum() > 0:
                    features_df[f'{col}_year'] = df[col].dt.year
                    features_df[f'{col}_month'] = df[col].dt.month
                    features_df[f'{col}_dayofweek'] = df[col].dt.dayofweek
                    
                    extracted_features.extend([
                        f'{col}_year',
                        f'{col}_month',
                        f'{col}_dayofweek'
                    ])
        
        return {'features_df': features_df, 'extracted_features': extracted_features}
    
    def post(self, shared, prep_res, exec_res):
        """后处理阶段：将特征添加到DataFrame或单独存储"""
        shared['processing_results']['processed_df'] = exec_res['features_df']
        shared['processing_results']['extracted_features'] = exec_res['extracted_features']
        
        # 记录处理日志
        shared['processing_results']['processing_log'].append({
            'step': 'feature_extraction',
            'status': 'success',
            'message': f'特征提取完成，新增 {len(exec_res["extracted_features"])} 个特征',
            'details': {'extracted_features': exec_res['extracted_features']}
        })
        
        return 'default'


class QualityReportNode(Node):
    """质量报告节点：生成数据质量报告和处理日志"""
    
    def prep(self, shared):
        """准备阶段：读取原始数据、处理后数据和所有中间结果"""
        return {
            'original_df': shared.get('input_data', {}).get('raw_df'),
            'processed_df': shared.get('processing_results', {}).get('processed_df'),
            'processing_log': shared.get('processing_results', {}).get('processing_log', []),
            'masked_columns': shared.get('processing_results', {}).get('masked_columns', []),
            'extracted_features': shared.get('processing_results', {}).get('extracted_features', [])
        }
    
    def exec(self, prep_data):
        """执行阶段：调用质量指标计算器，生成对比报告"""
        original_df = prep_data.get('original_df')
        processed_df = prep_data.get('processed_df')
        processing_log = prep_data.get('processing_log', [])
        
        if original_df is None or processed_df is None:
            raise ValueError("缺少原始数据或处理后数据")
        
        # 计算质量指标
        quality_metrics = calculate_quality_metrics(original_df, processed_df)
        
        # 生成文本报告
        text_report = generate_quality_report_text(quality_metrics)
        
        # 生成处理摘要
        processing_summary = {
            'total_steps': len(processing_log),
            'successful_steps': len([log for log in processing_log if log.get('status') == 'success']),
            'failed_steps': len([log for log in processing_log if log.get('status') == 'failed']),
            'masked_columns_count': len(prep_data.get('masked_columns', [])),
            'extracted_features_count': len(prep_data.get('extracted_features', [])),
            'processing_timeline': processing_log
        }
        
        return {
            'quality_metrics': quality_metrics,
            'text_report': text_report,
            'processing_summary': processing_summary
        }
    
    def post(self, shared, prep_res, exec_res):
        """后处理阶段：将质量报告写入共享存储"""
        shared['processing_results']['quality_report'] = exec_res['quality_metrics']
        shared['processing_results']['text_report'] = exec_res['text_report']
        shared['processing_results']['processing_summary'] = exec_res['processing_summary']
        
        # 记录最终日志
        shared['processing_results']['processing_log'].append({
            'step': 'quality_report',
            'status': 'success',
            'message': '质量报告生成完成',
            'details': exec_res['processing_summary']
        })
        
        return 'default'
