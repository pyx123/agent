"""
任务重调度器实现
根据实时反馈动态调整任务执行的分析器
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from analyzer_interface import TaskData, AnalysisResult, TaskType, Priority
from analyzer_selector import AnalyzerSelector


class TaskReallocator:
    """任务重调度器"""
    
    def __init__(self, analyzer_selector: AnalyzerSelector):
        self.analyzer_selector = analyzer_selector
        self.task_history: Dict[str, List[AnalysisResult]] = {}
        self.performance_metrics: Dict[str, Dict[str, Any]] = {}
        self.reallocation_rules: List[Dict[str, Any]] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """初始化默认重调度规则"""
        self.reallocation_rules = [
            {
                'condition': 'low_confidence',
                'threshold': 0.3,
                'action': 'retry_with_different_analyzer',
                'description': '置信度过低时尝试其他分析器'
            },
            {
                'condition': 'analysis_failure',
                'threshold': 1,
                'action': 'fallback_analyzer',
                'description': '分析失败时使用备用分析器'
            },
            {
                'condition': 'high_error_rate',
                'threshold': 0.5,
                'action': 'escalate_priority',
                'description': '错误率过高时提升任务优先级'
            }
        ]
    
    async def reallocate_task(self, task_data: TaskData, previous_result: Optional[AnalysisResult] = None) -> TaskData:
        """重新分配任务"""
        # 记录任务历史
        if previous_result:
            self._record_task_result(task_data.task_id, previous_result)
        
        # 分析是否需要重调度
        reallocation_needed, reason = self._should_reallocate(task_data, previous_result)
        
        if reallocation_needed:
            return self._perform_reallocation(task_data, reason)
        
        return task_data
    
    def _should_reallocate(self, task_data: TaskData, previous_result: Optional[AnalysisResult]) -> tuple[bool, str]:
        """判断是否需要重调度"""
        if not previous_result:
            return False, ""
        
        # 检查分析是否失败
        if not previous_result.success:
            return True, "analysis_failure"
        
        # 检查置信度是否过低
        if previous_result.confidence < 0.3:
            return True, "low_confidence"
        
        # 检查是否有足够的发现
        if len(previous_result.findings) == 0:
            return True, "insufficient_findings"
        
        return False, ""
    
    def _perform_reallocation(self, task_data: TaskData, reason: str) -> TaskData:
        """执行任务重分配"""
        new_task_data = TaskData(
            task_id=f"{task_data.task_id}_reallocated",
            task_type=task_data.task_type,
            priority=task_data.priority,
            input_data=task_data.input_data.copy(),
            metadata={
                'original_task_id': task_data.task_id,
                'reallocation_reason': reason,
                'reallocation_timestamp': datetime.now().isoformat()
            }
        )
        
        # 根据重调度原因调整任务
        if reason == "analysis_failure":
            # 尝试使用备用分析器
            new_task_data.metadata['use_fallback_analyzer'] = True
        
        elif reason == "low_confidence":
            # 提升任务优先级，使用更全面的分析
            if new_task_data.priority != Priority.CRITICAL:
                new_task_data.priority = Priority(min(new_task_data.priority.value + 1, 4))
            new_task_data.metadata['enhanced_analysis'] = True
        
        elif reason == "insufficient_findings":
            # 扩大分析范围
            new_task_data.metadata['expand_analysis_scope'] = True
        
        return new_task_data
    
    def _record_task_result(self, task_id: str, result: AnalysisResult):
        """记录任务结果"""
        if task_id not in self.task_history:
            self.task_history[task_id] = []
        
        self.task_history[task_id].append(result)
        
        # 更新性能指标
        analyzer_name = result.analyzer_name
        if analyzer_name not in self.performance_metrics:
            self.performance_metrics[analyzer_name] = {
                'total_tasks': 0,
                'successful_tasks': 0,
                'average_confidence': 0.0,
                'last_updated': datetime.now()
            }
        
        metrics = self.performance_metrics[analyzer_name]
        metrics['total_tasks'] += 1
        if result.success:
            metrics['successful_tasks'] += 1
        
        # 更新平均置信度
        success_rate = metrics['successful_tasks'] / metrics['total_tasks']
        metrics['success_rate'] = round(success_rate, 2)
        metrics['last_updated'] = datetime.now()
    
    def get_analyzer_performance(self, analyzer_name: str) -> Optional[Dict[str, Any]]:
        """获取分析器性能指标"""
        return self.performance_metrics.get(analyzer_name)
    
    def get_task_history(self, task_id: str) -> List[AnalysisResult]:
        """获取任务历史"""
        return self.task_history.get(task_id, [])
    
    def add_reallocation_rule(self, rule: Dict[str, Any]):
        """添加重调度规则"""
        required_fields = ['condition', 'threshold', 'action', 'description']
        if all(field in rule for field in required_fields):
            self.reallocation_rules.append(rule)
        else:
            raise ValueError("重调度规则必须包含所有必需字段")
    
    def remove_reallocation_rule(self, condition: str):
        """移除重调度规则"""
        self.reallocation_rules = [r for r in self.reallocation_rules if r['condition'] != condition]