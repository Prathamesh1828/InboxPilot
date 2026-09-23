"use client";

import { Mail, Clock, CheckCircle2, ShieldCheck, AlertCircle } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

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

const getIcon = (type: string) => {
  switch (type) {
    case "EMAIL_RECEIVED": return <Mail className="w-4 h-4 text-primary" />;
    case "CLASSIFICATION": return <ShieldCheck className="w-4 h-4 text-foreground" />;
    case "PLANNING": return <Clock className="w-4 h-4 text-warning" />;
    case "APPROVAL_REQUESTED": return <AlertCircle className="w-4 h-4 text-orange-500" />;
    case "ACTION_EXECUTED": return <CheckCircle2 className="w-4 h-4 text-success" />;
    default: return <Mail className="w-4 h-4 text-muted-foreground" />;
  }
};

export function ActivityList({ activities }: ActivityListProps) {
  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
      <div className="px-6 py-4 border-b border-border bg-secondary/10 flex justify-between items-center">
        <h3 className="font-semibold text-foreground">Recent Activity</h3>
      </div>
      <div className="relative py-2 px-2 sm:px-4">
        {activities.length === 0 ? (
          <div className="p-4 text-center text-sm text-muted-foreground">No recent activity</div>
        ) : (
          activities.map((activity, index) => (
            <div key={activity.id} className="relative p-2 sm:p-3 flex gap-4 hover:bg-secondary/40 rounded-lg transition-colors group">
              {/* Timeline connected line */}
              {index !== activities.length - 1 && (
                <div className="absolute left-[1.35rem] sm:left-[1.6rem] top-10 bottom-[-0.5rem] w-px bg-border group-hover:bg-primary/20 transition-colors" />
              )}
              
              <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0 mt-0.5 relative z-10 border-2 border-card group-hover:border-secondary/40 transition-colors">
                {getIcon(activity.event_type)}
              </div>
              
              <div className="flex-1 min-w-0 pt-1">
                <p className="text-sm font-medium text-foreground truncate">
                  {activity.event_type} {activity.status && `- ${activity.status}`}
                </p>
                <p className="text-sm text-muted-foreground truncate mt-0.5">
                  Email ID: {activity.email_id}
                </p>
              </div>
              
              <div className="shrink-0 text-xs text-muted-foreground whitespace-nowrap pt-2" suppressHydrationWarning>
                {formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
