"use client";

import { useState, useEffect } from "react";
import { ApprovalData, ApprovalCard } from "@/components/approvals/ApprovalCard";
import { CheckSquare } from "lucide-react";

const initialApprovals: ApprovalData[] = [
  {
    id: "app_1",
    emailId: "1",
    action: "CREATE_CALENDAR_EVENT",
    reasoning: "The email explicitly suggests a time for a 'sync up' and 'planning', which indicates a meeting.",
    risk: "MEDIUM",
    parameters: {
      title: "Q3 Planning Meeting with Alex",
      time: "Tomorrow at 2:00 PM",
      participants: "alex@acme.com",
    },
    status: "PENDING",
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
  },
  {
    id: "app_2",
    emailId: "5",
    action: "SEND_DRAFT_REPLY",
    reasoning: "The client asked for our standard pricing tier info. I have prepared a draft with the standard template.",
    risk: "MEDIUM",
    parameters: {
      to: "client@example.com",
      subject: "Re: Pricing inquiry",
      draft: "Hi there,\n\nOur standard pricing starts at $49/mo. Let me know if you need a demo.",
    },
    status: "PENDING",
    timestamp: new Date(Date.now() - 1000 * 60 * 45),
  },
];

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<ApprovalData[]>([]);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setApprovals(initialApprovals);
      setIsReady(true);
    }, 800);
    return () => clearTimeout(timer);
  }, []);

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


  const handleApprove = (id: string) => {
    setApprovals(current => current.filter(app => app.id !== id));
  };

  const handleReject = (id: string) => {
    setApprovals(current => current.filter(app => app.id !== id));
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
