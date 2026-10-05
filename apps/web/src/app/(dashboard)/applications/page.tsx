"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { applicationApi } from "@/lib/api";
import { useState } from "react";
import {
  Kanban,
  MoreVertical,
  Trash2,
  ChevronRight,
  FileText,
  Plus,
} from "lucide-react";

const COLUMNS = [
  { key: "interested", label: "Interested", color: "#667eea" },
  { key: "saved", label: "Saved", color: "#f59e0b" },
  { key: "applied", label: "Applied", color: "#10b981" },
  { key: "assessment", label: "Assessment", color: "#8b5cf6" },
  { key: "interview", label: "Interview", color: "#3b82f6" },
  { key: "offer", label: "Offer", color: "#14b8a6" },
  { key: "rejected", label: "Rejected", color: "#ef4444" },
];

export default function ApplicationsPage() {
  const queryClient = useQueryClient();
  const [view, setView] = useState<"kanban" | "list">("kanban");

  const { data: applications, isLoading } = useQuery({
    queryKey: ["applications"],
    queryFn: () => applicationApi.list(),
    select: (res) => res.data,
  });

  const getByStatus = (status: string) =>
    (applications || []).filter((a: any) => a.status === status);

  const moveApplication = async (id: string, newStatus: string) => {
    try {
      await applicationApi.update(id, { status: newStatus });
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    } catch {}
  };

  const deleteApplication = async (id: string) => {
    try {
      await applicationApi.delete(id);
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    } catch {}
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Applications</h1>
          <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
            Track your internship applications
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setView("kanban")}
            className={`btn-secondary p-2 ${view === "kanban" ? "border-[var(--accent)]" : ""}`}
          >
            <Kanban className="w-4 h-4" />
          </button>
          <button
            onClick={() => setView("list")}
            className={`btn-secondary p-2 ${view === "list" ? "border-[var(--accent)]" : ""}`}
          >
            <FileText className="w-4 h-4" />
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-48 rounded-xl" />
          ))}
        </div>
      ) : view === "kanban" ? (
        /* Kanban View */
        <div className="flex gap-4 overflow-x-auto pb-4">
          {COLUMNS.map((col) => {
            const items = getByStatus(col.key);
            return (
              <div
                key={col.key}
                className="min-w-[260px] w-[260px] shrink-0"
              >
                <div className="flex items-center gap-2 mb-3 px-1">
                  <div
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ background: col.color }}
                  />
                  <span className="text-sm font-semibold">{col.label}</span>
                  <span
                    className="text-xs px-1.5 py-0.5 rounded-md ml-auto"
                    style={{ background: "var(--bg-card)", color: "var(--text-muted)" }}
                  >
                    {items.length}
                  </span>
                </div>

                <div
                  className="space-y-2 min-h-[120px] rounded-xl p-2"
                  style={{ background: "var(--bg-secondary)" }}
                >
                  {items.map((app: any) => (
                    <div key={app.id} className="card p-3 group">
                      <div className="flex items-start justify-between">
                        <div className="min-w-0 flex-1">
                          <h4 className="text-sm font-medium truncate">
                            {app.internship_title || "Internship"}
                          </h4>
                          <p
                            className="text-xs truncate mt-0.5"
                            style={{ color: "var(--text-muted)" }}
                          >
                            {app.company_name || "Company"}
                          </p>
                        </div>
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          {col.key !== "offer" && col.key !== "rejected" && (
                            <button
                              className="p-1 rounded"
                              style={{ color: "var(--text-muted)" }}
                              onClick={() => {
                                const idx = COLUMNS.findIndex((c) => c.key === col.key);
                                if (idx < COLUMNS.length - 2) {
                                  moveApplication(app.id, COLUMNS[idx + 1].key);
                                }
                              }}
                              title="Move forward"
                            >
                              <ChevronRight className="w-3.5 h-3.5" />
                            </button>
                          )}
                          <button
                            className="p-1 rounded hover:text-red-400"
                            style={{ color: "var(--text-muted)" }}
                            onClick={() => deleteApplication(app.id)}
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                      {app.notes && (
                        <p className="text-xs mt-2 line-clamp-2"
                          style={{ color: "var(--text-muted)" }}>
                          {app.notes}
                        </p>
                      )}
                    </div>
                  ))}
                  {items.length === 0 && (
                    <p className="text-xs text-center py-6"
                      style={{ color: "var(--text-muted)" }}>
                      No applications
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* List View */
        <div className="space-y-2">
          {(applications || []).length > 0 ? (
            (applications || []).map((app: any) => (
              <div key={app.id} className="card p-4 flex items-center justify-between">
                <div className="flex items-center gap-4 min-w-0">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold shrink-0"
                    style={{ background: "linear-gradient(135deg, #667eea, #764ba2)" }}>
                    {app.company_name?.charAt(0) || "?"}
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-medium text-sm truncate">{app.internship_title || "Internship"}</h3>
                    <p className="text-xs" style={{ color: "var(--text-muted)" }}>{app.company_name}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`badge ${
                    app.status === "applied" ? "badge-success"
                    : app.status === "interview" ? "badge-info"
                    : app.status === "offer" ? "badge-success"
                    : app.status === "rejected" ? "badge-danger"
                    : "badge-neutral"
                  }`}>{app.status}</span>
                  <button onClick={() => deleteApplication(app.id)}
                    className="p-1.5 rounded hover:text-red-400" style={{ color: "var(--text-muted)" }}>
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="card p-12 text-center" style={{ color: "var(--text-muted)" }}>
              <Kanban className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p>No applications tracked yet.</p>
              <p className="text-sm mt-1">Start by saving an internship and clicking &quot;Track &amp; Apply&quot;.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
