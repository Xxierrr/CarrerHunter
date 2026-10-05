"use client";

import { useAuth } from "@/lib/auth";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useEffect, useState } from "react";
import {
  Sparkles,
  LayoutDashboard,
  Search,
  Bookmark,
  Kanban,
  User,
  Bell,
  Settings,
  LogOut,
  Shield,
  ChevronLeft,
  Menu,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/internships", label: "Internships", icon: Search },
  { href: "/saved", label: "Saved", icon: Bookmark },
  { href: "/applications", label: "Applications", icon: Kanban },
  { href: "/profile", label: "Profile", icon: User },
  { href: "/notifications", label: "Notifications", icon: Bell },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading || !isAuthenticated) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: "var(--bg-primary)" }}
      >
        <div className="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin"
          style={{ borderColor: "var(--accent)", borderTopColor: "transparent" }}
        />
      </div>
    );
  }

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <div className="min-h-screen flex" style={{ background: "var(--bg-primary)" }}>
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:sticky top-0 left-0 h-screen z-50 flex flex-col transition-all duration-300 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        } ${collapsed ? "w-[68px]" : "w-[240px]"}`}
        style={{
          background: "var(--bg-secondary)",
          borderRight: "1px solid var(--border)",
        }}
      >
        {/* Logo */}
        <div className="flex items-center gap-2 px-4 h-16 shrink-0"
          style={{ borderBottom: "1px solid var(--border)" }}>
          <Sparkles className="w-6 h-6 text-[var(--accent)] shrink-0" />
          {!collapsed && (
            <span className="font-bold text-sm whitespace-nowrap">
              Internship Intel
            </span>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 py-3 px-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "text-white"
                    : "hover:text-white"
                }`}
                style={{
                  background: isActive
                    ? "linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2))"
                    : "transparent",
                  color: isActive ? "white" : "var(--text-secondary)",
                  borderLeft: isActive ? "2px solid var(--accent)" : "2px solid transparent",
                }}
              >
                <item.icon className="w-[18px] h-[18px] shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}

          {/* Admin link */}
          {user?.is_admin && (
            <Link
              href="/admin"
              onClick={() => setMobileOpen(false)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all"
              style={{
                color:
                  pathname.startsWith("/admin")
                    ? "white"
                    : "var(--text-secondary)",
                background: pathname.startsWith("/admin")
                  ? "linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2))"
                  : "transparent",
              }}
            >
              <Shield className="w-[18px] h-[18px] shrink-0" />
              {!collapsed && <span>Admin</span>}
            </Link>
          )}
        </nav>

        {/* Bottom */}
        <div className="px-2 py-3 space-y-1" style={{ borderTop: "1px solid var(--border)" }}>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex items-center gap-3 px-3 py-2 rounded-lg text-sm w-full transition-all"
            style={{ color: "var(--text-muted)" }}
          >
            <ChevronLeft
              className={`w-[18px] h-[18px] shrink-0 transition-transform ${
                collapsed ? "rotate-180" : ""
              }`}
            />
            {!collapsed && <span>Collapse</span>}
          </button>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm w-full hover:text-red-400 transition-all"
            style={{ color: "var(--text-muted)" }}
          >
            <LogOut className="w-[18px] h-[18px] shrink-0" />
            {!collapsed && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0 flex flex-col">
        {/* Top bar */}
        <header
          className="h-16 flex items-center justify-between px-6 shrink-0 sticky top-0 z-30"
          style={{
            background: "rgba(10,10,15,0.8)",
            backdropFilter: "blur(12px)",
            borderBottom: "1px solid var(--border)",
          }}
        >
          <button
            className="lg:hidden p-1.5 rounded-lg"
            style={{ color: "var(--text-secondary)" }}
            onClick={() => setMobileOpen(true)}
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-3 ml-auto">
            <Link
              href="/notifications"
              className="relative p-2 rounded-lg transition-colors"
              style={{ color: "var(--text-secondary)" }}
            >
              <Bell className="w-5 h-5" />
              <span
                className="absolute top-1 right-1 w-2 h-2 rounded-full"
                style={{ background: "var(--accent)" }}
              />
            </Link>
            <div className="flex items-center gap-2">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold"
                style={{
                  background: "linear-gradient(135deg, #667eea, #764ba2)",
                }}
              >
                {user?.name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || "U"}
              </div>
              <span className="text-sm font-medium hidden sm:block">
                {user?.name || user?.email?.split("@")[0]}
              </span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <div className="flex-1 p-6 overflow-y-auto">{children}</div>
      </main>
    </div>
  );
}
