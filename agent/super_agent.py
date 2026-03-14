"""
super_agent.py
--------------
SuperAgent orchestrates the overall workflow:
  1. Decomposes the project into high-level tasks and workflow.
  2. Delegates tasks to specialized agents: DevOpsAgent, DevelopmentAgent, TestingAgent, DesignAgent.
  3. Collects and merges results from all agents.
"""


from typing import List, Dict, Any

class SuperAgent:
    def __init__(self, employees: List[Dict]):
        self.employees = employees

    def run(self, project: Dict[str, Any]):
        workflow = project.get('tasks', [])
        
        assignments = []
        for task in workflow:
            agent_type = task.get('type', 'development')
            
            if agent_type == 'devops':
                from agent.devops_agent import DevOpsAgent
                agent = DevOpsAgent(self.employees)
            elif agent_type == 'development':
                from agent.development_agent import DevelopmentAgent
                agent = DevelopmentAgent(self.employees)
            elif agent_type == 'testing':
                from agent.testing_agent import TestingAgent
                agent = TestingAgent(self.employees)
            elif agent_type == 'design':
                from agent.design_agent import DesignAgent
                agent = DesignAgent(self.employees)
            else:
                from agent.development_agent import DevelopmentAgent
                agent = DevelopmentAgent(self.employees)

            if agent:
                assignments.extend(agent.handle_task(task))
            
        return assignments
