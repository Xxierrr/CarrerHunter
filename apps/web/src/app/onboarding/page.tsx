"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { profileApi } from "@/lib/api";
import { Sparkles, ChevronRight, ChevronLeft, CheckCircle2, GraduationCap, Code, MapPin, Loader2 } from "lucide-react";

const STEPS = [
  { id: "education", title: "Education", icon: GraduationCap, desc: "Tell us about your academic background" },
  { id: "skills", title: "Skills", icon: Code, desc: "What technologies and skills do you know?" },
  { id: "preferences", title: "Preferences", icon: MapPin, desc: "Where and what would you like to work on?" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<any>({
    university: "", degree: "", degree_level: "bachelors", major: "",
    current_year: "", graduation_date: "", gpa: "", gpa_scale: "4.0",
    skills: [],
    preferred_countries: [], remote_preference: "any", preferred_domains: [],
  });
  const [skillInput, setSkillInput] = useState("");

  const addSkill = () => {
    if (skillInput.trim() && !form.skills.includes(skillInput.trim())) {
      setForm({ ...form, skills: [...form.skills, skillInput.trim()] });
    }
    setSkillInput("");
  };

  const handleFinish = async () => {
    setSaving(true);
    try {
      // Save profile
      await profileApi.update({
        university: form.university,
        degree: form.degree,
        degree_level: form.degree_level,
        major: form.major,
        current_year: form.current_year ? parseInt(form.current_year) : null,
        graduation_date: form.graduation_date || null,
        gpa: form.gpa ? parseFloat(form.gpa) : null,
        gpa_scale: form.gpa_scale ? parseFloat(form.gpa_scale) : null,
        remote_preference: form.remote_preference,
        preferred_countries: form.preferred_countries.length > 0 ? form.preferred_countries : null,
        preferred_domains: form.preferred_domains.length > 0 ? form.preferred_domains : null,
      });

      // Save skills
      if (form.skills.length > 0) {
        await profileApi.updateSkills(
          form.skills.map((s: string) => ({ name: s }))
        );
      }

      router.push("/dashboard");
    } catch (err) {
      console.error("Onboarding save error:", err);
    }
    setSaving(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: "var(--bg-primary)" }}>
      <div className="w-full max-w-lg fade-in">
        {/* Header */}
        <div className="text-center mb-8">
          <Sparkles className="w-8 h-8 text-[var(--accent)] mx-auto mb-3" />
          <h1 className="text-2xl font-bold">Set Up Your Profile</h1>
          <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
            This helps us find the right internships for you
          </p>
        </div>

        {/* Progress */}
        <div className="flex items-center gap-2 mb-8">
          {STEPS.map((s, i) => (
            <div key={s.id} className="flex items-center flex-1">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 transition-all ${
                i <= step ? "text-white" : ""
              }`} style={{
                background: i <= step ? "linear-gradient(135deg, #667eea, #764ba2)" : "var(--bg-card)",
                color: i <= step ? "white" : "var(--text-muted)",
              }}>
                {i < step ? <CheckCircle2 className="w-4 h-4" /> : i + 1}
              </div>
              {i < STEPS.length - 1 && (
                <div className="flex-1 h-0.5 mx-2" style={{
                  background: i < step ? "var(--accent)" : "var(--border)",
                }} />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div className="card p-6 mb-6">
          <div className="flex items-center gap-2 mb-5">
            {(() => { const Icon = STEPS[step].icon; return <Icon className="w-5 h-5 text-[var(--accent)]" />; })()}
            <h2 className="font-semibold">{STEPS[step].title}</h2>
          </div>

          {step === 0 && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>University</label>
                <input className="input" placeholder="Stanford University" value={form.university}
                  onChange={(e) => setForm({ ...form, university: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>Degree</label>
                  <input className="input" placeholder="B.S. Computer Science" value={form.degree}
                    onChange={(e) => setForm({ ...form, degree: e.target.value })} />
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>Level</label>
                  <select className="input" value={form.degree_level} onChange={(e) => setForm({ ...form, degree_level: e.target.value })}>
                    <option value="bachelors">Bachelor&apos;s</option>
                    <option value="masters">Master&apos;s</option>
                    <option value="phd">PhD</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>Major</label>
                  <input className="input" placeholder="Computer Science" value={form.major}
                    onChange={(e) => setForm({ ...form, major: e.target.value })} />
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>Year</label>
                  <input className="input" type="number" placeholder="3" value={form.current_year}
                    onChange={(e) => setForm({ ...form, current_year: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>GPA</label>
                  <input className="input" type="number" step="0.01" placeholder="3.8" value={form.gpa}
                    onChange={(e) => setForm({ ...form, gpa: e.target.value })} />
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>Graduation Date</label>
                  <input className="input" type="date" value={form.graduation_date}
                    onChange={(e) => setForm({ ...form, graduation_date: e.target.value })} />
                </div>
              </div>
            </div>
          )}

          {step === 1 && (
            <div>
              <p className="text-xs mb-3" style={{ color: "var(--text-muted)" }}>
                Add programming languages, frameworks, tools, and soft skills
              </p>
              <div className="flex gap-2 mb-4">
                <input className="input flex-1" placeholder="e.g., Python, React, TensorFlow..."
                  value={skillInput} onChange={(e) => setSkillInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addSkill())} />
                <button className="btn-primary px-4" onClick={addSkill}>Add</button>
              </div>
              <div className="flex flex-wrap gap-2">
                {form.skills.map((skill: string, i: number) => (
                  <span key={i} className="badge badge-info flex items-center gap-1.5 pr-1.5">
                    {skill}
                    <button onClick={() => setForm({ ...form, skills: form.skills.filter((_: any, idx: number) => idx !== i) })}
                      className="hover:text-red-400">×</button>
                  </span>
                ))}
              </div>
              {form.skills.length === 0 && (
                <div className="mt-4 p-3 rounded-lg text-xs" style={{ background: "var(--bg-input)", color: "var(--text-muted)" }}>
                  💡 Tip: Add at least 5-10 skills for better matching (e.g., Python, JavaScript, SQL, Git, Machine Learning)
                </div>
              )}
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>Work Mode Preference</label>
                <select className="input" value={form.remote_preference}
                  onChange={(e) => setForm({ ...form, remote_preference: e.target.value })}>
                  <option value="any">No preference</option>
                  <option value="remote">Remote only</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="onsite">On-site</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>Preferred Countries</label>
                <input className="input" placeholder="e.g., US, UK, Canada (comma-separated)"
                  value={form.preferred_countries?.join(", ") || ""}
                  onChange={(e) => setForm({ ...form, preferred_countries: e.target.value.split(",").map((s: string) => s.trim()).filter(Boolean) })} />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>Preferred Domains</label>
                <input className="input" placeholder="e.g., AI/ML, Web Dev, Data Science (comma-separated)"
                  value={form.preferred_domains?.join(", ") || ""}
                  onChange={(e) => setForm({ ...form, preferred_domains: e.target.value.split(",").map((s: string) => s.trim()).filter(Boolean) })} />
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          {step > 0 ? (
            <button className="btn-secondary flex items-center gap-1.5" onClick={() => setStep(step - 1)}>
              <ChevronLeft className="w-4 h-4" /> Back
            </button>
          ) : <div />}

          {step < STEPS.length - 1 ? (
            <button className="btn-primary flex items-center gap-1.5" onClick={() => setStep(step + 1)}>
              Next <ChevronRight className="w-4 h-4" />
            </button>
          ) : (
            <button className="btn-primary flex items-center gap-2" onClick={handleFinish} disabled={saving}>
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
              Finish Setup
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
