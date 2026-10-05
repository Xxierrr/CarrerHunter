"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { internshipApi } from "@/lib/api";
import Link from "next/link";
import {
  Search,
  Filter,
  MapPin,
  Clock,
  Building2,
  ExternalLink,
  Bookmark,
  BookmarkCheck,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";
import {
  formatDate,
  formatRelativeTime,
  getEligibilityBadge,
  getEligibilityLabel,
  truncate,
} from "@/lib/utils";

export default function InternshipsPage() {
  const [search, setSearch] = useState("");
  const [company, setCompany] = useState("");
  const [country, setCountry] = useState("");
  const [remote, setRemote] = useState<string>("");
  const [page, setPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);

  const params: any = { page, limit: 20, sort: "posted_at", order: "desc" };
  if (search) params.q = search;
  if (company) params.company = company;
  if (country) params.country = country;
  if (remote === "true") params.remote = true;
  if (remote === "false") params.remote = false;

  const { data, isLoading } = useQuery({
    queryKey: ["internships", params],
    queryFn: () => internshipApi.list(params),
    select: (res) => res.data,
  });

  const handleSave = async (e: React.MouseEvent, id: string, isSaved: boolean) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      if (isSaved) {
        await internshipApi.unsave(id);
      } else {
        await internshipApi.save(id);
      }
    } catch {}
  };

  const activeFilters = [company, country, remote].filter(Boolean).length;

  return (
    <div className="max-w-6xl mx-auto space-y-6 fade-in">
      <div>
        <h1 className="text-2xl font-bold">Internships</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
          Browse and search internship opportunities
        </p>
      </div>

      {/* Search & filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4"
            style={{ color: "var(--text-muted)" }} />
          <input
            type="text"
            className="input pl-10"
            placeholder="Search by title, company, skill..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        <button
          className={`btn-secondary flex items-center gap-2 ${activeFilters > 0 ? "border-[var(--accent)]" : ""}`}
          onClick={() => setShowFilters(!showFilters)}
        >
          <Filter className="w-4 h-4" />
          Filters {activeFilters > 0 && `(${activeFilters})`}
        </button>
      </div>

      {/* Filter panel */}
      {showFilters && (
        <div className="card p-4 grid sm:grid-cols-3 gap-4">
          <div>
            <label className="text-xs font-medium mb-1.5 block" style={{ color: "var(--text-secondary)" }}>
              Company
            </label>
            <input
              className="input"
              placeholder="e.g., Google"
              value={company}
              onChange={(e) => { setCompany(e.target.value); setPage(1); }}
            />
          </div>
          <div>
            <label className="text-xs font-medium mb-1.5 block" style={{ color: "var(--text-secondary)" }}>
              Country
            </label>
            <input
              className="input"
              placeholder="e.g., US"
              value={country}
              onChange={(e) => { setCountry(e.target.value); setPage(1); }}
            />
          </div>
          <div>
            <label className="text-xs font-medium mb-1.5 block" style={{ color: "var(--text-secondary)" }}>
              Remote
            </label>
            <select
              className="input"
              value={remote}
              onChange={(e) => { setRemote(e.target.value); setPage(1); }}
            >
              <option value="">Any</option>
              <option value="true">Remote Only</option>
              <option value="false">On-site</option>
            </select>
          </div>
          {activeFilters > 0 && (
            <button
              className="text-xs flex items-center gap-1 mt-2"
              style={{ color: "var(--accent)" }}
              onClick={() => { setCompany(""); setCountry(""); setRemote(""); setPage(1); }}
            >
              <X className="w-3 h-3" /> Clear filters
            </button>
          )}
        </div>
      )}

      {/* Results */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton h-20 rounded-xl" />
          ))}
        </div>
      ) : data?.items?.length ? (
        <>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>
            Showing {data.items.length} of {data.total} internships
          </p>

          <div className="space-y-3">
            {data.items.map((internship: any) => (
              <Link
                key={internship.id}
                href={`/internships/${internship.id}`}
                className="card p-4 flex items-start sm:items-center justify-between gap-4 group"
              >
                <div className="flex items-start gap-4 min-w-0 flex-1">
                  <div
                    className="w-11 h-11 rounded-xl flex items-center justify-center text-sm font-bold shrink-0"
                    style={{ background: "linear-gradient(135deg, #667eea, #764ba2)" }}
                  >
                    {internship.company_name?.charAt(0) || "?"}
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-semibold text-sm">{internship.title}</h3>
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1">
                      <span className="flex items-center gap-1 text-xs" style={{ color: "var(--text-secondary)" }}>
                        <Building2 className="w-3 h-3" /> {internship.company_name}
                      </span>
                      {internship.location && (
                        <span className="flex items-center gap-1 text-xs" style={{ color: "var(--text-muted)" }}>
                          <MapPin className="w-3 h-3" /> {internship.location}
                        </span>
                      )}
                      {internship.remote_status && internship.remote_status !== "unknown" && (
                        <span className={`badge text-[10px] ${internship.remote_status === "remote" ? "badge-success" : "badge-neutral"}`}>
                          {internship.remote_status}
                        </span>
                      )}
                    </div>
                    {internship.skills?.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {internship.skills.slice(0, 4).map((skill: string) => (
                          <span key={skill} className="badge badge-neutral text-[10px]">{skill}</span>
                        ))}
                        {internship.skills.length > 4 && (
                          <span className="badge badge-neutral text-[10px]">+{internship.skills.length - 4}</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex flex-col items-end gap-2 shrink-0">
                  <div className="flex items-center gap-2">
                    {internship.match_score != null && (
                      <span className="badge badge-success text-xs">{Math.round(internship.match_score)}%</span>
                    )}
                    {internship.eligibility_status && (
                      <span className="text-sm" title={getEligibilityLabel(internship.eligibility_status)}>
                        {getEligibilityBadge(internship.eligibility_status)}
                      </span>
                    )}
                  </div>
                  <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                    {formatRelativeTime(internship.posted_at)}
                  </span>
                  <button
                    onClick={(e) => handleSave(e, internship.id, internship.is_saved)}
                    className="p-1.5 rounded-lg transition-colors"
                    style={{ color: internship.is_saved ? "var(--warning)" : "var(--text-muted)" }}
                  >
                    {internship.is_saved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
                  </button>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {data.pages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              <button
                className="btn-secondary p-2"
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-sm px-3" style={{ color: "var(--text-secondary)" }}>
                Page {page} of {data.pages}
              </span>
              <button
                className="btn-secondary p-2"
                onClick={() => setPage(Math.min(data.pages, page + 1))}
                disabled={page === data.pages}
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="card p-12 text-center" style={{ color: "var(--text-muted)" }}>
          <Search className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p>No internships found matching your criteria.</p>
          <p className="text-sm mt-1">Try adjusting your search or filters.</p>
        </div>
      )}
    </div>
  );
}
