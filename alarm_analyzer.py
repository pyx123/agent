"""
告警分析器实现
负责分析监控系统中的告警信息，找出告警根本原因
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from analyzer_interface import AnalyzerInterface, TaskData, AnalysisResult, TaskType


class AlarmAnalyzer(AnalyzerInterface):
    """告警分析器"""
    
    def __init__(self):
        self.alarm_severity_mapping = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1,
            'warning': 1
        }
        
        self.alarm_categories = {
            'cpu': ['CPU使用率过高', 'CPU负载告警'],
            'memory': ['内存使用率告警', '内存不足'],
            'disk': ['磁盘空间不足', '磁盘IO异常'],
            'network': ['网络连接异常', '网络延迟过高'],
            'service': ['服务不可用', '服务响应异常'],
            'database': ['数据库连接异常', '查询超时']
        }
    
    def get_name(self) -> str:
        return "AlarmAnalyzer"
    
    def get_supported_task_types(self) -> List[TaskType]:
        return [TaskType.ALARM_ANALYSIS]
    
    def can_handle_task(self, task_data: TaskData) -> bool:
        return (task_data.task_type == TaskType.ALARM_ANALYSIS and 
                'alarms' in task_data.input_data)
    
    async def analyze(self, task_data: TaskData) -> AnalysisResult:
        """分析告警数据"""
        try:
            alarms = task_data.input_data.get('alarms', [])
            findings = []
            suggestions = []
            
            # 分析告警严重性
            severity_analysis = self._analyze_alarm_severity(alarms)
            findings.extend(severity_analysis)
            
            # 分析告警模式
            pattern_analysis = self._analyze_alarm_patterns(alarms)
            findings.extend(pattern_analysis)
            
            # 分析告警时间相关性
            temporal_analysis = self._analyze_temporal_patterns(alarms)
            findings.extend(temporal_analysis)
            
            # 分类告警
            categorized_alarms = self._categorize_alarms(alarms)
            findings.extend(categorized_alarms)
            
            # 生成修复建议
            suggestions = self._generate_alarm_suggestions(findings, alarms)
            
            # 计算置信度
            confidence = self._calculate_alarm_confidence(findings, alarms)
            
            return AnalysisResult(
                task_id=task_data.task_id,
                analyzer_name=self.get_name(),
                success=True,
                findings=findings,
                confidence=confidence,
                suggestions=suggestions,
                metadata={
                    'total_alarms_analyzed': len(alarms),
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
    
    def _analyze_alarm_severity(self, alarms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析告警严重性分布"""
        findings = []
        severity_counts = {}
        
        for alarm in alarms:
            severity = alarm.get('severity', 'unknown').lower()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        for severity, count in severity_counts.items():
            if count > 0:
                findings.append({
                    'type': 'severity_analysis',
                    'severity': severity,
                    'count': count,
                    'priority_score': self.alarm_severity_mapping.get(severity, 0)
                })
        
        return findings
    
    def _analyze_alarm_patterns(self, alarms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析告警模式"""
        findings = []
        
        # 分析重复告警
        alarm_messages = {}
        for alarm in alarms:
            message = alarm.get('message', '')
            alarm_messages[message] = alarm_messages.get(message, 0) + 1
        
        for message, count in alarm_messages.items():
            if count > 1:
                findings.append({
                    'type': 'repeated_alarm',
                    'message': message,
                    'occurrence_count': count,
                    'pattern': 'frequent_occurrence'
                })
        
        return findings
    
    def _analyze_temporal_patterns(self, alarms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析告警时间模式"""
        findings = []
        
        if not alarms:
            return findings
        
        # 分析告警时间集中度
        alarm_times = []
        for alarm in alarms:
            timestamp = alarm.get('timestamp')
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        alarm_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        alarm_time = timestamp
                    alarm_times.append(alarm_time)
                except:
                    continue
        
        if len(alarm_times) > 1:
            # 检查告警是否在短时间内集中发生
            alarm_times.sort()
            time_diffs = []
            for i in range(1, len(alarm_times)):
                diff = (alarm_times[i] - alarm_times[i-1]).total_seconds()
                time_diffs.append(diff)
            
            avg_interval = sum(time_diffs) / len(time_diffs) if time_diffs else 0
            
            if avg_interval < 300:  # 5分钟内
                findings.append({
                    'type': 'temporal_pattern',
                    'pattern': 'burst_alarms',
                    'avg_interval_seconds': avg_interval,
                    'description': '告警在短时间内集中发生，可能存在级联故障'
                })
        
        return findings
    
    def _categorize_alarms(self, alarms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对告警进行分类"""
        findings = []
        categorized = {category: [] for category in self.alarm_categories.keys()}
        uncategorized = []
        
        for alarm in alarms:
            message = alarm.get('message', '').lower()
            categorized_flag = False
            
            for category, keywords in self.alarm_categories.items():
                if any(keyword.lower() in message for keyword in keywords):
                    categorized[category].append(alarm)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                uncategorized.append(alarm)
        
        for category, category_alarms in categorized.items():
            if category_alarms:
                findings.append({
                    'type': 'alarm_category',
                    'category': category,
                    'count': len(category_alarms),
                    'alarms': category_alarms
                })
        
        if uncategorized:
            findings.append({
                'type': 'alarm_category',
                'category': 'uncategorized',
                'count': len(uncategorized),
                'alarms': uncategorized
            })
        
        return findings
    
    def _generate_alarm_suggestions(self, findings: List[Dict[str, Any]], alarms: List[Dict[str, Any]]) -> List[str]:
        """生成告警修复建议"""
        suggestions = []
        
        # 基于告警类别生成建议
        for finding in findings:
            if finding.get('type') == 'alarm_category':
                category = finding.get('category')
                count = finding.get('count', 0)
                
                if category == 'cpu' and count > 0:
                    suggestions.append(f"发现 {count} 个CPU相关告警，建议检查CPU使用率和进程负载")
                elif category == 'memory' and count > 0:
                    suggestions.append(f"发现 {count} 个内存相关告警，建议检查内存使用情况和内存泄漏")
                elif category == 'disk' and count > 0:
                    suggestions.append(f"发现 {count} 个磁盘相关告警，建议检查磁盘空间和IO性能")
                elif category == 'network' and count > 0:
                    suggestions.append(f"发现 {count} 个网络相关告警，建议检查网络连接和带宽使用")
                elif category == 'service' and count > 0:
                    suggestions.append(f"发现 {count} 个服务相关告警，建议检查服务状态和依赖关系")
                elif category == 'database' and count > 0:
                    suggestions.append(f"发现 {count} 个数据库相关告警，建议检查数据库连接和查询性能")
        
        # 基于告警模式生成建议
        for finding in findings:
            if finding.get('type') == 'repeated_alarm':
                count = finding.get('occurrence_count', 0)
                if count > 3:
                    suggestions.append(f"检测到重复告警 {count} 次，建议调查根本原因以避免告警风暴")
            
            elif finding.get('type') == 'temporal_pattern':
                if finding.get('pattern') == 'burst_alarms':
                    suggestions.append("检测到告警突发模式，建议检查是否存在级联故障或系统过载")
        
        return suggestions
    
    def _calculate_alarm_confidence(self, findings: List[Dict[str, Any]], alarms: List[Dict[str, Any]]) -> float:
        """计算告警分析置信度"""
        if not findings or not alarms:
            return 0.0
        
        # 基于分类告警的覆盖率计算置信度
        categorized_count = sum(f.get('count', 0) for f in findings if f.get('type') == 'alarm_category' and f.get('category') != 'uncategorized')
        total_alarms = len(alarms)
        
        coverage_ratio = categorized_count / total_alarms if total_alarms > 0 else 0
        base_confidence = 0.5 + (coverage_ratio * 0.4)
        
        # 根据告警严重性调整置信度
        high_severity_findings = len([f for f in findings if f.get('type') == 'alarm_category'])
        if high_severity_findings > 0:
            base_confidence += 0.1
        
        return round(min(base_confidence, 1.0), 2)