"use client";

import { useEffect, useState } from "react";

import { supabase } from "../../src/lib/supabase";

interface DimensionScore {
  dimension: string;
  label: string;
  score: number;
}

interface EvidenceItem {
  id: string;
  category: string;
  filename: string;
  status: string;
}

interface SignalItem {
  dimension: string;
  signal_type: string;
  signal_score: number;
  strength: number;
  evidence_ids: string[];
}

interface Recommendation {
  type: string;
  title: string;
  description: string;
  priority: string;
  source_dimension: string | null;
}

interface ResumeData {
  identity: {
    full_name: string;
    occupation: string;
    years_in_business: number;
    location: string;
    language: string;
  };

  assessment: {
    trust_score: number;
    confidence_score: number;
    dimension_scores: DimensionScore[];
  };

  evidence: {
    total_count: number;
    items: EvidenceItem[];
  };

  financial_signals: SignalItem[];

  positive_indicators: string[];

  uncertainties: string[];

  explanation: string | null;

  recommendations: Recommendation[];
}

interface ResumeResponse {
  version: number;
  resume: ResumeData;
  created_at: string;
  updated_at: string;
}

function scoreLabel(score: number): string {
  if (score >= 80) {
    return "Strong";
  }

  if (score >= 60) {
    return "Positive";
  }

  if (score >= 40) {
    return "Developing";
  }

  return "Limited";
}

function categoryLabel(category: string): string {
  return category
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function priorityLabel(priority: string): string {
  return priority.charAt(0).toUpperCase() + priority.slice(1);
}

export default function ResumePage() {
  const [resume, setResume] =
    useState<ResumeResponse | null>(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  useEffect(() => {
    async function loadResume() {
      try {
        const {
          data: { session },
        } = await supabase.auth.getSession();

        if (!session) {
          window.location.href = "/auth";
          return;
        }

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/resume`,
          {
            headers: {
              Authorization: `Bearer ${session.access_token}`,
            },
          },
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail ?? "Unable to load Financial Resume.",
          );
        }

        setResume(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load Financial Resume.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadResume();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-[#f8f5ec] px-6 py-16">
        <div className="mx-auto max-w-5xl">
          <div className="rounded-3xl bg-white p-10 text-center shadow-sm">
            <p className="text-gray-600">
              Loading your Financial Resume...
            </p>
          </div>
        </div>
      </main>
    );
  }

  if (error || !resume) {
    return (
      <main className="min-h-screen bg-[#f8f5ec] px-6 py-16">
        <div className="mx-auto max-w-5xl">
          <div className="rounded-3xl bg-white p-10 text-center shadow-sm">
            <h1 className="text-2xl font-bold text-gray-900">
              Financial Resume unavailable
            </h1>

            <p className="mt-3 text-gray-600">
              {error ||
                "Generate your Financial Resume before opening this page."}
            </p>

            <button
              type="button"
              onClick={() => {
                window.location.href = "/evidence";
              }}
              className="mt-6 rounded-xl bg-green-700 px-6 py-3 font-semibold text-white hover:bg-green-800"
            >
              Back to Evidence →
            </button>
          </div>
        </div>
      </main>
    );
  }

  const data = resume.resume;

  return (
    <main className="min-h-screen bg-[#f8f5ec] px-6 py-10">
      <div className="mx-auto max-w-6xl">
        {/* Header */}

        <div className="mb-8 flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-semibold text-green-700">
              03 · Financial Resume
            </p>

            <h1 className="mt-2 text-3xl font-bold text-gray-900 md:text-4xl">
              {data.identity.full_name}
            </h1>

            <p className="mt-2 text-gray-600">
              {data.identity.occupation} ·{" "}
              {data.identity.location}
            </p>
          </div>

          <div className="rounded-full border border-gray-200 bg-white px-4 py-2 text-sm text-gray-600">
            Resume v{resume.version}
          </div>
        </div>

        {/* Score cards */}

        <section className="grid gap-5 md:grid-cols-2">
          <div className="rounded-3xl bg-white p-7 shadow-sm">
            <p className="text-sm font-medium text-gray-500">
              Trust Score
            </p>

            <div className="mt-3 flex items-end gap-2">
              <span className="text-5xl font-bold text-gray-900">
                {Math.round(
                  data.assessment.trust_score,
                )}
              </span>

              <span className="mb-2 text-gray-500">
                / 100
              </span>
            </div>

            <p className="mt-3 text-sm text-gray-600">
              Based on observed financial-reliability signals.
            </p>
          </div>

          <div className="rounded-3xl bg-white p-7 shadow-sm">
            <p className="text-sm font-medium text-gray-500">
              Confidence
            </p>

            <div className="mt-3 flex items-end gap-2">
              <span className="text-5xl font-bold text-gray-900">
                {Math.round(
                  data.assessment.confidence_score,
                )}
              </span>

              <span className="mb-2 text-gray-500">
                / 100
              </span>
            </div>

            <p className="mt-3 text-sm text-gray-600">
              How strongly the available evidence supports this assessment.
            </p>
          </div>
        </section>

        {/* Identity */}

        <section className="mt-6 rounded-3xl bg-white p-7 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900">
            Financial Identity
          </h2>

          <div className="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
                Occupation
              </p>

              <p className="mt-1 text-sm font-medium text-gray-900">
                {data.identity.occupation}
              </p>
            </div>

            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
                Years in business
              </p>

              <p className="mt-1 text-sm font-medium text-gray-900">
                {data.identity.years_in_business}
              </p>
            </div>

            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
                Location
              </p>

              <p className="mt-1 text-sm font-medium text-gray-900">
                {data.identity.location}
              </p>
            </div>

            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
                Evidence records
              </p>

              <p className="mt-1 text-sm font-medium text-gray-900">
                {data.evidence.total_count}
              </p>
            </div>
          </div>
        </section>

        {/* Dimension breakdown */}

        <section className="mt-6 rounded-3xl bg-white p-7 shadow-sm">
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              Trust Breakdown
            </h2>

            <p className="mt-1 text-sm text-gray-600">
              Your current observed financial signals by dimension.
            </p>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {data.assessment.dimension_scores.map(
              (dimension) => (
                <div
                  key={dimension.dimension}
                  className="rounded-2xl border border-gray-200 p-5"
                >
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="font-semibold text-gray-900">
                        {dimension.label}
                      </p>

                      <p className="mt-1 text-xs font-medium text-gray-500">
                        {scoreLabel(dimension.score)}
                      </p>
                    </div>

                    <p className="text-2xl font-bold text-gray-900">
                      {Math.round(dimension.score)}
                    </p>
                  </div>

                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-gray-100">
                    <div
                      className="h-full rounded-full bg-green-700"
                      style={{
                        width: `${Math.min(
                          100,
                          Math.max(
                            0,
                            dimension.score,
                          ),
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              ),
            )}
          </div>
        </section>

        {/* Why */}

        <section className="mt-6 grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl bg-white p-7 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900">
              Why this assessment?
            </h2>

            <p className="mt-4 leading-7 text-gray-600">
              {data.explanation ||
                "Your assessment is based on the financial evidence currently available."}
            </p>

            {data.positive_indicators.length >
              0 && (
              <div className="mt-6">
                <p className="text-sm font-semibold text-gray-900">
                  Positive indicators
                </p>

                <div className="mt-3 space-y-3">
                  {data.positive_indicators.map(
                    (item) => (
                      <div
                        key={item}
                        className="rounded-xl bg-green-50 p-3 text-sm text-green-900"
                      >
                        ✓ {item}
                      </div>
                    ),
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="rounded-3xl bg-white p-7 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900">
              What are we less certain about?
            </h2>

            {data.uncertainties.length > 0 ? (
              <div className="mt-4 space-y-3">
                {data.uncertainties.map(
                  (item) => (
                    <div
                      key={item}
                      className="rounded-xl bg-amber-50 p-3 text-sm text-amber-900"
                    >
                      ⚠ {item}
                    </div>
                  ),
                )}
              </div>
            ) : (
              <p className="mt-4 text-sm text-gray-600">
                No major uncertainty was identified in the current assessment.
              </p>
            )}
          </div>
        </section>

        {/* Evidence */}

        <section className="mt-6 rounded-3xl bg-white p-7 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Evidence used
              </h2>

              <p className="mt-1 text-sm text-gray-600">
                Records currently contributing to your Financial Resume.
              </p>
            </div>

            <span className="rounded-full bg-gray-100 px-3 py-1 text-sm font-semibold text-gray-700">
              {data.evidence.total_count}
            </span>
          </div>

          <div className="mt-6 grid gap-3">
            {data.evidence.items.map(
              (item) => (
                <div
                  key={item.id}
                  className="flex flex-col gap-3 rounded-2xl border border-gray-200 p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="min-w-0">
                    <p className="break-all font-medium text-gray-900">
                      {item.filename}
                    </p>

                    <p className="mt-1 text-sm text-gray-500">
                      {categoryLabel(item.category)}
                    </p>
                  </div>

                  <span className="w-fit rounded-full bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
                    {categoryLabel(item.status)}
                  </span>
                </div>
              ),
            )}
          </div>
        </section>

        {/* Recommendations */}

        <section className="mt-6 rounded-3xl bg-white p-7 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900">
            Recommended next steps
          </h2>

          <p className="mt-1 text-sm text-gray-600">
            Actions that could strengthen your financial profile.
          </p>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {data.recommendations.map(
              (recommendation) => (
                <div
                  key={`${recommendation.type}-${recommendation.title}`}
                  className="rounded-2xl border border-gray-200 p-5"
                >
                  <div className="flex items-center justify-between gap-4">
                    <h3 className="font-semibold text-gray-900">
                      {recommendation.title}
                    </h3>

                    <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
                      {priorityLabel(
                        recommendation.priority,
                      )}
                    </span>
                  </div>

                  <p className="mt-3 text-sm leading-6 text-gray-600">
                    {recommendation.description}
                  </p>
                </div>
              ),
            )}
          </div>
        </section>

        {/* Footer disclaimer */}

        <section className="mt-6 rounded-2xl border border-gray-200 bg-white p-5">
          <p className="text-sm font-medium text-gray-900">
            Document authenticity note
          </p>

          <p className="mt-1 text-sm leading-6 text-gray-600">
            TrustPulse assesses submitted documents for signs of
            manipulation or AI-generated/edited content. This does not
            provide forensic or legal authentication. Official issuer
            verification would require authorized external institutional
            access.
          </p>
        </section>
      </div>
    </main>
  );
}