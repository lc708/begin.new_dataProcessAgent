"""
数据处理Agent的MACore流程实现
连接各个数据处理节点形成完整的处理流水线
"""
from macore import Flow
from nodes import (
    DataValidationNode, 
    TableStandardizationNode, 
    MissingDataHandlingNode, 
    DataMaskingAgentNode, 
    FeatureExtractionNode, 
    QualityReportNode
)


def create_data_processing_flow():
    """创建数据处理流程"""
    # 创建所有节点
    validation_node = DataValidationNode()
    standardization_node = TableStandardizationNode()
    missing_handling_node = MissingDataHandlingNode()
    masking_node = DataMaskingAgentNode()
    feature_extraction_node = FeatureExtractionNode()
    quality_report_node = QualityReportNode()
    
    # 连接节点流程
    # 数据验证 -> 标准化 (验证通过) 或者结束 (验证失败)
    validation_node - "valid" >> standardization_node
    # 验证失败直接结束，不继续处理
    
    # 标准化 -> 缺失值处理
    standardization_node >> missing_handling_node
    
    # 缺失值处理 -> 数据脱敏
    missing_handling_node >> masking_node
    
    # 数据脱敏 -> 特征提取
    masking_node >> feature_extraction_node
    
    # 特征提取 -> 质量报告
    feature_extraction_node >> quality_report_node
    
    # 创建流程，从数据验证开始
    return Flow(start=validation_node)


def create_simple_data_processing_flow():
    """创建简化的数据处理流程（跳过特征提取）"""
    # 创建核心节点
    validation_node = DataValidationNode()
    standardization_node = TableStandardizationNode()
    missing_handling_node = MissingDataHandlingNode()
    masking_node = DataMaskingAgentNode()
    quality_report_node = QualityReportNode()
    
    # 连接节点流程
    validation_node - "valid" >> standardization_node
    standardization_node >> missing_handling_node
    missing_handling_node >> masking_node
    masking_node >> quality_report_node
    
    return Flow(start=validation_node)


def create_validation_only_flow():
    """创建仅数据验证的流程（用于快速检查）"""
    validation_node = DataValidationNode()
    return Flow(start=validation_node)

# 导出主要的流程创建函数
data_processing_flow = create_data_processing_flow()
simple_flow = create_simple_data_processing_flow()
validation_flow = create_validation_only_flow()