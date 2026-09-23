import type { Observation } from "@/lib/api";

// 구름량 관측 데이터가 없어 강수량 + 기온만으로 맑음/비/눈 3가지만 구분한다
// (predict 페이지의 AI 예측 판정과 동일한 기준).
export function weatherIcon(obs: Observation): { emoji: string; label: string } {
  const rained = obs.precipitation != null && obs.precipitation > 0.1;
  if (!rained) return { emoji: "☀️", label: "맑음" };
  if (obs.temperature != null && obs.temperature <= 1) return { emoji: "❄️", label: "눈" };
  return { emoji: "🌧️", label: "비" };
}
