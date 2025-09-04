"""
DevOps智能体主应用程序
基于LangGraph的工作流实现
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from planner import Planner


class AgentState(TypedDict):
    """智能体状态定义"""
    incident_data: Dict[str, Any]
    current_task: Optional[str]
    analysis_results: List[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]
    error_message: Optional[str]
    messages: List[Dict[str, Any]]


class DevOpsAgent:
    """DevOps智能体主类"""
    
    def __init__(self):
        self.planner = Planner()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """创建LangGraph工作流"""
        
        # 定义工作流节点
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("parse_input", self._parse_input_node)
        workflow.add_node("plan_analysis", self._plan_analysis_node)
        workflow.add_node("execute_analysis", self._execute_analysis_node)
        workflow.add_node("generate_summary", self._generate_summary_node)
        workflow.add_node("create_report", self._create_report_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # 定义工作流边
        workflow.set_entry_point("parse_input")
        workflow.add_edge("parse_input", "plan_analysis")
        workflow.add_edge("plan_analysis", "execute_analysis")
        workflow.add_edge("execute_analysis", "generate_summary")
        workflow.add_edge("generate_summary", "create_report")
        workflow.add_edge("create_report", END)
        workflow.add_edge("handle_error", END)
        
        # 添加条件边用于错误处理
        workflow.add_conditional_edges(
            "parse_input",
            self._should_handle_error,
            {
                "error": "handle_error",
                "continue": "plan_analysis"
            }
        )
        
        return workflow.compile()
    
    async def _parse_input_node(self, state: AgentState) -> AgentState:
        """解析输入数据节点"""
        try:
            incident_data = state.get('incident_data', {})
            
            # 验证输入数据
            if not incident_data:
                state['error_message'] = "未提供故障数据"
                return state
            
            # 添加处理消息
            state['messages'] = add_messages(
                state.get('messages', []),
                [{"role": "system", "content": "开始解析故障数据"}]
            )
            
            state['current_task'] = "input_parsed"
            return state
            
        except Exception as e:
            state['error_message'] = f"输入解析失败: {str(e)}"
            return state
    
    async def _plan_analysis_node(self, state: AgentState) -> AgentState:
        """规划分析任务节点"""
        try:
            incident_data = state['incident_data']
            
            # 创建分析计划
            tasks = self.planner._create_analysis_plan(incident_data)
            
            state['messages'] = add_messages(
                state.get('messages', []),
                [{"role": "system", "content": f"创建了 {len(tasks)} 个分析任务"}]
            )
            
            state['current_task'] = "plan_created"
            state['analysis_tasks'] = tasks
            return state
            
        except Exception as e:
            state['error_message'] = f"任务规划失败: {str(e)}"
            return state
    
    async def _execute_analysis_node(self, state: AgentState) -> AgentState:
        """执行分析任务节点"""
        try:
            tasks = state.get('analysis_tasks', [])
            
            # 执行分析任务
            results = await self.planner._execute_analysis_tasks(tasks)
            
            # 转换结果格式
            analysis_results = [
                {
                    'task_id': r.task_id,
                    'analyzer_name': r.analyzer_name,
                    'success': r.success,
                    'findings': r.findings,
                    'confidence': r.confidence,
                    'suggestions': r.suggestions,
                    'error_message': r.error_message
                }
                for r in results
            ]
            
            state['analysis_results'] = analysis_results
            state['messages'] = add_messages(
                state.get('messages', []),
                [{"role": "system", "content": f"完成 {len(results)} 个分析任务"}]
            )
            
            state['current_task'] = "analysis_completed"
            return state
            
        except Exception as e:
            state['error_message'] = f"分析执行失败: {str(e)}"
            return state
    
    async def _generate_summary_node(self, state: AgentState) -> AgentState:
        """生成总结报告节点"""
        try:
            analysis_results = state.get('analysis_results', [])
            
            # 生成总结
            summary_result = await self.planner._generate_summary_report([
                AnalysisResult(
                    task_id=r['task_id'],
                    analyzer_name=r['analyzer_name'],
                    success=r['success'],
                    findings=r['findings'],
                    confidence=r['confidence'],
                    suggestions=r['suggestions'],
                    error_message=r.get('error_message')
                )
                for r in analysis_results
            ])
            
            state['summary_result'] = {
                'success': summary_result.success,
                'findings': summary_result.findings,
                'confidence': summary_result.confidence,
                'suggestions': summary_result.suggestions,
                'error_message': summary_result.error_message
            }
            
            state['messages'] = add_messages(
                state.get('messages', []),
                [{"role": "system", "content": "生成总结报告完成"}]
            )
            
            state['current_task'] = "summary_generated"
            return state
            
        except Exception as e:
            state['error_message'] = f"总结生成失败: {str(e)}"
            return state
    
    async def _create_report_node(self, state: AgentState) -> AgentState:
        """创建最终报告节点"""
        try:
            incident_data = state['incident_data']
            analysis_results = state.get('analysis_results', [])
            summary_result = state.get('summary_result', {})
            
            # 创建最终报告
            final_report = {
                'success': True,
                'incident_id': incident_data.get('incident_id', str(uuid.uuid4())),
                'analysis_timestamp': datetime.now().isoformat(),
                'input_summary': {
                    'logs_provided': 'logs' in incident_data,
                    'alarms_provided': 'alarms' in incident_data,
                    'incident_description': incident_data.get('description', '')
                },
                'analysis_summary': {
                    'total_analyzers_used': len(analysis_results),
                    'successful_analyses': len([r for r in analysis_results if r.get('success', False)]),
                    'overall_confidence': summary_result.get('confidence', 0.0)
                },
                'findings': summary_result.get('findings', []),
                'recommendations': summary_result.get('suggestions', []),
                'detailed_results': analysis_results
            }
            
            state['final_report'] = final_report
            state['messages'] = add_messages(
                state.get('messages', []),
                [{"role": "system", "content": "最终报告生成完成"}]
            )
            
            state['current_task'] = "completed"
            return state
            
        except Exception as e:
            state['error_message'] = f"报告创建失败: {str(e)}"
            return state
    
    async def _handle_error_node(self, state: AgentState) -> AgentState:
        """处理错误节点"""
        error_message = state.get('error_message', '未知错误')
        
        state['final_report'] = {
            'success': False,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }
        
        state['messages'] = add_messages(
            state.get('messages', []),
            [{"role": "system", "content": f"处理过程中发生错误: {error_message}"}]
        )
        
        return state
    
    def _should_handle_error(self, state: AgentState) -> str:
        """判断是否需要处理错误"""
        if state.get('error_message'):
            return "error"
        return "continue"
    
    async def analyze_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析故障事件"""
        initial_state = AgentState(
            incident_data=incident_data,
            current_task=None,
            analysis_results=[],
            final_report=None,
            error_message=None,
            messages=[]
        )
        
        # 执行工作流
        final_state = await self.workflow.ainvoke(initial_state)
        
        return final_state.get('final_report', {
            'success': False,
            'error': '工作流执行失败',
            'timestamp': datetime.now().isoformat()
        })