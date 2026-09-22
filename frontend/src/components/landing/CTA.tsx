import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function CTA() {
  return (
    <section className="bg-foreground text-background py-24">
      <div className="container mx-auto px-4 sm:px-8 text-center max-w-3xl">
        <h2 className="text-4xl md:text-5xl font-bold mb-6 text-background">
          Take back your inbox.
        </h2>
        <p className="text-xl text-background/70 mb-10 leading-relaxed max-w-2xl mx-auto">
          Join the professionals who save hours every week by letting InboxPilot handle the routine.
        </p>
        <Link href="/dashboard">
          <Button size="lg" className="h-14 px-10 text-lg bg-primary text-primary-foreground hover:bg-primary/90">
            Go to Dashboard
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </Link>
      </div>
    </section>
  );
}
