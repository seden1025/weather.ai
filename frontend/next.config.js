/** @type {import('next').NextConfig} */
const nextConfig = {
  // react-leaflet v4의 MapContainer가 StrictMode의 effect 이중 실행과
  // 충돌해 "Map container is already initialized" 오류를 일으켜서 끔.
  reactStrictMode: false,
};

module.exports = nextConfig;
