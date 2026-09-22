"use client";

import { useEffect, useRef } from "react";

import type { Station } from "@/lib/api";

const KAKAO_JS_KEY = process.env.NEXT_PUBLIC_KAKAO_JS_KEY ?? "";

declare global {
  interface Window {
    kakao: any;
  }
}

let kakaoLoadPromise: Promise<void> | null = null;

function loadKakaoSdk(): Promise<void> {
  if (kakaoLoadPromise) return kakaoLoadPromise;

  kakaoLoadPromise = new Promise((resolve, reject) => {
    if (window.kakao?.maps) {
      resolve();
      return;
    }
    const existing = document.getElementById("kakao-maps-sdk") as HTMLScriptElement | null;
    if (existing) {
      existing.addEventListener("load", () => window.kakao.maps.load(() => resolve()));
      existing.addEventListener("error", reject);
      return;
    }
    const script = document.createElement("script");
    script.id = "kakao-maps-sdk";
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_JS_KEY}&autoload=false`;
    script.onload = () => window.kakao.maps.load(() => resolve());
    script.onerror = reject;
    document.head.appendChild(script);
  });

  return kakaoLoadPromise;
}

export default function WeatherMap({
  stations,
  onSelectStation,
  flyToCenter,
}: {
  stations: Station[];
  onSelectStation: (id: string) => void;
  flyToCenter: [number, number] | null;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const myLocationMarkerRef = useRef<any>(null);

  useEffect(() => {
    if (!KAKAO_JS_KEY) return;
    let cancelled = false;

    loadKakaoSdk()
      .then(() => {
        if (cancelled || !containerRef.current) return;
        const kakao = window.kakao;
        const map = new kakao.maps.Map(containerRef.current, {
          center: new kakao.maps.LatLng(36.5, 127.8),
          level: 12,
        });
        mapRef.current = map;

        stations.forEach((s) => {
          const position = new kakao.maps.LatLng(s.lat, s.lon);
          const marker = new kakao.maps.Marker({ position, map });
          const infowindow = new kakao.maps.InfoWindow({
            content: `<div style="padding:4px 8px;font-size:12px;white-space:nowrap;">${s.name}</div>`,
          });
          kakao.maps.event.addListener(marker, "click", () => onSelectStation(s.id));
          kakao.maps.event.addListener(marker, "mouseover", () => infowindow.open(map, marker));
          kakao.maps.event.addListener(marker, "mouseout", () => infowindow.close());
        });
      })
      .catch(() => {
        // 키가 잘못됐거나 플랫폼(도메인) 등록이 안 된 경우 등 - 콘솔에서 확인
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stations]);

  useEffect(() => {
    if (!mapRef.current || !flyToCenter || !window.kakao) return;
    const kakao = window.kakao;
    const pos = new kakao.maps.LatLng(flyToCenter[0], flyToCenter[1]);
    mapRef.current.panTo(pos);

    if (myLocationMarkerRef.current) {
      myLocationMarkerRef.current.setMap(null);
    }
    myLocationMarkerRef.current = new kakao.maps.Marker({
      position: pos,
      map: mapRef.current,
      image: new kakao.maps.MarkerImage(
        "https://t1.daumcdn.net/mapjsapi/images/marker.png",
        new kakao.maps.Size(35, 47)
      ),
    });
  }, [flyToCenter]);

  if (!KAKAO_JS_KEY) {
    return (
      <div className="flex h-[360px] items-center justify-center rounded-xl border border-gray-200 text-sm text-gray-400">
        카카오 지도 키(NEXT_PUBLIC_KAKAO_JS_KEY)가 설정되지 않았습니다.
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      style={{ height: "360px", width: "100%" }}
      className="overflow-hidden rounded-xl border border-gray-200"
    />
  );
}
