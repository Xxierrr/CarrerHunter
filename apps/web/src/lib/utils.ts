import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return "Unknown";
  const d = new Date(date);
  if (isNaN(d.getTime())) return "Unknown";
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return "Unknown";
  const d = new Date(date);
  if (isNaN(d.getTime())) return "Unknown";
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(date);
}

export function getEligibilityColor(status: string | null | undefined): string {
  switch (status) {
    case "eligible":
      return "text-emerald-400";
    case "likely_eligible":
      return "text-green-400";
    case "possibly_eligible":
      return "text-yellow-400";
    case "uncertain":
      return "text-orange-400";
    case "likely_ineligible":
      return "text-red-400";
    case "ineligible":
      return "text-red-500";
    default:
      return "text-gray-400";
  }
}

export function getEligibilityBadge(status: string | null | undefined): string {
  switch (status) {
    case "eligible":
      return "🟢";
    case "likely_eligible":
      return "🟢";
    case "possibly_eligible":
      return "🟡";
    case "uncertain":
      return "🟠";
    case "likely_ineligible":
      return "🔴";
    case "ineligible":
      return "🔴";
    default:
      return "⚪";
  }
}

export function getEligibilityLabel(status: string | null | undefined): string {
  switch (status) {
    case "eligible":
      return "Eligible";
    case "likely_eligible":
      return "Likely Eligible";
    case "possibly_eligible":
      return "Possibly Eligible";
    case "uncertain":
      return "Uncertain";
    case "likely_ineligible":
      return "Likely Ineligible";
    case "ineligible":
      return "Ineligible";
    default:
      return "Not Analyzed";
  }
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + "...";
}
