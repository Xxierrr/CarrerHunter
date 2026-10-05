"use client";

import { useAuth } from "@/lib/auth";
import { useQuery } from "@tanstack/react-query";
import { internshipApi, applicationApi, notificationApi } from "@/lib/api";
import {
  TrendingUp,
  Target,
  Bookmark,
  FileText,
  Bell,
  ExternalLink,
  ArrowRight,
  Sparkles,
  Zap,
} from "lucide-react";
import Link from "next/link";
import {
  formatRelativeTime,
  getEligibilityBadge,
  getEligibilityLabel,
  truncate,
} from "@/lib/utils";

export default function DashboardPage() {
  const { user } = useAuth();

  const { data: internships } = useQuery({
    queryKey: ["internships", { limit: 5, sort: "posted_at" }],
    queryFn: () =>
      internshipApi.list({ limit: 5, sort: "posted_at", order: "desc" }),
    select: (res) => res.data,
  });

  const { data: applications } = useQuery({
    queryKey: ["applications"],
    queryFn: () => applicationApi.list(),
    select: (res) => res.data,
  });

  const { data: notifications } = useQuery({
    queryKey: ["notifications", { unread_only: true }],
    queryFn: () => notificationApi.list({ unread_only: true }),
    select: (res) => res.data,
  });

  const { data: recommendations } = useQuery({
    queryKey: ["recommendations"],
    queryFn: () => internshipApi.getRecommendations(5),
    select: (res) => res.data,
  });

  const stats = [
    {
      label: "New Matches",
      value: internships?.items?.length ?? "—",
      icon: Target,
      color: "#667eea",
      href: "/internships",
    },
    {
      label: "Saved",
      value: "—",
      icon: Bookmark,
      color: "#f59e0b",
      href: "/saved",
    },
    {
      label: "Applications",
      value: applications?.length ?? "—",
      icon: FileText,
      color: "#10b981",
      href: "/applications",
    },
    {
      label: "Notifications",
      value: notifications?.length ?? "—",
      icon: Bell,
      color: "#8b5cf6",
      href: "/notifications",
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8 fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">
          Welcome back, {user?.name?.split(" ")[0] || "there"} 👋
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
          Here&apos;s what&apos;s happening with your internship search today.
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Link
            key={stat.label}
            href={stat.href}
            className="card p-5 group cursor-pointer"
          >
            <div className="flex items-center justify-between mb-3">
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center"
                style={{ background: `${stat.color}15` }}
              >
                <stat.icon className="w-4 h-4" style={{ color: stat.color }} />
              </div>
              <ArrowRight
                className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity"
                style={{ color: "var(--text-muted)" }}
              />
            </div>
            <p
              className="text-2xl font-bold"
              style={{ color: "var(--text-primary)" }}
            >
              {stat.value}
            </p>
            <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
              {stat.label}
            </p>
          </Link>
        ))}
      </div>

      {/* Recent Internships */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Latest Internships</h2>
          <Link
            href="/internships"
            className="text-sm font-medium flex items-center gap-1"
            style={{ color: "var(--accent)" }}
          >
            View all <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {internships?.items?.length ? (
          <div className="space-y-3">
            {internships.items.map((internship: any) => (
              <Link
                key={internship.id}
                href={`/internships/${internship.id}`}
                className="card p-4 flex items-center justify-between group"
              >
                <div className="flex items-center gap-4 min-w-0">
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold shrink-0"
                    style={{
                      background: "linear-gradient(135deg, #667eea, #764ba2)",
                    }}
                  >
                    {internship.company_name?.charAt(0) || "?"}
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-medium text-sm truncate">
                      {internship.title}
                    </h3>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span
                        className="text-xs"
                        style={{ color: "var(--text-secondary)" }}
                      >
                        {internship.company_name}
                      </span>
                      {internship.location && (
                        <span
                          className="text-xs"
                          style={{ color: "var(--text-muted)" }}
                        >
                          • {internship.location}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  {internship.match_score != null && (
                    <span className="badge badge-success">
                      {Math.round(internship.match_score)}% match
                    </span>
                  )}
                  {internship.eligibility_status && (
                    <span className="text-sm">
                      {getEligibilityBadge(internship.eligibility_status)}
                    </span>
                  )}
                  <span
                    className="text-xs hidden sm:block"
                    style={{ color: "var(--text-muted)" }}
                  >
                    {formatRelativeTime(internship.posted_at)}
                  </span>
                  <ExternalLink
                    className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity"
                    style={{ color: "var(--text-muted)" }}
                  />
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div
            className="card p-8 text-center"
            style={{ color: "var(--text-muted)" }}
          >
            <Sparkles className="w-8 h-8 mx-auto mb-3 opacity-50" />
            <p className="text-sm">
              No internships discovered yet. The crawler will start finding
              opportunities soon.
            </p>
            <Link
              href="/profile"
              className="btn-primary inline-flex items-center gap-2 mt-4 text-sm"
            >
              Complete Your Profile
            </Link>
          </div>
        )}
      </div>

      {/* Recent Applications */}
      {applications?.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Your Applications</h2>
            <Link
              href="/applications"
              className="text-sm font-medium flex items-center gap-1"
              style={{ color: "var(--accent)" }}
            >
              View all <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {applications.slice(0, 3).map((app: any) => (
              <div key={app.id} className="card p-4">
                <h4 className="font-medium text-sm truncate">
                  {app.internship_title || "Internship"}
                </h4>
                <p
                  className="text-xs mt-0.5"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {app.company_name || "Company"}
                </p>
                <div className="mt-3">
                  <span
                    className={`badge ${
                      app.status === "applied"
                        ? "badge-success"
                        : app.status === "interview"
                        ? "badge-info"
                        : app.status === "rejected"
                        ? "badge-danger"
                        : "badge-neutral"
                    }`}
                  >
                    {app.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations?.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Zap className="w-4 h-4 text-[var(--accent)]" /> For You
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {recommendations.slice(0, 6).map((rec: any) => (
              <Link key={rec.id} href={`/internships/${rec.id}`} className="card p-4 group">
                <div className="flex items-start gap-3">
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold shrink-0"
                    style={{ background: "linear-gradient(135deg, #667eea, #764ba2)" }}
                  >
                    {rec.company_name?.charAt(0) || "?"}
                  </div>
                  <div className="min-w-0">
                    <h4 className="font-medium text-sm truncate">{rec.title}</h4>
                    <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>
                      {rec.company_name}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-3 flex-wrap">
                  {rec.match_score != null && (
                    <span className="badge badge-success text-[10px]">
                      {Math.round(rec.match_score)}% match
                    </span>
                  )}
                  {rec.reasons?.slice(0, 2).map((reason: string) => (
                    <span key={reason} className="badge badge-neutral text-[10px]">
                      {reason}
                    </span>
                  ))}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
