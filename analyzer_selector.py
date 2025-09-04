"""
分析器选择器实现
根据任务类型动态选择合适的分析器，支持插件式扩展
"""

from typing import Dict, Any, List, Optional, Type
from analyzer_interface import AnalyzerInterface, TaskData, TaskType
from log_analyzer import LogAnalyzer
from alarm_analyzer import AlarmAnalyzer


class AnalyzerSelector:
    """分析器选择器"""
    
    def __init__(self):
        self.analyzers: Dict[str, AnalyzerInterface] = {}
        self.task_type_mapping: Dict[TaskType, List[str]] = {}
        self._initialize_default_analyzers()
    
    def _initialize_default_analyzers(self):
        """初始化默认分析器"""
        # 注册默认分析器
        self.register_analyzer(LogAnalyzer())
        self.register_analyzer(AlarmAnalyzer())
    
    def register_analyzer(self, analyzer: AnalyzerInterface):
        """注册分析器"""
        name = analyzer.get_name()
        self.analyzers[name] = analyzer
        
        # 更新任务类型映射
        for task_type in analyzer.get_supported_task_types():
            if task_type not in self.task_type_mapping:
                self.task_type_mapping[task_type] = []
            if name not in self.task_type_mapping[task_type]:
                self.task_type_mapping[task_type].append(name)
    
    def unregister_analyzer(self, analyzer_name: str):
        """注销分析器"""
        if analyzer_name in self.analyzers:
            analyzer = self.analyzers[analyzer_name]
            del self.analyzers[analyzer_name]
            
            # 更新任务类型映射
            for task_type in analyzer.get_supported_task_types():
                if task_type in self.task_type_mapping:
                    if analyzer_name in self.task_type_mapping[task_type]:
                        self.task_type_mapping[task_type].remove(analyzer_name)
    
    def select_analyzers(self, task_data: TaskData) -> List[AnalyzerInterface]:
        """根据任务数据选择合适的分析器"""
        suitable_analyzers = []
        
        # 根据任务类型查找分析器
        task_type = task_data.task_type
        if task_type in self.task_type_mapping:
            analyzer_names = self.task_type_mapping[task_type]
            
            for name in analyzer_names:
                analyzer = self.analyzers.get(name)
                if analyzer and analyzer.can_handle_task(task_data):
                    suitable_analyzers.append(analyzer)
        
        return suitable_analyzers
    
    def get_analyzer_by_name(self, name: str) -> Optional[AnalyzerInterface]:
        """根据名称获取分析器"""
        return self.analyzers.get(name)
    
    def get_all_analyzers(self) -> List[AnalyzerInterface]:
        """获取所有注册的分析器"""
        return list(self.analyzers.values())
    
    def get_supported_task_types(self) -> List[TaskType]:
        """获取所有支持的任务类型"""
        return list(self.task_type_mapping.keys())
    
    def validate_analyzer_compatibility(self, analyzer: AnalyzerInterface) -> bool:
        """验证分析器兼容性"""
        try:
            # 检查必要方法是否实现
            required_methods = ['get_name', 'get_supported_task_types', 'analyze', 'can_handle_task']
            for method in required_methods:
                if not hasattr(analyzer, method):
                    return False
            
            # 检查任务类型是否有效
            supported_types = analyzer.get_supported_task_types()
            for task_type in supported_types:
                if not isinstance(task_type, TaskType):
                    return False
            
            return True
        except Exception:
            return False