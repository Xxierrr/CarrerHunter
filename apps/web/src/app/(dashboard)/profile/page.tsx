"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { profileApi } from "@/lib/api";
import { useState } from "react";
import { User, GraduationCap, Code, Briefcase, Link as LinkIcon, Save, Loader2, Plus, X, Upload } from "lucide-react";

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("personal");
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => profileApi.get(),
    select: (res) => res.data,
  });

  const [form, setForm] = useState<any>({});

  // Init form when profile loads
  const initForm = () => {
    if (profile && Object.keys(form).length === 0) {
      setForm({ ...profile });
    }
  };
  if (profile) initForm();

  const handleSave = async () => {
    setSaving(true);
    setSuccessMsg("");
    try {
      await profileApi.update(form);
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      setSuccessMsg("Profile saved successfully!");
      setTimeout(() => setSuccessMsg(""), 3000);
    } catch {}
    setSaving(false);
  };

  const [skillInput, setSkillInput] = useState("");
  const handleAddSkill = () => {
    if (!skillInput.trim()) return;
    const current = form.skills?.map((s: any) => s.name || s) || [];
    if (!current.includes(skillInput.trim())) {
      setForm({ ...form, skills: [...(form.skills || []), { name: skillInput.trim() }] });
    }
    setSkillInput("");
  };
  const handleRemoveSkill = (idx: number) => {
    const updated = [...(form.skills || [])];
    updated.splice(idx, 1);
    setForm({ ...form, skills: updated });
  };

  const saveSkills = async () => {
    setSaving(true);
    try {
      await profileApi.updateSkills(
        (form.skills || []).map((s: any) => ({ name: s.name || s }))
      );
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      setSuccessMsg("Skills updated!");
      setTimeout(() => setSuccessMsg(""), 3000);
    } catch {}
    setSaving(false);
  };

  const tabs = [
    { key: "personal", label: "Personal", icon: User },
    { key: "education", label: "Education", icon: GraduationCap },
    { key: "skills", label: "Skills", icon: Code },
    { key: "experience", label: "Experience", icon: Briefcase },
    { key: "links", label: "Links", icon: LinkIcon },
  ];

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-4">
        <div className="skeleton h-8 w-48" />
        <div className="skeleton h-96 rounded-xl" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 fade-in">
      <div>
        <h1 className="text-2xl font-bold">Profile</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
          Your internship profile is used for eligibility analysis and matching
        </p>
      </div>

      {successMsg && (
        <div className="p-3 rounded-lg text-sm text-emerald-400"
          style={{ background: "rgba(16, 185, 129, 0.1)" }}>
          {successMsg}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto pb-2" style={{ borderBottom: "1px solid var(--border)" }}>
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap"
            style={{
              color: activeTab === tab.key ? "var(--accent)" : "var(--text-muted)",
              borderBottom: activeTab === tab.key ? "2px solid var(--accent)" : "2px solid transparent",
            }}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="card p-6">
        {activeTab === "personal" && (
          <div className="grid sm:grid-cols-2 gap-5">
            {[
              { label: "Name", key: "name", placeholder: "John Doe" },
              { label: "Phone", key: "phone", placeholder: "+1 234 567 890" },
              { label: "Country", key: "country", placeholder: "United States" },
              { label: "City", key: "city", placeholder: "San Francisco" },
            ].map((field) => (
              <div key={field.key}>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                  {field.label}
                </label>
                <input
                  className="input"
                  placeholder={field.placeholder}
                  value={form[field.key] || ""}
                  onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                />
              </div>
            ))}
          </div>
        )}

        {activeTab === "education" && (
          <div className="grid sm:grid-cols-2 gap-5">
            {[
              { label: "University", key: "university", placeholder: "Stanford University" },
              { label: "Degree", key: "degree", placeholder: "Bachelor of Science" },
              { label: "Degree Level", key: "degree_level", placeholder: "bachelors", type: "select", options: ["bachelors", "masters", "phd"] },
              { label: "Major", key: "major", placeholder: "Computer Science" },
              { label: "Current Year", key: "current_year", placeholder: "3", type: "number" },
              { label: "Current Semester", key: "current_semester", placeholder: "6", type: "number" },
              { label: "Graduation Date", key: "graduation_date", placeholder: "", type: "date" },
              { label: "GPA", key: "gpa", placeholder: "3.8", type: "number" },
              { label: "GPA Scale", key: "gpa_scale", placeholder: "4.0", type: "number" },
            ].map((field) => (
              <div key={field.key}>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                  {field.label}
                </label>
                {field.type === "select" ? (
                  <select className="input" value={form[field.key] || ""} onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}>
                    <option value="">Select...</option>
                    {field.options?.map((o) => <option key={o} value={o}>{o}</option>)}
                  </select>
                ) : (
                  <input
                    className="input"
                    type={field.type || "text"}
                    placeholder={field.placeholder}
                    value={form[field.key] || ""}
                    onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                  />
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === "skills" && (
          <div>
            <div className="flex gap-2 mb-4">
              <input
                className="input flex-1"
                placeholder="Add a skill (e.g., Python, React, TensorFlow)"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddSkill())}
              />
              <button className="btn-primary flex items-center gap-1.5" onClick={handleAddSkill}>
                <Plus className="w-4 h-4" /> Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {(form.skills || []).map((skill: any, i: number) => (
                <span key={i} className="badge badge-info flex items-center gap-1.5 pr-1.5">
                  {skill.name || skill}
                  <button onClick={() => handleRemoveSkill(i)} className="hover:text-red-400 transition-colors">
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
            {(form.skills || []).length > 0 && (
              <button className="btn-primary mt-4 flex items-center gap-2" onClick={saveSkills} disabled={saving}>
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                Save Skills
              </button>
            )}
          </div>
        )}

        {activeTab === "experience" && (
          <div>
            {(form.experiences || []).length > 0 ? (
              <div className="space-y-4">
                {form.experiences.map((exp: any, i: number) => (
                  <div key={i} className="p-4 rounded-lg" style={{ background: "var(--bg-input)" }}>
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium text-sm">{exp.title}</h4>
                        <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>{exp.organization}</p>
                        <span className="badge badge-neutral text-[10px] mt-1">{exp.type}</span>
                      </div>
                    </div>
                    {exp.description && <p className="text-xs mt-2" style={{ color: "var(--text-muted)" }}>{exp.description}</p>}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                No experiences added. Add your projects, internships, and work experience to improve matching.
              </p>
            )}
          </div>
        )}

        {activeTab === "links" && (
          <div className="grid sm:grid-cols-2 gap-5">
            {[
              { label: "GitHub", key: "github_url", placeholder: "https://github.com/username" },
              { label: "LinkedIn", key: "linkedin_url", placeholder: "https://linkedin.com/in/username" },
              { label: "Portfolio", key: "portfolio_url", placeholder: "https://yoursite.com" },
            ].map((field) => (
              <div key={field.key}>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                  {field.label}
                </label>
                <input
                  className="input"
                  placeholder={field.placeholder}
                  value={form[field.key] || ""}
                  onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                />
              </div>
            ))}
          </div>
        )}

        {/* Save button for non-skills tabs */}
        {activeTab !== "skills" && activeTab !== "experience" && (
          <div className="mt-6 pt-4" style={{ borderTop: "1px solid var(--border)" }}>
            <button className="btn-primary flex items-center gap-2" onClick={handleSave} disabled={saving}>
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Save Changes
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
