"use client";

import { useEffect, useState } from "react";
import { Mail, CheckSquare, Zap, Percent } from "lucide-react";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { ActivityList } from "@/components/dashboard/ActivityList";
import { Greeting } from "@/components/dashboard/Greeting";
import Link from "next/link";
import { dashboardApi } from "@/lib/api/emails";

export default function DashboardPage() {
  const [stats, setStats] = useState({
    emails_processed: 0,
    pending_approvals: 0,
    actions_executed: 0,
    automation_rate: 0,
    system_status: {
      gmail_integration: "Not Connected",
      google_calendar: "Not Connected",
      telegram: "Not Connected"
    },
    recent_activity: []
  });

  const fetchStats = () => {
    dashboardApi.getStats()
      .then(setStats)
      .catch(console.error);
  };

  useEffect(() => {
    fetchStats();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const currentDate = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <Greeting />
        <p className="text-muted-foreground mt-1">
          Here&apos;s what&apos;s happening in your inbox. &middot; {currentDate}
        </p>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          title="Emails Processed"
          value={stats.emails_processed.toLocaleString()}
          subtitle="Total ingested"
          icon={Mail}
        />
        <KpiCard
          title="Pending Approvals"
          value={stats.pending_approvals.toString()}
          subtitle="Requires your attention"
          icon={CheckSquare}
        />
        <KpiCard
          title="Actions Executed"
          value={stats.actions_executed.toLocaleString()}
          subtitle="Processed successfully"
          icon={Zap}
        />
        <KpiCard
          title="Automation Rate"
          value={`${stats.automation_rate}%`}
          subtitle="Of all incoming email"
          icon={Percent}
        />
      </div>

      {/* Main Content Area */}
      <div className="grid gap-6 md:grid-cols-7">
        <div className="md:col-span-4 lg:col-span-5 space-y-6">
          <ActivityList activities={stats.recent_activity} />
        </div>
        
        <div className="md:col-span-3 lg:col-span-2 space-y-6">
          {/* System Status */}
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-4">
            <h3 className="font-semibold text-foreground">System Status</h3>
            <div className="space-y-3">
              {[
                { name: "Gmail", status: stats.system_status.gmail_integration, href: "/integrations" },
                { name: "Google Calendar", status: stats.system_status.google_calendar, href: "/integrations" },
                { name: "Telegram", status: stats.system_status.telegram, href: "/integrations" },
              ].map((service) => {
                const isOperational = service.status === 'Operational';
                const showLink = service.href && !isOperational;
                
                const content = (
                  <div key={service.name} className={`flex items-center justify-between group p-1.5 -mx-1.5 rounded-lg transition-colors ${showLink ? 'hover:bg-secondary/50 cursor-pointer' : ''}`}>
                    <span className={`text-sm transition-colors ${showLink ? 'text-primary group-hover:text-primary/80 underline-offset-2 group-hover:underline' : 'text-muted-foreground group-hover:text-foreground'}`}>
                      {service.name}
                    </span>
                    <span className={`flex items-center gap-1.5 text-sm font-medium ${isOperational ? 'text-success' : 'text-muted-foreground'}`}>
                      {isOperational ? (
                        <span className="w-2 h-2 rounded-full bg-success relative">
                          <span className="absolute inline-flex h-full w-full rounded-full bg-success opacity-20 animate-ping" />
                        </span>
                      ) : (
                        <span className="w-2 h-2 rounded-full bg-muted-foreground relative" />
                      )}
                      {service.status}
                    </span>
                  </div>
                );

                if (showLink) {
                  return (
                    <Link href={service.href} key={service.name} className="block">
                      {content}
                    </Link>
                  );
                }
                
                return content;
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
