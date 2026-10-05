"use client";

import { useQuery } from "@tanstack/react-query";
import { internshipApi } from "@/lib/api";
import Link from "next/link";
import { Bookmark, Building2, MapPin } from "lucide-react";
import { formatRelativeTime, getEligibilityBadge } from "@/lib/utils";

export default function SavedPage() {
  const { data: saved, isLoading } = useQuery({
    queryKey: ["saved-internships"],
    queryFn: () => internshipApi.getSaved(),
    select: (res) => res.data,
  });

  return (
    <div className="max-w-6xl mx-auto space-y-6 fade-in">
      <div>
        <h1 className="text-2xl font-bold">Saved Internships</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
          Internships you&apos;ve bookmarked for later
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-20 rounded-xl" />)}
        </div>
      ) : saved?.length ? (
        <div className="space-y-3">
          {saved.map((internship: any) => (
            <Link key={internship.id} href={`/internships/${internship.id}`} className="card p-4 flex items-center justify-between group">
              <div className="flex items-center gap-4 min-w-0">
                <div className="w-11 h-11 rounded-xl flex items-center justify-center text-sm font-bold shrink-0"
                  style={{ background: "linear-gradient(135deg, #667eea, #764ba2)" }}>
                  {internship.company_name?.charAt(0) || "?"}
                </div>
                <div className="min-w-0">
                  <h3 className="font-semibold text-sm">{internship.title}</h3>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="flex items-center gap-1 text-xs" style={{ color: "var(--text-secondary)" }}>
                      <Building2 className="w-3 h-3" /> {internship.company_name}
                    </span>
                    {internship.location && (
                      <span className="flex items-center gap-1 text-xs" style={{ color: "var(--text-muted)" }}>
                        <MapPin className="w-3 h-3" /> {internship.location}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                {internship.match_score != null && (
                  <span className="badge badge-success text-xs">{Math.round(internship.match_score)}%</span>
                )}
                {internship.eligibility_status && (
                  <span>{getEligibilityBadge(internship.eligibility_status)}</span>
                )}
                <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                  {formatRelativeTime(internship.posted_at)}
                </span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="card p-12 text-center" style={{ color: "var(--text-muted)" }}>
          <Bookmark className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p>No saved internships yet.</p>
          <Link href="/internships" className="btn-primary inline-block mt-4 text-sm">Browse Internships</Link>
        </div>
      )}
    </div>
  );
}
