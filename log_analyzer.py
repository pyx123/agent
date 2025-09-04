"""
日志分析器实现
负责分析系统日志、应用日志等，识别异常和故障
"""

import re
import json
from typing import Dict, Any, List
from datetime import datetime
from analyzer_interface import AnalyzerInterface, TaskData, AnalysisResult, TaskType, Priority


class LogAnalyzer(AnalyzerInterface):
    """日志分析器"""
    
    def __init__(self):
        self.error_patterns = [
            r'ERROR',
            r'FATAL',
            r'Exception',
            r'Failed',
            r'Timeout',
            r'Connection refused',
            r'Out of memory',
            r'Stack overflow'
        ]
        
        self.warning_patterns = [
            r'WARNING',
            r'WARN',
            r'Deprecated',
            r'Slow query',
            r'High CPU',
            r'Memory usage'
        ]
    
    def get_name(self) -> str:
        return "LogAnalyzer"
    
    def get_supported_task_types(self) -> List[TaskType]:
        return [TaskType.LOG_ANALYSIS]
    
    def can_handle_task(self, task_data: TaskData) -> bool:
        return (task_data.task_type == TaskType.LOG_ANALYSIS and 
                'logs' in task_data.input_data)
    
    async def analyze(self, task_data: TaskData) -> AnalysisResult:
        """分析日志数据"""
        try:
            logs = task_data.input_data.get('logs', [])
            findings = []
            suggestions = []
            
            # 分析错误日志
            error_findings = self._analyze_errors(logs)
            findings.extend(error_findings)
            
            # 分析警告日志
            warning_findings = self._analyze_warnings(logs)
            findings.extend(warning_findings)
            
            # 分析性能问题
            performance_findings = self._analyze_performance(logs)
            findings.extend(performance_findings)
            
            # 生成修复建议
            suggestions = self._generate_suggestions(findings)
            
            # 计算置信度
            confidence = self._calculate_confidence(findings)
            
            return AnalysisResult(
                task_id=task_data.task_id,
                analyzer_name=self.get_name(),
                success=True,
                findings=findings,
                confidence=confidence,
                suggestions=suggestions,
                metadata={
                    'total_logs_analyzed': len(logs),
                    'analysis_timestamp': datetime.now().isoformat()
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
    
    def _analyze_errors(self, logs: List[str]) -> List[Dict[str, Any]]:
        """分析错误日志"""
        findings = []
        
        for i, log in enumerate(logs):
            for pattern in self.error_patterns:
                if re.search(pattern, log, re.IGNORECASE):
                    findings.append({
                        'type': 'error',
                        'pattern': pattern,
                        'log_line': i + 1,
                        'content': log.strip(),
                        'severity': 'high'
                    })
        
        return findings
    
    def _analyze_warnings(self, logs: List[str]) -> List[Dict[str, Any]]:
        """分析警告日志"""
        findings = []
        
        for i, log in enumerate(logs):
            for pattern in self.warning_patterns:
                if re.search(pattern, log, re.IGNORECASE):
                    findings.append({
                        'type': 'warning',
                        'pattern': pattern,
                        'log_line': i + 1,
                        'content': log.strip(),
                        'severity': 'medium'
                    })
        
        return findings
    
    def _analyze_performance(self, logs: List[str]) -> List[Dict[str, Any]]:
        """分析性能相关日志"""
        findings = []
        
        performance_patterns = [
            r'slow.*query',
            r'high.*cpu',
            r'memory.*usage',
            r'response.*time.*\d+ms',
            r'timeout'
        ]
        
        for i, log in enumerate(logs):
            for pattern in performance_patterns:
                if re.search(pattern, log, re.IGNORECASE):
                    findings.append({
                        'type': 'performance',
                        'pattern': pattern,
                        'log_line': i + 1,
                        'content': log.strip(),
                        'severity': 'medium'
                    })
        
        return findings
    
    def _generate_suggestions(self, findings: List[Dict[str, Any]]) -> List[str]:
        """基于发现的问题生成修复建议"""
        suggestions = []
        
        error_count = len([f for f in findings if f['type'] == 'error'])
        warning_count = len([f for f in findings if f['type'] == 'warning'])
        performance_count = len([f for f in findings if f['type'] == 'performance'])
        
        if error_count > 0:
            suggestions.append(f"发现 {error_count} 个错误，建议优先处理错误日志中的异常")
        
        if warning_count > 5:
            suggestions.append(f"发现 {warning_count} 个警告，建议检查系统配置和资源使用情况")
        
        if performance_count > 0:
            suggestions.append(f"发现 {performance_count} 个性能问题，建议优化查询和资源配置")
        
        # 具体模式建议
        patterns_found = [f['pattern'] for f in findings]
        if 'Connection refused' in str(patterns_found):
            suggestions.append("检测到连接拒绝错误，建议检查服务状态和网络连接")
        
        if 'Out of memory' in str(patterns_found):
            suggestions.append("检测到内存不足，建议增加内存或优化内存使用")
        
        if 'Timeout' in str(patterns_found):
            suggestions.append("检测到超时错误，建议检查网络延迟和服务响应时间")
        
        return suggestions
    
    def _calculate_confidence(self, findings: List[Dict[str, Any]]) -> float:
        """计算分析置信度"""
        if not findings:
            return 0.0
        
        # 根据发现的问题数量和严重程度计算置信度
        high_severity_count = len([f for f in findings if f.get('severity') == 'high'])
        medium_severity_count = len([f for f in findings if f.get('severity') == 'medium'])
        
        base_confidence = min(0.9, 0.3 + (high_severity_count * 0.2) + (medium_severity_count * 0.1))
        
        return round(base_confidence, 2)