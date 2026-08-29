"use client";

import { FormEvent, useState } from "react";
import { supabase } from "../../src/lib/supabase";

export default function AuthPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [message, setMessage] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("Please wait...");

    if (mode === "signup") {
      const { error } = await supabase.auth.signUp({
        email,
        password,
      });

      if (error) {
        setMessage(error.message);
        return;
      }

      setMessage(
        "Account created. You can now continue to your Financial Identity.",
      );

      return;
    }

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      setMessage(error.message);
      return;
    }

    window.location.href = "/identity";
  }

  return (
    <main className="min-h-screen bg-[#f8f5ec] px-6 py-10">
      <div className="mx-auto flex min-h-[80vh] max-w-md items-center">
        <div className="w-full rounded-3xl bg-white p-8 shadow-sm">
          <p className="text-sm font-semibold text-green-700">
            TrustPulse
          </p>

          <h1 className="mt-3 text-3xl font-bold text-gray-900">
            {mode === "login"
              ? "Welcome back"
              : "Create your account"}
          </h1>

          <p className="mt-2 text-gray-600">
            Your financial identity belongs to you.
          </p>

          <form
            onSubmit={handleSubmit}
            className="mt-8 space-y-5"
          >
            <div>
              <label className="mb-2 block text-sm font-medium">
                Email
              </label>

              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                className="w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:border-green-600"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                required
                minLength={6}
                className="w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:border-green-600"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-xl bg-green-700 px-6 py-3 font-semibold text-white hover:bg-green-800"
            >
              {mode === "login" ? "Sign In" : "Create Account"}
            </button>
          </form>

          {message && (
            <p className="mt-5 rounded-xl bg-gray-50 p-4 text-sm text-gray-700">
              {message}
            </p>
          )}

          <button
            type="button"
            onClick={() =>
              setMode(mode === "login" ? "signup" : "login")
            }
            className="mt-5 text-sm font-medium text-green-700"
          >
            {mode === "login"
              ? "Need an account? Create one"
              : "Already have an account? Sign in"}
          </button>
        </div>
      </div>
    </main>
  );
}