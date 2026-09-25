"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { usePathname, useRouter } from "next/navigation";

const navItems = [
  { name: "Product", href: "#product" },
  { name: "How it works", href: "#how-it-works" },
  { name: "Features", href: "#features" },
];

export function Navbar() {
  const [activeSection, setActiveSection] = useState<string>("product");
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (pathname !== "/") return; // Only track sections on home page

    const handleScroll = () => {
      const sections = ["product", "how-it-works", "features"];
      let current = activeSection;
      for (const section of sections) {
        const element = document.getElementById(section);
        if (element) {
          const rect = element.getBoundingClientRect();
          // If the top of the section is within the top half of the viewport
          if (rect.top <= window.innerHeight / 2 && rect.bottom >= window.innerHeight / 2) {
            current = section;
          }
        }
      }
      setActiveSection(current);
    };

    window.addEventListener("scroll", handleScroll);
    handleScroll(); // Initial check
    
    return () => window.removeEventListener("scroll", handleScroll);
  }, [activeSection, pathname]);

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    if (pathname !== "/") {
      router.push(`/${id}`);
      return;
    }

    const targetId = id.replace("#", "");
    const element = document.getElementById(targetId);
    if (element) {
      const y = element.getBoundingClientRect().top + window.scrollY - 80; // Offset for navbar
      window.scrollTo({ top: y, behavior: "smooth" });
    }
  };

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 transition-all duration-300">
      <div className="container mx-auto flex h-20 items-center justify-between px-4 sm:px-8">
        
        {/* Left: Logo */}
        <div className="flex-1 flex items-center">
          <Link href="#product" onClick={(e) => handleClick(e, "#product")} className="flex items-center space-x-2 shrink-0">
            <img src="/InboxPilot%20Logo%20without%20text.png" alt="InboxPilot" className="h-14 w-auto object-contain origin-left hover:scale-105 transition-transform" />
          </Link>
        </div>

        {/* Center: Navigation Options */}
        <nav className="hidden md:flex flex-1 justify-center gap-1 relative">
          {navItems.map((item) => {
            const isActive = activeSection === item.href.replace("#", "");
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={(e) => handleClick(e, item.href)}
                className={`relative px-4 py-2 text-sm font-medium transition-colors ${
                  isActive ? "text-primary" : "text-foreground/70 hover:text-foreground"
                }`}
              >
                {item.name}
                {isActive && (
                  <motion.div
                    layoutId="navbar-active"
                    className="absolute left-0 right-0 bottom-0 h-0.5 bg-primary"
                    initial={false}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right: Actions */}
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
