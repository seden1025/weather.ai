import WeatherDashboard from "@/components/WeatherDashboard";

export default function Home() {
  return (
    <main className="mx-auto max-w-3xl space-y-10 p-8">
      <header className="space-y-3 border-b border-gray-200 pb-6">
        <h1 className="text-3xl font-bold">Weather AI</h1>
        <p className="text-gray-600">
          기상청 수치예보 모델과는 별개로, 과거 관측 데이터를 지도학습한 AI로 날씨를
          예측하고 사람의 경험적 직관과 비교해보는 연구 프로젝트입니다.
        </p>
        <p className="text-gray-600">
          평년과 크게 다른 이상치가 관측되면 과거 유사 사례와 관련 뉴스를 함께
          찾아 보여줍니다. 아래에서 지역을 선택하거나 내 위치로 가장 가까운
          관측지점을 찾아보세요.
        </p>
      </header>

      <WeatherDashboard />
    </main>
  );
}
