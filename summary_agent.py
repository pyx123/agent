"""
总结智能体实现
负责汇总各个分析器的结果，进行根因分析并提供修复建议
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from analyzer_interface import AnalyzerInterface, TaskData, AnalysisResult, TaskType


class SummaryAgent(AnalyzerInterface):
    """总结智能体"""
    
    def get_name(self) -> str:
        return "SummaryAgent"
    
    def get_supported_task_types(self) -> List[TaskType]:
        return [TaskType.SUMMARY, TaskType.ROOT_CAUSE_ANALYSIS]
    
    def can_handle_task(self, task_data: TaskData) -> bool:
        return (task_data.task_type in [TaskType.SUMMARY, TaskType.ROOT_CAUSE_ANALYSIS] and
                'analysis_results' in task_data.input_data)
    
    async def analyze(self, task_data: TaskData) -> AnalysisResult:
        """汇总分析结果并进行根因分析"""
        try:
            analysis_results = task_data.input_data.get('analysis_results', [])
            
            # 汇总所有发现
            all_findings = self._aggregate_findings(analysis_results)
            
            # 进行根因分析
            root_causes = self._perform_root_cause_analysis(all_findings)
            
            # 生成综合修复建议
            suggestions = self._generate_comprehensive_suggestions(all_findings, root_causes)
            
            # 计算总体置信度
            confidence = self._calculate_overall_confidence(analysis_results)
            
            # 生成最终报告
            final_findings = self._generate_final_report(all_findings, root_causes)
            
            return AnalysisResult(
                task_id=task_data.task_id,
                analyzer_name=self.get_name(),
                success=True,
                findings=final_findings,
                confidence=confidence,
                suggestions=suggestions,
                metadata={
                    'analyzers_involved': [result.get('analyzer_name') for result in analysis_results],
                    'total_findings': len(all_findings),
                    'root_causes_identified': len(root_causes),
                    'summary_timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return AnalysisResult(
                task_id=task_data.task_id,
                analyzer_name=self.get_name(),
                success=False,
                findings=[],
                confidence=0.0,
                suggestions=[],
                error_message=str(e)
            )
    
    def _aggregate_findings(self, analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """汇总所有分析器的发现"""
        all_findings = []
        
        for result in analysis_results:
            if result.get('success', False):
                findings = result.get('findings', [])
                analyzer_name = result.get('analyzer_name', 'unknown')
                
                for finding in findings:
                    finding['source_analyzer'] = analyzer_name
                    all_findings.append(finding)
        
        return all_findings
    
    def _perform_root_cause_analysis(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """执行根因分析"""
        root_causes = []
        
        # 分析错误和告警的关联性
        errors = [f for f in findings if f.get('type') == 'error']
        alarms = [f for f in findings if f.get('type') in ['alarm_category', 'repeated_alarm']]
        
        # 查找时间相关的根因
        temporal_correlations = self._find_temporal_correlations(findings)
        root_causes.extend(temporal_correlations)
        
        # 查找资源相关的根因
        resource_issues = self._identify_resource_issues(findings)
        root_causes.extend(resource_issues)
        
        # 查找服务依赖相关的根因
        dependency_issues = self._identify_dependency_issues(findings)
        root_causes.extend(dependency_issues)
        
        return root_causes
    
    def _find_temporal_correlations(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """查找时间相关的关联性"""
        correlations = []
        
        # 检查是否有突发告警模式
        burst_patterns = [f for f in findings if f.get('pattern') == 'burst_alarms']
        if burst_patterns:
            correlations.append({
                'type': 'root_cause',
                'category': 'temporal',
                'description': '检测到告警突发模式，可能存在级联故障',
                'evidence': burst_patterns,
                'confidence': 0.8
            })
        
        return correlations
    
    def _identify_resource_issues(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别资源相关问题"""
        resource_issues = []
        
        # 检查CPU相关问题
        cpu_findings = [f for f in findings if 'cpu' in str(f).lower()]
        if cpu_findings:
            resource_issues.append({
                'type': 'root_cause',
                'category': 'resource',
                'resource_type': 'cpu',
                'description': 'CPU资源出现问题，可能导致系统性能下降',
                'evidence': cpu_findings,
                'confidence': 0.7
            })
        
        # 检查内存相关问题
        memory_findings = [f for f in findings if 'memory' in str(f).lower() or 'out of memory' in str(f).lower()]
        if memory_findings:
            resource_issues.append({
                'type': 'root_cause',
                'category': 'resource',
                'resource_type': 'memory',
                'description': '内存资源不足，可能导致服务异常',
                'evidence': memory_findings,
                'confidence': 0.8
            })
        
        # 检查磁盘相关问题
        disk_findings = [f for f in findings if 'disk' in str(f).lower()]
        if disk_findings:
            resource_issues.append({
                'type': 'root_cause',
                'category': 'resource',
                'resource_type': 'disk',
                'description': '磁盘资源问题，可能影响数据读写性能',
                'evidence': disk_findings,
                'confidence': 0.7
            })
        
        return resource_issues
    
    def _identify_dependency_issues(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别服务依赖问题"""
        dependency_issues = []
        
        # 检查连接相关问题
        connection_findings = [f for f in findings if 'connection' in str(f).lower()]
        if connection_findings:
            dependency_issues.append({
                'type': 'root_cause',
                'category': 'dependency',
                'dependency_type': 'network',
                'description': '网络连接问题，可能影响服务间通信',
                'evidence': connection_findings,
                'confidence': 0.8
            })
        
        # 检查数据库相关问题
        db_findings = [f for f in findings if 'database' in str(f).lower() or 'query' in str(f).lower()]
        if db_findings:
            dependency_issues.append({
                'type': 'root_cause',
                'category': 'dependency',
                'dependency_type': 'database',
                'description': '数据库相关问题，可能影响数据访问',
                'evidence': db_findings,
                'confidence': 0.7
            })
        
        return dependency_issues
    
    def _generate_comprehensive_suggestions(self, findings: List[Dict[str, Any]], root_causes: List[Dict[str, Any]]) -> List[str]:
        """生成综合修复建议"""
        suggestions = []
        
        # 基于根因生成建议
        for root_cause in root_causes:
            category = root_cause.get('category')
            confidence = root_cause.get('confidence', 0)
            
            if category == 'resource':
                resource_type = root_cause.get('resource_type')
                if resource_type == 'cpu':
                    suggestions.append("【高优先级】CPU资源不足，建议：1) 检查高CPU进程 2) 考虑扩容或优化算法")
                elif resource_type == 'memory':
                    suggestions.append("【高优先级】内存资源不足，建议：1) 检查内存泄漏 2) 增加内存或优化内存使用")
                elif resource_type == 'disk':
                    suggestions.append("【中优先级】磁盘资源问题，建议：1) 清理磁盘空间 2) 优化IO操作")
            
            elif category == 'dependency':
                dependency_type = root_cause.get('dependency_type')
                if dependency_type == 'network':
                    suggestions.append("【高优先级】网络连接问题，建议：1) 检查网络配置 2) 验证服务可达性")
                elif dependency_type == 'database':
                    suggestions.append("【高优先级】数据库问题，建议：1) 检查数据库连接 2) 优化查询性能")
            
            elif category == 'temporal':
                suggestions.append("【中优先级】检测到时间相关模式，建议：1) 检查系统负载 2) 分析级联故障原因")
        
        # 基于发现的问题严重性排序建议
        high_severity_count = len([f for f in findings if f.get('severity') == 'high'])
        if high_severity_count > 0:
            suggestions.insert(0, f"【紧急】发现 {high_severity_count} 个高严重性问题，建议立即处理")
        
        return suggestions
    
    def _calculate_overall_confidence(self, analysis_results: List[Dict[str, Any]]) -> float:
        """计算总体置信度"""
        if not analysis_results:
            return 0.0
        
        successful_results = [r for r in analysis_results if r.get('success', False)]
        if not successful_results:
            return 0.0
        
        # 计算平均置信度
        confidences = [r.get('confidence', 0) for r in successful_results]
        avg_confidence = sum(confidences) / len(confidences)
        
        # 根据成功分析器数量调整置信度
        success_ratio = len(successful_results) / len(analysis_results)
        adjusted_confidence = avg_confidence * success_ratio
        
        return round(adjusted_confidence, 2)
    
    def _generate_final_report(self, findings: List[Dict[str, Any]], root_causes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成最终报告"""
        final_findings = []
        
        # 添加汇总信息
        summary = {
            'type': 'summary',
            'total_findings': len(findings),
            'error_count': len([f for f in findings if f.get('type') == 'error']),
            'warning_count': len([f for f in findings if f.get('type') == 'warning']),
            'alarm_count': len([f for f in findings if 'alarm' in f.get('type', '')]),
            'root_causes_count': len(root_causes)
        }
        final_findings.append(summary)
        
        # 添加根因分析
        final_findings.extend(root_causes)
        
        # 添加关键发现（高优先级）
        critical_findings = [f for f in findings if f.get('severity') in ['high', 'critical']]
        if critical_findings:
            final_findings.append({
                'type': 'critical_findings',
                'count': len(critical_findings),
                'findings': critical_findings
            })
        
        return final_findings