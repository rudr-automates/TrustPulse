"use client";

import {
  ChangeEvent,
  FormEvent,
  useEffect,
  useState,
} from "react";

import { supabase } from "../../src/lib/supabase";

type EvidenceCategory =
  | "repayment"
  | "recurring_payment"
  | "business"
  | "income_sales"
  | "tax"
  | "asset"
  | "supporting";

interface EvidenceItem {
  id: string;
  profile_id: string;
  category: EvidenceCategory;
  original_filename: string;
  mime_type: string;
  storage_path: string;
  status: string;
}

const categories: {
  value: EvidenceCategory;
  label: string;
  description: string;
}[] = [
  {
    value: "repayment",
    label: "Repayment",
    description: "Loan repayments, instalments, lender receipts",
  },
  {
    value: "recurring_payment",
    label: "Bills & recurring payments",
    description:
      "Electricity, water, rent, telecom and similar payments",
  },
  {
    value: "business",
    label: "Business evidence",
    description:
      "Supplier invoices, business invoices, transaction records",
  },
  {
    value: "income_sales",
    label: "Income & sales",
    description:
      "Sales records, income records, payment records",
  },
  {
    value: "tax",
    label: "Tax",
    description:
      "Tax-payment receipts and GST-related records",
  },
  {
    value: "asset",
    label: "Assets",
    description:
      "Asset ownership, purchase records, warranty cards",
  },
  {
    value: "supporting",
    label: "Supporting evidence",
    description:
      "Affidavits, references and other supporting documents",
  },
];

export default function EvidencePage() {
  const [category, setCategory] =
    useState<EvidenceCategory>("repayment");

  const [file, setFile] = useState<File | null>(null);

  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);

  const [status, setStatus] = useState("");

  const [isUploading, setIsUploading] = useState(false);

  const [deletingId, setDeletingId] = useState<string | null>(
    null,
  );

  const [isBuildingResume, setIsBuildingResume] =
    useState(false);

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

  async function loadEvidence() {
    const session = await getSession();

    if (!session) {
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/evidence`,
        {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ?? "Unable to load evidence.",
        );
      }

      setEvidence(data);
    } catch (error) {
      setStatus(
        error instanceof Error
          ? error.message
          : "Unable to load evidence.",
      );
    }
  }

  useEffect(() => {
    loadEvidence();
  }, []);

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const selectedFile = event.target.files?.[0] ?? null;

    setFile(selectedFile);
    setStatus("");
  }

  async function handleUpload(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!file) {
      setStatus("Please choose a file first.");
      return;
    }

    setIsUploading(true);
    setStatus("Uploading your evidence...");

    try {
      const session = await getSession();

      if (!session) {
        return;
      }

      const formData = new FormData();

      formData.append("category", category);
      formData.append("file", file);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/evidence`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
          body: formData,
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ?? "Unable to upload evidence.",
        );
      }

      setEvidence((current) => [data, ...current]);

      setFile(null);

      const input = document.getElementById(
        "evidence-file",
      ) as HTMLInputElement | null;

      if (input) {
        input.value = "";
      }

      setStatus("Evidence uploaded successfully.");
    } catch (error) {
      setStatus(
        error instanceof Error
          ? error.message
          : "Something went wrong while uploading.",
      );
    } finally {
      setIsUploading(false);
    }
  }

  async function handleDelete(evidenceId: string) {
    const confirmed = window.confirm(
      "Delete this evidence permanently?",
    );

    if (!confirmed) {
      return;
    }

    setDeletingId(evidenceId);
    setStatus("Deleting evidence...");

    try {
      const session = await getSession();

      if (!session) {
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/evidence/${evidenceId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ?? "Unable to delete evidence.",
        );
      }

      setEvidence((current) =>
        current.filter(
          (item) => item.id !== evidenceId,
        ),
      );

      setStatus("Evidence deleted.");
    } catch (error) {
      setStatus(
        error instanceof Error
          ? error.message
          : "Unable to delete evidence.",
      );
    } finally {
      setDeletingId(null);
    }
  }

  async function buildResume() {
    setIsBuildingResume(true);
    setStatus(
      "Preparing your Financial Resume...",
    );

    try {
      const session = await getSession();

      if (!session) {
        return;
      }

      const token = session.access_token;

      // -----------------------------------------------------
      // 1. Load all evidence
      // -----------------------------------------------------

      const evidenceResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/evidence`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      const evidenceData =
        await evidenceResponse.json();

      if (!evidenceResponse.ok) {
        throw new Error(
          evidenceData.detail ??
            "Unable to load evidence.",
        );
      }

      const evidenceItems: EvidenceItem[] =
        evidenceData;

      if (evidenceItems.length === 0) {
        throw new Error(
          "Add at least one evidence document before building your Financial Resume.",
        );
      }

      // -----------------------------------------------------
      // 2. Analyze every evidence item
      // -----------------------------------------------------

      for (const item of evidenceItems) {
        setStatus(
          `Analyzing ${item.original_filename}...`,
        );

        const analysisResponse =
          await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/api/v1/evidence/${item.id}/analyze`,
            {
              method: "POST",
              headers: {
                Authorization: `Bearer ${token}`,
              },
            },
          );

        const analysisData =
          await analysisResponse.json();

        if (!analysisResponse.ok) {
          throw new Error(
            analysisData.detail ??
              `Unable to analyze ${item.original_filename}.`,
          );
        }
      }

      // -----------------------------------------------------
      // 3. Triangulate evidence
      // -----------------------------------------------------

      setStatus(
        "Comparing evidence across your financial records...",
      );

      const triangulationResponse =
        await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/evidence/triangulate`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );

      const triangulationData =
        await triangulationResponse.json();

      if (!triangulationResponse.ok) {
        throw new Error(
          triangulationData.detail ??
            "Unable to triangulate evidence.",
        );
      }

      // -----------------------------------------------------
      // 4. Generate financial signals
      // -----------------------------------------------------

      setStatus(
        "Generating financial signals...",
      );

      const signalsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/evidence/generate-signals`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      const signalsData =
        await signalsResponse.json();

      if (!signalsResponse.ok) {
        throw new Error(
          signalsData.detail ??
            "Unable to generate financial signals.",
        );
      }

      // -----------------------------------------------------
      // 5. Calculate Trust + Confidence
      // -----------------------------------------------------

      setStatus(
        "Calculating your Trust and Confidence...",
      );

      const trustResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/trust/calculate`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      const trustData =
        await trustResponse.json();

      if (!trustResponse.ok) {
        throw new Error(
          trustData.detail ??
            "Unable to calculate Trust.",
        );
      }

      // -----------------------------------------------------
      // 6. Generate Financial Resume
      // -----------------------------------------------------

      setStatus(
        "Building your Financial Resume...",
      );

      const resumeResponse =
        await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/resume/generate`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );

      const resumeData =
        await resumeResponse.json();

      if (!resumeResponse.ok) {
        throw new Error(
          resumeData.detail ??
            "Unable to generate Financial Resume.",
        );
      }

      // -----------------------------------------------------
      // 7. Open the completed Resume
      // -----------------------------------------------------

      window.location.href = "/resume";
    } catch (error) {
      setStatus(
        error instanceof Error
          ? error.message
          : "Something went wrong while building your Financial Resume.",
      );
    } finally {
      setIsBuildingResume(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f8f5ec] px-6 py-10">
      <div className="mx-auto max-w-5xl">
        {/* Header */}

        <div className="mb-8">
          <p className="text-sm font-semibold text-green-700">
            02 · Evidence Vault
          </p>

          <h1 className="mt-2 text-3xl font-bold text-gray-900 md:text-4xl">
            Build your Evidence Vault
          </h1>

          <p className="mt-3 max-w-2xl text-gray-600">
            Add legitimate records from your financial life.
            These records help TrustPulse build a clearer
            financial identity.
          </p>
        </div>

        {/* Upload + Evidence */}

        <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <form
            onSubmit={handleUpload}
            className="rounded-3xl bg-white p-8 shadow-sm"
          >
            <div>
              <label className="mb-2 block text-sm font-semibold text-gray-900">
                What kind of evidence are you adding?
              </label>

              <select
                value={category}
                onChange={(event) =>
                  setCategory(
                    event.target.value as EvidenceCategory,
                  )
                }
                disabled={
                  isUploading ||
                  isBuildingResume
                }
                className="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none focus:border-green-600 disabled:cursor-not-allowed disabled:bg-gray-50"
              >
                {categories.map((item) => (
                  <option
                    key={item.value}
                    value={item.value}
                  >
                    {item.label}
                  </option>
                ))}
              </select>

              <p className="mt-2 text-sm text-gray-500">
                {
                  categories.find(
                    (item) =>
                      item.value === category,
                  )?.description
                }
              </p>
            </div>

            <div className="mt-6">
              <label
                htmlFor="evidence-file"
                className="mb-2 block text-sm font-semibold text-gray-900"
              >
                Upload your document
              </label>

              <input
                id="evidence-file"
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.docx"
                onChange={handleFileChange}
                disabled={
                  isUploading ||
                  isBuildingResume
                }
                className="block w-full rounded-xl border border-gray-300 bg-white p-3 text-sm text-gray-900 disabled:cursor-not-allowed disabled:bg-gray-50"
              />

              <p className="mt-2 text-xs text-gray-500">
                Supported: PDF, JPG, JPEG, PNG, DOCX ·
                Maximum 6 MB
              </p>
            </div>

            {file && (
              <div className="mt-5 rounded-xl bg-gray-50 p-4">
                <p className="text-sm font-medium text-gray-900">
                  Selected file
                </p>

                <p className="mt-1 break-all text-sm text-gray-600">
                  {file.name}
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={
                isUploading ||
                isBuildingResume
              }
              className="mt-6 w-full rounded-xl bg-green-700 px-6 py-3 font-semibold text-white transition hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isUploading
                ? "Uploading..."
                : "Add Evidence →"}
            </button>

            {status && (
              <div className="mt-5 rounded-xl bg-gray-50 p-4 text-sm text-gray-700">
                {status}
              </div>
            )}
          </form>

          <section className="rounded-3xl bg-white p-8 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  Your evidence
                </h2>

                <p className="mt-1 text-sm text-gray-600">
                  Your uploaded records are stored securely.
                </p>
              </div>

              <span className="rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-700">
                {evidence.length}
              </span>
            </div>

            <div className="mt-6 space-y-3">
              {evidence.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-gray-300 p-6 text-center">
                  <p className="text-sm font-medium text-gray-800">
                    No evidence added yet
                  </p>

                  <p className="mt-1 text-sm text-gray-500">
                    Your first uploaded document will
                    appear here.
                  </p>
                </div>
              ) : (
                evidence.map((item) => (
                  <div
                    key={item.id}
                    className="rounded-2xl border border-gray-200 p-4"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <p className="break-all font-medium text-gray-900">
                          {item.original_filename}
                        </p>

                        <p className="mt-1 text-sm capitalize text-gray-500">
                          {item.category.replace(
                            "_",
                            " ",
                          )}
                        </p>
                      </div>

                      <span className="shrink-0 rounded-full bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
                        {item.status}
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        handleDelete(item.id)
                      }
                      disabled={
                        deletingId === item.id ||
                        isBuildingResume
                      }
                      className="mt-4 text-sm font-medium text-red-600 hover:text-red-700 disabled:opacity-50"
                    >
                      {deletingId === item.id
                        ? "Deleting..."
                        : "Delete evidence"}
                    </button>
                  </div>
                ))
              )}
            </div>

            {/* Build Financial Resume */}

            <div className="mt-8 border-t border-gray-200 pt-6">
              <button
                type="button"
                onClick={buildResume}
                disabled={
                  isBuildingResume ||
                  isUploading ||
                  evidence.length === 0
                }
                className="w-full rounded-xl bg-green-700 px-6 py-4 font-semibold text-white transition hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isBuildingResume
                  ? "Building Financial Resume..."
                  : "Build My Financial Resume →"}
              </button>

              <p className="mt-3 text-center text-xs leading-5 text-gray-500">
                TrustPulse will analyze, validate and compare
                your available evidence before generating
                your assessment.
              </p>
            </div>
          </section>
        </div>

        {/* Authenticity note */}

        <div className="mt-8 rounded-2xl border border-gray-200 bg-white p-5">
          <p className="text-sm font-medium text-gray-900">
            Authenticity note
          </p>

          <p className="mt-1 text-sm leading-6 text-gray-600">
            TrustPulse will assess submitted documents for
            signs of manipulation or AI-generated/edited
            content. This does not provide forensic or legal
            authentication. Official issuer verification
            would require authorized external institutional
            access.
          </p>
        </div>
      </div>
    </main>
  );
}