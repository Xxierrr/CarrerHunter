"use client";

import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { useState } from "react";
import {
  Shield,
  Users,
  Database,
  Activity,
  Brain,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
} from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";

export default function AdminPage() {
  const [tab, setTab] = useState<"overview" | "sources" | "ai" | "crawls">("overview");

  const { data: stats } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: () => adminApi.getStats(),
    select: (res) => res.data,
  });

  const { data: sources } = useQuery({
    queryKey: ["admin-sources"],
    queryFn: () => adminApi.getSources(),
    select: (res) => res.data,
    enabled: tab === "sources" || tab === "overview",
  });

  const { data: aiUsage } = useQuery({
    queryKey: ["admin-ai-usage"],
    queryFn: () => adminApi.getAiUsage(),
    select: (res) => res.data,
    enabled: tab === "ai" || tab === "overview",
  });

  const { data: crawlRuns } = useQuery({
    queryKey: ["admin-crawl-runs"],
    queryFn: () => adminApi.getCrawlRuns(20),
    select: (res) => res.data,
    enabled: tab === "crawls",
  });

  const tabs = [
    { key: "overview", label: "Overview", icon: Activity },
    { key: "sources", label: "Sources", icon: Database },
    { key: "ai", label: "AI Usage", icon: Brain },
    { key: "crawls", label: "Crawl Runs", icon: RefreshCw },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6 fade-in">
      <div className="flex items-center gap-2">
        <Shield className="w-6 h-6 text-[var(--accent)]" />
        <h1 className="text-2xl font-bold">Admin Panel</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto" style={{ borderBottom: "1px solid var(--border)" }}>
        {tabs.map((t) => (
          <button key={t.key}
            onClick={() => setTab(t.key as any)}
            className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium whitespace-nowrap"
            style={{
              color: tab === t.key ? "var(--accent)" : "var(--text-muted)",
              borderBottom: tab === t.key ? "2px solid var(--accent)" : "2px solid transparent",
            }}>
            <t.icon className="w-4 h-4" /> {t.label}
          </button>
        ))}
      </div>

      {/* Overview */}
      {tab === "overview" && stats && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Total Users", value: stats.users?.total ?? 0, icon: Users, color: "#667eea" },
              { label: "Active Internships", value: stats.internships?.active ?? 0, icon: Database, color: "#10b981" },
              { label: "New Today", value: stats.internships?.new_today ?? 0, icon: Activity, color: "#f59e0b" },
              { label: "Sources Enabled", value: stats.sources?.enabled ?? 0, icon: RefreshCw, color: "#8b5cf6" },
            ].map((s) => (
              <div key={s.label} className="card p-5">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center mb-3"
                  style={{ background: `${s.color}15` }}>
                  <s.icon className="w-4 h-4" style={{ color: s.color }} />
                </div>
                <p className="text-2xl font-bold">{s.value}</p>
                <p className="text-xs" style={{ color: "var(--text-muted)" }}>{s.label}</p>
              </div>
            ))}
          </div>

          {/* AI Stats */}
          {aiUsage && (
            <div className="card p-6">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Brain className="w-4 h-4 text-[var(--accent)]" /> AI Usage Today
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div><p className="text-xl font-bold">{aiUsage.today?.total_requests ?? 0}</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>Total Requests</p></div>
                <div><p className="text-xl font-bold text-emerald-400">{aiUsage.today?.cached ?? 0}</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>Cached</p></div>
                <div><p className="text-xl font-bold">{aiUsage.today?.cache_hit_rate ?? 0}%</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>Cache Hit Rate</p></div>
                <div><p className="text-xl font-bold">{aiUsage.rate_limiter?.daily_remaining ?? "—"}</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>Daily Remaining</p></div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sources */}
      {tab === "sources" && (
        <div className="space-y-3">
          {(sources || []).map((source: any) => (
            <div key={source.id} className="card p-4 flex items-center justify-between">
              <div className="flex items-center gap-4 min-w-0">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: "var(--bg-input)" }}>
                  {source.health === "healthy" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> :
                   source.health === "failing" ? <XCircle className="w-4 h-4 text-red-400" /> :
                   <AlertTriangle className="w-4 h-4 text-yellow-400" />}
                </div>
                <div className="min-w-0">
                  <h3 className="font-medium text-sm">{source.name}</h3>
                  <div className="flex items-center gap-3 mt-0.5">
                    <span className={`badge text-[10px] ${source.automation_status === "supported" ? "badge-success" : "badge-warning"}`}>
                      {source.automation_status}
                    </span>
                    <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                      {source.jobs_found_total} jobs found
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right shrink-0">
                <span className={`badge ${source.enabled ? "badge-success" : "badge-neutral"}`}>
                  {source.enabled ? "Enabled" : "Disabled"}
                </span>
                {source.last_crawled_at && (
                  <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                    Last crawl: {formatRelativeTime(source.last_crawled_at)}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* AI Usage */}
      {tab === "ai" && aiUsage && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Requests Today", value: aiUsage.today?.total_requests, color: "#667eea" },
              { label: "Successful", value: aiUsage.today?.successful, color: "#10b981" },
              { label: "Cached", value: aiUsage.today?.cached, color: "#f59e0b" },
              { label: "Failed", value: aiUsage.today?.failed, color: "#ef4444" },
            ].map((s) => (
              <div key={s.label} className="card p-5">
                <p className="text-2xl font-bold" style={{ color: s.color }}>{s.value ?? 0}</p>
                <p className="text-xs" style={{ color: "var(--text-muted)" }}>{s.label}</p>
              </div>
            ))}
          </div>

          <div className="card p-6">
            <h3 className="font-semibold mb-4">Rate Limiter Status</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <div><p className="text-lg font-bold">{aiUsage.rate_limiter?.rpm_used ?? 0}/{aiUsage.rate_limiter?.rpm_limit ?? 15}</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>RPM Used</p></div>
              <div><p className="text-lg font-bold">{aiUsage.rate_limiter?.daily_used ?? 0}/{aiUsage.rate_limiter?.daily_limit ?? 1500}</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>Daily Used</p></div>
              <div><p className="text-lg font-bold">{aiUsage.cache?.total_entries ?? 0}</p><p className="text-xs" style={{ color: "var(--text-muted)" }}>Cache Entries</p></div>
            </div>
          </div>
        </div>
      )}

      {/* Crawl Runs */}
      {tab === "crawls" && (
        <div className="space-y-2">
          {(crawlRuns || []).length > 0 ? (
            (crawlRuns || []).map((run: any) => (
              <div key={run.id} className="card p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "var(--bg-input)" }}>
                    {run.status === "completed" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> :
                     run.status === "failed" ? <XCircle className="w-4 h-4 text-red-400" /> :
                     <Clock className="w-4 h-4 text-yellow-400" />}
                  </div>
                  <div>
                    <h4 className="text-sm font-medium">{run.source_name || "Unknown source"}</h4>
                    <div className="flex gap-3 mt-0.5 text-xs" style={{ color: "var(--text-muted)" }}>
                      {run.jobs_new > 0 && <span className="text-emerald-400">+{run.jobs_new} new</span>}
                      {run.jobs_updated > 0 && <span className="text-blue-400">{run.jobs_updated} updated</span>}
                      <span>{run.jobs_found ?? 0} total</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`badge ${run.status === "completed" ? "badge-success" : run.status === "failed" ? "badge-danger" : "badge-warning"}`}>
                    {run.status}
                  </span>
                  <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                    {run.duration_ms ? `${run.duration_ms}ms` : ""} • {formatRelativeTime(run.started_at)}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div className="card p-12 text-center" style={{ color: "var(--text-muted)" }}>
              <RefreshCw className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p>No crawl runs yet. The scheduler will start automatically.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
