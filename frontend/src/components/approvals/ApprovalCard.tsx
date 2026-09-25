"use client";

import { useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ShieldCheck, Calendar, ArrowRight, Loader2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { motion } from "framer-motion";

export interface ApprovalData {
  id: string;
  emailId: string;
  emailSubject: string;
  emailSender: string;
  action: string;
  reasoning: string;
  risk: "LOW" | "MEDIUM" | "HIGH";
  parameters: Record<string, string>;
  status: "PENDING" | "APPROVED" | "REJECTED" | "EXECUTING" | "EXECUTED" | "FAILED";
  timestamp: Date;
}

interface ApprovalCardProps {
  approval: ApprovalData;
  onApprove: (id: string) => Promise<void>;
  onReject: (id: string) => Promise<void>;
  onRemove: (id: string) => void;
}

export function ApprovalCard({ approval, onApprove, onReject, onRemove }: ApprovalCardProps) {
  const [isApproving, setIsApproving] = useState(false);
  const [isRejecting, setIsRejecting] = useState(false);
  const [isExiting, setIsExiting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleApprove = async () => {
    if (isApproving || isRejecting || isExiting) return;
    setIsApproving(true);
    setError(null);
    try {
      await onApprove(approval.id);
      setIsExiting(true);
      setTimeout(() => onRemove(approval.id), 300);
    } catch (err) {
      console.error(err);
      setError("Failed to approve. Please try again.");
      setIsApproving(false);
    }
  };

  const handleReject = async () => {
    if (isApproving || isRejecting || isExiting) return;
    setIsRejecting(true);
    setError(null);
    try {
      await onReject(approval.id);
      setIsExiting(true);
      setTimeout(() => onRemove(approval.id), 300);
    } catch (err) {
      console.error(err);
      setError("Failed to reject. Please try again.");
      setIsRejecting(false);
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 1, scale: 1, height: "auto" }}
      animate={isExiting ? { opacity: 0, scale: 0.95, height: 0, overflow: "hidden", marginTop: 0, marginBottom: 0 } : { opacity: 1, scale: 1, height: "auto" }}
      transition={{ duration: 0.3 }}
      className={`bg-card border ${error ? "border-destructive" : "border-border"} rounded-xl shadow-sm flex flex-col hover:-translate-y-1 hover:shadow-md transition-all duration-300 ${isExiting ? "pointer-events-none" : ""}`}
    >
      <div className="p-5 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Calendar className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-lg text-foreground">{approval.action}</h3>
          </div>
          <div className="mb-2">
            <p className="text-sm font-medium text-foreground">{approval.emailSubject}</p>
            <p className="text-xs text-muted-foreground">From: {approval.emailSender}</p>
          </div>
          <p className="text-sm text-muted-foreground line-clamp-2">{approval.reasoning}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Badge variant="outline" className="border-orange-500/20 bg-orange-500/10 text-orange-500">
            <ShieldCheck className="w-3 h-3 mr-1" />
            {approval.risk} RISK
          </Badge>
          <span className="text-xs text-muted-foreground whitespace-nowrap" suppressHydrationWarning>
            {formatDistanceToNow(approval.timestamp, { addSuffix: true })}
          </span>
        </div>
      </div>

      <div className="p-5 flex-1 bg-secondary/10">
        <h4 className="text-sm font-medium text-muted-foreground mb-3">Extracted Parameters</h4>
        <div className="space-y-2">
          {Object.entries(approval.parameters).map(([key, value]) => (
            <div key={key} className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2 text-sm">
              <span className="font-medium text-foreground w-24 shrink-0">{key}:</span>
              <span className="text-muted-foreground bg-background px-2 py-1 rounded border border-border flex-1 truncate">{value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-4 border-t border-border bg-background flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <Link href={`/inbox/${approval.emailId}`}>
          <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
            View Source Email <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </Link>
        <div className="flex items-center gap-2">
          {error && <span className="text-xs text-destructive mr-2 font-medium">{error}</span>}
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleReject} 
            disabled={isApproving || isRejecting || isExiting}
            className="border-border hover:bg-destructive/10 text-destructive w-24"
          >
            {isRejecting ? <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Rejecting...</> : "Reject"}
          </Button>
          <Button 
            size="sm" 
            onClick={handleApprove} 
            disabled={isApproving || isRejecting || isExiting}
            className="bg-primary text-primary-foreground hover:bg-primary/90 w-44"
          >
            {isApproving ? <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Approving...</> : "Approve & Execute"}
          </Button>
        </div>
      </div>
    </motion.div>
  );
}
