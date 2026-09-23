"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { ArrowLeft, User, BrainCircuit, ListTodo, ShieldCheck, FileText, CheckCircle2, XCircle, AlertTriangle, PlayCircle, Send, Reply, Forward, ExternalLink, Calendar, Copy, Check, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { WorkflowTimeline, TimelineStep } from "@/components/inbox/WorkflowTimeline";
import { emailsApi, approvalsApi, EmailDetailData } from "@/lib/api/emails";
import { formatDistanceToNow } from "date-fns";

export default function EmailDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [email, setEmail] = useState<EmailDetailData | null>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [processing, setProcessing] = useState(false);

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      emailsApi.getOne(id),
      emailsApi.getAudit(id)
    ])
    .then(([emailData, auditData]) => {
      setEmail(emailData);
      setAuditLogs(auditData);
      setLoading(false);
    })
    .catch((err) => {
      console.error(err);
      setLoading(false);
    });
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const handleApprove = async () => {
    if (!email?.approval_id) return;
    setProcessing(true);
    try {
      await approvalsApi.approve(email.approval_id);
      fetchData();
    } catch (e) {
      console.error("Failed to approve", e);
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!email?.approval_id) return;
    setProcessing(true);
    try {
      await approvalsApi.reject(email.approval_id);
      fetchData();
    } catch (e) {
      console.error("Failed to reject", e);
    } finally {
      setProcessing(false);
    }
  };

  const copyEmail = () => {
    if (email?.sender) {
      navigator.clipboard.writeText(email.sender);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading && !email) {
    return (
      <div className="flex h-[50vh] items-center justify-center space-x-2">
        <div className="w-4 h-4 rounded-full bg-primary/40 animate-bounce"></div>
        <div className="w-4 h-4 rounded-full bg-primary/60 animate-bounce [animation-delay:-.3s]"></div>
        <div className="w-4 h-4 rounded-full bg-primary animate-bounce [animation-delay:-.5s]"></div>
      </div>
    );
  }

  if (!email) {
    return (
      <div className="flex flex-col h-[50vh] items-center justify-center text-muted-foreground gap-4">
        <AlertTriangle className="w-12 h-12 text-muted-foreground/30" />
        <p>Email not found or unavailable.</p>
        <Link href="/inbox">
          <Button variant="outline">Back to Inbox</Button>
        </Link>
      </div>
    );
  }

  const workflowSteps: TimelineStep[] = auditLogs.map(log => ({
    id: String(log.id),
    title: log.event_type,
    status: log.status === "FAILED" ? "FAILED" : (log.event_type.includes("COMPLETED") || log.event_type.includes("CREATED") || log.event_type.includes("PASSED") || log.event_type.includes("EVALUATED") || log.event_type.includes("APPROVED") || log.event_type.includes("REJECTED") ? "COMPLETED" : "IN_PROGRESS"),
    description: log.details?.error || log.details?.grounding_errors ? String(log.details?.error || log.details?.grounding_errors) : log.action || undefined,
    timestamp: log.created_at,
    metadata: log.details
  }));

  const receivedDate = new Date(email.received_at || email.timestamp);
  const relativeTime = !isNaN(receivedDate.getTime()) ? formatDistanceToNow(receivedDate, { addSuffix: true }) : "";

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div className="flex items-center gap-4">
        <Link href="/inbox">
          <Button variant="ghost" size="icon" className="rounded-full hover:bg-secondary">
            <ArrowLeft className="w-5 h-5 text-foreground" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Email Details</h1>
          <p className="text-muted-foreground text-sm flex items-center gap-2">
            ID: {email.id} • {email.status}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Email Content & AI Stuff */}
        <div className="lg:col-span-8 space-y-6">
          
          {/* EMAIL HEADER & CONTENT */}
          <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
            <div className="p-6 border-b border-border space-y-4 bg-secondary/10">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                <h2 className="text-xl font-bold text-foreground leading-tight">
                  {email.subject || "(No Subject)"}
                </h2>
                
                <div className="flex items-center gap-2 shrink-0">
                  <Button variant="outline" size="sm" className="h-8 gap-1.5 hidden sm:flex">
                    <Reply className="w-3.5 h-3.5" /> Reply
                  </Button>
                  <Button variant="outline" size="sm" className="h-8 gap-1.5 hidden sm:flex">
                    <Forward className="w-3.5 h-3.5" /> Forward
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <ExternalLink className="w-4 h-4 text-muted-foreground" />
                  </Button>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold shrink-0">
                  {email.sender.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 truncate">
                      <span className="font-semibold text-foreground truncate">{email.sender}</span>
                      <button onClick={copyEmail} className="text-muted-foreground hover:text-foreground shrink-0 transition-colors" title="Copy email">
                        {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                    <div className="text-sm text-muted-foreground shrink-0 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5" />
                      {!isNaN(receivedDate.getTime()) ? (
                        <span title={receivedDate.toLocaleString()}>{relativeTime}</span>
                      ) : (
                        <span>{email.received_at || String(email.timestamp)}</span>
                      )}
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground truncate">
                    To: {email.recipients?.join(", ") || "-"}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <div className="prose prose-sm dark:prose-invert max-w-none text-foreground whitespace-pre-wrap font-sans leading-relaxed">
                {email.body}
              </div>
            </div>
          </div>

          {/* AI ANALYSIS SECTION */}
          {(email.category || email.action_plan) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* CLASSIFICATION CARD */}
              <div className="bg-card border border-border rounded-2xl shadow-sm p-5 space-y-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-8 h-8 rounded-full bg-purple-500/10 flex items-center justify-center text-purple-500">
                    <BrainCircuit className="w-4 h-4" />
                  </div>
                  <h3 className="font-semibold text-foreground text-base">Classification</h3>
                </div>
                
                {email.category ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Badge className="bg-purple-500 hover:bg-purple-600 font-medium px-2.5 py-0.5">
                        {email.category}
                      </Badge>
                      {email.classification_confidence !== null && (
                        <span className="text-sm font-bold text-purple-500">
                          {Math.round((email.classification_confidence || 0) * 100)}% Match
                        </span>
                      )}
                    </div>
                    {email.classification_reasoning && (
                      <div className="bg-secondary/30 rounded-xl p-3 text-sm text-muted-foreground border border-border/50">
                        {email.classification_reasoning}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">Classification unavailable.</div>
                )}
              </div>

              {/* ACTION PLAN CARD */}
              <div className="bg-card border border-border rounded-2xl shadow-sm p-5 space-y-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-500">
                    <ListTodo className="w-4 h-4" />
                  </div>
                  <h3 className="font-semibold text-foreground text-base">Action Plan</h3>
                </div>
                
                {email.action_plan ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Badge variant="outline" className="text-blue-500 border-blue-500/30 bg-blue-500/5 px-2.5 py-0.5 font-medium">
                        {email.action_plan.action.replace(/_/g, " ")}
                      </Badge>
                      {email.action_plan.requires_approval && (
                        <span className="text-xs font-medium text-orange-500 flex items-center gap-1 border border-orange-500/20 bg-orange-500/10 px-2 rounded-full py-0.5">
                          <ShieldCheck className="w-3 h-3" /> Approval Required
                        </span>
                      )}
                    </div>
                    
                    {email.action_plan.parameters && Object.keys(email.action_plan.parameters).length > 0 ? (
                      <div className="bg-secondary/30 rounded-xl p-3 text-sm border border-border/50 space-y-2">
                        {Object.entries(email.action_plan.parameters).map(([key, value]) => (
                          <div key={key} className="flex flex-col sm:flex-row sm:items-baseline gap-1 sm:gap-2">
                            <span className="text-muted-foreground capitalize shrink-0">{key.replace(/_/g, " ")}:</span>
                            <span className="font-medium text-foreground truncate" title={String(value)}>{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="bg-secondary/30 rounded-xl p-3 text-sm text-muted-foreground border border-border/50">
                        No additional parameters required.
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">No action plan generated.</div>
                )}
              </div>
            </div>
          )}

          {/* SAFETY & APPROVAL / EXECUTION STATUS */}
          {email.status !== "PENDING" && (
            <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
              
              {/* Approval Bar (if pending) */}
              {email.approval_status === "PENDING" ? (
                <div className="bg-orange-500/10 border-b border-orange-500/20 p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="flex items-center gap-3 text-orange-600 dark:text-orange-400">
                    <ShieldCheck className="w-5 h-5 shrink-0" />
                    <p className="font-medium text-sm">Human approval required before execution.</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 w-full sm:w-auto">
                    <Button 
                      variant="outline" 
                      className="flex-1 sm:flex-none border-destructive/30 text-destructive hover:bg-destructive/10"
                      onClick={handleReject}
                      disabled={processing}
                    >
                      Reject
                    </Button>
                    <Button 
                      className="flex-1 sm:flex-none bg-primary hover:bg-primary/90 text-primary-foreground"
                      onClick={handleApprove}
                      disabled={processing}
                    >
                      Approve Action
                    </Button>
                  </div>
                </div>
              ) : email.approval_status === "APPROVED" || email.approval_status === "REJECTED" ? (
                <div className={`border-b p-4 flex items-center gap-3 ${email.approval_status === "APPROVED" ? "bg-green-500/10 border-green-500/20 text-green-600 dark:text-green-400" : "bg-destructive/10 border-destructive/20 text-destructive"}`}>
                  {email.approval_status === "APPROVED" ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                  <p className="font-medium text-sm">Action {email.approval_status.toLowerCase()} by user.</p>
                </div>
              ) : null}

              {/* Execution Status */}
              <div className="p-5">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-foreground">
                    <Send className="w-4 h-4" />
                  </div>
                  <h3 className="font-semibold text-foreground text-base">Execution Status</h3>
                </div>
                
                {email.error_message ? (
                  <div className="bg-destructive/10 border border-destructive/20 rounded-xl p-4 text-sm text-destructive flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold mb-1">Execution Failed</p>
                      <p className="opacity-90">{email.error_message}</p>
                    </div>
                  </div>
                ) : email.execution_result ? (
                  <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-4 text-sm space-y-2">
                    <div className="flex items-center gap-2 text-green-600 dark:text-green-400 font-semibold mb-2">
                      <CheckCircle2 className="w-4 h-4" /> Action Executed Successfully
                    </div>
                    {Object.entries(email.execution_result).map(([key, value]) => (
                      <div key={key} className="flex gap-2 text-muted-foreground">
                        <span className="capitalize">{key.replace(/_/g, " ")}:</span>
                        <span className="font-medium text-foreground">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">
                    {email.approval_status === "PENDING" ? "Awaiting approval to execute." :
                     email.approval_status === "REJECTED" ? "Execution cancelled." :
                     "Execution details not available."}
                  </div>
                )}
              </div>
            </div>
          )}

        </div>

        {/* Right Column: Sidebar */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* Workflow Status Summary */}
          <div className="bg-card border border-border rounded-2xl shadow-sm p-5 sticky top-6">
            <h3 className="font-semibold text-foreground text-base mb-4 flex items-center gap-2">
              <Clock className="w-4 h-4 text-muted-foreground" /> Workflow State
            </h3>
            
            <div className="space-y-4 mb-6">
               <div className="flex justify-between items-center text-sm">
                 <span className="text-muted-foreground">Status</span>
                 <Badge variant="outline" className={
                    email.status === "COMPLETED" || email.status === "EXECUTED" ? "bg-green-500/10 text-green-500 border-green-500/20" :
                    email.status === "FAILED" ? "bg-destructive/10 text-destructive border-destructive/20" :
                    "bg-secondary text-foreground"
                 }>
                   {email.status}
                 </Badge>
               </div>
               {email.approval_status && (
                 <div className="flex justify-between items-center text-sm">
                   <span className="text-muted-foreground">Approval</span>
                   <span className={`font-medium ${
                     email.approval_status === "APPROVED" ? "text-green-500" :
                     email.approval_status === "REJECTED" ? "text-destructive" :
                     "text-orange-500"
                   }`}>
                     {email.approval_status}
                   </span>
                 </div>
               )}
            </div>

            <hr className="border-border mb-4" />
            
            <h4 className="text-sm font-medium text-muted-foreground mb-4">Timeline</h4>
            <div className="pl-1">
              <WorkflowTimeline steps={workflowSteps} />
            </div>
            
          </div>
        </div>
      </div>
    </div>
  );
}
