import { CheckCircle2, Clock, PlayCircle, ShieldCheck, Mail, BrainCircuit, ListTodo, XCircle, Send } from "lucide-react";

export type StepStatus = "COMPLETED" | "IN_PROGRESS" | "PENDING" | "FAILED";

export interface TimelineStep {
  id: string;
  title: string;
  status: StepStatus;
  description?: string;
  timestamp?: string;
  metadata?: Record<string, unknown>;
}

interface WorkflowTimelineProps {
  steps: TimelineStep[];
}

export function WorkflowTimeline({ steps }: WorkflowTimelineProps) {
  
  const getIcon = (title: string, status: StepStatus) => {
    if (status === "FAILED") return <XCircle className="w-4 h-4 text-destructive" />;
    
    if (title.includes("EMAIL_RECEIVED")) return <Mail className="w-4 h-4 text-muted-foreground" />;
    if (title.includes("CLASSIFI")) return <BrainCircuit className="w-4 h-4 text-purple-500" />;
    if (title.includes("PLAN")) return <ListTodo className="w-4 h-4 text-blue-500" />;
    if (title.includes("SAFETY") || title.includes("GROUNDING")) return <ShieldCheck className="w-4 h-4 text-orange-500" />;
    if (title.includes("APPROVAL")) return <CheckCircle2 className="w-4 h-4 text-yellow-600" />;
    if (title.includes("EXECUTION")) return <Send className="w-4 h-4 text-green-500" />;
    
    if (status === "COMPLETED") return <CheckCircle2 className="w-4 h-4 text-green-500" />;
    if (status === "IN_PROGRESS") return <PlayCircle className="w-4 h-4 animate-pulse text-primary" />;
    return <Clock className="w-4 h-4 text-muted-foreground" />;
  };

  const formatTitle = (title: string) => {
    return title.split("_").map(w => w.charAt(0) + w.slice(1).toLowerCase()).join(" ");
  };

  return (
    <div className="relative space-y-0 before:absolute before:inset-0 before:ml-[1.4rem] before:h-full before:w-0.5 before:bg-border">
      {steps.map((step) => {
        const isCompleted = step.status === "COMPLETED";
        const isFailed = step.status === "FAILED";
        
        return (
          <div key={step.id} className="relative flex gap-4 pb-6 group">
            <div className={`relative flex items-center justify-center w-11 h-11 rounded-full border-2 bg-card shrink-0 z-10 shadow-sm ${
              isFailed ? "border-destructive/30 bg-destructive/5" :
              isCompleted ? "border-border" : "border-border border-dashed"
            }`}>
              {getIcon(step.title, step.status)}
            </div>
            
            <div className="flex-1 pt-1.5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1">
                <h4 className={`text-sm font-semibold ${isFailed ? "text-destructive" : "text-foreground"}`}>
                  {formatTitle(step.title)}
                </h4>
                {step.timestamp && (
                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {new Date(step.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                )}
              </div>
              
              {step.description && (
                <p className="text-sm text-muted-foreground">{step.description}</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
