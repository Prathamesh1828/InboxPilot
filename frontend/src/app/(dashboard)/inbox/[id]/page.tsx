"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { ArrowLeft, User, BrainCircuit, ListTodo, ShieldCheck, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { WorkflowTimeline, TimelineStep } from "@/components/inbox/WorkflowTimeline";
import { emailsApi } from "@/lib/api/emails";
import { EmailData } from "@/components/inbox/EmailRow";

export default function EmailDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [email, setEmail] = useState<EmailData | null>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      emailsApi.getOne(id),
      emailsApi.getAudit(id)
    ])
    .then(([emailData, auditData]) => {
      setEmail(emailData);
      setAuditLogs(auditData);
      setLoading(false);
    })
    .catch(console.error);
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center text-muted-foreground">
        Loading email details...
      </div>
    );
  }

  if (!email) {
    return (
      <div className="flex flex-col h-[50vh] items-center justify-center text-muted-foreground gap-4">
        <p>Email not found.</p>
        <Link href="/inbox">
          <Button variant="outline">Back to Inbox</Button>
        </Link>
      </div>
    );
  }

  const workflowSteps: TimelineStep[] = auditLogs.map(log => ({
    id: String(log.id),
    title: log.event_type,
    status: log.status === "FAILED" ? "FAILED" : (log.status === "SUCCESS" ? "COMPLETED" : "IN_PROGRESS"),
    description: log.action || "System event",
  }));

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-4">
        <Link href="/inbox">
          <Button variant="ghost" size="icon" className="rounded-full">
            <ArrowLeft className="w-5 h-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Email Details</h1>
          <p className="text-muted-foreground text-sm">ID: {email.id}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Email Content */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-6">
            <div className="space-y-2 border-b border-border pb-4">
              <h2 className="text-xl font-semibold text-foreground">{email.subject}</h2>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <User className="w-4 h-4" />
                <span>From: <span className="font-medium text-foreground">{email.sender}</span></span>
              </div>
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 opacity-0" />
                  <span>To: {email.recipients?.join(", ") || "-"}</span>
                </div>
                <span>{new Date(email.timestamp).toLocaleString()}</span>
              </div>
            </div>
            <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap text-foreground">
              {email.preview}
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-6">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <BrainCircuit className="w-5 h-5 text-primary" />
              AI Analysis
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-secondary/30 p-4 rounded-lg border border-border space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Classification</div>
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-blue-500 border-blue-500/20 bg-blue-500/10">
                    {email.category}
                  </Badge>
                  <span className="text-sm font-bold text-foreground">{email.confidence}%</span>
                </div>
                <p className="text-sm text-muted-foreground mt-2">{email.reasoning}</p>
              </div>

              <div className="bg-secondary/30 p-4 rounded-lg border border-border space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Action Plan</div>
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-primary border-primary/20 bg-primary/10">
                    {"AUTOMATED_ACTION"}
                  </Badge>
                  <div className="flex items-center gap-1 text-sm font-bold text-orange-500">
                    <ShieldCheck className="w-4 h-4" /> {"SYSTEM"}
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mt-2">{"Processed according to policies."}</p>
              </div>
            </div>

            <div className="bg-secondary/30 p-4 rounded-lg border border-border space-y-3">
              <div className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <ListTodo className="w-4 h-4" /> Grounded Parameters
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div className="bg-background rounded px-3 py-2 text-sm border border-border">
                  <span className="text-muted-foreground">Parameters are stored in action logs.</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Workflow Timeline & Actions */}
        <div className="space-y-6">
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="text-lg font-semibold flex items-center gap-2 mb-6">
              <FileText className="w-5 h-5 text-primary" />
              Workflow Timeline
            </h3>
            <WorkflowTimeline steps={workflowSteps} />
          </div>

          <div className="flex flex-col gap-3">
            <Button className="w-full bg-green-500 hover:bg-green-600 text-white">
              Approve Action
            </Button>
            <Button variant="outline" className="w-full text-destructive border-border hover:bg-destructive/10">
              Reject Action
            </Button>
            <Link href="/audit" className="w-full">
              <Button variant="ghost" className="w-full">View Audit Logs</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
