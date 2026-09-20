"use client";

import { useState } from "react";

import { geocodeAddress } from "@/lib/api";

export default function AddressSearch({
  onFound,
}: {
  onFound: (lat: number, lon: number, label: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch() {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    const results = await geocodeAddress(query);
    setLoading(false);
    if (results.length === 0) {
      setError("검색 결과가 없습니다.");
      return;
    }
    onFound(results[0].lat, results[0].lon, results[0].display_name);
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        placeholder="예: 일도이동, 강남구, 해운대구..."
        className="min-w-[200px] flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm"
      />
      <button
        onClick={handleSearch}
        disabled={loading}
        className="rounded-lg bg-gray-800 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {loading ? "검색 중..." : "검색"}
      </button>
      {error && <span className="text-sm text-red-600">{error}</span>}
    </div>
  );
}
