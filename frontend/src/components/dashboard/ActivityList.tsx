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

const mockActivities: Activity[] = [
  {
    id: "1",
    type: "EMAIL_RECEIVED",
    title: "Email Received",
    description: "New email from client@acme.com",
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
  },
  {
    id: "2",
    type: "AI_CLASSIFIED",
    title: "Classified",
    description: "Email classified as MEETING",
    timestamp: new Date(Date.now() - 1000 * 60 * 4.5),
  },
  {
    id: "3",
    type: "ACTION_PLANNED",
    title: "Action Planned",
    description: "Create Google Calendar Event for Tomorrow 2 PM",
    timestamp: new Date(Date.now() - 1000 * 60 * 4),
  },
  {
    id: "4",
    type: "APPROVAL_REQUESTED",
    title: "Approval Requested",
    description: "Medium risk action routed for user approval",
    timestamp: new Date(Date.now() - 1000 * 60 * 3),
  },
  {
    id: "5",
    type: "ACTION_EXECUTED",
    title: "Approved & Executed",
    description: "Calendar Event created automatically",
    timestamp: new Date(Date.now() - 1000 * 60 * 1),
  },
];

const getIcon = (type: ActivityType) => {
  switch (type) {
    case "EMAIL_RECEIVED": return <Mail className="w-4 h-4 text-primary" />;
    case "AI_CLASSIFIED": return <ShieldCheck className="w-4 h-4 text-foreground" />;
    case "ACTION_PLANNED": return <Clock className="w-4 h-4 text-warning" />;
    case "APPROVAL_REQUESTED": return <AlertCircle className="w-4 h-4 text-orange-500" />;
    case "ACTION_EXECUTED": return <CheckCircle2 className="w-4 h-4 text-success" />;
    default: return <Mail className="w-4 h-4 text-muted-foreground" />;
  }
};

export function ActivityList() {
  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
      <div className="px-6 py-4 border-b border-border bg-secondary/10 flex justify-between items-center">
        <h3 className="font-semibold text-foreground">Recent Activity</h3>
      </div>
      <div className="relative py-2 px-2 sm:px-4">
        {mockActivities.map((activity, index) => (
          <div key={activity.id} className="relative p-2 sm:p-3 flex gap-4 hover:bg-secondary/40 rounded-lg transition-colors group">
            {/* Timeline connected line */}
            {index !== mockActivities.length - 1 && (
              <div className="absolute left-[1.35rem] sm:left-[1.6rem] top-10 bottom-[-0.5rem] w-px bg-border group-hover:bg-primary/20 transition-colors" />
            )}
            
            <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0 mt-0.5 relative z-10 border-2 border-card group-hover:border-secondary/40 transition-colors">
              {getIcon(activity.type)}
            </div>
            
            <div className="flex-1 min-w-0 pt-1">
              <p className="text-sm font-medium text-foreground truncate">{activity.title}</p>
              <p className="text-sm text-muted-foreground truncate mt-0.5">{activity.description}</p>
            </div>
            
            <div className="shrink-0 text-xs text-muted-foreground whitespace-nowrap pt-2" suppressHydrationWarning>
              {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
