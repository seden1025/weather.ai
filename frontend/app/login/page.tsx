"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { login, signup, useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (mode === "signup" && password.length < 8) {
      setError("비밀번호는 8자 이상으로 입력해주세요.");
      return;
    }
    setSubmitting(true);
    try {
      if (mode === "signup") {
        await signup(email, password);
      } else {
        await login(email, password);
      }
      router.push("/predict");
    } catch (err) {
      setError(err instanceof Error ? err.message : "요청에 실패했어요.");
    } finally {
      setSubmitting(false);
    }
  }

  if (user) {
    return (
      <main className="mx-auto max-w-md space-y-4 p-8">
        <h1 className="text-2xl font-bold">로그인됨</h1>
        <p className="text-sm text-gray-600">{user.email} 계정으로 로그인되어 있어요.</p>
        <div className="flex gap-2">
          <Link
            href="/predict"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white"
          >
            날씨 예상해보기
          </Link>
          <button
            onClick={logout}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700"
          >
            로그아웃
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-md space-y-6 p-8">
      <header className="space-y-2 border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold">{mode === "login" ? "로그인" : "회원가입"}</h1>
        <p className="text-sm text-gray-600">
          로그인하면 내가 한 예측을 계정에 모아서 다시 볼 수 있어요. 로그인하지 않아도 예측은
          할 수 있어요.
        </p>
      </header>

      <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-gray-200 p-5">
        <div>
          <label htmlFor="email" className="mb-1 block text-sm font-medium text-gray-700">
            이메일
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label htmlFor="password" className="mb-1 block text-sm font-medium text-gray-700">
            비밀번호
          </label>
          <input
            id="password"
            type="password"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={mode === "signup" ? 8 : undefined}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />
          {mode === "signup" && <p className="mt-1 text-xs text-gray-400">8자 이상</p>}
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {submitting ? "처리 중..." : mode === "login" ? "로그인" : "가입하고 시작하기"}
        </button>
      </form>

      <p className="text-center text-sm text-gray-600">
        {mode === "login" ? "아직 계정이 없나요?" : "이미 계정이 있나요?"}{" "}
        <button
          type="button"
          onClick={() => {
            setMode(mode === "login" ? "signup" : "login");
            setError(null);
          }}
          className="font-medium text-blue-600 underline"
        >
          {mode === "login" ? "회원가입" : "로그인"}
        </button>
      </p>
    </main>
  );
}
