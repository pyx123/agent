"""
DevOps智能体使用示例
展示如何使用系统进行故障分析
"""

import asyncio
from devops_agent import DevOpsAgent


async def main():
    """主函数示例"""
    # 创建DevOps智能体实例
    agent = DevOpsAgent()
    
    # 示例故障数据
    incident_data = {
        'incident_id': 'INC-2024-001',
        'description': '应用服务响应缓慢，部分用户无法访问',
        'logs': [
            '2024-01-15 10:30:01 ERROR: Connection timeout to database server',
            '2024-01-15 10:30:02 WARNING: High CPU usage detected: 95%',
            '2024-01-15 10:30:05 ERROR: Out of memory exception in service worker',
            '2024-01-15 10:30:10 FATAL: Service unavailable - too many connections',
            '2024-01-15 10:30:15 WARNING: Slow query detected: SELECT * FROM users took 5000ms'
        ],
        'alarms': [
            {
                'id': 'ALM-001',
                'severity': 'critical',
                'message': 'CPU使用率过高',
                'timestamp': '2024-01-15T10:30:00Z',
                'source': 'monitoring_system'
            },
            {
                'id': 'ALM-002',
                'severity': 'high',
                'message': '内存使用率告警',
                'timestamp': '2024-01-15T10:30:02Z',
                'source': 'monitoring_system'
            },
            {
                'id': 'ALM-003',
                'severity': 'critical',
                'message': '服务不可用',
                'timestamp': '2024-01-15T10:30:10Z',
                'source': 'service_monitor'
            }
        ]
    }
    
    # 分析故障
    print("开始分析故障...")
    result = await agent.analyze_incident(incident_data)
    
    # 输出结果
    print("\n=== 故障分析报告 ===")
    print(f"分析状态: {'成功' if result.get('success') else '失败'}")
    print(f"分析时间: {result.get('analysis_timestamp')}")
    
    if result.get('success'):
        summary = result.get('summary', {})
        print(f"总体置信度: {summary.get('confidence', 0)}")
        
        print("\n发现的问题:")
        for finding in summary.get('findings', []):
            print(f"- {finding}")
        
        print("\n修复建议:")
        recommendations = result.get('recommendations', {})
        
        immediate_actions = recommendations.get('immediate_actions', [])
        if immediate_actions:
            print("立即行动:")
            for action in immediate_actions:
                print(f"  • {action}")
        
        follow_up_actions = recommendations.get('follow_up_actions', [])
        if follow_up_actions:
            print("后续行动:")
            for action in follow_up_actions:
                print(f"  • {action}")
    
    else:
        print(f"分析失败: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())