import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export function MinimalHeader() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-20 items-center justify-between px-4 sm:px-8">
        
        {/* Left: Logo */}
        <div className="flex items-center">
          <Link href="/" className="flex items-center space-x-3 group">
            <img 
              src="/InboxPilot%20Logo%20without%20text.png" 
              alt="InboxPilot" 
              className="h-10 w-auto object-contain transition-transform group-hover:scale-105" 
            />
            <span className="font-bold text-xl text-foreground">InboxPilot</span>
          </Link>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center justify-end">
          <Link href="/">
            <Button variant="ghost" className="text-foreground hover:bg-secondary flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Button>
          </Link>
        </div>

      </div>
    </nav>
  );
}
