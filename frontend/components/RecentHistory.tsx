import type { Observation } from "@/lib/api";

export default function RecentHistory({ observations }: { observations: Observation[] }) {
  if (observations.length === 0) {
    return <p className="text-sm text-gray-500">최근 관측 데이터가 없습니다.</p>;
  }

  const items = [...observations].reverse();

  return (
    <ul className="divide-y divide-gray-200 rounded-xl border border-gray-200">
      {items.map((obs) => (
        <li key={obs.observed_at} className="flex items-center justify-between px-4 py-2 text-sm">
          <span className="text-gray-500">
            {new Date(obs.observed_at).toLocaleString("ko-KR", {
              month: "numeric",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
          <span className="font-medium">
            {obs.temperature != null ? `${obs.temperature}°C` : "-"}
          </span>
          <span className="text-gray-500">습도 {obs.humidity ?? "-"}%</span>
          <span className="text-gray-500">풍속 {obs.wind_speed ?? "-"}m/s</span>
        </li>
      ))}
    </ul>
  );
}
