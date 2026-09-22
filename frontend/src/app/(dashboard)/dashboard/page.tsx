import { Metadata } from "next";
import { Mail, CheckSquare, Zap, Percent } from "lucide-react";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { ActivityList } from "@/components/dashboard/ActivityList";

export const metadata: Metadata = {
  title: "Dashboard | InboxPilot",
  description: "Overview of your autonomous inbox.",
};

export default async function DashboardPage() {
  await new Promise((resolve) => setTimeout(resolve, 800));

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
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Good morning, Jane</h1>
        <p className="text-muted-foreground mt-1">
          Here&apos;s what&apos;s happening in your inbox. &middot; {currentDate}
        </p>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          title="Emails Processed"
          value="1,248"
          subtitle="In the last 30 days"
          icon={Mail}
          trend={{ value: "12%", isPositive: true }}
        />
        <KpiCard
          title="Pending Approvals"
          value="4"
          subtitle="Requires your attention"
          icon={CheckSquare}
          trend={{ value: "2", isPositive: false }}
        />
        <KpiCard
          title="Actions Executed"
          value="342"
          subtitle="Automated entirely"
          icon={Zap}
          trend={{ value: "18%", isPositive: true }}
        />
        <KpiCard
          title="Automation Rate"
          value="27%"
          subtitle="Of all incoming email"
          icon={Percent}
          trend={{ value: "4%", isPositive: true }}
        />
      </div>

      {/* Main Content Area */}
      <div className="grid gap-6 md:grid-cols-7">
        <div className="md:col-span-4 lg:col-span-5 space-y-6">
          <ActivityList />
        </div>
        
        <div className="md:col-span-3 lg:col-span-2 space-y-6">
          {/* System Status */}
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-4">
            <h3 className="font-semibold text-foreground">System Status</h3>
            <div className="space-y-3">
              {[
                { name: "API Layer", status: "Operational" },
                { name: "Gmail Integration", status: "Operational" },
                { name: "AI Engine", status: "Operational" },
                { name: "Celery Workers", status: "Operational" },
                { name: "Database", status: "Operational" },
                { name: "Redis", status: "Operational" },
              ].map((service) => (
                <div key={service.name} className="flex items-center justify-between group p-1.5 -mx-1.5 rounded-lg hover:bg-secondary/50 transition-colors">
                  <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">{service.name}</span>
                  <span className="flex items-center gap-1.5 text-sm font-medium text-success">
                    <span className="w-2 h-2 rounded-full bg-success relative">
                      <span className="absolute inline-flex h-full w-full rounded-full bg-success opacity-20 animate-ping" />
                    </span>
                    {service.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
