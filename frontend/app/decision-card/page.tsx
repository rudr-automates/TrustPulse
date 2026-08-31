"use client";

import { useEffect, useState } from "react";

import { supabase } from "../../src/lib/supabase";

interface Dimension {
  label: string;
  score: number;
  dimension: string;
}

interface Recommendation {
  type: string;
  title: string;
  description: string;
  priority: string;
  source_dimension: string | null;
}

interface DecisionCard {
  borrower: {
    full_name: string;
    occupation: string;
    location: string;
  };

  trust: {
    score: number;
    confidence: number;
    dimensions: Dimension[];
  };

  summary: {
    evidence_count: number;
    positive_indicators: string[];
    uncertainties: string[];
  };

  recommendations: Recommendation[];

  explanation: string | null;

  disclaimer: string;
}

interface DecisionCardResponse {
  id: string;
  profile_id: string;
  resume_id: string;
  card: DecisionCard;
  created_at: string;
  updated_at: string;
}

function priorityLabel(
  priority: string,
): string {
  return (
    priority.charAt(0).toUpperCase() +
    priority.slice(1)
  );
}

export default function DecisionCardPage() {
  const [data, setData] =
    useState<DecisionCardResponse | null>(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDecisionCard() {
      try {
        const {
          data: { session },
        } = await supabase.auth.getSession();

        if (!session) {
          window.location.href = "/auth";
          return;
        }

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/decision-card`,
          {
            headers: {
              Authorization: `Bearer ${session.access_token}`,
            },
          },
        );

        const responseData =
          await response.json();

        if (!response.ok) {
          throw new Error(
            responseData.detail ??
              "Unable to load Decision Card.",
          );
        }

        setData(responseData);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load Decision Card.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadDecisionCard();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-[#f8f5ec] px-6 py-16">
        <div className="mx-auto max-w-4xl">
          <div className="rounded-3xl bg-white p-10 text-center shadow-sm">
            <p className="text-gray-600">
              Loading your Decision Card...
            </p>
          </div>
        </div>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="min-h-screen bg-[#f8f5ec] px-6 py-16">
        <div className="mx-auto max-w-4xl">
          <div className="rounded-3xl bg-white p-10 text-center shadow-sm">
            <h1 className="text-2xl font-bold text-gray-900">
              Decision Card unavailable
            </h1>

            <p className="mt-3 text-gray-600">
              {error ||
                "Generate your Decision Card before opening this page."}
            </p>

            <button
              type="button"
              onClick={() => {
                window.location.href = "/resume";
              }}
              className="mt-6 rounded-xl bg-green-700 px-6 py-3 font-semibold text-white hover:bg-green-800"
            >
              Back to Financial Resume →
            </button>
          </div>
        </div>
      </main>
    );
  }

  const card = data.card;

  return (
    <main className="min-h-screen bg-[#f8f5ec] px-6 py-10">
      <div className="mx-auto max-w-4xl">
        {/* Header */}

        <div className="mb-8">
          <p className="text-sm font-semibold text-green-700">
            04 · Decision Card
          </p>

          <h1 className="mt-2 text-3xl font-bold text-gray-900 md:text-4xl">
            {card.borrower.full_name}
          </h1>

          <p className="mt-2 text-gray-600">
            {card.borrower.occupation} ·{" "}
            {card.borrower.location}
          </p>
        </div>

        {/* Main score */}

        <section className="rounded-3xl bg-white p-8 shadow-sm">
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-2xl bg-gray-50 p-6">
              <p className="text-sm font-medium text-gray-500">
                Trust Score
              </p>

              <div className="mt-3 flex items-end gap-2">
                <span className="text-6xl font-bold text-gray-900">
                  {Math.round(card.trust.score)}
                </span>

                <span className="mb-2 text-gray-500">
                  / 100
                </span>
              </div>

              <p className="mt-3 text-sm text-gray-600">
                Observed financial-reliability signal.
              </p>
            </div>

            <div className="rounded-2xl bg-gray-50 p-6">
              <p className="text-sm font-medium text-gray-500">
                Confidence
              </p>

              <div className="mt-3 flex items-end gap-2">
                <span className="text-6xl font-bold text-gray-900">
                  {Math.round(
                    card.trust.confidence,
                  )}
                </span>

                <span className="mb-2 text-gray-500">
                  / 100
                </span>
              </div>

              <p className="mt-3 text-sm text-gray-600">
                Strength of support behind the assessment.
              </p>
            </div>
          </div>
        </section>

        {/* Dimensions */}

        <section className="mt-6 rounded-3xl bg-white p-7 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900">
            Financial Dimensions
          </h2>

          <div className="mt-5 space-y-4">
            {card.trust.dimensions.map(
              (dimension) => (
                <div
                  key={dimension.dimension}
                  className="rounded-2xl border border-gray-200 p-5"
                >
                  <div className="flex items-center justify-between gap-4">
                    <span className="font-semibold text-gray-900">
                      {dimension.label}
                    </span>

                    <span className="text-xl font-bold text-gray-900">
                      {Math.round(
                        dimension.score,
                      )}
                    </span>
                  </div>

                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-gray-100">
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

        {/* Summary */}

        <section className="mt-6 grid gap-6 md:grid-cols-2">
          <div className="rounded-3xl bg-white p-7 shadow-sm">
            <p className="text-sm text-gray-500">
              Evidence records
            </p>

            <p className="mt-2 text-3xl font-bold text-gray-900">
              {card.summary.evidence_count}
            </p>

            <p className="mt-2 text-sm text-gray-600">
              Records contributing to this Decision Card.
            </p>
          </div>

          <div className="rounded-3xl bg-white p-7 shadow-sm">
            <p className="text-sm font-medium text-gray-500">
              Assessment
            </p>

            <p className="mt-3 text-sm leading-6 text-gray-700">
              {card.explanation ||
                "This assessment is based on the evidence currently available."}
            </p>
          </div>
        </section>

        {/* Positive indicators */}

        {card.summary.positive_indicators.length >
          0 && (
          <section className="mt-6 rounded-3xl bg-white p-7 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900">
              Positive indicators
            </h2>

            <div className="mt-5 space-y-3">
              {card.summary.positive_indicators.map(
                (item) => (
                  <div
                    key={item}
                    className="rounded-xl bg-green-50 p-4 text-sm text-green-900"
                  >
                    ✓ {item}
                  </div>
                ),
              )}
            </div>
          </section>
        )}

        {/* Uncertainties */}

        {card.summary.uncertainties.length >
          0 && (
          <section className="mt-6 rounded-3xl bg-white p-7 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900">
              Areas of uncertainty
            </h2>

            <div className="mt-5 space-y-3">
              {card.summary.uncertainties.map(
                (item) => (
                  <div
                    key={item}
                    className="rounded-xl bg-amber-50 p-4 text-sm text-amber-900"
                  >
                    ⚠ {item}
                  </div>
                ),
              )}
            </div>
          </section>
        )}

        {/* Recommendations */}

        {card.recommendations.length > 0 && (
          <section className="mt-6 rounded-3xl bg-white p-7 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900">
              Recommended next steps
            </h2>

            <div className="mt-5 space-y-4">
              {card.recommendations.map(
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
        )}

        {/* Disclaimer */}

        <section className="mt-6 rounded-2xl border border-gray-200 bg-white p-5">
          <p className="text-sm leading-6 text-gray-600">
            {card.disclaimer}
          </p>
        </section>

        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={() => {
              window.location.href = "/resume";
            }}
            className="rounded-xl border border-gray-300 bg-white px-6 py-3 font-semibold text-gray-800 hover:bg-gray-50"
          >
            ← Back to Financial Resume
          </button>

          <button
            type="button"
            onClick={() => {
              window.location.href = "/evidence";
            }}
            className="rounded-xl bg-green-700 px-6 py-3 font-semibold text-white hover:bg-green-800"
          >
            Back to Evidence Vault
          </button>
        </div>
      </div>
    </main>
  );
}