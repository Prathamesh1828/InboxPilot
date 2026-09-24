"use client";

import { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Search, Filter, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { auditApi } from "@/lib/api/emails";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [connectionState, setConnectionState] = useState<"Connecting..." | "Live" | "Reconnecting..." | "Offline">("Connecting...");


  useEffect(() => {
    let mounted = true;

    auditApi.getGlobalAudit(0, 50)
      .then(data => {
        if (!mounted) return;
        setLogs(data);
        setLoading(false);
      })
      .catch(console.error);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const token = localStorage.getItem("inboxpilot_token");
    let sseUrl = `${API_URL}/audit/stream`;
    if (token) sseUrl += `?token=${token}`;

    const sse = new EventSource(sseUrl, { withCredentials: true });

    sse.onopen = () => {
      if (mounted) setConnectionState("Live");
    };

    sse.onerror = () => {
      if (mounted) setConnectionState("Reconnecting...");
    };

    sse.addEventListener("connected", () => {
      if (mounted) setConnectionState("Live");
    });

    sse.addEventListener("audit_log", (e) => {
      if (!mounted) return;
      try {
        const newEvent = JSON.parse(e.data);
        setLogs(prev => {
          // Avoid duplicates
          if (prev.some(log => log.id === newEvent.id)) return prev;
          
          // Adding a temporary "isNew" flag for animation highlight
          const eventWithFlag = { ...newEvent, isNew: true };
          
          // Remove the isNew flag after animation duration
          setTimeout(() => {
            if (mounted) {
              setLogs(current => current.map(l => l.id === newEvent.id ? { ...l, isNew: false } : l));
            }
          }, 2000);

          return [eventWithFlag, ...prev];
        });
      } catch (err) {
        console.error("Failed to parse SSE audit log", err);
      }
    });

    return () => {
      mounted = false;
      sse.close();
      setConnectionState("Offline");
    };
  }, []);
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
              Audit Logs
              <Badge variant={connectionState === "Live" ? "default" : "secondary"} className="text-xs transition-colors bg-green-500/10 text-green-600 border-green-500/20 hover:bg-green-500/20 font-normal">
                {connectionState === "Live" && <span className="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5 animate-pulse" />}
                {connectionState}
              </Badge>
            </h1>
            <p className="text-muted-foreground mt-1">Complete history of all automated actions and decisions.</p>
          </div>
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
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">
                    Loading audit logs...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">
                    No audit logs found.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className={`transition-colors duration-1000 ${log.isNew ? 'bg-primary/10' : 'hover:bg-secondary/5'}`}>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Activity className="w-4 h-4 text-muted-foreground" />
                        <span className="font-medium text-foreground">{log.event_type}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">{log.action || "-"}</td>
                    <td className="px-6 py-4">
                      <Badge variant="outline" className={
                        log.status === "SUCCESS" ? "border-green-500/20 text-green-600 bg-green-500/10" :
                        log.status === "FAILED" ? "border-destructive/20 text-destructive bg-destructive/10" :
                        "border-yellow-500/20 text-yellow-600 bg-yellow-500/10"
                      }>
                        {log.status || "INFO"}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground whitespace-nowrap" suppressHydrationWarning>
                      {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link href={`/inbox/${log.email_id}`} className="text-primary hover:underline font-medium">
                        View Email
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
