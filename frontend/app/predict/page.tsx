"use client";

import { useEffect, useState } from "react";

import StationSelect from "@/components/StationSelect";
import { type Prediction, getPredictions, submitPrediction } from "@/lib/api";
import { useSelectedStation } from "@/lib/useStation";

const SKY_OPTIONS = ["맑음", "구름조금", "흐림", "비", "눈"];
const WIND_OPTIONS = ["없음", "약함", "보통", "강함"];

// 구름 데이터가 없어 실제/AI 판정은 "맑음(비 안 옴)" · "비" · "눈" 3버킷으로만 가능하다.
function toBucket(condition: string | null): string | null {
  if (!condition) return null;
  if (condition === "비" || condition === "눈") return condition;
  return "맑음";
}

function actualSkyBucket(p: Prediction): string | null {
  if (p.actual_rained == null) return null;
  if (!p.actual_rained) return "맑음";
  return p.actual_max_temp != null && p.actual_max_temp <= 1 ? "눈" : "비";
}

function ResultRow({ p }: { p: Prediction }) {
  const hasActual = p.actual_max_temp != null;
  const userDiff = hasActual ? Math.abs(p.predicted_max_temp - p.actual_max_temp!) : null;
  const aiDiff =
    hasActual && p.ai_predicted_max_temp != null
      ? Math.abs(p.ai_predicted_max_temp - p.actual_max_temp!)
      : null;
  const winner =
    userDiff != null && aiDiff != null
      ? userDiff < aiDiff
        ? "사람"
        : userDiff > aiDiff
        ? "AI"
        : "무승부"
      : null;

  const actualBucket = actualSkyBucket(p);
  const userSkyCorrect =
    actualBucket != null && toBucket(p.predicted_sky_condition) === actualBucket;
  const aiSkyCorrect =
    actualBucket != null && toBucket(p.ai_predicted_sky_condition) === actualBucket;

  return (
    <li className="rounded-xl border border-gray-200 p-4 text-sm">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-gray-500">
          {p.predict_date} · 관찰: {p.sky_condition} · 바람 {p.wind_feel}
        </span>
        {winner && (
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              winner === "사람"
                ? "bg-green-100 text-green-700"
                : winner === "AI"
                ? "bg-blue-100 text-blue-700"
                : "bg-gray-100 text-gray-600"
            }`}
          >
            {winner === "무승부" ? "무승부" : `기온: ${winner} 승리`}
          </span>
        )}
      </div>

      <div className="mt-2 grid grid-cols-3 gap-2 text-center">
        <div>
          <p className="text-xs text-gray-400">내 예측 최고기온</p>
          <p className="font-semibold">{p.predicted_max_temp}°C</p>
        </div>
        <div>
          <p className="text-xs text-gray-400">AI 예측 최고기온</p>
          <p className="font-semibold">
            {p.ai_predicted_max_temp != null ? `${p.ai_predicted_max_temp}°C` : "-"}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400">실제 최고기온</p>
          <p className="font-semibold">{hasActual ? `${p.actual_max_temp}°C` : "집계 전"}</p>
        </div>
      </div>

      {(p.predicted_sky_condition || p.ai_predicted_sky_condition) && (
        <div className="mt-2 grid grid-cols-3 gap-2 text-center">
          <div>
            <p className="text-xs text-gray-400">내 예측 날씨</p>
            <p className="font-semibold">
              {p.predicted_sky_condition ?? "-"} {userSkyCorrect && "✅"}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-400">AI 예측 날씨</p>
            <p className="font-semibold">
              {p.ai_predicted_sky_condition ?? "-"} {aiSkyCorrect && "✅"}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-400">실제 날씨</p>
            <p className="font-semibold">{actualBucket ?? "집계 전"}</p>
          </div>
        </div>
      )}

      {p.memo && <p className="mt-2 text-xs text-gray-500">메모: {p.memo}</p>}
    </li>
  );
}

export default function PredictPage() {
  const [stationId, setStationId] = useSelectedStation();
  const [sky, setSky] = useState(SKY_OPTIONS[0]);
  const [wind, setWind] = useState(WIND_OPTIONS[0]);
  const [predictedSky, setPredictedSky] = useState(SKY_OPTIONS[0]);
  const [temp, setTemp] = useState("");
  const [memo, setMemo] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<Prediction | null>(null);
  const [history, setHistory] = useState<Prediction[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPredictions(stationId).then(setHistory);
    setResult(null);
  }, [stationId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const value = parseFloat(temp);
    if (Number.isNaN(value)) {
      setError("예측 기온을 숫자로 입력해주세요.");
      return;
    }
    setError(null);
    setSubmitting(true);
    const prediction = await submitPrediction(stationId, {
      sky_condition: sky,
      wind_feel: wind,
      predicted_max_temp: value,
      predicted_sky_condition: predictedSky,
      memo: memo || undefined,
    });
    setSubmitting(false);
    if (!prediction) {
      setError(
        "제출에 실패했습니다. 잠시 후 다시 시도해주세요 (서버가 방금 깨어난 경우 최대 1분 걸릴 수 있어요)."
      );
      return;
    }
    setResult(prediction);
    setHistory((prev) => [prediction, ...prev]);
  }

  return (
    <main className="mx-auto max-w-3xl space-y-8 p-8">
      <header className="space-y-2 border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold">오늘의 날씨 예상해보기</h1>
        <p className="text-sm text-gray-600">
          창문 밖을 직접 내다보고 하늘 상태와 바람을 관찰한 뒤, 오늘 하루의
          날씨와 최고기온을 예측해보세요. 같은 순간 AI 모델도 똑같이
          예측합니다 — 사람의 직관과 AI 중 누가 더 정확할지 비교해보는 게 이
          프로젝트의 원래 출발점이었어요. 저녁에 다시 와서 실제 결과와
          비교해보세요.
        </p>
        <p className="text-xs text-gray-400">
          * 구름량 관측 데이터가 없어 AI와 실제 결과 판정은 "맑음/비/눈" 3가지로만 구분돼요.
        </p>
      </header>

      <StationSelect stationId={stationId} onChange={setStationId} />

      <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-gray-200 p-5">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            1. (관찰) 지금 창밖 하늘은 어떤가요?
          </label>
          <select
            value={sky}
            onChange={(e) => setSky(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          >
            {SKY_OPTIONS.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            2. (관찰) 지금 바람은 얼마나 부나요?
          </label>
          <select
            value={wind}
            onChange={(e) => setWind(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          >
            {WIND_OPTIONS.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            3. (예측) 관찰을 근거로, 오늘 하루 날씨는 어떨 것 같나요?
          </label>
          <select
            value={predictedSky}
            onChange={(e) => setPredictedSky(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          >
            {SKY_OPTIONS.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            4. (예측) 오늘 최고기온은 몇 °C일까요?
          </label>
          <input
            type="number"
            step="0.1"
            value={temp}
            onChange={(e) => setTemp(e.target.value)}
            placeholder="예: 24.5"
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">메모 (선택)</label>
          <textarea
            value={memo}
            onChange={(e) => setMemo(e.target.value)}
            placeholder="예: 구름이 빠르게 지나가고 있음, 그늘은 선선함"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            rows={2}
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {submitting ? "예측 제출 중..." : "예측 제출하기"}
        </button>
      </form>

      {result && (
        <section className="rounded-xl border border-purple-200 bg-purple-50 p-5">
          <h2 className="mb-3 font-semibold">제출 완료!</h2>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-500">당신의 예측</p>
              <p className="text-lg font-bold">{result.predicted_sky_condition}</p>
              <p className="text-2xl font-bold">{result.predicted_max_temp}°C</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">AI의 예측</p>
              <p className="text-lg font-bold">{result.ai_predicted_sky_condition ?? "모델 없음"}</p>
              <p className="text-2xl font-bold">
                {result.ai_predicted_max_temp != null
                  ? `${result.ai_predicted_max_temp}°C`
                  : "모델 없음"}
              </p>
            </div>
          </div>
          <p className="mt-3 text-center text-xs text-gray-500">
            오늘 하루가 지나면 실제 날씨/최고기온과 비교해서 누가 더 정확했는지
            아래 기록에서 확인할 수 있어요.
          </p>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-lg font-semibold">예측 기록</h2>
        {history.length === 0 ? (
          <p className="text-sm text-gray-500">아직 예측 기록이 없습니다.</p>
        ) : (
          <ul className="space-y-3">
            {history.map((p) => (
              <ResultRow key={p.id} p={p} />
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
