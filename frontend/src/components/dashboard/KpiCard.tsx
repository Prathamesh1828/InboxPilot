import { type LucideIcon } from "lucide-react";

interface KpiCardProps {
  title: string;
  value: string;
  subtitle: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
}

export function KpiCard({ title, value, subtitle, icon: Icon, trend }: KpiCardProps) {
  return (
    <div className="bg-card border border-border rounded-xl p-6 shadow-sm hover:-translate-y-1 hover:shadow-lg hover:border-primary/20 transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
        <div className="w-8 h-8 rounded-full bg-secondary/50 flex items-center justify-center">
          <Icon className="w-4 h-4 text-primary" />
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold text-foreground">{value}</span>
        {trend && (
          <span className={`text-xs font-medium ${trend.isPositive ? "text-success" : "text-destructive"}`}>
            {trend.isPositive ? "+" : "-"}{trend.value}
          </span>
        )}
      </div>
      <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
    </div>
  );
}
