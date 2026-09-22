import { CheckCircle2, Shield, Zap, Mail, Bot } from "lucide-react";

export function TrustStrip() {
  const items = [
    { icon: Bot, label: "AI-powered" },
    { icon: Shield, label: "Secure by design" },
    { icon: CheckCircle2, label: "Human approval" },
    { icon: Mail, label: "Gmail integration" },
    { icon: Zap, label: "Real-time automation" },
  ];

  return (
    <div className="w-full border-y border-border bg-secondary/30 py-8">
      <div className="container mx-auto px-4 sm:px-8">
        <div className="flex flex-wrap justify-center gap-8 md:gap-16">
          {items.map((item, index) => (
            <div key={index} className="flex items-center gap-2 text-muted-foreground">
              <item.icon className="h-5 w-5 text-primary" />
              <span className="font-medium text-sm md:text-base">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
