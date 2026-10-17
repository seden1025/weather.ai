"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import StationSelect from "@/components/StationSelect";
import {
  type Prediction,
  getMyPredictions,
  getPredictions,
  submitPrediction,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useSelectedStation } from "@/lib/useStation";

const SKY_OPTIONS = ["맑음", "구름조금", "흐림", "비", "눈"];
const WIND_OPTIONS = ["없음", "약함", "보통", "강함"];

// 예측 근거 선택지. 백엔드 backend/app/schemas/prediction.py의 BASIS_OPTIONS와 글자까지 같아야 한다.
const BASIS_OPTIONS = [
  "지금 하늘·구름 모습",
  "바람의 세기·방향",
  "지금 기온·체감 온도",
  "습도·공기의 느낌",
  "어제·최근 며칠의 날씨",
  "일기예보·날씨 앱",
  "계절·평소 경험",
  "그냥 직감",
  "기타",
];

const TEXT_MAX = 500;

// 보상 안내용 연락처 수집·이용 동의 문구. 운영 방침에 맞게 여기서 고치면 된다.
const CONSENT_ITEMS = [
  ["수집 항목", "이메일 주소 또는 전화번호"],
  ["이용 목적", "이벤트 보상 지급 안내 (다른 목적으로는 사용하지 않아요)"],
  ["보유 기간", "보상 안내가 끝날 때까지"],
];

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

function ResultRow({ p, showStation = false }: { p: Prediction; showStation?: boolean }) {
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
          {p.predict_date}
          {showStation && ` · 지점 ${p.station_id}`} · 관찰: {p.sky_condition} · 바람 {p.wind_feel}
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

      {((p.prediction_basis && p.prediction_basis.length > 0) || p.basis_detail) && (
        <div className="mt-2 space-y-1">
          {p.prediction_basis && p.prediction_basis.length > 0 && (
            <div className="flex flex-wrap items-center gap-1">
              <span className="text-xs text-gray-400">예측 근거:</span>
              {p.prediction_basis.map((b) => (
                <span key={b} className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                  {b}
                </span>
              ))}
            </div>
          )}
          {p.basis_detail && <p className="text-xs text-gray-500">근거 설명: {p.basis_detail}</p>}
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
  const [basis, setBasis] = useState<string[]>([]);
  const [basisDetail, setBasisDetail] = useState("");
  const [memo, setMemo] = useState("");
  const [contact, setContact] = useState("");
  const [consent, setConsent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<Prediction | null>(null);
  const [history, setHistory] = useState<Prediction[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [showMine, setShowMine] = useState(false);
  const { user, ready } = useAuth();

  // 로그아웃되면 '내 예측만 보기'도 끈다.
  useEffect(() => {
    if (!user) setShowMine(false);
  }, [user]);

  useEffect(() => {
    let cancelled = false;
    const load = showMine ? getMyPredictions() : getPredictions(stationId);
    load.then((rows) => {
      if (!cancelled) setHistory(rows);
    });
    return () => {
      cancelled = true;
    };
  }, [stationId, showMine]);

  useEffect(() => {
    setResult(null);
  }, [stationId]);

  function toggleBasis(option: string) {
    setBasis((prev) =>
      prev.includes(option) ? prev.filter((b) => b !== option) : [...prev, option]
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const value = parseFloat(temp);
    if (Number.isNaN(value)) {
      setError("예측 기온을 숫자로 입력해주세요.");
      return;
    }
    if (basis.length === 0 && !basisDetail.trim()) {
      setError("5번: 예측의 근거를 하나 이상 고르거나 직접 적어주세요.");
      return;
    }
    const contactValue = contact.trim();
    if (contactValue && !consent) {
      setError("연락처를 남기려면 개인정보 수집·이용에 동의해주세요.");
      return;
    }
    setError(null);
    setSubmitting(true);
    const res = await submitPrediction(stationId, {
      sky_condition: sky,
      wind_feel: wind,
      predicted_max_temp: value,
      predicted_sky_condition: predictedSky,
      memo: memo.trim() || undefined,
      prediction_basis: basis,
      basis_detail: basisDetail.trim() || undefined,
      reward_contact: contactValue || undefined,
      contact_consent: contactValue ? consent : false,
    });
    setSubmitting(false);
    if (!res.ok) {
      setError(res.message);
      return;
    }
    setResult(res.prediction);
    setHistory((prev) => [res.prediction, ...prev]);
    // 같은 연락처가 다음 제출에 자동으로 따라가지 않도록 비운다.
    setContact("");
    setConsent(false);
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

      <div className="flex flex-wrap items-center justify-between gap-2">
        <StationSelect stationId={stationId} onChange={setStationId} />
        {ready && !user && (
          <p className="text-xs text-gray-500">
            <Link href="/login" className="font-medium text-blue-600 underline">
              로그인
            </Link>
            하면 내 예측 기록을 모아볼 수 있어요. (로그인 없이도 제출할 수 있어요)
          </p>
        )}
        {ready && user && (
          <p className="truncate text-xs text-gray-500">{user.email} 로그인 중</p>
        )}
      </div>

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

        <fieldset>
          <legend className="mb-1 block text-sm font-medium text-gray-700">
            5. (근거) 위 예측은 무엇을 근거로 했나요? (여러 개 선택 가능)
          </legend>
          <div className="grid grid-cols-1 gap-1 sm:grid-cols-2">
            {BASIS_OPTIONS.map((o) => (
              <label key={o} className="flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={basis.includes(o)}
                  onChange={() => toggleBasis(o)}
                  className="h-4 w-4"
                />
                {o}
              </label>
            ))}
          </div>
          <textarea
            value={basisDetail}
            onChange={(e) => setBasisDetail(e.target.value)}
            maxLength={TEXT_MAX}
            placeholder="근거를 직접 적어도 좋아요. 예: 서쪽 하늘에 먹구름이 몰려오고 어제보다 공기가 눅눅해서"
            aria-label="예측 근거 직접 설명"
            className="mt-2 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            rows={2}
          />
          <p className="mt-1 text-xs text-gray-400">
            하나 이상 고르거나 직접 적어주세요. 나중에 AI와 비교할 때 어떤 단서가 잘 맞는지
            살펴보는 데 쓰여요.
          </p>
        </fieldset>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">메모 (선택)</label>
          <textarea
            value={memo}
            onChange={(e) => setMemo(e.target.value)}
            maxLength={TEXT_MAX}
            placeholder="예: 구름이 빠르게 지나가고 있음, 그늘은 선선함"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            rows={2}
          />
        </div>

        <fieldset className="space-y-2 rounded-lg bg-gray-50 p-4">
          <legend className="px-1 text-sm font-medium text-gray-700">
            보상 안내를 받을 연락처 (선택)
          </legend>
          <p className="text-xs text-gray-500">
            보상을 받고 싶다면 이메일 또는 전화번호를 남겨주세요. 남기지 않아도 예측은 제출할 수
            있어요. 이 연락처는 다른 사용자에게 공개되지 않아요.
          </p>
          <div className="flex gap-2">
            <input
              type="text"
              inputMode="email"
              autoComplete="off"
              value={contact}
              onChange={(e) => setContact(e.target.value)}
              maxLength={254}
              placeholder="이메일 또는 전화번호 (예: 010-1234-5678)"
              aria-label="보상 안내용 연락처"
              className="min-w-0 flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
            {user && contact !== user.email && (
              <button
                type="button"
                onClick={() => setContact(user.email)}
                className="shrink-0 rounded-lg border border-gray-300 px-3 py-2 text-xs text-gray-700 hover:bg-white"
              >
                로그인 이메일 사용
              </button>
            )}
          </div>
          {contact.trim() && (
            <div className="space-y-2 rounded-lg border border-gray-200 bg-white p-3">
              <dl className="space-y-1 text-xs text-gray-600">
                {CONSENT_ITEMS.map(([k, v]) => (
                  <div key={k} className="flex gap-2">
                    <dt className="w-16 shrink-0 text-gray-400">{k}</dt>
                    <dd>{v}</dd>
                  </div>
                ))}
              </dl>
              <label className="flex items-start gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={consent}
                  onChange={(e) => setConsent(e.target.checked)}
                  className="mt-0.5 h-4 w-4"
                />
                위 내용에 동의하고 연락처를 남깁니다. (필수)
              </label>
              <p className="text-xs text-gray-400">
                동의하지 않으면 연락처 칸을 비워두고 제출해주세요.
              </p>
            </div>
          )}
        </fieldset>

        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}

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
          {result.reward_contact_registered && (
            <p className="mt-3 text-center text-xs text-green-700">
              보상 안내용 연락처가 등록되었어요.
            </p>
          )}
          <p className="mt-3 text-center text-xs text-gray-500">
            오늘 하루가 지나면 실제 날씨/최고기온과 비교해서 누가 더 정확했는지
            아래 기록에서 확인할 수 있어요.
          </p>
        </section>
      )}

      <section>
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-semibold">예측 기록</h2>
          {user && (
            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={showMine}
                onChange={(e) => setShowMine(e.target.checked)}
                className="h-4 w-4"
              />
              내 예측만 보기 (모든 지점)
            </label>
          )}
        </div>
        {history.length === 0 ? (
          <p className="text-sm text-gray-500">아직 예측 기록이 없습니다.</p>
        ) : (
          <ul className="space-y-3">
            {history.map((p) => (
              <ResultRow key={p.id} p={p} showStation={showMine} />
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
