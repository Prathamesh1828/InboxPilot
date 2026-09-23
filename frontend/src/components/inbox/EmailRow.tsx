"use client";

import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";
import { motion } from "framer-motion";

export type EmailStatus = "PENDING" | "PROCESSED" | "FAILED";
export type EmailCategory = "BILL" | "MEETING" | "FORM" | "REMINDER" | "SPAM" | "OTHER";

export interface EmailData {
  id: string;
  sender: string;
  subject: string;
  preview: string;
  category: EmailCategory;
  confidence: number;
  status: EmailStatus;
  timestamp: Date;
  isUnread: boolean;
}

interface EmailRowProps {
  email: EmailData;
}

const categoryColors: Record<EmailCategory, string> = {
  BILL: "bg-red-500/10 text-red-500 border-red-500/20",
  MEETING: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  FORM: "bg-purple-500/10 text-purple-500 border-purple-500/20",
  REMINDER: "bg-yellow-500/10 text-yellow-600 border-yellow-500/20",
  SPAM: "bg-slate-500/10 text-slate-500 border-slate-500/20",
  OTHER: "bg-secondary text-muted-foreground border-border",
};

const statusColors: Record<EmailStatus, string> = {
  PENDING: "bg-yellow-500/10 text-yellow-600",
  PROCESSED: "bg-green-500/10 text-green-600",
  FAILED: "bg-destructive/10 text-destructive",
};

export function EmailRow({ email }: EmailRowProps) {
  const router = useRouter();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      onClick={() => router.push(`/inbox/${email.id}`)}
      className={`group flex items-center gap-4 px-4 py-3 cursor-pointer border-b border-border transition-colors hover:bg-secondary/30 ${
        email.isUnread ? "bg-secondary/10" : "bg-transparent"
      }`}
    >
      <div className="w-2 shrink-0">
        {email.isUnread && <div className="w-2 h-2 rounded-full bg-primary" />}
      </div>
      
      <div className="w-1/4 min-w-[150px] shrink-0 truncate">
        <span className={`text-sm ${email.isUnread ? "font-bold text-foreground" : "font-medium text-foreground/80"}`}>
          {email.sender}
        </span>
      </div>
      
      <div className="flex-1 min-w-0 flex items-center gap-2">
        <span className={`text-sm truncate ${email.isUnread ? "font-bold text-foreground" : "text-foreground/80"}`}>
          {email.subject}
        </span>
        <span className="text-sm text-muted-foreground truncate hidden md:inline-block">
          <span className="mx-1">-</span>
          {email.preview}
        </span>
      </div>
      
      <div className="hidden lg:flex shrink-0 items-center gap-2 w-[220px]">
        <Badge variant="outline" className={`text-[10px] uppercase font-bold tracking-wider ${categoryColors[email.category]}`}>
          {email.category}
        </Badge>
        <span className="text-xs text-muted-foreground font-medium w-12 text-right">
          {email.confidence}%
        </span>
        <Badge variant="secondary" className={`text-[10px] uppercase ${statusColors[email.status]}`}>
          {email.status}
        </Badge>
      </div>
      
      <div className="shrink-0 text-xs text-muted-foreground w-20 text-right whitespace-nowrap">
        {formatDistanceToNow(new Date(email.timestamp), { addSuffix: true }).replace("about ", "")}
      </div>
    </motion.div>
  );
}
