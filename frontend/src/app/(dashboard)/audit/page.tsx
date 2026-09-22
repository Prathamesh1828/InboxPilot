import { Metadata } from "next";
import { Input } from "@/components/ui/input";
import { Search, Filter, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";

export const metadata: Metadata = {
  title: "Audit Logs | InboxPilot",
};

interface AuditLog {
  id: string;
  emailId: string;
  event: string;
  action: string;
  status: "SUCCESS" | "FAILED" | "PENDING";
  timestamp: Date;
}

const mockLogs: AuditLog[] = [
  {
    id: "log_1",
    emailId: "1",
    event: "ACTION_EXECUTED",
    action: "CREATE_CALENDAR_EVENT",
    status: "SUCCESS",
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
  },
  {
    id: "log_2",
    emailId: "1",
    event: "APPROVAL_APPROVED",
    action: "CREATE_CALENDAR_EVENT",
    status: "SUCCESS",
    timestamp: new Date(Date.now() - 1000 * 60 * 6),
  },
  {
    id: "log_3",
    emailId: "1",
    event: "APPROVAL_REQUESTED",
    action: "CREATE_CALENDAR_EVENT",
    status: "SUCCESS",
    timestamp: new Date(Date.now() - 1000 * 60 * 10),
  },
  {
    id: "log_4",
    emailId: "1",
    event: "AI_CLASSIFIED",
    action: "CLASSIFY_MEETING",
    status: "SUCCESS",
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
  },
  {
    id: "log_5",
    emailId: "2",
    event: "ACTION_FAILED",
    action: "SEND_DRAFT_REPLY",
    status: "FAILED",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
  },
];

export default function AuditLogsPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Audit Logs</h1>
          <p className="text-muted-foreground mt-1">Complete history of all automated actions and decisions.</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search logs..."
              className="pl-8 w-full sm:w-[300px] bg-card border-border"
            />
          </div>
          <Button variant="outline" size="icon" className="shrink-0 border-border">
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground uppercase bg-secondary/10 border-b border-border">
              <tr>
                <th className="px-6 py-4 font-medium">Event</th>
                <th className="px-6 py-4 font-medium">Action</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium">Timestamp</th>
                <th className="px-6 py-4 font-medium text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {mockLogs.map((log) => (
                <tr key={log.id} className="hover:bg-secondary/5 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-muted-foreground" />
                      <span className="font-medium text-foreground">{log.event}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-muted-foreground">{log.action}</td>
                  <td className="px-6 py-4">
                    <Badge variant="outline" className={
                      log.status === "SUCCESS" ? "border-green-500/20 text-green-600 bg-green-500/10" :
                      log.status === "FAILED" ? "border-destructive/20 text-destructive bg-destructive/10" :
                      "border-yellow-500/20 text-yellow-600 bg-yellow-500/10"
                    }>
                      {log.status}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-muted-foreground whitespace-nowrap" suppressHydrationWarning>
                    {formatDistanceToNow(log.timestamp, { addSuffix: true })}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link href={`/inbox/${log.emailId}`} className="text-primary hover:underline font-medium">
                      View Email
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
