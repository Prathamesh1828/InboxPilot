import { CheckCircle2, Clock, PlayCircle } from "lucide-react";

export type StepStatus = "COMPLETED" | "IN_PROGRESS" | "PENDING" | "FAILED";

export interface TimelineStep {
  id: string;
  title: string;
  status: StepStatus;
  description?: string;
}

interface WorkflowTimelineProps {
  steps: TimelineStep[];
}

export function WorkflowTimeline({ steps }: WorkflowTimelineProps) {
  return (
    <div className="relative space-y-4 before:absolute before:inset-0 before:ml-4 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
      {steps.map((step) => {
        const isCompleted = step.status === "COMPLETED";
        const isInProgress = step.status === "IN_PROGRESS";
        const isFailed = step.status === "FAILED";
        
        return (
          <div key={step.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 bg-background shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm ${
              isCompleted ? "border-green-500 text-green-500" :
              isFailed ? "border-destructive text-destructive" :
              isInProgress ? "border-primary text-primary" :
              "border-muted-foreground/30 text-muted-foreground/30"
            }`}>
              {isCompleted ? <CheckCircle2 className="w-4 h-4" /> :
               isInProgress ? <PlayCircle className="w-4 h-4 animate-pulse" /> :
               <Clock className="w-4 h-4" />}
            </div>
            
            <div className="w-[calc(100%-3rem)] md:w-[calc(50%-2rem)] p-4 rounded-xl border border-border bg-card shadow-sm">
              <div className="flex items-center justify-between mb-1">
                <h4 className={`font-medium ${isCompleted || isInProgress || isFailed ? "text-foreground" : "text-muted-foreground"}`}>
                  {step.title}
                </h4>
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
