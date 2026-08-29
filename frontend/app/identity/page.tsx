"use client";

import { FormEvent, useState } from "react";
import { supabase } from "../../src/lib/supabase";

interface ProfileForm {
  full_name: string;
  occupation: string;
  years_in_business: string;
  location: string;
  language: "en" | "hi";
  consent_accepted: boolean;
}

const initialForm: ProfileForm = {
  full_name: "",
  occupation: "",
  years_in_business: "",
  location: "",
  language: "en",
  consent_accepted: false,
};

export default function IdentityPage() {
  const [form, setForm] = useState<ProfileForm>(initialForm);
  const [status, setStatus] = useState<string>("");

  function updateField(
    field: keyof ProfileForm,
    value: string | boolean,
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

async function handleSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();
  setStatus("Saving...");

  try {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session) {
      window.location.href = "/auth";
      return;
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/profile`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          full_name: form.full_name,
          occupation: form.occupation,
          years_in_business: Number(form.years_in_business),
          location: form.location,
          language: form.language,
          consent_accepted: form.consent_accepted,
        }),
      },
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail ?? "Unable to save profile.");
    }

    setStatus(`Profile created for ${data.full_name}.`);
  } catch (error) {
    setStatus(
      error instanceof Error
        ? error.message
        : "Something went wrong.",
    );
  }
}

  return (
    <main className="min-h-screen bg-[#f8f5ec] px-6 py-10">
      <div className="mx-auto max-w-3xl">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-green-700">
              01 · Financial Identity
            </p>

            <h1 className="mt-2 text-3xl font-bold text-gray-900">
              Who are you?
            </h1>

            <p className="mt-2 text-gray-600">
              Start building your Financial Resume.
            </p>
          </div>

          <div className="rounded-full border border-gray-200 bg-white px-4 py-2 text-sm">
            English · हिंदी
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-6 rounded-3xl bg-white p-8 shadow-sm"
        >
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-800">
              Full name
            </label>

            <input
              value={form.full_name}
              onChange={(event) =>
                updateField("full_name", event.target.value)
              }
              placeholder="Ramesh Kumar"
              required
              className="w-full rounded-xl border border-gray-300 px-4 py-3 text-gray-900 placeholder:text-gray-400 outline-none focus:border-green-600"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-800">
              Occupation / Business
            </label>

            <input
              value={form.occupation}
              onChange={(event) =>
                updateField("occupation", event.target.value)
              }
              placeholder="Kirana Store Owner"
              required
              className="w-full rounded-xl border border-gray-300 px-4 py-3 text-gray-900 placeholder:text-gray-400 outline-none focus:border-green-600"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-800">
              Years in business
            </label>

            <input
              type="number"
              min="0"
              max="100"
              value={form.years_in_business}
              onChange={(event) =>
                updateField(
                  "years_in_business",
                  event.target.value,
                )
              }
              placeholder="6"
              required
              className="w-full rounded-xl border border-gray-300 px-4 py-3 text-gray-900 placeholder:text-gray-400 outline-none focus:border-green-600"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-800">
              Location
            </label>

            <input
              value={form.location}
              onChange={(event) =>
                updateField("location", event.target.value)
              }
              placeholder="Jaipur, Rajasthan"
              required
              className="w-full rounded-xl border border-gray-300 px-4 py-3 text-gray-900 placeholder:text-gray-400 outline-none focus:border-green-600"
            />
          </div>

          <label className="flex gap-3 rounded-xl bg-gray-50 p-4">
            <input
              type="checkbox"
              checked={form.consent_accepted}
              onChange={(event) =>
                updateField(
                  "consent_accepted",
                  event.target.checked,
                )
              }
              required
              className="mt-1"
            />

            <span className="text-sm leading-6 text-gray-600">
              I consent to TrustPulse using the financial information I
              provide to create my Financial Resume.
            </span>
          </label>

          <button
            type="submit"
            className="w-full rounded-xl bg-green-700 px-6 py-3 font-semibold text-white transition hover:bg-green-800"
          >
            Continue →
          </button>

          {status && (
            <p className="rounded-xl bg-gray-50 p-4 text-sm text-gray-700">
              {status}
            </p>
          )}
        </form>
      </div>
    </main>
  );
}