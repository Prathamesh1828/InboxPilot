"use client";

import { useEffect, useState, useCallback } from "react";
import { Input } from "@/components/ui/input";
import { Search, Filter, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { formatDistanceToNow, subDays } from "date-fns";
import { auditApi, AuditQueryParams } from "@/lib/api/emails";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";

function formatEventType(eventType: string) {
  const mapping: Record<string, string> = {
    "WORKFLOW_COMPLETED": "Workflow Completed",
    "EXECUTION_STARTED": "Action Started",
    "EXECUTION_COMPLETED": "Action Completed",
    "SAFETY_EVALUATED": "Safety Check",
    "GROUNDING_PASSED": "Information Verified"
  };
  return mapping[eventType] || eventType;
}

function formatAction(action: string | null) {
  if (!action) return "-";
  const mapping: Record<string, string> = {
    "ARCHIVE": "Archive",
    "NO_ACTION": "No Action",
    "DRAFT_REPLY": "Draft Reply",
    "CREATE_CALENDAR_EVENT": "Add to Calendar",
  };
  return mapping[action] || action;
}

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [connectionState, setConnectionState] = useState<"Connecting..." | "Live" | "Reconnecting..." | "Offline">("Connecting...");
  
  // Filters State
  const [search, setSearch] = useState("");
  const [eventTypeFilter, setEventTypeFilter] = useState("All");
  const [actionFilter, setActionFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");
  const [timeRange, setTimeRange] = useState("All Time");
  
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  const fetchLogs = useCallback(() => {
    setLoading(true);
    
    const params: AuditQueryParams = { skip: 0, limit: 50 };
    
    if (search) params.search = search;
    if (eventTypeFilter !== "All") params.event_type = eventTypeFilter;
    if (actionFilter !== "All") params.action = actionFilter;
    if (statusFilter !== "All") params.status = statusFilter;
    
    if (timeRange === "Today") {
      params.date_from = new Date(new Date().setHours(0,0,0,0)).toISOString();
    } else if (timeRange === "Last 7 Days") {
      params.date_from = subDays(new Date(), 7).toISOString();
    } else if (timeRange === "Last 30 Days") {
      params.date_from = subDays(new Date(), 30).toISOString();
    }

    auditApi.getGlobalAudit(params)
      .then(data => {
        setLogs(data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [search, eventTypeFilter, actionFilter, statusFilter, timeRange]);

  // Initial load & filter changes
  useEffect(() => {
    // Debounce search
    const handler = setTimeout(() => {
      fetchLogs();
    }, 300);
    return () => clearTimeout(handler);
  }, [fetchLogs]);

  // SSE Real-time logic
  useEffect(() => {
    let mounted = true;
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
        
        // Client-side filtering check for SSE events
        if (eventTypeFilter !== "All" && newEvent.event_type !== eventTypeFilter) return;
        if (actionFilter !== "All" && newEvent.action !== actionFilter) return;
        if (statusFilter !== "All" && newEvent.status !== statusFilter) return;
        if (search) {
           const match = (newEvent.event_type || "").toLowerCase().includes(search.toLowerCase()) || 
                         (newEvent.action || "").toLowerCase().includes(search.toLowerCase()) ||
                         (newEvent.status || "").toLowerCase().includes(search.toLowerCase());
           if (!match) return;
        }

        setLogs(prev => {
          if (prev.some(log => log.id === newEvent.id)) return prev;
          
          const eventWithFlag = { ...newEvent, isNew: true };
          
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
  }, [eventTypeFilter, actionFilter, statusFilter, search]);

  const clearFilters = () => {
    setEventTypeFilter("All");
    setActionFilter("All");
    setStatusFilter("All");
    setTimeRange("All Time");
    setIsFilterOpen(false);
  };

  const activeFilterCount = [
    eventTypeFilter !== "All",
    actionFilter !== "All",
    statusFilter !== "All",
    timeRange !== "All Time"
  ].filter(Boolean).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
              Audit Logs
              <Badge variant={connectionState === "Live" ? "default" : "secondary"} className="text-xs transition-colors bg-green-500/10 text-green-600 border-green-500/20 font-normal">
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
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 w-full sm:w-[300px] bg-card border-border"
            />
          </div>
          
          <Popover open={isFilterOpen} onOpenChange={setIsFilterOpen}>
            <PopoverTrigger className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 relative">
              <Filter className="h-4 w-4 mr-2" />
              Filters
              {activeFilterCount > 0 && (
                <span className="ml-2 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] text-primary-foreground">
                  {activeFilterCount}
                </span>
              )}
            </PopoverTrigger>
            <PopoverContent className="w-80" align="end">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium leading-none text-sm">Filters</h4>
                  {activeFilterCount > 0 && (
                    <Button variant="ghost" size="sm" onClick={clearFilters} className="h-auto p-0 text-xs text-muted-foreground hover:text-foreground">
                      Clear filters
                    </Button>
                  )}
                </div>
                
                <div className="grid gap-2">
                  <div className="grid gap-1">
                    <label className="text-xs text-muted-foreground">Event Type</label>
                    <Select value={eventTypeFilter} onValueChange={(val) => setEventTypeFilter(val as string)}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="All">All</SelectItem>
                        <SelectItem value="WORKFLOW_COMPLETED">Workflow Completed</SelectItem>
                        <SelectItem value="EXECUTION_STARTED">Action Started</SelectItem>
                        <SelectItem value="EXECUTION_COMPLETED">Action Completed</SelectItem>
                        <SelectItem value="SAFETY_EVALUATED">Safety Check</SelectItem>
                        <SelectItem value="GROUNDING_PASSED">Information Verified</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="grid gap-1">
                    <label className="text-xs text-muted-foreground">Action</label>
                    <Select value={actionFilter} onValueChange={(val) => setActionFilter(val as string)}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="All">All</SelectItem>
                        <SelectItem value="ARCHIVE">Archive</SelectItem>
                        <SelectItem value="NO_ACTION">No Action</SelectItem>
                        <SelectItem value="DRAFT_REPLY">Draft Reply</SelectItem>
                        <SelectItem value="CREATE_CALENDAR_EVENT">Add to Calendar</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="grid gap-1">
                    <label className="text-xs text-muted-foreground">Status</label>
                    <Select value={statusFilter} onValueChange={(val) => setStatusFilter(val as string)}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="All">All</SelectItem>
                        <SelectItem value="SUCCESS">SUCCESS</SelectItem>
                        <SelectItem value="PENDING">PENDING</SelectItem>
                        <SelectItem value="FAILED">FAILED</SelectItem>
                        <SelectItem value="INFO">INFO</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="grid gap-1">
                    <label className="text-xs text-muted-foreground">Time Range</label>
                    <Select value={timeRange} onValueChange={(val) => setTimeRange(val as string)}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="All Time">All Time</SelectItem>
                        <SelectItem value="Today">Today</SelectItem>
                        <SelectItem value="Last 7 Days">Last 7 Days</SelectItem>
                        <SelectItem value="Last 30 Days">Last 30 Days</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {activeFilterCount > 0 && (
        <div className="flex flex-wrap gap-2 items-center">
          <span className="text-sm text-muted-foreground">Active filters:</span>
          {eventTypeFilter !== "All" && (
            <Badge variant="secondary" className="flex items-center gap-1 font-normal bg-secondary">
              Event: {formatEventType(eventTypeFilter)}
              <X className="h-3 w-3 cursor-pointer hover:text-foreground" onClick={() => setEventTypeFilter("All")} />
            </Badge>
          )}
          {actionFilter !== "All" && (
            <Badge variant="secondary" className="flex items-center gap-1 font-normal bg-secondary">
              Action: {formatAction(actionFilter)}
              <X className="h-3 w-3 cursor-pointer hover:text-foreground" onClick={() => setActionFilter("All")} />
            </Badge>
          )}
          {statusFilter !== "All" && (
            <Badge variant="secondary" className="flex items-center gap-1 font-normal bg-secondary">
              Status: {statusFilter}
              <X className="h-3 w-3 cursor-pointer hover:text-foreground" onClick={() => setStatusFilter("All")} />
            </Badge>
          )}
          {timeRange !== "All Time" && (
            <Badge variant="secondary" className="flex items-center gap-1 font-normal bg-secondary">
              Time: {timeRange}
              <X className="h-3 w-3 cursor-pointer hover:text-foreground" onClick={() => setTimeRange("All Time")} />
            </Badge>
          )}
        </div>
      )}

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
                [...Array(10)].map((_, i) => (
                  <tr key={i} className="animate-in fade-in duration-500">
                    <td className="px-6 py-4"><Skeleton className="h-5 w-[150px]" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-5 w-[100px]" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-6 w-[80px] rounded-full" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-5 w-[100px]" /></td>
                    <td className="px-6 py-4 text-right flex justify-end"><Skeleton className="h-5 w-[80px]" /></td>
                  </tr>
                ))
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">
                    No audit logs found. Try adjusting your filters.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className={`transition-colors duration-1000 ${log.isNew ? 'bg-primary/10' : 'hover:bg-secondary/5'}`}>
                    <td className="px-6 py-4">
                      <span className="font-medium text-foreground">{formatEventType(log.event_type)}</span>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">{formatAction(log.action)}</td>
                    <td className="px-6 py-4">
                      <Badge variant="outline" className={
                        log.status === "SUCCESS" || log.status === "Executed" ? "border-green-500/20 text-green-600 bg-green-500/10" :
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
                      {log.email_id ? (
                        <Link href={`/inbox/${log.email_id}`} className="text-primary hover:underline font-medium">
                          View Email
                        </Link>
                      ) : (
                        <span className="text-muted-foreground italic text-xs">No email linked</span>
                      )}
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
