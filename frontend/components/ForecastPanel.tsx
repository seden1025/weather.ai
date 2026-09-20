import type { Forecast, Observation } from "@/lib/api";

export default function ForecastPanel({
  forecasts,
  observation,
}: {
  forecasts: Forecast[];
  observation: Observation | null;
}) {
  if (forecasts.length === 0) {
    return (
      <p className="text-sm text-gray-500">
        이 지역은 아직 학습된 예측 모델이 없습니다. (현재 서울만 지원)
      </p>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {forecasts.map((f) => {
        const diff =
          observation?.temperature != null
            ? (f.predicted_temperature - observation.temperature).toFixed(1)
            : null;
        return (
          <div key={f.horizon_hours} className="rounded-xl border border-purple-200 bg-purple-50 p-4">
            <p className="text-xs text-gray-500">{f.horizon_hours}시간 뒤 AI 예측</p>
            <p className="text-2xl font-semibold">{f.predicted_temperature}°C</p>
            {diff != null && (
              <p className="text-xs text-gray-500">
                현재 대비 {Number(diff) > 0 ? "+" : ""}
                {diff}°C
              </p>
            )}
            <p className="mt-1 text-xs text-gray-400">테스트 오차(MAE) ±{f.model_test_mae}°C</p>
          </div>
        );
      })}
    </div>
  );
}
