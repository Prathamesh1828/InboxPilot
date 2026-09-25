"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Inbox, CheckSquare, Activity, Settings, LayoutDashboard, Menu, X, Plug, ChevronLeft, ChevronRight, LogOut } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";
import { useEffect } from "react";
import { dashboardApi } from "@/lib/api/emails";

const navItemsBase = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Inbox", href: "/inbox", icon: Inbox },
  { name: "Approvals", href: "/approvals", icon: CheckSquare, badge: 0 },
  { name: "Audit Logs", href: "/audit", icon: Activity },
  { name: "Integrations", href: "/integrations", icon: Plug },
  { name: "Settings", href: "/settings", icon: Settings },
];

interface SidebarProps {
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export function Sidebar({ isCollapsed = false, onToggleCollapse }: SidebarProps) {
  const pathname = usePathname();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const { user, logout } = useAuth();
  const [pendingApprovals, setPendingApprovals] = useState(0);

  // We can fetch stats globally here, or import a specialized hook.
  // Using a simple fetch effect to get the pending_approvals for the badge.

  useEffect(() => {
    const fetchStats = () => {
      dashboardApi.getStats()
        .then(stats => setPendingApprovals(stats.pending_approvals))
        .catch(console.error);
    };
    
    fetchStats();
    const intervalId = setInterval(fetchStats, 15000);
      
    const handleApprovalsChanged = (e: Event) => {
      const customEvent = e as CustomEvent;
      if (customEvent.detail && customEvent.detail.action === 'decrement') {
        setPendingApprovals(prev => Math.max(0, prev - 1));
      } else {
        fetchStats();
      }
    };
    
    window.addEventListener('approvals_changed', handleApprovalsChanged);
    return () => {
      window.removeEventListener('approvals_changed', handleApprovalsChanged);
      clearInterval(intervalId);
    };
  }, []);

  const navItems = navItemsBase.map(item => 
    item.name === "Approvals" && pendingApprovals > 0
      ? { ...item, badge: pendingApprovals }
      : item.name === "Approvals" ? { ...item, badge: undefined } : item
  );

  const sidebarContent = (
    <div className="flex h-full flex-col bg-sidebar border-r border-sidebar-border">
      <div className="flex h-24 shrink-0 items-center justify-center overflow-hidden">
        <Link href="/dashboard" className="flex items-center justify-center">
          {isCollapsed ? (
            <img src="/InboxPilot%20Logo%20without%20text.png" alt="InboxPilot" className="h-12 w-12 object-cover shrink-0 rounded-full scale-150" />
          ) : (
            <img src="/InboxPilot%20Logo%20without%20text.png" alt="InboxPilot" className="h-24 w-auto object-contain shrink-0 scale-125" />
          )}
        </Link>
      </div>
      
      <nav className={`flex-1 space-y-1 py-4 overflow-y-auto ${isCollapsed ? "px-2" : "px-4"}`}>
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`relative flex items-center gap-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isCollapsed ? "justify-center px-0" : "px-3"
              } ${
                isActive 
                  ? "bg-sidebar-primary/10 text-primary" 
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground"
              }`}
              title={isCollapsed ? item.name : undefined}
            >
              <item.icon className={`h-5 w-5 shrink-0 ${isActive ? "text-primary" : "text-sidebar-foreground/50"}`} />
              {!isCollapsed && <span className="truncate flex-1">{item.name}</span>}
              {!isCollapsed && item.badge && (
                <span className="inline-flex items-center justify-center w-5 h-5 shrink-0 text-xs font-bold text-white bg-red-500 rounded-full">
                  {item.badge}
                </span>
              )}
              {isCollapsed && item.badge && (
                <span className="absolute top-1.5 right-1.5 flex items-center justify-center w-3.5 h-3.5 text-[9px] font-bold text-white bg-red-500 rounded-full border-2 border-sidebar">
                  {item.badge > 9 ? '9+' : item.badge}
                </span>
              )}
              {isActive && !isCollapsed && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute left-0 w-1 h-8 bg-primary rounded-r-full"
                  initial={false}
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-sidebar-border flex flex-col gap-2">
        {onToggleCollapse && (
          <div className={`hidden lg:flex ${isCollapsed ? "justify-center" : "justify-end"} px-1`}>
            <button
              onClick={onToggleCollapse}
              className="p-1.5 rounded-lg text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent transition-colors"
            >
              {isCollapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
            </button>
          </div>
        )}
        
        <div className={`flex items-center py-2 ${isCollapsed ? "flex-col justify-center px-0" : "px-3 gap-3"}`}>
          <div className="w-8 h-8 rounded-full bg-sidebar-primary/20 flex items-center justify-center text-primary font-bold shrink-0">
            {user?.name?.charAt(0).toUpperCase() || "U"}
          </div>
          {!isCollapsed && (
            <div className="flex-1 truncate">
              <p className="text-sm font-medium text-sidebar-foreground truncate">{user?.name || "User"}</p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <div className="w-2 h-2 rounded-full bg-success shrink-0" />
                <p className="text-xs text-sidebar-foreground/60 truncate">System online</p>
              </div>
            </div>
          )}
          {!isCollapsed ? (
            <button
              onClick={logout}
              className="p-1.5 rounded-lg text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent transition-colors"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          ) : (
            <button
              onClick={logout}
              className="p-1.5 mt-2 rounded-lg text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent transition-colors"
              title="Logout"
            >
              <LogOut className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <div className={`hidden lg:flex lg:flex-col lg:fixed lg:inset-y-0 z-40 transition-all duration-300 ${isCollapsed ? "lg:w-20" : "lg:w-64"}`}>
        {sidebarContent}
      </div>

      {/* Mobile Toggle & Header (Visible only on small screens) */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-20 border-b border-sidebar-border bg-background flex items-center justify-between px-4 z-40">
        <div className="flex items-center space-x-2 overflow-hidden">
          <img src="/InboxPilot%20Logo%20without%20text.png" alt="InboxPilot" className="h-20 w-auto object-contain shrink-0 scale-125 origin-left" />
        </div>
        <button
          onClick={() => setIsMobileOpen(true)}
          className="p-2 -mr-2 text-foreground"
        >
          <Menu className="h-6 w-6" />
        </button>
      </div>

      {/* Mobile Sidebar (Never collapsed) */}
      <AnimatePresence>
        {isMobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileOpen(false)}
              className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 lg:hidden"
            />
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", bounce: 0, duration: 0.4 }}
              className="fixed inset-y-0 left-0 w-64 bg-sidebar z-50 lg:hidden shadow-xl"
            >
              <button
                onClick={() => setIsMobileOpen(false)}
                className="absolute top-4 right-4 p-2 text-sidebar-foreground"
              >
                <X className="h-5 w-5" />
              </button>
              {/* Force non-collapsed render on mobile */}
              <Sidebar isCollapsed={false} />
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
