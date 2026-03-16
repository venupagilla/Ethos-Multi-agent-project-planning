
export interface ProjectInput {
  project_id: string;
  project_name: string;
  description: string;
  required_skills: string[];
  deadline_days: number;
  priority: string;
}

export interface Employee {
  employee_id: string;
  name: string;
  role: string;
  skills: string[];
  experience_years: number;
  current_workload_percent: number;
  mail: string;
}

export interface Assignment {
  task_id: string;
  task_title: string;
  task_description: string;
  assigned_employee_id: string;
  assigned_employee_name: string;
  assigned_role: string;
  fitness_score: number;
  estimated_days: number;
  workload_after_assignment: number;
  explanation: string;
}

export interface RunResult {
  success: boolean;
  tasks: any[];
  assignments: Assignment[];
  risk_report: {
    overall_risk_score: number;
    risk_summary: string;
    task_risks: any[];
  };
  skill_gaps: {
    has_gaps: boolean;
    recommendations: string[];
    task_level_gaps: any[];
  };
  rebalance_log: string[];
  markdown: string;
  markdown_path?: string;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
const ASSIGNMENT_WEBHOOK_URL = process.env.NEXT_PUBLIC_ASSIGNMENT_WEBHOOK_URL || "https://hook.eu1.make.com/bcmh8kqm46gbz1ub1lxeg4up4uqyqisv";

export const agentService = {
  async getProjects(): Promise<ProjectInput[]> {
    const res = await fetch(`${BACKEND_URL}/api/projects`);
    if (!res.ok) throw new Error("Failed to fetch projects");
    return res.json();
  },

  async getEmployees(): Promise<Employee[]> {
    const res = await fetch(`${BACKEND_URL}/api/employees`);
    if (!res.ok) throw new Error("Failed to fetch employees");
    return res.json();
  },

  async uploadEmployees(employees: any[]): Promise<{ success: boolean; count: number }> {
    const res = await fetch(`${BACKEND_URL}/api/employees`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ employees }),
    });
    if (!res.ok) throw new Error("Failed to upload employees");
    return res.json();
  },

  /** Upload a raw CSV file — preferred for large datasets (500+ rows). */
  async uploadEmployeesCSV(file: File): Promise<{ success: boolean; count: number }> {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BACKEND_URL}/api/employees/csv`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) {
      const detail = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(detail.detail ?? "CSV upload failed");
    }
    return res.json();
  },


  async getAnalytics(): Promise<Record<string, number>> {
    const res = await fetch(`${BACKEND_URL}/api/analytics`);
    return res.json();
  },

  async runAgent(project: ProjectInput): Promise<RunResult> {
    const res = await fetch(`${BACKEND_URL}/api/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(project),
    });
    if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail?.message || errorData.detail || "Agent execution failed");
    }
    return res.json();
  },

  async sendAssignmentWebhook(employees: any[]): Promise<any> {
    const res = await fetch(ASSIGNMENT_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ employees }),
    });
    const text = await res.text();
    try {
      return JSON.parse(text);
    } catch (e) {
      return { status: text };
    }
  },

  async sendEmailWebhook(emails: any[]): Promise<any> {
    const res = await fetch(`${BACKEND_URL}/api/send-emails`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ emails }),
    });
    const text = await res.text();
    try {
      return JSON.parse(text);
    } catch (e) {
      return { status: text };
    }
  },

  async ragChat(projectId: string, query: string): Promise<{ response: string }> {
    const res = await fetch(`${BACKEND_URL}/api/rag-chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projectId, query }),
    });
    if (!res.ok) throw new Error("Chat failed");
    return res.json();
  },

  getMarkdownUrl(path: string): string {
    if (!path) return "#";
    const filename = path.split(/[\\/]/).pop();
    return `${BACKEND_URL}/static/${filename}`;
  }
};
