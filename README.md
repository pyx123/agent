# DevOps 智能体系统

基于 LangGraph 的 DevOps 智能体，能够自动化处理故障排查、根因分析和修复建议生成。

## 功能特性

- 🔍 **智能日志分析**: 自动识别日志中的错误、警告和性能问题
- 🚨 **告警分析**: 分析监控告警，识别告警模式和根本原因
- 🧠 **根因分析**: 汇总多源数据，进行智能根因分析
- 📊 **自动报告生成**: 生成详细的故障分析报告和修复建议
- 🔄 **动态任务调度**: 根据分析结果动态调整任务执行策略
- 🧩 **插件化架构**: 支持自定义分析器的动态加载和扩展

## 系统架构

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Planner   │────│Log Analyser  │────│  Summary Agent  │
│  (规划器)    │    │ (日志分析器)   │    │   (总结智能体)   │
└─────────────┘    └──────────────┘    └─────────────────┘
       │                    │                     │
       └────────────────────┼─────────────────────┘
                           │
                  ┌──────────────┐
                  │Alarm Analyser│
                  │ (告警分析器)   │
                  └──────────────┘
```

## 项目结构

```
devops-agent/
├── analyzer_interface.py      # 分析器统一接口定义
├── log_analyzer.py           # 日志分析器实现
├── alarm_analyzer.py         # 告警分析器实现
├── summary_agent.py          # 总结智能体实现
├── analyzer_selector.py     # 分析器选择器
├── task_reallocator.py      # 任务重调度器
├── planner.py               # 核心规划器
├── devops_agent.py          # 主应用程序
├── config.py                # 系统配置
├── example_usage.py         # 使用示例
├── requirements.txt         # 项目依赖
└── README.md               # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行示例

```bash
python example_usage.py
```

### 3. 自定义使用

```python
from devops_agent import DevOpsAgent

# 创建智能体实例
agent = DevOpsAgent()

# 准备故障数据
incident_data = {
    'incident_id': 'your-incident-id',
    'description': '故障描述',
    'logs': ['日志行1', '日志行2', ...],
    'alarms': [{'id': '告警ID', 'severity': '严重性', ...}]
}

# 分析故障
result = await agent.analyze_incident(incident_data)
print(result)
```

## 核心模块说明

### Planner (规划器)
- 系统核心调度模块
- 负责解析输入、创建任务计划
- 协调各个分析器的工作
- 生成最终分析报告

### Log Analyzer (日志分析器)
- 分析系统和应用日志
- 识别错误、警告和性能问题
- 支持自定义错误模式匹配
- 提供基于模式的修复建议

### Alarm Analyzer (告警分析器)
- 分析监控系统告警
- 识别告警模式和时间相关性
- 对告警进行智能分类
- 提供告警根因分析

### Summary Agent (总结智能体)
- 汇总各分析器结果
- 执行跨模块根因分析
- 生成综合修复建议
- 计算总体分析置信度

### Analyzer Selector (分析器选择器)
- 动态选择合适的分析器
- 支持分析器的注册和注销
- 验证分析器兼容性
- 支持插件化扩展

### Task Reallocator (任务重调度器)
- 根据分析结果动态调整任务
- 记录分析器性能指标
- 支持自定义重调度规则
- 提供任务执行历史

## 扩展开发

### 添加自定义分析器

1. 继承 `AnalyzerInterface` 接口
2. 实现所有抽象方法
3. 在 `AnalyzerSelector` 中注册新分析器

```python
from analyzer_interface import AnalyzerInterface, TaskData, AnalysisResult

class CustomAnalyzer(AnalyzerInterface):
    def get_name(self) -> str:
        return "CustomAnalyzer"
    
    def get_supported_task_types(self) -> List[TaskType]:
        return [TaskType.CUSTOM_ANALYSIS]
    
    async def analyze(self, task_data: TaskData) -> AnalysisResult:
        # 实现自定义分析逻辑
        pass
    
    def can_handle_task(self, task_data: TaskData) -> bool:
        # 实现任务处理能力检查
        pass
```

## 配置说明

系统配置在 `config.py` 中定义，包括：

- **LangGraph配置**: 工作流执行参数
- **分析器配置**: 各个分析器的特定参数
- **系统配置**: 并发、超时等系统级参数

## API 使用示例

### 基本故障分析

```python
import asyncio
from devops_agent import DevOpsAgent

async def analyze_incident():
    agent = DevOpsAgent()
    
    incident_data = {
        'incident_id': 'INC-001',
        'description': '服务响应异常',
        'logs': [
            '2024-01-15 10:30:01 ERROR: Database connection failed',
            '2024-01-15 10:30:02 WARNING: High memory usage: 90%'
        ],
        'alarms': [
            {
                'id': 'ALM-001',
                'severity': 'critical',
                'message': '服务不可用',
                'timestamp': '2024-01-15T10:30:00Z'
            }
        ]
    }
    
    result = await agent.analyze_incident(incident_data)
    return result

# 运行分析
result = asyncio.run(analyze_incident())
print(f"分析结果: {result}")
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目仓库: [https://github.com/pyx123/agent](https://github.com/pyx123/agent)
- Issues: [https://github.com/pyx123/agent/issues](https://github.com/pyx123/agent/issues)

## 更新日志

### v1.0.0
- 初始版本发布
- 实现基础的日志和告警分析功能
- 支持 LangGraph 工作流
- 提供完整的根因分析和修复建议