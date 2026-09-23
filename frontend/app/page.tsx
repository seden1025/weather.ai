import Link from "next/link";

import WeatherDashboard from "@/components/WeatherDashboard";

export default function Home() {
  return (
    <main className="mx-auto max-w-3xl space-y-10 p-8">
      <header className="space-y-3 border-b border-gray-200 pb-6">
        <h1 className="text-2xl font-bold">Weather AI란?</h1>
        <p className="text-gray-600">
          기상청 슈퍼컴퓨터의 수치예보와는 별개로, 지난 5년간의 실제 관측
          데이터를 지도학습(machine learning)한 AI 모델로 날씨를 예측해보는
          연구 프로젝트입니다. 가끔 사람의 경험적 직관이 공식 예보보다 맞는
          경우를 보고, "그렇다면 AI는 어떨까?", "사람의 관찰은 정말 쓸모가
          있을까?"라는 궁금증에서 시작했습니다.
        </p>
        <p className="text-gray-600">
          평년과 크게 다른 이상치가 관측되면 과거 유사 사례와 관련 뉴스를 함께
          찾아 보여주고, 아래에서 지역을 선택하거나 내 위치로 가장 가까운
          관측지점을 찾아볼 수 있습니다.
        </p>
        <Link
          href="/predict"
          className="inline-block rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700"
        >
          🔭 오늘의 날씨 예상해보기 — 내 직관 vs AI
        </Link>
      </header>

      <WeatherDashboard />
    </main>
  );
}
