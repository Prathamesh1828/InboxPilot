"use client";

import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";
import { motion } from "framer-motion";

export type EmailStatus = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED" | "APPROVAL_PENDING" | "EXECUTED" | "REJECTED" | "IMPORTED";
export type EmailCategory = "BILL" | "MEETING" | "FORM" | "REMINDER" | "SPAM" | "OTHER";

export interface EmailData {
  id: string;
  sender: string;
  subject: string;
  preview: string;
  category: EmailCategory;
  confidence: number | null;
  reasoning?: string;
  status: EmailStatus;
  timestamp: Date;
  isUnread: boolean;
  recipients?: string[];
}

interface EmailRowProps {
  email: EmailData;
}

const categoryColors: Record<string, string> = {
  BILL: "bg-red-500/10 text-red-500 border-red-500/20",
  MEETING: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  FORM: "bg-purple-500/10 text-purple-500 border-purple-500/20",
  REMINDER: "bg-yellow-500/10 text-yellow-600 border-yellow-500/20",
  SPAM: "bg-slate-500/10 text-slate-500 border-slate-500/20",
  OTHER: "bg-secondary text-muted-foreground border-border",
};

const statusColors: Record<string, string> = {
  PENDING: "bg-yellow-500/10 text-yellow-600",
  PROCESSING: "bg-blue-500/10 text-blue-600",
  COMPLETED: "bg-green-500/10 text-green-600",
  FAILED: "bg-destructive/10 text-destructive",
  APPROVAL_PENDING: "bg-orange-500/10 text-orange-600",
  EXECUTED: "bg-green-500/10 text-green-600",
  REJECTED: "bg-red-500/10 text-red-600",
  IMPORTED: "bg-slate-500/10 text-slate-500",
};

export function EmailRow({ email }: EmailRowProps) {
  const router = useRouter();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      onClick={() => router.push(`/inbox/${email.id}`)}
      className={`group flex flex-col lg:flex-row lg:items-center gap-2 lg:gap-4 px-4 py-3 cursor-pointer border-b border-border transition-colors hover:bg-secondary/30 ${
        email.isUnread ? "bg-secondary/10" : "bg-transparent"
      }`}
    >
      <div className="flex items-center gap-4 flex-1 min-w-0 w-full lg:w-auto">
        <div className="w-2 shrink-0 hidden lg:block">
          {email.isUnread && <div className="w-2 h-2 rounded-full bg-primary" />}
        </div>
        
        <div className="w-full lg:w-1/4 lg:min-w-[120px] lg:max-w-[200px] shrink-0 truncate">
          <span 
            className={`text-sm ${email.isUnread ? "font-bold text-foreground" : "font-medium text-foreground/80"}`}
            title={email.sender}
          >
            {email.sender}
          </span>
        </div>
        
        <div className="flex-1 min-w-0 flex items-center gap-2 truncate">
          <span 
            className={`text-sm truncate ${email.isUnread ? "font-bold text-foreground" : "text-foreground/80"}`}
            title={email.subject}
          >
            {email.subject}
          </span>
          <span 
            className="text-sm text-muted-foreground truncate hidden lg:inline-block min-w-0"
            title={email.preview}
          >
            <span className="mx-1 shrink-0">-</span>
            {email.preview}
          </span>
        </div>
      </div>
      
      {/* Mobile-only Preview */}
      <div className="text-sm text-muted-foreground truncate block lg:hidden w-full px-0 pl-0">
        {email.preview}
      </div>
      
      <div className="flex items-center justify-between lg:justify-end gap-2 lg:gap-4 w-full lg:w-[380px] shrink-0 mt-2 lg:mt-0">
        <div className="flex items-center gap-2 lg:w-[260px] lg:justify-start shrink-0">
          <Badge variant="outline" className={`text-[10px] uppercase font-bold tracking-wider lg:w-[70px] justify-center ${email.category ? (categoryColors[email.category] || categoryColors.OTHER) : "text-muted-foreground border-border/50 bg-transparent"}`}>
            {email.category || "--"}
          </Badge>
          <span className="text-xs text-muted-foreground font-medium w-auto lg:w-[60px] text-center inline-block">
            {email.confidence !== null ? `${email.confidence}%` : "--"}
          </span>
          <Badge variant="secondary" className={`text-[10px] uppercase truncate lg:w-[100px] justify-center ${statusColors[email.status] || statusColors.PENDING}`}>
            {email.status}
          </Badge>
        </div>
        
        <div className="shrink-0 text-xs text-muted-foreground lg:w-[100px] text-center whitespace-nowrap">
          {formatDistanceToNow(new Date(email.timestamp), { addSuffix: true }).replace("about ", "")}
        </div>
      </div>
    </motion.div>
  );
}
