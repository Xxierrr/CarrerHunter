"use client";

import { useQuery } from "@tanstack/react-query";
import { internshipApi, applicationApi } from "@/lib/api";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Building2,
  MapPin,
  Clock,
  Calendar,
  DollarSign,
  ExternalLink,
  Bookmark,
  BookmarkCheck,
  CheckCircle2,
  XCircle,
  HelpCircle,
  AlertTriangle,
  FileText,
} from "lucide-react";
import {
  formatDate,
  getEligibilityBadge,
  getEligibilityLabel,
  getEligibilityColor,
} from "@/lib/utils";
import { useState } from "react";

export default function InternshipDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [applying, setApplying] = useState(false);

  const { data: internship, isLoading } = useQuery({
    queryKey: ["internship", id],
    queryFn: () => internshipApi.get(id),
    select: (res) => res.data,
  });

  const handleApply = async () => {
    setApplying(true);
    try {
      await applicationApi.create({ internship_id: id, status: "interested" });
      if (internship?.application_url) {
        window.open(internship.application_url, "_blank");
      }
    } catch {}
    setApplying(false);
  };

  const handleToggleSave = async () => {
    try {
      if (internship?.is_saved) {
        await internshipApi.unsave(id);
      } else {
        await internshipApi.save(id);
      }
    } catch {}
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-4">
        <div className="skeleton h-8 w-48" />
        <div className="skeleton h-64 rounded-xl" />
        <div className="skeleton h-48 rounded-xl" />
      </div>
    );
  }

  if (!internship) {
    return (
      <div className="max-w-4xl mx-auto card p-12 text-center" style={{ color: "var(--text-muted)" }}>
        <p>Internship not found.</p>
        <Link href="/internships" className="btn-primary inline-block mt-4">Back to search</Link>
      </div>
    );
  }

  const getCriterionIcon = (result: string) => {
    if (result === "pass") return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
    if (result === "fail") return <XCircle className="w-4 h-4 text-red-400" />;
    return <HelpCircle className="w-4 h-4 text-yellow-400" />;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 fade-in">
      {/* Back */}
      <button onClick={() => router.back()} className="flex items-center gap-1.5 text-sm"
        style={{ color: "var(--text-secondary)" }}>
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      {/* Header */}
      <div className="card p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-xl flex items-center justify-center text-lg font-bold shrink-0"
              style={{ background: "linear-gradient(135deg, #667eea, #764ba2)" }}>
              {internship.company_name?.charAt(0) || "?"}
            </div>
            <div>
              <h1 className="text-xl font-bold">{internship.title}</h1>
              <div className="flex flex-wrap items-center gap-3 mt-2">
                <span className="flex items-center gap-1 text-sm" style={{ color: "var(--text-secondary)" }}>
                  <Building2 className="w-4 h-4" /> {internship.company_name}
                </span>
                {internship.location && (
                  <span className="flex items-center gap-1 text-sm" style={{ color: "var(--text-muted)" }}>
                    <MapPin className="w-4 h-4" /> {internship.location}
                  </span>
                )}
                {internship.remote_status && internship.remote_status !== "unknown" && (
                  <span className={`badge ${internship.remote_status === "remote" ? "badge-success" : "badge-neutral"}`}>
                    {internship.remote_status}
                  </span>
                )}
              </div>
            </div>
          </div>
          <button onClick={handleToggleSave} className="p-2 rounded-lg"
            style={{ color: internship.is_saved ? "var(--warning)" : "var(--text-muted)" }}>
            {internship.is_saved ? <BookmarkCheck className="w-5 h-5" /> : <Bookmark className="w-5 h-5" />}
          </button>
        </div>

        {/* Meta */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6" style={{ borderTop: "1px solid var(--border)" }}>
          {internship.application_deadline && (
            <div>
              <p className="text-xs mb-1" style={{ color: "var(--text-muted)" }}>Deadline</p>
              <p className="text-sm font-medium flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" /> {formatDate(internship.application_deadline)}
              </p>
            </div>
          )}
          {internship.duration_weeks && (
            <div>
              <p className="text-xs mb-1" style={{ color: "var(--text-muted)" }}>Duration</p>
              <p className="text-sm font-medium flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" /> {internship.duration_weeks} weeks
              </p>
            </div>
          )}
          {internship.salary_min && (
            <div>
              <p className="text-xs mb-1" style={{ color: "var(--text-muted)" }}>Salary</p>
              <p className="text-sm font-medium flex items-center gap-1">
                <DollarSign className="w-3.5 h-3.5" />
                {internship.salary_min}–{internship.salary_max} {internship.salary_currency}/{internship.salary_period}
              </p>
            </div>
          )}
          {internship.posted_at && (
            <div>
              <p className="text-xs mb-1" style={{ color: "var(--text-muted)" }}>Posted</p>
              <p className="text-sm font-medium">{formatDate(internship.posted_at)}</p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3 mt-6">
          <button onClick={handleApply} disabled={applying} className="btn-primary flex items-center gap-2">
            <FileText className="w-4 h-4" /> {applying ? "Opening..." : "Track & Apply"}
          </button>
          {internship.application_url && (
            <a href={internship.application_url} target="_blank" rel="noopener noreferrer"
              className="btn-secondary flex items-center gap-2">
              <ExternalLink className="w-4 h-4" /> View Original
            </a>
          )}
        </div>
      </div>

      {/* Eligibility */}
      {internship.eligibility_status && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            {getEligibilityBadge(internship.eligibility_status)} Eligibility Analysis
          </h2>
          <p className={`font-medium text-sm mb-4 ${getEligibilityColor(internship.eligibility_status)}`}>
            {getEligibilityLabel(internship.eligibility_status)}
          </p>
          {internship.eligibility_explanation && (
            <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>
              {internship.eligibility_explanation}
            </p>
          )}
          {internship.eligibility_criteria?.length > 0 && (
            <div className="space-y-2">
              {internship.eligibility_criteria.map((c: any, i: number) => (
                <div key={i} className="flex items-center gap-3 p-3 rounded-lg"
                  style={{ background: "var(--bg-input)" }}>
                  {getCriterionIcon(c.result)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{c.requirement}</p>
                    <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                      You: {c.candidate_value} | Required: {c.job_requirement}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Match Score */}
      {internship.match_score != null && internship.match_breakdown && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4">
            Match Score: <span className="gradient-text">{Math.round(internship.match_score)}%</span>
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            {Object.entries(internship.match_breakdown as Record<string, any>).map(([key, val]: [string, any]) => (
              <div key={key} className="text-center">
                <div className="text-xl font-bold" style={{ color: val.score > 70 ? "var(--success)" : val.score > 40 ? "var(--warning)" : "var(--danger)" }}>
                  {Math.round(val.score)}
                </div>
                <p className="text-xs capitalize mt-0.5" style={{ color: "var(--text-muted)" }}>{key}</p>
                <div className="w-full h-1.5 rounded-full mt-2" style={{ background: "var(--bg-input)" }}>
                  <div className="h-1.5 rounded-full" style={{
                    width: `${val.score}%`,
                    background: val.score > 70 ? "var(--success)" : val.score > 40 ? "var(--warning)" : "var(--danger)",
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Skills */}
      {internship.skills?.length > 0 && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-3">Required Skills</h2>
          <div className="flex flex-wrap gap-2">
            {internship.skills.map((skill: string) => (
              <span key={skill} className="badge badge-info">{skill}</span>
            ))}
          </div>
        </div>
      )}

      {/* Description */}
      {internship.description && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-3">Description</h2>
          <div className="prose prose-invert prose-sm max-w-none text-sm leading-relaxed"
            style={{ color: "var(--text-secondary)" }}
            dangerouslySetInnerHTML={{ __html: internship.description }}
          />
        </div>
      )}
    </div>
  );
}
