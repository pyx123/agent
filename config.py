"""
系统配置文件
"""

import os
from typing import Dict, Any


class Config:
    """系统配置类"""
    
    # LangGraph配置
    LANGGRAPH_CONFIG = {
        'max_iterations': 10,
        'timeout': 300,  # 5分钟超时
    }
    
    # 分析器配置
    ANALYZER_CONFIG = {
        'log_analyzer': {
            'max_log_lines': 10000,
            'error_pattern_file': 'error_patterns.txt',
            'warning_pattern_file': 'warning_patterns.txt'
        },
        'alarm_analyzer': {
            'max_alarms': 1000,
            'temporal_window': 3600,  # 1小时时间窗口
        },
        'summary_agent': {
            'min_confidence_threshold': 0.3,
            'max_suggestions': 10
        }
    }
    
    # 系统配置
    SYSTEM_CONFIG = {
        'max_concurrent_tasks': 5,
        'task_timeout': 120,  # 2分钟任务超时
        'retry_attempts': 3
    }
    
    @classmethod
    def get_config(cls, section: str) -> Dict[str, Any]:
        """获取配置段"""
        config_map = {
            'langgraph': cls.LANGGRAPH_CONFIG,
            'analyzer': cls.ANALYZER_CONFIG,
            'system': cls.SYSTEM_CONFIG
        }
        return config_map.get(section, {})
    
    @classmethod
    def update_config(cls, section: str, key: str, value: Any):
        """更新配置"""
        if section == 'langgraph' and key in cls.LANGGRAPH_CONFIG:
            cls.LANGGRAPH_CONFIG[key] = value
        elif section == 'analyzer' and key in cls.ANALYZER_CONFIG:
            cls.ANALYZER_CONFIG[key] = value
        elif section == 'system' and key in cls.SYSTEM_CONFIG:
            cls.SYSTEM_CONFIG[key] = value