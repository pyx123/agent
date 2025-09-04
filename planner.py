"""
规划器实现
系统核心模块，负责任务调度、协调各个分析模块的工作
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from analyzer_interface import TaskData, AnalysisResult, TaskType, Priority
from analyzer_selector import AnalyzerSelector
from task_reallocator import TaskReallocator
from summary_agent import SummaryAgent


class Planner:
    """DevOps智能体规划器"""
    
    def __init__(self):
        self.analyzer_selector = AnalyzerSelector()
        self.task_reallocator = TaskReallocator(self.analyzer_selector)
        self.summary_agent = SummaryAgent()
        self.task_queue: List[TaskData] = []
        self.completed_tasks: Dict[str, AnalysisResult] = {}
        self.active_tasks: Dict[str, TaskData] = {}
    
    async def process_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理故障事件的主入口"""
        try:
            # 解析输入并生成任务计划
            tasks = self._create_analysis_plan(incident_data)
            
            # 执行分析任务
            analysis_results = await self._execute_analysis_tasks(tasks)
            
            # 生成总结报告
            summary_result = await self._generate_summary_report(analysis_results)
            
            # 生成最终报告
            final_report = self._create_final_report(incident_data, analysis_results, summary_result)
            
            return final_report
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_analysis_plan(self, incident_data: Dict[str, Any]) -> List[TaskData]:
        """根据输入数据创建分析计划"""
        tasks = []
        
        # 分析输入数据类型，创建相应的任务
        if 'logs' in incident_data:
            log_task = TaskData(
                task_id=str(uuid.uuid4()),
                task_type=TaskType.LOG_ANALYSIS,
                priority=Priority.HIGH,
                input_data={'logs': incident_data['logs']},
                timestamp=datetime.now().isoformat()
            )
            tasks.append(log_task)
        
        if 'alarms' in incident_data:
            alarm_task = TaskData(
                task_id=str(uuid.uuid4()),
                task_type=TaskType.ALARM_ANALYSIS,
                priority=Priority.HIGH,
                input_data={'alarms': incident_data['alarms']},
                timestamp=datetime.now().isoformat()
            )
            tasks.append(alarm_task)
        
        # 根据优先级排序任务
        tasks.sort(key=lambda x: x.priority.value, reverse=True)
        
        return tasks
    
    async def _execute_analysis_tasks(self, tasks: List[TaskData]) -> List[AnalysisResult]:
        """执行分析任务"""
        results = []
        
        for task in tasks:
            # 选择合适的分析器
            analyzers = self.analyzer_selector.select_analyzers(task)
            
            if not analyzers:
                # 没有合适的分析器
                result = AnalysisResult(
                    task_id=task.task_id,
                    analyzer_name="none",
                    success=False,
                    findings=[],
                    confidence=0.0,
                    suggestions=[],
                    error_message="没有找到合适的分析器"
                )
                results.append(result)
                continue
            
            # 使用第一个合适的分析器执行任务
            analyzer = analyzers[0]
            self.active_tasks[task.task_id] = task
            
            try:
                result = await analyzer.analyze(task)
                
                # 检查是否需要重调度
                if not result.success or result.confidence < 0.3:
                    reallocated_task = await self.task_reallocator.reallocate_task(task, result)
                    if reallocated_task.task_id != task.task_id:
                        # 重新执行任务
                        new_analyzers = self.analyzer_selector.select_analyzers(reallocated_task)
                        if new_analyzers:
                            result = await new_analyzers[0].analyze(reallocated_task)
                
                results.append(result)
                self.completed_tasks[task.task_id] = result
                
            except Exception as e:
                error_result = AnalysisResult(
                    task_id=task.task_id,
                    analyzer_name=analyzer.get_name(),
                    success=False,
                    findings=[],
                    confidence=0.0,
                    suggestions=[],
                    error_message=str(e)
                )
                results.append(error_result)
            
            finally:
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]
        
        return results
    
    async def _generate_summary_report(self, analysis_results: List[AnalysisResult]) -> AnalysisResult:
        """生成总结报告"""
        summary_task = TaskData(
            task_id=str(uuid.uuid4()),
            task_type=TaskType.SUMMARY,
            priority=Priority.CRITICAL,
            input_data={
                'analysis_results': [
                    {
                        'task_id': r.task_id,
                        'analyzer_name': r.analyzer_name,
                        'success': r.success,
                        'findings': r.findings,
                        'confidence': r.confidence,
                        'suggestions': r.suggestions,
                        'error_message': r.error_message
                    }
                    for r in analysis_results
                ]
            },
            timestamp=datetime.now().isoformat()
        )
        
        return await self.summary_agent.analyze(summary_task)
    
    def _create_final_report(self, incident_data: Dict[str, Any], 
                           analysis_results: List[AnalysisResult], 
                           summary_result: AnalysisResult) -> Dict[str, Any]:
        """创建最终报告"""
        return {
            'success': True,
            'incident_id': incident_data.get('incident_id', str(uuid.uuid4())),
            'analysis_timestamp': datetime.now().isoformat(),
            'input_summary': {
                'logs_provided': 'logs' in incident_data,
                'alarms_provided': 'alarms' in incident_data,
                'incident_description': incident_data.get('description', '')
            },
            'analysis_results': [
                {
                    'analyzer': result.analyzer_name,
                    'success': result.success,
                    'confidence': result.confidence,
                    'findings_count': len(result.findings),
                    'suggestions_count': len(result.suggestions)
                }
                for result in analysis_results
            ],
            'summary': {
                'success': summary_result.success,
                'confidence': summary_result.confidence,
                'findings': summary_result.findings,
                'suggestions': summary_result.suggestions
            },
            'recommendations': {
                'immediate_actions': self._extract_immediate_actions(summary_result),
                'follow_up_actions': self._extract_follow_up_actions(summary_result),
                'preventive_measures': self._extract_preventive_measures(summary_result)
            }
        }
    
    def _extract_immediate_actions(self, summary_result: AnalysisResult) -> List[str]:
        """提取立即行动建议"""
        immediate_actions = []
        
        for suggestion in summary_result.suggestions:
            if '【紧急】' in suggestion or '【高优先级】' in suggestion:
                immediate_actions.append(suggestion)
        
        return immediate_actions
    
    def _extract_follow_up_actions(self, summary_result: AnalysisResult) -> List[str]:
        """提取后续行动建议"""
        follow_up_actions = []
        
        for suggestion in summary_result.suggestions:
            if '【中优先级】' in suggestion:
                follow_up_actions.append(suggestion)
        
        return follow_up_actions
    
    def _extract_preventive_measures(self, summary_result: AnalysisResult) -> List[str]:
        """提取预防措施建议"""
        preventive_measures = [
            "建立完善的监控体系，及时发现潜在问题",
            "定期进行系统健康检查和性能调优",
            "建立故障处理流程和应急预案",
            "加强日志管理和告警规则优化"
        ]
        
        # 根据发现的问题类型添加特定预防措施
        for finding in summary_result.findings:
            if finding.get('type') == 'root_cause':
                category = finding.get('category')
                if category == 'resource':
                    preventive_measures.append("建立资源使用监控和自动扩容机制")
                elif category == 'dependency':
                    preventive_measures.append("加强服务依赖管理和故障隔离机制")
        
        return list(set(preventive_measures))  # 去重
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        if task_id in self.active_tasks:
            return {
                'status': 'active',
                'task': self.active_tasks[task_id]
            }
        elif task_id in self.completed_tasks:
            return {
                'status': 'completed',
                'result': self.completed_tasks[task_id]
            }
        else:
            return {
                'status': 'not_found'
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'active_tasks_count': len(self.active_tasks),
            'completed_tasks_count': len(self.completed_tasks),
            'registered_analyzers': [analyzer.get_name() for analyzer in self.analyzer_selector.get_all_analyzers()],
            'supported_task_types': [task_type.value for task_type in self.analyzer_selector.get_supported_task_types()]
        }