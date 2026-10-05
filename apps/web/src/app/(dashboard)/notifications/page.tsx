"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { notificationApi } from "@/lib/api";
import { Bell, CheckCheck, Mail, AlertTriangle, Target, Clock } from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";

export default function NotificationsPage() {
  const queryClient = useQueryClient();

  const { data: notifications, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationApi.list({ page: 1 }),
    select: (res) => res.data,
  });

  const markAllRead = async () => {
    try {
      await notificationApi.markAllRead();
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    } catch {}
  };

  const markRead = async (id: string) => {
    try {
      await notificationApi.markRead(id);
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    } catch {}
  };

  const getIcon = (type: string | null) => {
    switch (type) {
      case "new_match": return <Target className="w-4 h-4 text-emerald-400" />;
      case "deadline": return <Clock className="w-4 h-4 text-amber-400" />;
      case "change": return <AlertTriangle className="w-4 h-4 text-orange-400" />;
      case "digest": return <Mail className="w-4 h-4 text-blue-400" />;
      default: return <Bell className="w-4 h-4 text-[var(--accent)]" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Notifications</h1>
          <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
            Stay updated on new matches and deadlines
          </p>
        </div>
        {notifications?.length > 0 && (
          <button onClick={markAllRead} className="btn-secondary text-sm flex items-center gap-1.5">
            <CheckCheck className="w-4 h-4" /> Mark All Read
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-16 rounded-xl" />)}
        </div>
      ) : notifications?.length ? (
        <div className="space-y-2">
          {notifications.map((notif: any) => (
            <div
              key={notif.id}
              onClick={() => !notif.is_read && markRead(notif.id)}
              className={`card p-4 flex items-start gap-4 cursor-pointer transition-all ${!notif.is_read ? "border-l-2" : ""}`}
              style={{
                borderLeftColor: !notif.is_read ? "var(--accent)" : "transparent",
                opacity: notif.is_read ? 0.6 : 1,
              }}
            >
              <div className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
                style={{ background: "var(--bg-input)" }}>
                {getIcon(notif.type)}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium">{notif.title || "Notification"}</h3>
                {notif.body && (
                  <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>
                    {notif.body}
                  </p>
                )}
                <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                  {formatRelativeTime(notif.created_at)}
                </p>
              </div>
              {!notif.is_read && (
                <div className="w-2 h-2 rounded-full shrink-0 mt-2" style={{ background: "var(--accent)" }} />
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="card p-12 text-center" style={{ color: "var(--text-muted)" }}>
          <Bell className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p>No notifications yet.</p>
          <p className="text-sm mt-1">You&apos;ll receive alerts for new matches and approaching deadlines.</p>
        </div>
      )}
    </div>
  );
}
