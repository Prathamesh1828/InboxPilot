import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-24 items-center justify-between px-4 sm:px-8">
        <div className="flex gap-6 md:gap-10">
          <Link href="/" className="flex items-center space-x-2 shrink-0">
            <img src="/InboxPilot%20Logo.png" alt="InboxPilot" className="h-20 w-auto object-contain scale-125 origin-left" />
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link
              href="#product"
              className="flex items-center text-sm font-medium text-foreground/80 hover:text-foreground transition-colors"
            >
              Product
            </Link>
            <Link
              href="#how-it-works"
              className="flex items-center text-sm font-medium text-foreground/80 hover:text-foreground transition-colors"
            >
              How it works
            </Link>
            <Link
              href="#features"
              className="flex items-center text-sm font-medium text-foreground/80 hover:text-foreground transition-colors"
            >
              Features
            </Link>
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-4">
          <nav className="flex items-center space-x-2">
            <Link href="/dashboard">
              <Button variant="ghost" className="text-foreground hover:bg-secondary">
                Dashboard
              </Button>
            </Link>
          </nav>
        </div>
      </div>
    </nav>
  );
}
