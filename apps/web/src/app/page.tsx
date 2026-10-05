"use client";

import Link from "next/link";
import {
  Search,
  Target,
  Bell,
  Shield,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Zap,
  Globe,
  Brain,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen" style={{ background: "var(--bg-primary)" }}>
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-[var(--accent)]" />
          <span className="font-bold text-lg">Internship Intelligence</span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="px-4 py-2 text-sm font-medium text-[var(--text-secondary)] hover:text-white transition-colors"
          >
            Sign In
          </Link>
          <Link href="/register" className="btn-primary text-sm">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 pt-20 pb-16 text-center">
        <div className="fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium mb-6"
            style={{ background: "var(--accent-glow)", color: "var(--accent)" }}>
            <Zap className="w-3 h-3" />
            AI-Powered Internship Discovery
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold leading-tight mb-6">
            Find Your{" "}
            <span className="gradient-text">Perfect Internship</span>
            <br />
            While You Sleep
          </h1>
          <p className="text-lg md:text-xl max-w-2xl mx-auto mb-10"
            style={{ color: "var(--text-secondary)" }}>
            We continuously scan career pages, determine your eligibility, and
            notify you the moment a matching opportunity appears. No more
            manually checking 50 company websites.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/register"
              className="btn-primary text-base px-8 py-3 flex items-center gap-2 justify-center"
            >
              Start Free <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="#features"
              className="btn-secondary text-base px-8 py-3 flex items-center gap-2 justify-center"
            >
              See How It Works
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-8 max-w-lg mx-auto mt-16">
          {[
            { value: "15+", label: "Sources Tracked" },
            { value: "24/7", label: "Monitoring" },
            { value: "Free", label: "AI-Powered" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl font-bold gradient-text">{stat.value}</div>
              <div className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="max-w-7xl mx-auto px-6 py-20">
        <h2 className="text-3xl font-bold text-center mb-4">
          Everything You Need
        </h2>
        <p className="text-center mb-12" style={{ color: "var(--text-secondary)" }}>
          From discovery to application tracking — we handle the entire pipeline.
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            {
              icon: Globe,
              title: "Multi-Source Discovery",
              desc: "Scans Greenhouse, Lever, Ashby, SmartRecruiters, and direct career pages. New sources added regularly.",
            },
            {
              icon: Brain,
              title: "AI Eligibility Analysis",
              desc: "Gemini AI interprets job requirements and explains exactly why you qualify — or what's missing.",
            },
            {
              icon: Target,
              title: "Transparent Match Scoring",
              desc: "See exactly how you match: skills, education, location, experience — each scored independently.",
            },
            {
              icon: Bell,
              title: "Smart Notifications",
              desc: "Get emailed when strong matches appear. Daily digests, deadline reminders, and change alerts.",
            },
            {
              icon: Search,
              title: "Powerful Search",
              desc: "Filter by company, role, technology, location, remote status, eligibility, and posted date.",
            },
            {
              icon: Shield,
              title: "Ethical & Transparent",
              desc: "We only use public APIs and permitted sources. Every AI conclusion includes evidence.",
            },
          ].map((feature) => (
            <div key={feature.title} className="card p-6">
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center mb-4"
                style={{ background: "var(--accent-glow)" }}
              >
                <feature.icon className="w-5 h-5 text-[var(--accent)]" />
              </div>
              <h3 className="font-semibold mb-2">{feature.title}</h3>
              <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-4xl mx-auto px-6 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div className="space-y-8">
          {[
            {
              step: "1",
              title: "Create your profile",
              desc: "Tell us about your education, skills, experience, and preferences. Upload your resume for automatic extraction.",
            },
            {
              step: "2",
              title: "We scan continuously",
              desc: "Our system checks 15+ sources every few hours, discovering new internship postings and detecting changes.",
            },
            {
              step: "3",
              title: "AI determines eligibility",
              desc: "Deterministic rules check hard requirements first. Gemini AI interprets ambiguous natural-language criteria.",
            },
            {
              step: "4",
              title: "You get notified",
              desc: "Matching internships appear on your dashboard. Strong matches trigger email notifications instantly.",
            },
            {
              step: "5",
              title: "Apply with confidence",
              desc: "Open the official application, track your status with the Kanban board, and let AI help prepare your application.",
            },
          ].map((item) => (
            <div key={item.step} className="flex gap-6 items-start">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shrink-0"
                style={{
                  background: "linear-gradient(135deg, #667eea, #764ba2)",
                }}
              >
                {item.step}
              </div>
              <div>
                <h3 className="font-semibold mb-1">{item.title}</h3>
                <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                  {item.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-4xl mx-auto px-6 py-20 text-center">
        <div
          className="rounded-2xl p-12"
          style={{
            background: "linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.15))",
            border: "1px solid var(--border)",
          }}
        >
          <h2 className="text-3xl font-bold mb-4">
            Stop Checking 50 Career Pages Daily
          </h2>
          <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
            Let AI do the searching. Focus on what matters — preparing great
            applications.
          </p>
          <Link href="/register" className="btn-primary text-base px-8 py-3 inline-flex items-center gap-2">
            Create Free Account <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-6 py-8 border-t" style={{ borderColor: "var(--border)" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[var(--accent)]" />
            <span className="text-sm font-medium">Internship Intelligence</span>
          </div>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>
            © 2026 Internship Intelligence. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
