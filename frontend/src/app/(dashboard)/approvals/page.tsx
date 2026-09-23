"use client";

import { useState, useEffect, useCallback } from "react";
import { ApprovalData, ApprovalCard } from "@/components/approvals/ApprovalCard";
import { CheckSquare, Loader2 } from "lucide-react";
import { approvalsApi } from "@/lib/api/emails";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<ApprovalData[]>([]);
  const [isReady, setIsReady] = useState(false);

  const fetchApprovals = useCallback(async () => {
    try {
      const data = await approvalsApi.getPending();
      
      // Map the backend ApprovalResponse to the frontend ApprovalData type
      const mappedApprovals = data.map((item: any) => ({
        id: String(item.id),
        emailId: String(item.email_id),
        emailSubject: item.email_subject || "No Subject",
        emailSender: item.email_sender || "Unknown Sender",
        action: item.action,
        reasoning: item.action_plan?.reasoning || "Review required for action execution.",
        risk: item.action_plan?.risk_level || "MEDIUM",
        parameters: item.action_plan?.parameters || {},
        status: item.status,
        timestamp: new Date(item.created_at)
      }));
      
      setApprovals(mappedApprovals);
    } catch (error) {
      console.error("Failed to fetch approvals:", error);
    } finally {
      setIsReady(true);
    }
  }, []);

  useEffect(() => {
    fetchApprovals();
  }, [fetchApprovals]);

  if (!isReady) {
    return (
      <div className="space-y-6 animate-in fade-in duration-500">
        <div>
          <div className="h-9 w-48 mb-2 bg-secondary/50 animate-pulse rounded-md" />
          <div className="h-5 w-96 bg-secondary/50 animate-pulse rounded-md" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-card border border-border rounded-xl shadow-sm overflow-hidden h-64 animate-pulse"></div>
          ))}
        </div>
      </div>
    );
  }


  const handleApprove = async (id: string) => {
    try {
      await approvalsApi.approve(id);
      setApprovals(current => current.filter(app => app.id !== id));
    } catch (error) {
      console.error("Approval failed:", error);
    }
  };

  const handleReject = async (id: string) => {
    try {
      await approvalsApi.reject(id);
      setApprovals(current => current.filter(app => app.id !== id));
    } catch (error) {
      console.error("Rejection failed:", error);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Approvals</h1>
        <p className="text-muted-foreground mt-1">Review actions proposed by InboxPilot before they execute.</p>
      </div>

      {approvals.length === 0 ? (
        <div className="bg-card border border-border rounded-xl p-12 text-center flex flex-col items-center">
          <div className="w-16 h-16 bg-green-500/10 text-green-500 rounded-full flex items-center justify-center mb-4">
            <CheckSquare className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-semibold text-foreground mb-2">You&apos;re all caught up!</h2>
          <p className="text-muted-foreground max-w-md">
            There are no actions requiring your attention right now. Enjoy your automated inbox.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {approvals.map(approval => (
            <ApprovalCard 
              key={approval.id} 
              approval={approval} 
              onApprove={handleApprove}
              onReject={handleReject}
            />
          ))}
        </div>
      )}
    </div>
  );
}
