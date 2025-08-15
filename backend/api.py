"""
数据处理Agent的FastAPI后端实现
提供RESTful API接口用于数据处理
"""
import os
import dotenv

# 确保环境变量在应用启动时加载
dotenv.load_dotenv('.env')       # 先加载默认环境变量
dotenv.load_dotenv('.env.local') # 再加载本地环境变量（会覆盖同名变量）

import uuid
import asyncio
import io
import base64
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import process_dataframe, process_data_from_content, validate_data_only, export_processed_data
from utils.config_validator import validate_config, get_default_config, get_config_template


# 创建FastAPI应用
app = FastAPI(
    title="数据处理Agent API",
    description="基于MACore框架的数据标准化和预处理服务",
    version="1.0.0"
)

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点，用于Railway等平台的健康监控"""
    try:
        # 检查基本组件是否正常
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "running",
                "macore": "available", 
                "llm": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured"
            },
            "version": "1.0.0"
        }
        
        return health_status
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局存储，用于保存处理任务状态
PROCESSING_JOBS: Dict[str, Dict[str, Any]] = {}


# Pydantic模型定义
class ProcessingConfig(BaseModel):
    """数据处理配置模型"""
    standardization: Optional[Dict[str, Any]] = None
    missing_handling: Optional[Dict[str, Any]] = None
    masking_rules: Optional[Dict[str, Any]] = None
    feature_extraction: Optional[Dict[str, Any]] = None


class ProcessDataRequest(BaseModel):
    """数据处理请求模型"""
    file_data: str = Field(..., description="Base64编码的文件内容")
    filename: str = Field(..., description="文件名")
    config: Optional[ProcessingConfig] = None


class ProcessDataResponse(BaseModel):
    """数据处理响应模型"""
    job_id: str
    status: str
    message: str


class ProcessingStatusResponse(BaseModel):
    """处理状态响应模型"""
    job_id: str
    status: str
    progress: Optional[int] = None
    current_step: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ConfigValidationRequest(BaseModel):
    """配置验证请求模型"""
    config: Dict[str, Any]


class ConfigValidationResponse(BaseModel):
    """配置验证响应模型"""
    valid: bool
    errors: List[str] = []


# API路由实现
@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "数据处理Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "process_data": "POST /api/v1/process-data",
            "processing_status": "GET /api/v1/processing-status/{job_id}",
            "validate_config": "POST /api/v1/validate-config",
            "default_config": "GET /api/v1/default-config",
            "config_template": "GET /api/v1/config-template"
        }
    }


@app.post("/api/v1/process-data", response_model=ProcessDataResponse)
async def process_data(request: ProcessDataRequest, background_tasks: BackgroundTasks):
    """
    处理数据接口
    
    Args:
        request: 数据处理请求
        background_tasks: 后台任务管理器
        
    Returns:
        ProcessDataResponse: 处理任务信息
    """
    try:
        # 生成任务ID
        job_id = str(uuid.uuid4())
        
        # 解码文件内容
        try:
            file_content = base64.b64decode(request.file_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"文件数据解码失败: {str(e)}")
        
        # 验证文件格式
        supported_formats = ['.csv', '.xlsx', '.xls', '.json']
        if not any(request.filename.lower().endswith(fmt) for fmt in supported_formats):
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件格式。支持的格式: {', '.join(supported_formats)}"
            )
        
        # 初始化任务状态
        PROCESSING_JOBS[job_id] = {
            'status': 'processing',
            'progress': 0,
            'current_step': 'initializing',
            'created_at': datetime.now(),
            'filename': request.filename,
            'result': None,
            'error': None
        }
        
        # 启动后台处理任务
        background_tasks.add_task(
            process_data_background,
            job_id,
            file_content,
            request.filename,
            request.config.dict() if request.config else None
        )
        
        return ProcessDataResponse(
            job_id=job_id,
            status="processing",
            message="数据处理任务已启动"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动处理任务失败: {str(e)}")


async def process_data_background(job_id: str, file_content: bytes, filename: str, config: Optional[Dict[str, Any]]):
    """
    后台数据处理任务
    
    Args:
        job_id: 任务ID
        file_content: 文件内容
        filename: 文件名
        config: 处理配置
    """
    try:
        # 更新状态
        PROCESSING_JOBS[job_id]['progress'] = 10
        PROCESSING_JOBS[job_id]['current_step'] = 'data_loading'
        
        # 处理数据
        result = process_data_from_content(file_content, filename, config)
        
        if result['success']:
            # 处理成功
            PROCESSING_JOBS[job_id]['status'] = 'completed'
            PROCESSING_JOBS[job_id]['progress'] = 100
            PROCESSING_JOBS[job_id]['current_step'] = 'completed'
            
            # 清理结果中的DataFrame（无法序列化）
            processed_result = result.copy()
            if 'processed_data' in processed_result and processed_result['processed_data'] is not None:
                # 将DataFrame转换为JSON格式
                df = processed_result['processed_data']
                processed_result['processed_data'] = {
                    'data': df.to_dict('records'),
                    'columns': list(df.columns),
                    'shape': df.shape,
                    'dtypes': df.dtypes.astype(str).to_dict()
                }
            
            PROCESSING_JOBS[job_id]['result'] = processed_result
            
        else:
            # 处理失败
            PROCESSING_JOBS[job_id]['status'] = 'failed'
            PROCESSING_JOBS[job_id]['error'] = result['error']
            
    except Exception as e:
        PROCESSING_JOBS[job_id]['status'] = 'failed'
        PROCESSING_JOBS[job_id]['error'] = f"处理异常: {str(e)}"


@app.get("/api/v1/processing-status/{job_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(job_id: str):
    """
    获取处理状态
    
    Args:
        job_id: 任务ID
        
    Returns:
        ProcessingStatusResponse: 处理状态信息
    """
    if job_id not in PROCESSING_JOBS:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    job = PROCESSING_JOBS[job_id]
    
    return ProcessingStatusResponse(
        job_id=job_id,
        status=job['status'],
        progress=job.get('progress'),
        current_step=job.get('current_step'),
        result=job.get('result'),
        error=job.get('error')
    )


@app.post("/api/v1/validate-config", response_model=ConfigValidationResponse)
async def validate_configuration(request: ConfigValidationRequest):
    """
    验证配置
    
    Args:
        request: 配置验证请求
        
    Returns:
        ConfigValidationResponse: 验证结果
    """
    try:
        is_valid, errors = validate_config(request.config)
        
        return ConfigValidationResponse(
            valid=is_valid,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置验证失败: {str(e)}")


@app.get("/api/v1/default-config")
async def get_default_configuration():
    """
    获取默认配置
    
    Returns:
        Dict: 默认配置
    """
    try:
        return get_default_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取默认配置失败: {str(e)}")


@app.get("/api/v1/config-template")
async def get_configuration_template():
    """
    获取配置模板
    
    Returns:
        Dict: 配置模板和说明
    """
    try:
        return {
            "template": get_config_template(),
            "description": "数据处理配置文件模板",
            "format": "YAML"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置模板失败: {str(e)}")


@app.post("/api/v1/export-data/{job_id}")
async def export_processed_data_endpoint(job_id: str, format: str = "csv"):
    """
    导出处理后的数据
    
    Args:
        job_id: 任务ID
        format: 导出格式 (csv, xlsx, json)
        
    Returns:
        Response: 文件响应
    """
    if job_id not in PROCESSING_JOBS:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    job = PROCESSING_JOBS[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="任务未完成")
    
    if not job.get('result') or not job['result'].get('processed_data'):
        raise HTTPException(status_code=400, detail="没有可导出的数据")
    
    try:
        # 重建DataFrame
        data_info = job['result']['processed_data']
        df = pd.DataFrame(data_info['data'])
        
        # 导出数据
        file_content = export_processed_data(df, format)
        
        # 设置响应头
        if format == 'csv':
            media_type = 'text/csv'
            filename = f"processed_data_{job_id}.csv"
        elif format == 'xlsx':
            media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f"processed_data_{job_id}.xlsx"
        elif format == 'json':
            media_type = 'application/json'
            filename = f"processed_data_{job_id}.json"
        else:
            raise HTTPException(status_code=400, detail="不支持的导出格式")
        
        return Response(
            content=file_content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出数据失败: {str(e)}")


@app.post("/api/v1/validate-data")
async def validate_data_endpoint(file: UploadFile = File(...)):
    """
    仅验证数据质量，不进行处理
    
    Args:
        file: 上传的文件
        
    Returns:
        Dict: 验证结果
    """
    try:
        # 检查文件格式
        supported_formats = ['.csv', '.xlsx', '.xls', '.json']
        if not any(file.filename.lower().endswith(fmt) for fmt in supported_formats):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式。支持的格式: {', '.join(supported_formats)}"
            )
        
        # 读取文件内容
        content = await file.read()
        
        # 解析文件
        file_like = io.BytesIO(content)
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_like)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_like)
        elif file.filename.endswith('.json'):
            df = pd.read_json(file_like)
        
        # 验证数据
        result = validate_data_only(df)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据验证失败: {str(e)}")


@app.delete("/api/v1/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    删除处理任务
    
    Args:
        job_id: 任务ID
        
    Returns:
        Dict: 删除结果
    """
    if job_id not in PROCESSING_JOBS:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    del PROCESSING_JOBS[job_id]
    
    return {"message": f"任务 {job_id} 已删除"}


@app.get("/api/v1/jobs")
async def list_jobs():
    """
    列出所有处理任务
    
    Returns:
        Dict: 任务列表
    """
    jobs_summary = {}
    for job_id, job_info in PROCESSING_JOBS.items():
        jobs_summary[job_id] = {
            'status': job_info['status'],
            'progress': job_info.get('progress'),
            'current_step': job_info.get('current_step'),
            'created_at': job_info['created_at'].isoformat(),
            'filename': job_info.get('filename'),
            'has_error': job_info.get('error') is not None
        }
    
    return {
        "total_jobs": len(jobs_summary),
        "jobs": jobs_summary
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len(PROCESSING_JOBS)
    }


# 异常处理器
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "接口不存在", "status_code": 404}


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return {"error": "服务器内部错误", "status_code": 500}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
