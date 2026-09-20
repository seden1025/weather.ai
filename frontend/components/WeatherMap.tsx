"use client";

import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";

import type { Station } from "@/lib/api";

const markerIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

function FlyTo({ center }: { center: [number, number] | null }) {
  const map = useMap();
  useEffect(() => {
    if (center) map.flyTo(center, 11);
  }, [center, map]);
  return null;
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
  return (
    <MapContainer
      center={[36.5, 127.8]}
      zoom={7}
      scrollWheelZoom
      style={{ height: "360px", width: "100%", borderRadius: "0.75rem" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FlyTo center={flyToCenter} />
      {stations.map((s) => (
        <Marker
          key={s.id}
          position={[s.lat, s.lon]}
          icon={markerIcon}
          eventHandlers={{ click: () => onSelectStation(s.id) }}
        >
          <Popup>{s.name}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
