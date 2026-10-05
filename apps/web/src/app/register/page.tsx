"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Sparkles, Eye, EyeOff, Loader2, CheckCircle2 } from "lucide-react";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const passwordChecks = [
    { label: "8+ characters", valid: password.length >= 8 },
    { label: "Uppercase letter", valid: /[A-Z]/.test(password) },
    { label: "Lowercase letter", valid: /[a-z]/.test(password) },
    { label: "Number", valid: /\d/.test(password) },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (passwordChecks.some((c) => !c.valid)) {
      setError("Please meet all password requirements");
      return;
    }
    setLoading(true);
    try {
      await register(email, password, name);
      router.push("/onboarding");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4"
      style={{ background: "var(--bg-primary)" }}>
      <div className="w-full max-w-md fade-in">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-4">
            <Sparkles className="w-7 h-7 text-[var(--accent)]" />
            <span className="font-bold text-xl">Internship Intelligence</span>
          </Link>
          <h1 className="text-2xl font-bold mt-2">Create your account</h1>
          <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
            Start discovering internships in minutes
          </p>
        </div>

        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="p-3 rounded-lg text-sm text-red-400"
                style={{ background: "rgba(239, 68, 68, 0.1)" }}>
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-1.5">Full Name</label>
              <input
                type="text"
                className="input"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Email</label>
              <input
                type="email"
                className="input"
                placeholder="you@university.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  className="input pr-10"
                  placeholder="Create a strong password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                  style={{ color: "var(--text-muted)" }}
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {/* Password strength */}
              {password.length > 0 && (
                <div className="mt-3 grid grid-cols-2 gap-1.5">
                  {passwordChecks.map((check) => (
                    <div
                      key={check.label}
                      className="flex items-center gap-1.5 text-xs"
                      style={{ color: check.valid ? "var(--success)" : "var(--text-muted)" }}
                    >
                      <CheckCircle2 className="w-3 h-3" />
                      {check.label}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button
              type="submit"
              className="btn-primary w-full flex items-center justify-center gap-2 py-3"
              disabled={loading}
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create Account"}
            </button>
          </form>
        </div>

        <p className="text-center text-sm mt-6" style={{ color: "var(--text-secondary)" }}>
          Already have an account?{" "}
          <Link href="/login" className="text-[var(--accent)] font-medium hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
