"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { notificationApi } from "@/lib/api";
import { useState } from "react";
import { Settings as SettingsIcon, Bell, Mail, Save, Loader2 } from "lucide-react";

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  const { data: prefs, isLoading } = useQuery({
    queryKey: ["email-preferences"],
    queryFn: () => notificationApi.getPreferences(),
    select: (res) => res.data,
  });

  const [form, setForm] = useState<any>(null);

  if (prefs && !form) {
    setForm({ ...prefs });
  }

  const handleSave = async () => {
    if (!form) return;
    setSaving(true);
    try {
      await notificationApi.updatePreferences(form);
      queryClient.invalidateQueries({ queryKey: ["email-preferences"] });
      setSuccessMsg("Preferences saved!");
      setTimeout(() => setSuccessMsg(""), 3000);
    } catch {}
    setSaving(false);
  };

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto space-y-4">
        <div className="skeleton h-8 w-48" />
        <div className="skeleton h-64 rounded-xl" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 fade-in">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
          Manage your notification and email preferences
        </p>
      </div>

      {successMsg && (
        <div className="p-3 rounded-lg text-sm text-emerald-400"
          style={{ background: "rgba(16, 185, 129, 0.1)" }}>
          {successMsg}
        </div>
      )}

      {/* Email Notifications */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold flex items-center gap-2 mb-6">
          <Mail className="w-5 h-5 text-[var(--accent)]" />
          Email Notifications
        </h2>

        <div className="space-y-5">
          <div>
            <label className="block text-sm font-medium mb-1.5">Digest Frequency</label>
            <select
              className="input max-w-xs"
              value={form?.digest_frequency || "daily"}
              onChange={(e) => setForm({ ...form, digest_frequency: e.target.value })}
            >
              <option value="immediate">Immediate (each match)</option>
              <option value="daily">Daily digest</option>
              <option value="every_2_days">Every 2 days</option>
              <option value="weekly">Weekly digest</option>
              <option value="disabled">Disabled</option>
            </select>
          </div>

          <div className="space-y-3">
            {[
              { key: "notify_new_match", label: "New internship matches", desc: "Get notified when we find internships matching your profile" },
              { key: "notify_deadline", label: "Deadline reminders", desc: "Receive reminders before application deadlines" },
              { key: "notify_changes", label: "Listing changes", desc: "Alert when saved internships are updated or removed" },
            ].map((toggle) => (
              <div key={toggle.key} className="flex items-center justify-between p-3 rounded-lg"
                style={{ background: "var(--bg-input)" }}>
                <div>
                  <p className="text-sm font-medium">{toggle.label}</p>
                  <p className="text-xs" style={{ color: "var(--text-muted)" }}>{toggle.desc}</p>
                </div>
                <button
                  onClick={() => setForm({ ...form, [toggle.key]: !form?.[toggle.key] })}
                  className="relative w-11 h-6 rounded-full transition-colors"
                  style={{
                    background: form?.[toggle.key] ? "var(--accent)" : "var(--border)",
                  }}
                >
                  <div
                    className="absolute w-5 h-5 bg-white rounded-full top-0.5 transition-transform"
                    style={{
                      transform: form?.[toggle.key] ? "translateX(22px)" : "translateX(2px)",
                    }}
                  />
                </button>
              </div>
            ))}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Minimum Match Score</label>
            <p className="text-xs mb-2" style={{ color: "var(--text-muted)" }}>
              Only notify for matches above this score (0–100)
            </p>
            <input
              type="number"
              className="input max-w-[120px]"
              min={0}
              max={100}
              value={form?.min_match_score ?? 50}
              onChange={(e) => setForm({ ...form, min_match_score: Number(e.target.value) })}
            />
          </div>
        </div>

        <div className="mt-6 pt-4" style={{ borderTop: "1px solid var(--border)" }}>
          <button className="btn-primary flex items-center gap-2" onClick={handleSave} disabled={saving}>
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );
}
