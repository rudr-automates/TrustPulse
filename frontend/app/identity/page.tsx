"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

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
  const [form, setForm] =
    useState<ProfileForm>(initialForm);

  const [status, setStatus] = useState("");

  const [loadingProfile, setLoadingProfile] =
    useState(true);

  const [existingProfile, setExistingProfile] =
    useState(false);

  const [saving, setSaving] = useState(false);

  function updateField(
    field: keyof ProfileForm,
    value: string | boolean,
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function getSession() {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session) {
      window.location.href = "/auth";
      return null;
    }

    return session;
  }

  useEffect(() => {
    async function loadExistingProfile() {
      const session = await getSession();

      if (!session) {
        return;
      }

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/profile`,
          {
            headers: {
              Authorization: `Bearer ${session.access_token}`,
            },
          },
        );

        if (response.status === 404) {
          // First-time user: profile does not exist yet.
          setExistingProfile(false);
          return;
        }

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail ??
              "Unable to load your profile.",
          );
        }

        // Existing profile found.
        setExistingProfile(true);

        setForm({
          full_name: data.full_name ?? "",
          occupation: data.occupation ?? "",
          years_in_business:
            data.years_in_business !== null &&
            data.years_in_business !== undefined
              ? String(data.years_in_business)
              : "",
          location: data.location ?? "",
          language:
            data.language === "hi"
              ? "hi"
              : "en",
          consent_accepted:
            Boolean(data.consent_accepted),
        });

        setStatus(
          "Your Financial Identity already exists.",
        );
      } catch (error) {
        setStatus(
          error instanceof Error
            ? error.message
            : "Unable to load your profile.",
        );
      } finally {
        setLoadingProfile(false);
      }
    }

    loadExistingProfile();
  }, []);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const session = await getSession();

    if (!session) {
      return;
    }

    // -------------------------------------------------------
    // Existing user → simply continue
    // -------------------------------------------------------

    if (existingProfile) {
      window.location.href = "/evidence";
      return;
    }

    setSaving(true);
    setStatus("Saving...");

    try {
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
            years_in_business: Number(
              form.years_in_business,
            ),
            location: form.location,
            language: form.language,
            consent_accepted:
              form.consent_accepted,
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ??
            "Unable to save profile.",
        );
      }

      setStatus(
        "Financial Identity created successfully.",
      );

      window.location.href = "/evidence";
    } catch (error) {
      setStatus(
        error instanceof Error
          ? error.message
          : "Something went wrong.",
      );
    } finally {
      setSaving(false);
    }
  }

  if (loadingProfile) {
    return (
      <main className="min-h-screen bg-[#f8f5ec] px-6 py-10">
        <div className="mx-auto max-w-3xl">
          <div className="rounded-3xl bg-white p-8 shadow-sm">
            <p className="text-gray-600">
              Loading your Financial Identity...
            </p>
          </div>
        </div>
      </main>
    );
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

          <div className="rounded-full border border-gray-200 bg-white px-4 py-2 text-sm text-gray-700">
            English · हिंदी
          </div>
        </div>

        {existingProfile && (
          <div className="mb-5 rounded-2xl border border-green-200 bg-green-50 p-4">
            <p className="text-sm font-semibold text-green-900">
              Financial Identity already exists
            </p>

            <p className="mt-1 text-sm text-green-800">
              Your existing profile has been loaded.
              Continue to your Evidence Vault.
            </p>
          </div>
        )}

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
                updateField(
                  "full_name",
                  event.target.value,
                )
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
                updateField(
                  "occupation",
                  event.target.value,
                )
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
                updateField(
                  "location",
                  event.target.value,
                )
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
              required={!existingProfile}
              className="mt-1"
            />

            <span className="text-sm leading-6 text-gray-600">
              I consent to TrustPulse using the
              financial information I provide to
              create my Financial Resume.
            </span>
          </label>

          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-xl bg-green-700 px-6 py-3 font-semibold text-white transition hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {saving
              ? "Saving..."
              : existingProfile
                ? "Continue to Evidence →"
                : "Create Financial Identity →"}
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