"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Plus, 
  Upload, 
  Play, 
  CheckCircle2, 
  AlertTriangle, 
  Zap, 
  BarChart3, 
  FileText,
  User,
  X,
  ChevronRight,
  TrendingUp,
  MapPin, 
  Target, 
  Clock, 
  ShieldAlert, 
  Lightbulb, 
  ScrollText, 
  Users,
  Layout,
  MessageSquare,
  Send
} from "lucide-react";
import { agentService, ProjectInput, RunResult, Employee, Assignment } from "@/lib/agent-service";
import { Button } from "./ui/Button";

export function AgentDashboard() {
  const [project, setProject] = useState<ProjectInput>({
    project_id: "PRJ-" + Math.floor(Math.random() * 1000).toString().padStart(3, '0'),
    project_name: "",
    description: "",
    required_skills: [],
    deadline_days: 30,
    priority: "Medium"
  });

  const [skillsInput, setSkillsInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [consoleLogs, setConsoleLogs] = useState<string[]>([]);
  const [chatQuery, setChatQuery] = useState("");
  const [chatHistory, setChatHistory] = useState<{role: 'user' | 'assistant', text: string}[]>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  const addLog = (msg: string) => {
    setConsoleLogs(prev => [...prev.slice(-9), `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  const downloadSampleCSV = () => {
    const csvContent = "employee_id,name,role,skills,experience_years,current_workload_percent,mail\n" +
      "EMP001,Aarav Sharma,AI Engineer,\"Python;LLMs;LangChain;ML\",4,40,pagillavenu909@gmail.com\n" +
      "EMP002,Riya Patel,Data Scientist,\"Python;Data Analysis;ML;Pandas\",3,35,pagillavenu909@gmail.com";
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "workforce_sample.csv");
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    addLog("Sample workforce CSV downloaded.");
  };

  useEffect(() => {
    fetchEmployees();
    addLog("Neural system initialized. Ready for orchestration.");
  }, []);

  const fetchEmployees = async () => {
    try {
      const data = await agentService.getEmployees();
      setEmployees(data);
    } catch (err) {
      console.error("Failed to fetch employees:", err);
    }
  };


  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    setError(null);
    
    try {
      const reader = new FileReader();
      reader.onload = async (event) => {
        const text = event.target?.result as string;
        const lines = text.split(/\r?\n/).filter(line => line.trim());
        
        // Robust CSV splitting (handles quotes)
        const splitCSV = (line: string) => {
          const result = [];
          let current = "";
          let inQuotes = false;
          for (let i = 0; i < line.length; i++) {
            const char = line[i];
            if (char === '"') inQuotes = !inQuotes;
            else if (char === ',' && !inQuotes) {
              result.push(current.trim());
              current = "";
            } else current += char;
          }
          result.push(current.trim());
          return result;
        };

        const headers = splitCSV(lines[0]).map(h => h.trim().toLowerCase().replace(/"/g, ''));
        
        const parsedEmployees = lines.slice(1).map(line => {
          const values = splitCSV(line);
          const emp: any = {};
          headers.forEach((header, i) => {
            let val = values[i] ? values[i].replace(/"/g, '') : "";
            if (header === "skills") {
              // Handle both semicolon and comma separated skills within quotes
              emp[header] = val ? val.split(/[;,]/).map(s => s.trim()).filter(Boolean) : [];
            } else if (header === "experience_years" || header === "current_workload_percent") {
              emp[header] = parseFloat(val) || 0;
            } else {
              emp[header] = val;
            }
          });
          return emp;
        });

        await agentService.uploadEmployees(parsedEmployees);
        await fetchEmployees();
        addLog(`Workforce optimized: ${parsedEmployees.length} profiles synchronized.`);
      };
      reader.readAsText(file);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunAgent = async () => {
    if (!project.project_name || !project.description) {
      setError("Please fill in project name and description.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);
    setConsoleLogs([]);
    addLog("Initiating agent sequence...");

    try {
      addLog("Decomposing project requirements...");
      setTimeout(() => addLog("Mapping task dependencies..."), 1000);
      setTimeout(() => addLog("Scanning workforce database..."), 2500);
      setTimeout(() => addLog("Applying greedy fitness optimization..."), 4000);
      
      const data = await agentService.runAgent({
        ...project,
        required_skills: skillsInput.split(",").map(s => s.trim()).filter(Boolean)
      });
      
      addLog("Assignments optimized successfully.");
      setResult(data);

      // Trigger Webhooks
      if (data.success && data.assignments) {
        addLog("Triggering assignment webhooks...");
        const today = new Date();
        const employeesPayload = data.assignments
          .filter(a => a.assigned_employee_id)
          .map(a => {
            const deadline = new Date(today);
            deadline.setDate(today.getDate() + (a.estimated_days || 0));
            return {
              employee_id: a.assigned_employee_id,
              task: a.task_title,
              deadline: deadline.toISOString().split('T')[0]
            };
          });

        const emailPayload = data.assignments
          .filter(a => a.assigned_employee_id)
          .map(a => {
            const empInfo = employees.find(e => e.employee_id === a.assigned_employee_id);
            const toEmail = empInfo?.mail || "pagillavenu909@gmail.com"; // Fallback
            return {
              email: toEmail,
              body: `Hello ${empInfo?.name || a.assigned_employee_id}, you've been assigned the task '${a.task_title}' for project ${project.project_name}.\n\nTask Description: ${a.task_description || 'N/A'}`
            };
          }).filter(Boolean);

        if (employeesPayload.length > 0) {
          agentService.sendAssignmentWebhook(employeesPayload).catch(e => console.error("Assignment webhook failed", e));
        }
        if (emailPayload.length > 0) {
          addLog(`Triggering email via backend for ${emailPayload.length} assignments...`);
          agentService.sendEmailWebhook(emailPayload).catch(e => console.error("Email webhook failed", e));
        } else {
          addLog("No valid emails found to trigger webhooks.");
        }
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatQuery.trim() || isChatLoading) return;
    
    const userMsg = chatQuery;
    setChatQuery("");
    setChatHistory(prev => [...prev, { role: 'user', text: userMsg }]);
    setIsChatLoading(true);
    
    try {
      const { response } = await agentService.ragChat(project.project_id, userMsg);
      setChatHistory(prev => [...prev, { role: 'assistant', text: response }]);
    } catch (err: any) {
      setChatHistory(prev => [...prev, { role: 'assistant', text: "Sorry, I couldn't process that request." }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <section id="workflows" className="py-24 bg-black relative overflow-hidden">
      <div className="container mx-auto px-6 md:px-12 relative z-10">
        <div className="flex flex-col md:flex-row justify-between items-start gap-12 mb-16">
          <div className="max-w-2xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="flex items-center gap-2 mb-4"
            >
              <div className="w-8 h-[1px] bg-white/40" />
              <span className="text-xs uppercase tracking-widest text-white/60 font-semibold font-sans">
                Neural Orchestration
              </span>
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 uppercase tracking-tighter"
            >
              PROJECT <span className="text-white/40">ASSIGNMENT</span> AGENT
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="text-lg text-white/60 font-sans"
            >
              Configure your project parameters and let the Ethos agent handle task decomposition, skill mapping, and resource allocation using advanced neural models.
            </motion.p>
          </div>
          
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}

            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="p-6 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-md flex items-center gap-4"
          >
            <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center text-white">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold text-white">{employees.length}</div>
              <div className="text-xs text-white/40 uppercase tracking-widest font-semibold">Active Agents</div>
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          {/* Configuration Form */}
          <div className="lg:col-span-5 space-y-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="p-8 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-xl"
            >
              <h3 className="text-xl font-bold text-white mb-8 uppercase tracking-widest flex items-center gap-3">
                <Zap className="w-5 h-5 text-white/60" /> Configuration
              </h3>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-xs uppercase tracking-widest text-white/40 font-bold mb-2">Project ID</label>
                  <input 
                    type="text" 
                    value={project.project_id}
                    onChange={(e) => setProject({...project, project_id: e.target.value})}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/30 transition-colors font-sans"
                  />
                </div>
                
                <div>
                  <label className="block text-xs uppercase tracking-widest text-white/40 font-bold mb-2">Project Name</label>
                  <input 
                    type="text" 
                    placeholder="e.g. AI-Powered Marketing"
                    value={project.project_name}
                    onChange={(e) => setProject({...project, project_name: e.target.value})}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/30 transition-colors font-sans"
                  />
                </div>
                
                <div>
                  <label className="block text-xs uppercase tracking-widest text-white/40 font-bold mb-2">Skills (Comma Separated)</label>
                  <input 
                    type="text" 
                    placeholder="React, Python, LLMs"
                    value={skillsInput}
                    onChange={(e) => setSkillsInput(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/30 transition-colors font-sans"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs uppercase tracking-widest text-white/40 font-bold mb-2">Deadline (Days)</label>
                    <input 
                      type="number" 
                      value={project.deadline_days}
                      onChange={(e) => setProject({...project, deadline_days: parseInt(e.target.value)})}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/30 transition-colors font-sans"
                    />
                  </div>
                  <div>
                    <label className="block text-xs uppercase tracking-widest text-white/40 font-bold mb-2">Priority</label>
                    <select 
                      value={project.priority}
                      onChange={(e) => setProject({...project, priority: e.target.value})}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/30 transition-colors font-sans appearance-none"
                    >
                      <option className="bg-black text-white">High</option>
                      <option className="bg-black text-white">Medium</option>
                      <option className="bg-black text-white">Low</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-xs uppercase tracking-widest text-white/40 font-bold mb-2">Description</label>
                  <textarea 
                    rows={4}
                    placeholder="Describe the core objectives..."
                    value={project.description}
                    onChange={(e) => setProject({...project, description: e.target.value})}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/30 transition-colors font-sans resize-none"
                  />
                </div>

                <div className="pt-4 flex flex-col gap-4">
                  <div className="relative">
                    <input 
                      type="file" 
                      id="file-upload" 
                      hidden 
                      onChange={handleFileUpload}
                      accept=".csv,.xlsx"
                    />
                    <label 
                      htmlFor="file-upload"
                      className="flex items-center justify-center gap-2 w-full py-4 border border-dashed border-white/20 rounded-xl text-white/40 hover:text-white hover:border-white/40 transition-all cursor-pointer font-sans uppercase tracking-widest text-xs font-bold"
                    >
                      <Upload className="w-4 h-4" /> Upload Workforce
                    </label>
                    <button 
                      onClick={downloadSampleCSV}
                      className="mt-2 text-[10px] text-white/20 hover:text-white/60 transition-colors uppercase tracking-widest font-bold flex items-center gap-1 mx-auto"
                    >
                      <FileText className="w-3 h-3" /> Download Sample CSV
                    </button>
                  </div>
                  
                  <Button 
                    onClick={handleRunAgent} 
                    disabled={isLoading}
                    className="w-full py-4"
                  >
                    {isLoading ? "Processing..." : <>Initiate Agent <Play className="w-4 h-4 ml-2" /></>}
                  </Button>
                </div>

                {error && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-3 text-red-500 text-sm font-sans"
                  >
                    <AlertTriangle className="w-5 h-5 shrink-0" />
                    {error}
                  </motion.div>
                )}
              </div>
            </motion.div>
          </div>

          {/* Console & Analytics Column */}
          <div className="lg:col-span-7 space-y-8">
            {/* Live Agent Console - Higher contrast and highlighted */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 bg-black border-2 border-white/20 rounded-2xl font-mono text-[11px] relative overflow-hidden group shadow-[0_0_30px_rgba(255,255,255,0.05)] ring-1 ring-white/10"
            >
              <div className="flex items-center justify-between mb-4 border-b border-white/10 pb-3">
                <div className="flex items-center gap-3">
                  <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500/80 animate-pulse" />
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
                    <div className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-cyan-500 animate-ping" />
                    <span className="text-white font-bold uppercase tracking-widest text-[10px]">Ethos Live Console</span>
                  </div>
                </div>
                <div className="text-[10px] text-cyan-400 font-bold uppercase tracking-widest animate-pulse">System Active</div>
              </div>
              <div className="space-y-1.5 h-40 overflow-y-auto scrollbar-hide pr-2">
                {consoleLogs.length === 0 ? (
                  <div className="text-white/20 italic">Waiting for orchestration signal...</div>
                ) : (
                  consoleLogs.map((log, i) => (
                    <motion.div 
                      key={i} 
                      initial={{ opacity: 0, x: -5 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={`flex gap-3 ${i === consoleLogs.length - 1 ? "text-cyan-400 font-bold" : "text-white/40"}`}
                    >
                      <span className="text-white/20 shrink-0">{" > "}</span>
                      <span className="leading-relaxed">{log}</span>
                    </motion.div>
                  ))
                )}
                {isLoading && (
                  <motion.div 
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="flex gap-3 text-cyan-500 font-bold"
                  >
                    <span className="text-white/20 shrink-0">{" > "}</span>
                    <span className="flex items-center gap-2">
                      Initializing multi-agent graph sequence
                      <span className="flex gap-1">
                        <span className="w-1 h-1 bg-cyan-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                        <span className="w-1 h-1 bg-cyan-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                        <span className="w-1 h-1 bg-cyan-500 rounded-full animate-bounce" />
                      </span>
                    </span>
                  </motion.div>
                )}
              </div>
              <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-black to-transparent pointer-events-none" />
            </motion.div>

            {/* AI Project Assistant (RAG Chat) */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="p-1 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-[32px]"
            >
              <div className="bg-zinc-950 rounded-[31px] overflow-hidden flex flex-col h-[500px]">
                {/* Chat Header */}
                <div className="p-6 border-b border-white/10 bg-white/[0.02] flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-2xl bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                      <MessageSquare className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <h3 className="font-black text-white uppercase tracking-widest text-sm">Project Assistant</h3>
                      <p className="text-[10px] text-white/40 uppercase tracking-widest mt-0.5">RAG Powered Knowledge Base</p>
                    </div>
                  </div>
                  {result && (
                    <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
                      <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                      <span className="text-[10px] font-black text-green-500 uppercase tracking-tighter">Docs Indexed</span>
                    </div>
                  )}
                </div>

                {/* Chat Messages */}
                <div className="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.05),transparent_70%)]">
                  {chatHistory.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-30">
                      <Zap className="w-8 h-8 text-white" />
                      <p className="text-xs uppercase tracking-[0.2em] max-w-[240px] leading-relaxed">
                        {result ? "Documents ready. Ask about the SRS, DRD, or team assignments." : "Initiate the agent to generate project documents and enable chat."}
                      </p>
                    </div>
                  )}
                  {chatHistory.map((chat, i) => (
                    <motion.div 
                      key={i}
                      initial={{ opacity: 0, y: 10, x: chat.role === 'user' ? 20 : -20 }}
                      animate={{ opacity: 1, y: 0, x: 0 }}
                      className={`flex ${chat.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[85%] rounded-[24px] px-6 py-4 text-sm font-sans ${
                        chat.role === 'user' 
                          ? 'bg-blue-600 text-white rounded-tr-none shadow-[0_10px_30px_rgba(37,99,235,0.2)]' 
                          : 'bg-white/5 text-white/90 border border-white/10 rounded-tl-none backdrop-blur-md'
                      }`}>
                        {chat.text}
                      </div>
                    </motion.div>
                  ))}
                  {isChatLoading && (
                    <div className="flex justify-start">
                      <div className="bg-white/5 border border-white/10 rounded-[24px] rounded-tl-none px-6 py-4 text-sm font-sans text-white/40 animate-pulse">
                        Neural engine scanning documentation...
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                {/* Chat Input */}
                <form onSubmit={handleChat} className="p-6 bg-white/[0.02] border-t border-white/10">
                  <div className="relative group">
                    <input 
                      type="text" 
                      placeholder={result ? "Type your question..." : "Waiting for project generation..."}
                      disabled={!result || isChatLoading}
                      value={chatQuery}
                      onChange={(e) => setChatQuery(e.target.value)}
                      className="w-full bg-black border border-white/10 rounded-2xl py-4 pl-6 pr-14 text-sm text-white focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all font-sans placeholder:text-white/20 disabled:opacity-50"
                    />
                    <button 
                      type="submit"
                      disabled={!result || isChatLoading || !chatQuery.trim()}
                      className="absolute right-2 top-2 p-2.5 bg-blue-600 rounded-xl text-white hover:bg-blue-500 disabled:opacity-20 transition-all hover:scale-105 active:scale-95 shadow-lg shadow-blue-600/20"
                    >
                      <Send size={18} />
                    </button>
                  </div>
                </form>
              </div>
            </motion.div>

          </div>
        </div>

        {/* Full-width Results Section */}
        <div className="mt-12">
            <AnimatePresence mode="wait">
              {!result && !isLoading ? (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="min-h-[300px] border border-white/5 rounded-3xl flex flex-col items-center justify-center text-center p-12 bg-white/[0.02]"
                >
                  <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center text-white/20 mb-6">
                    <BarChart3 className="w-10 h-10" />
                  </div>
                  <h4 className="text-xl font-bold text-white mb-2 uppercase tracking-widest">Waiting for Input</h4>
                  <p className="text-white/40 font-sans max-w-sm">
                    Configure your project and workforce in the left panel to begin.
                  </p>
                </motion.div>
              ) : isLoading ? (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="min-h-[300px] border border-white/5 rounded-3xl flex flex-col items-center justify-center p-12 bg-white/[0.02]"
                >
                  <div className="relative w-24 h-24 mb-8">
                    <motion.div 
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      className="absolute inset-0 border-4 border-white/10 border-t-white rounded-full"
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Zap className="w-8 h-8 text-white animate-pulse" />
                    </div>
                  </div>
                  <h4 className="text-xl font-bold text-white mb-2 uppercase tracking-widest">Orchestrating</h4>
                  <p className="text-white/40 font-sans">Watch the live console above for details.</p>
                </motion.div>
              ) : (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  {/* Summary Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <motion.div 
                      whileHover={{ y: -5 }}
                      className="p-6 bg-gradient-to-br from-white/10 to-transparent border border-white/10 rounded-2xl shadow-lg relative overflow-hidden group"
                    >
                      <div className="text-xs text-white/40 uppercase tracking-[0.2em] font-bold mb-2">Risk Score</div>
                      <div className="text-3xl font-bold text-white flex items-center gap-3">
                        {result?.risk_report.overall_risk_score}
                        {(result?.risk_report.overall_risk_score ?? 0) > 70 ? 
                          <AlertTriangle className="w-6 h-6 text-red-500 animate-pulse" /> : 
                          <CheckCircle2 className="w-6 h-6 text-green-500" />
                        }
                      </div>
                      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                         <ShieldAlert className="w-12 h-12 text-white" />
                      </div>
                    </motion.div>
                    
                    <motion.div 
                      whileHover={{ y: -5 }}
                      className="p-6 bg-gradient-to-br from-white/10 to-transparent border border-white/10 rounded-2xl shadow-lg relative overflow-hidden group"
                    >
                      <div className="text-xs text-white/40 uppercase tracking-[0.2em] font-bold mb-2">Plan Complexity</div>
                      <div className="text-3xl font-bold text-white">{result?.assignments.length} <span className="text-xs text-white/40 font-normal">TASKS</span></div>
                      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                         <Layout className="w-12 h-12 text-white" />
                      </div>
                    </motion.div>

                    <motion.div 
                      whileHover={{ y: -5 }}
                      className="p-6 bg-gradient-to-br from-white/10 to-transparent border border-white/10 rounded-2xl shadow-lg relative overflow-hidden group"
                    >
                      <div className="text-xs text-white/40 uppercase tracking-[0.2em] font-bold mb-2">Resource Utilization</div>
                      <div className="text-3xl font-bold text-white">
                        {Math.round((result?.assignments.filter(a => a.assigned_employee_id).length || 0) / (result?.assignments.length || 1) * 100)}%
                      </div>
                      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                         <Users className="w-12 h-12 text-white" />
                      </div>
                    </motion.div>
                  </div>

                  {/* Main Grid for Results */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                    
                    {/* Left Column: Assignments & Logs */}
                    <div className="space-y-8">
                      {/* Assignments List */}
                      <div className="p-8 bg-white/[0.03] border border-white/10 rounded-[32px] shadow-2xl backdrop-blur-sm">
                        <h3 className="text-xl font-bold text-white mb-8 uppercase tracking-widest flex items-center gap-3">
                          <ScrollText className="w-5 h-5 text-cyan-400" /> Optimization Map
                        </h3>
                        <div className="space-y-4">
                          {result?.assignments.map((assignment, idx) => (
                            <motion.div 
                              key={assignment.task_id}
                              initial={{ opacity: 0, x: 20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: idx * 0.05 }}
                              className="group p-5 bg-white/[0.02] hover:bg-white/[0.08] border border-white/5 hover:border-white/20 rounded-2xl transition-all relative overflow-hidden"
                            >
                              <div className="flex justify-between items-start relative z-10">
                                <div className="space-y-1">
                                  <div className="flex items-center gap-3">
                                    <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded text-white/40 uppercase font-mono tracking-tighter">
                                      {assignment.task_id}
                                    </span>
                                    <h4 className="font-bold text-white group-hover:text-cyan-400 transition-colors uppercase tracking-tight">
                                      {assignment.task_title}
                                    </h4>
                                  </div>
                                  <p className="text-[11px] text-white/40 leading-relaxed max-w-md line-clamp-1 italic">
                                    {assignment.explanation || "No explanation provided."}
                                  </p>
                                </div>
                                <div className="text-right">
                                  <div className="text-lg font-black text-white">{assignment.fitness_score}%</div>
                                  <div className="text-[9px] uppercase tracking-widest text-white/20 font-bold">Fit Score</div>
                                </div>
                              </div>
                              
                              <div className="flex items-center gap-4 mt-6 pt-4 border-t border-white/5">
                                <div className="w-10 h-10 rounded-full bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                                  <User className="w-5 h-5" />
                                </div>
                                <div>
                                  <div className="text-xs font-bold text-white uppercase tracking-wider">
                                    {assignment.assigned_employee_name || "Neural Outsource Needed"}
                                  </div>
                                  <div className="text-[10px] text-white/40 uppercase tracking-widest italic">{assignment.assigned_role}</div>
                                </div>
                                <div className="ml-auto px-3 py-1 bg-white/5 rounded-full text-[9px] font-bold text-white/60 uppercase tracking-widest border border-white/5">
                                  {assignment.estimated_days}d sprint
                                </div>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </div>

                      {/* Rebalancing Log */}
                      {result?.rebalance_log && result.rebalance_log.length > 0 && (
                        <div className="p-8 bg-white/[0.03] border border-white/10 rounded-[32px] overflow-hidden">
                          <h3 className="text-xl font-bold text-white mb-6 uppercase tracking-widest flex items-center gap-3">
                            <Zap className="w-5 h-5 text-yellow-500" /> Neural Rebalancing
                          </h3>
                          <div className="space-y-2 font-mono text-[10px] text-white/40 bg-black/40 p-6 rounded-2xl border border-white/5 max-h-60 overflow-y-auto scrollbar-hide">
                            {result.rebalance_log.map((log, i) => (
                              <div key={i} className="flex gap-3 border-l border-white/10 pl-3">
                                <span className="text-white/20 shrink-0">#{i.toString().padStart(2, '0')}</span>
                                <span className="leading-relaxed">{log}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Right Column: Workload, Risk, Skills */}
                    <div className="space-y-8">
                       {/* Final Workforce Load */}
                       <div className="p-8 bg-white/[0.03] border border-white/10 rounded-[32px] shadow-xl">
                          <h3 className="text-xl font-bold text-white mb-8 uppercase tracking-widest flex items-center gap-3">
                            <TrendingUp className="w-5 h-5 text-purple-400" /> Operational Load
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 gap-4">
                            {Array.from(new Set(result?.assignments.map(a => a.assigned_employee_id)))
                              .filter(id => id)
                              .map(id => {
                                const assignments = result?.assignments.filter(a => a.assigned_employee_id === id);
                                const lastAssignment = assignments?.[assignments.length - 1];
                                const empName = lastAssignment?.assigned_employee_name;
                                const role = lastAssignment?.assigned_role;
                                const finalWL = lastAssignment?.workload_after_assignment;
                                const tasks = assignments?.length || 0;
                                
                                return (
                                  <motion.div 
                                    key={id} 
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="p-5 bg-black/40 border border-white/10 rounded-2xl group hover:border-purple-500/30 transition-all"
                                  >
                                    <div className="flex justify-between items-center mb-1">
                                      <div className="font-bold text-white text-sm uppercase tracking-tight">{empName}</div>
                                      <div className={`text-sm font-black ${finalWL && finalWL > 85 ? "text-red-500" : "text-white"}`}>{finalWL}%</div>
                                    </div>
                                    <div className="text-[10px] text-white/30 truncate mb-4 uppercase tracking-[0.15em]">{role}</div>
                                    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden mb-4">
                                       <motion.div 
                                         initial={{ width: 0 }}
                                         animate={{ width: `${Math.min(finalWL || 0, 100)}%` }}
                                         className={`h-full ${finalWL && finalWL > 85 ? "bg-red-500" : "bg-purple-500"} shadow-[0_0_10px_rgba(168,85,247,0.3)]`}
                                       />
                                    </div>
                                    <div className="flex justify-between items-center text-[9px] uppercase tracking-widest font-bold text-white/20">
                                       <span>Resource Bound</span>
                                       <span>{tasks} ACTIVE TASKS</span>
                                    </div>
                                  </motion.div>
                                );
                              })}
                          </div>
                       </div>

                       {/* Risk Flags */}
                       {result?.risk_report.task_risks && result.risk_report.task_risks.length > 0 && (
                          <div className="p-8 bg-red-500/[0.02] border border-red-500/10 rounded-[32px] shadow-inner">
                            <h3 className="text-xl font-bold text-white mb-8 uppercase tracking-widest flex items-center gap-3">
                              <ShieldAlert className="w-5 h-5 text-red-500" /> Operational Risks
                            </h3>
                            <div className="space-y-4">
                              {result.risk_report.task_risks.map((tr: any) => (
                                <div key={tr.task_id} className="p-5 bg-red-500/[0.03] border border-red-500/10 rounded-2xl">
                                  <div className="flex justify-between items-center mb-3">
                                    <span className="font-bold text-white text-xs uppercase tracking-tight">{tr.task_title}</span>
                                    <span className={`text-[9px] px-2 py-1 rounded-md ${
                                      tr.risk_level === 'High' ? 'bg-red-500 text-white' : 
                                      tr.risk_level === 'Medium' ? 'bg-orange-500/20 text-orange-500 border border-orange-500/20' : 
                                      'bg-green-500/20 text-green-500 border border-green-500/20'
                                    } uppercase font-bold tracking-widest`}>{tr.risk_level}</span>
                                  </div>
                                  <ul className="space-y-2">
                                    {tr.flags.map((flag: string, i: number) => (
                                      <li key={i} className="text-[11px] text-white/50 flex items-start gap-2 leading-relaxed italic">
                                        <div className="mt-1.5 w-1 h-1 rounded-full bg-red-500 shrink-0" />
                                        {flag}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              ))}
                            </div>
                          </div>
                       )}

                       {/* Skill Analysis */}
                       <div className="p-8 bg-blue-500/[0.02] border border-blue-500/10 rounded-[32px]">
                          <h3 className="text-xl font-bold text-white mb-8 uppercase tracking-widest flex items-center gap-3">
                            <Target className="w-5 h-5 text-blue-400" /> Capability Gaps
                          </h3>
                          {!result?.skill_gaps.has_gaps ? (
                            <div className="p-6 bg-green-500/5 border border-green-500/10 rounded-2xl flex items-center gap-4 text-green-400 text-xs font-bold uppercase tracking-widest">
                              <CheckCircle2 className="w-6 h-6 shrink-0" />
                              Full competency match across all task vectors.
                            </div>
                          ) : (
                            <div className="space-y-6">
                              <div className="p-5 bg-blue-500/5 border border-blue-500/10 rounded-2xl text-xs text-blue-300 leading-relaxed italic pr-8 relative">
                                {result?.skill_gaps.recommendations[0]}
                                <Lightbulb className="absolute top-4 right-4 w-4 h-4 text-blue-400 opacity-30" />
                              </div>
                              <div className="grid grid-cols-1 gap-3">
                                {result?.skill_gaps.task_level_gaps.map((tg: any) => (
                                  <div key={tg.task_id} className="p-4 bg-white/5 border border-white/5 rounded-xl hover:bg-white/[0.08] transition-colors">
                                    <div className="text-[10px] font-bold text-white/60 mb-3 uppercase tracking-widest truncate">{tg.task_title}</div>
                                    <div className="flex flex-wrap gap-2">
                                      {tg.missing_skills.map((s: string) => (
                                        <span key={s} className="text-[9px] px-2 py-1 bg-blue-500/10 border border-blue-500/20 rounded text-blue-400 uppercase font-black tracking-widest">
                                          Missing {s}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                       </div>
                    </div>
                  </div>

                  {/* Markdown Report Download */}
                  <div className="flex flex-col gap-4 mt-12">
                    <button 
                      onClick={() => {
                        const content = result?.markdown || '# No report available';
                        const blob = new Blob([content], { type: 'text/markdown;charset=utf-8;' });
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = `report_${result?.markdown_path?.split(/[\\/]/).pop() || 'report.md'}`;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        URL.revokeObjectURL(url);
                      }}
                      className="w-full p-8 bg-white text-black rounded-[32px] flex items-center justify-between group overflow-hidden relative"
                    >
                      <div className="relative z-10 flex items-center gap-6">
                        <div className="w-12 h-12 rounded-full bg-black/5 flex items-center justify-center">
                           <FileText className="w-6 h-6" />
                        </div>
                        <div className="text-left">
                           <span className="font-black uppercase tracking-widest text-lg block">Assignment Report</span>
                           <span className="text-xs uppercase tracking-widest text-black/40 block mt-1">Audit complete. Download markdown.</span>
                        </div>
                      </div>
                      <ChevronRight className="relative z-10 w-8 h-8 group-hover:translate-x-2 transition-transform duration-500" />
                    </button>

                    <div className="grid grid-cols-2 gap-4">
                      {['srs', 'drd'].map(type => (
                        <a 
                          key={type}
                          href={agentService.getMarkdownUrl(`${project.project_id}_${type}.md`)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-6 bg-white/[0.03] border border-white/10 rounded-2xl flex items-center justify-between hover:bg-white/5 transition-all group"
                        >
                          <div className="flex items-center gap-3">
                            <ScrollText size={16} className="text-blue-400" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-white/60">{type} Document</span>
                          </div>
                          <ChevronRight size={14} className="text-white/20 group-hover:translate-x-1 transition-transform" />
                        </a>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

      <div className="absolute top-1/4 -right-24 w-96 h-96 bg-white/5 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-1/4 -left-24 w-64 h-64 bg-white/5 blur-[100px] rounded-full pointer-events-none" />
    </section>
  );
}
