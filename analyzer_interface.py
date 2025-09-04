"""
DevOps智能体分析器接口定义
定义了所有分析器必须实现的统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import datetime


class TaskType(Enum):
    """任务类型枚举"""
    LOG_ANALYSIS = "log_analysis"
    ALARM_ANALYSIS = "alarm_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    SUMMARY = "summary"


class Priority(Enum):
    """优先级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskData:
    """任务数据结构"""
    task_id: str
    task_type: TaskType
    priority: Priority
    input_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


@dataclass
class AnalysisResult:
    """分析结果数据结构"""
    task_id: str
    analyzer_name: str
    success: bool
    findings: List[Dict[str, Any]]
    confidence: float
    suggestions: List[str]
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AnalyzerInterface(ABC):
    """分析器统一接口"""
    
    @abstractmethod
    def get_name(self) -> str:
        """获取分析器名称"""
        pass
    
    @abstractmethod
    def get_supported_task_types(self) -> List[TaskType]:
        """获取支持的任务类型"""
        pass
    
    @abstractmethod
    async def analyze(self, task_data: TaskData) -> AnalysisResult:
        """执行分析任务"""
        pass
    
    @abstractmethod
    def can_handle_task(self, task_data: TaskData) -> bool:
        """判断是否能处理指定任务"""
        pass
    
    def validate_input(self, task_data: TaskData) -> bool:
        """验证输入数据"""
        return task_data.task_type in self.get_supported_task_types()