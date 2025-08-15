#!/usr/bin/env python3
"""
Railway部署启动脚本
同时启动后端FastAPI和前端Streamlit服务
"""

import os
import sys
import time
import signal
import threading
import subprocess
import logging
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/services.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.running = True
        
        # 注册信号处理器
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理关闭信号"""
        logger.info(f"收到信号 {signum}，正在关闭服务...")
        self.shutdown()
    
    def start_backend(self):
        """启动后端服务"""
        try:
            backend_port = os.getenv('BACKEND_PORT', '8000')
            cmd = [
                'uvicorn', 
                'backend.api:app',
                '--host', '0.0.0.0',
                '--port', backend_port,
                '--reload' if os.getenv('RAILWAY_ENVIRONMENT') != 'production' else '--no-reload'
            ]
            
            logger.info(f"启动后端服务: {' '.join(cmd)}")
            self.backend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 监控后端日志
            def log_backend():
                for line in iter(self.backend_process.stdout.readline, ''):
                    if line.strip():
                        logger.info(f"[Backend] {line.strip()}")
            
            threading.Thread(target=log_backend, daemon=True).start()
            logger.info(f"后端服务已启动，PID: {self.backend_process.pid}")
            
        except Exception as e:
            logger.error(f"启动后端服务失败: {e}")
            raise
    
    def start_frontend(self):
        """启动前端服务"""
        try:
            # 等待后端启动
            time.sleep(3)
            
            frontend_port = os.getenv('FRONTEND_PORT', '8501')
            base_url = os.getenv('BASE_URL', 'http://localhost:8000')
            
            # 设置Streamlit配置
            os.environ['STREAMLIT_SERVER_PORT'] = frontend_port
            os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
            os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
            os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
            os.environ['BACKEND_API_URL'] = f"{base_url}/api/v1"
            
            cmd = [
                'streamlit', 'run', 'frontend/app.py',
                '--server.port', frontend_port,
                '--server.address', '0.0.0.0',
                '--server.headless', 'true',
                '--browser.gatherUsageStats', 'false'
            ]
            
            logger.info(f"启动前端服务: {' '.join(cmd)}")
            self.frontend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 监控前端日志
            def log_frontend():
                for line in iter(self.frontend_process.stdout.readline, ''):
                    if line.strip():
                        logger.info(f"[Frontend] {line.strip()}")
            
            threading.Thread(target=log_frontend, daemon=True).start()
            logger.info(f"前端服务已启动，PID: {self.frontend_process.pid}")
            
        except Exception as e:
            logger.error(f"启动前端服务失败: {e}")
            raise
    
    def check_health(self):
        """检查服务健康状态"""
        backend_healthy = (
            self.backend_process and 
            self.backend_process.poll() is None
        )
        frontend_healthy = (
            self.frontend_process and 
            self.frontend_process.poll() is None
        )
        
        return backend_healthy and frontend_healthy
    
    def restart_service(self, service_name: str):
        """重启指定服务"""
        logger.warning(f"重启服务: {service_name}")
        
        if service_name == 'backend':
            if self.backend_process:
                self.backend_process.terminate()
                time.sleep(2)
            self.start_backend()
        elif service_name == 'frontend':
            if self.frontend_process:
                self.frontend_process.terminate()
                time.sleep(2)
            self.start_frontend()
    
    def monitor_services(self):
        """监控服务状态"""
        logger.info("开始监控服务状态...")
        
        while self.running:
            try:
                # 检查后端
                if self.backend_process and self.backend_process.poll() is not None:
                    logger.error("后端服务异常退出，正在重启...")
                    self.restart_service('backend')
                
                # 检查前端
                if self.frontend_process and self.frontend_process.poll() is not None:
                    logger.error("前端服务异常退出，正在重启...")
                    self.restart_service('frontend')
                
                time.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                logger.error(f"监控服务时发生错误: {e}")
                time.sleep(10)
    
    def run(self):
        """运行所有服务"""
        try:
            logger.info("=== 启动数据处理Agent服务 ===")
            logger.info(f"环境: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
            logger.info(f"基础URL: {os.getenv('BASE_URL', 'http://localhost:8000')}")
            
            # 启动后端
            self.start_backend()
            
            # 启动前端
            self.start_frontend()
            
            # 启动监控
            monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
            monitor_thread.start()
            
            logger.info("=== 所有服务已启动 ===")
            logger.info(f"后端API: http://0.0.0.0:{os.getenv('BACKEND_PORT', '8000')}")
            logger.info(f"前端界面: http://0.0.0.0:{os.getenv('FRONTEND_PORT', '8501')}")
            
            # 主循环
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("收到中断信号...")
        except Exception as e:
            logger.error(f"服务运行错误: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """关闭所有服务"""
        logger.info("正在关闭服务...")
        self.running = False
        
        # 关闭前端
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=10)
                logger.info("前端服务已关闭")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                logger.warning("强制关闭前端服务")
            except Exception as e:
                logger.error(f"关闭前端服务失败: {e}")
        
        # 关闭后端
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=10)
                logger.info("后端服务已关闭")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                logger.warning("强制关闭后端服务")
            except Exception as e:
                logger.error(f"关闭后端服务失败: {e}")
        
        logger.info("所有服务已关闭")

def main():
    """主函数"""
    # 确保必要的目录存在
    os.makedirs('logs', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    # 启动服务管理器
    manager = ServiceManager()
    manager.run()

if __name__ == "__main__":
    main()
