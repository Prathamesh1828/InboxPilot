"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

export function Footer() {
  const pathname = usePathname();
  const router = useRouter();

  const handleScrollClick = (e: React.MouseEvent<HTMLAnchorElement>, targetId: string) => {
    e.preventDefault();
    if (pathname !== "/") {
      router.push(`/${targetId}`);
      return;
    }
    
    const id = targetId.replace("#", "");
    const element = document.getElementById(id);
    if (element) {
      const y = element.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top: y, behavior: "smooth" });
    }
  };

  return (
    <footer className="border-t border-border bg-background py-12 md:py-16">
      <div className="container mx-auto px-4 sm:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 lg:gap-12">
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center space-x-2 mb-4">
              <img src="/InboxPilot%20Logo%20without%20text.png" alt="InboxPilot" className="h-12 w-auto object-contain" />
            </Link>
            <p className="text-sm text-muted-foreground max-w-xs">
              Your inbox, on autopilot. AI-powered email automation platform.
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold text-foreground mb-4">Product</h4>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li><Link href="#features" onClick={(e) => handleScrollClick(e, "#features")} className="hover:text-foreground transition-colors">Features</Link></li>
              <li><Link href="#how-it-works" onClick={(e) => handleScrollClick(e, "#how-it-works")} className="hover:text-foreground transition-colors">How it works</Link></li>
              <li><Link href="#security" onClick={(e) => handleScrollClick(e, "#security")} className="hover:text-foreground transition-colors">Security</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold text-foreground mb-4">Company</h4>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li><Link href="/about" className="hover:text-foreground transition-colors">About</Link></li>
              <li><Link href="/contact" className="hover:text-foreground transition-colors">Contact</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold text-foreground mb-4">Legal</h4>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li><Link href="/privacy" className="hover:text-foreground transition-colors">Privacy Policy</Link></li>
              <li><Link href="/tos" className="hover:text-foreground transition-colors">Terms of Service</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="mt-12 pt-8 border-t border-border flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} InboxPilot. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
