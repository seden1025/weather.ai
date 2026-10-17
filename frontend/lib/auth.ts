"use client";

import { useCallback, useEffect, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const TOKEN_KEY = "weather_ai_token";
const USER_KEY = "weather_ai_user";
const AUTH_EVENT = "weather-ai-auth";

export interface AuthUser {
  id: number;
  email: string;
}

interface AuthResponse {
  token: string;
  user: AuthUser;
}

// 브라우저 저장소는 막혀 있거나 비어 있을 수 있어서(시크릿 모드 등) 항상 try/catch로 감싼다.
function readStorage(key: string): string | null {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return readStorage(TOKEN_KEY);
}

function getStoredUser(): AuthUser | null {
  const raw = readStorage(USER_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (typeof parsed?.id === "number" && typeof parsed?.email === "string") return parsed;
  } catch {
    // 손상된 값은 무시
  }
  return null;
}

function setSession(token: string, user: AuthUser) {
  try {
    window.localStorage.setItem(TOKEN_KEY, token);
    window.localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch {
    // 저장 불가 환경에서는 이번 페이지에서만 로그인 상태가 유지되지 않는다.
  }
  window.dispatchEvent(new Event(AUTH_EVENT));
}

export function clearSession() {
  try {
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(USER_KEY);
  } catch {
    // 무시
  }
  window.dispatchEvent(new Event(AUTH_EVENT));
}

/** 로그인되어 있으면 Authorization 헤더를, 아니면 빈 객체를 돌려준다. */
export function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** FastAPI 오류 응답({detail: 문자열 | 검증 오류 배열})에서 사용자에게 보여줄 문장을 뽑는다. */
export async function readError(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    const detail = data?.detail;
    if (typeof detail === "string" && detail) return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      const msg = String(detail[0]?.msg ?? "").replace(/^Value error, /, "");
      if (msg) return msg;
    }
  } catch {
    // 본문이 JSON이 아니면 기본 문구 사용
  }
  return fallback;
}

async function authRequest(path: "signup" | "login", email: string, password: string) {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}/auth/${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
  } catch {
    throw new Error(
      "서버에 연결하지 못했어요. 잠시 후 다시 시도해주세요 (서버가 방금 깨어난 경우 최대 1분 걸릴 수 있어요)."
    );
  }
  if (!res.ok) {
    throw new Error(await readError(res, "요청에 실패했어요. 잠시 후 다시 시도해주세요."));
  }
  const data: AuthResponse = await res.json();
  setSession(data.token, data.user);
  return data.user;
}

export const signup = (email: string, password: string) => authRequest("signup", email, password);
export const login = (email: string, password: string) => authRequest("login", email, password);

/**
 * 현재 로그인 사용자. 처음 한 번 서버에 토큰이 아직 유효한지 확인하고,
 * 만료/위조된 토큰이면 로그아웃 상태로 되돌린다. (서버에 닿지 않을 때는 로그인 상태를 유지한다)
 */
export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const sync = () => setUser(getToken() ? getStoredUser() : null);
    sync();
    setReady(true);
    window.addEventListener(AUTH_EVENT, sync);
    window.addEventListener("storage", sync);

    const token = getToken();
    if (token) {
      fetch(`${API_BASE_URL}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
        .then((res) => {
          if (res.status === 401) clearSession();
        })
        .catch(() => {});
    }

    return () => {
      window.removeEventListener(AUTH_EVENT, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  const logout = useCallback(() => clearSession(), []);

  return { user, ready, logout };
}
