import type { AnomalyEvent } from "@/lib/api";

export default function AnomalyPanel({ events }: { events: AnomalyEvent[] }) {
  if (events.length === 0) {
    return <p className="text-sm text-gray-500">최근 감지된 이상치가 없습니다.</p>;
  }

  return (
    <ul className="space-y-4">
      {events.map((event) => (
        <li key={event.id} className="rounded-lg border border-amber-200 bg-amber-50 p-4">
          <div className="flex items-baseline justify-between">
            <span className="font-medium">
              {event.station_id} · {event.variable}: {event.value}
            </span>
            <span className="text-xs text-gray-500">
              {new Date(event.observed_at).toLocaleString("ko-KR")}
            </span>
          </div>
          {event.expected_low != null && event.expected_high != null && (
            <p className="mt-1 text-xs text-gray-600">
              평년 범위: {event.expected_low.toFixed(1)} ~ {event.expected_high.toFixed(1)}
            </p>
          )}
          {event.news_summary && (
            <p className="mt-2 text-sm text-gray-700">관련 뉴스: {event.news_summary}</p>
          )}
          {event.news_sources && event.news_sources.length > 0 && (
            <ul className="mt-1 list-disc pl-5 text-xs text-blue-600">
              {event.news_sources.map((src, i) => (
                <li key={i}>
                  <a href={src.link} target="_blank" rel="noreferrer">
                    {src.title}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </li>
      ))}
    </ul>
  );
}
