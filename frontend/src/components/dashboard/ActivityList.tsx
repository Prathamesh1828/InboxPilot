"use client";

import { CheckCircle2, ShieldCheck, AlertCircle, XCircle, ArrowRight } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";

type ActivityType = "EMAIL_RECEIVED" | "AI_CLASSIFIED" | "ACTION_PLANNED" | "APPROVAL_REQUESTED" | "ACTION_EXECUTED";

interface Activity {
  id: string;
  type: ActivityType;
  title: string;
  description: string;
  timestamp: Date;
}

interface ActivityListProps {
  activities: any[];
}

const getIcon = (title: string) => {
  if (title.includes("approved")) return <CheckCircle2 className="w-4 h-4 text-green-500" />;
  if (title.includes("completed")) return <CheckCircle2 className="w-4 h-4 text-green-500" />;
  if (title.includes("processed") || title.includes("No action required")) return <CheckCircle2 className="w-4 h-4 text-green-500" />;
  if (title.includes("required") || title.includes("requested")) return <ShieldCheck className="w-4 h-4 text-orange-500" />;
  if (title.includes("failed") || title.includes("rejected")) return <XCircle className="w-4 h-4 text-destructive" />;
  return <CheckCircle2 className="w-4 h-4 text-green-500" />;
};

export function ActivityList({ activities }: ActivityListProps) {
  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm flex flex-col">
      <div className="px-6 py-4 border-b border-border bg-secondary/10 flex justify-between items-center shrink-0">
        <h3 className="font-semibold text-foreground">Recent Activity</h3>
        <Link href="/audit" className="text-sm font-medium text-primary hover:underline flex items-center gap-1">
          View all <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
      <div className="relative py-2 px-2 sm:px-4">
        {activities.length === 0 ? (
          <div className="p-4 text-center text-sm text-muted-foreground">No recent activity</div>
        ) : (
          activities.map((activity, index) => (
            <Link key={activity.id} href={`/inbox/${activity.email_id}`} className="block">
              <div className="relative p-3 sm:p-4 flex gap-4 hover:bg-secondary/40 rounded-lg transition-colors group">
                {/* Timeline connected line */}
                {index !== activities.length - 1 && (
                  <div className="absolute left-[1.6rem] sm:left-[1.85rem] top-12 bottom-[-1rem] w-px bg-border group-hover:bg-primary/20 transition-colors" />
                )}
                
                <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0 mt-0.5 relative z-10 border-2 border-card group-hover:border-secondary/40 transition-colors">
                  {getIcon(activity.title)}
                </div>
                
                <div className="flex-1 min-w-0 pt-0.5 space-y-1">
                  <div className="flex items-center justify-between gap-4">
                    <p className="text-[15px] font-semibold text-foreground truncate">
                      {activity.title}
                    </p>
                    <div className="shrink-0 text-xs text-muted-foreground whitespace-nowrap" suppressHydrationWarning>
                      {formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })}
                    </div>
                  </div>
                  
                  <p className="text-sm text-muted-foreground truncate">
                    &quot;{activity.email_subject}&quot;
                  </p>
                  
                  <p className="text-sm font-medium text-muted-foreground truncate">
                    {activity.email_category && (
                      <span className="capitalize">{activity.email_category.toLowerCase()}</span>
                    )}
                    {activity.email_category && activity.description && <span className="mx-1.5">•</span>}
                    {activity.description}
                  </p>
                </div>
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
