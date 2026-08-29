import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[#f8f5ec] px-6 py-10">
      <div className="mx-auto flex min-h-[80vh] max-w-5xl items-center">
        <div className="w-full rounded-3xl bg-white p-8 shadow-sm md:p-12">
          <div className="mb-10 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-700">
                TrustPulse
              </p>

              <h1 className="mt-2 text-3xl font-bold tracking-tight text-gray-900 md:text-5xl">
                Build your Financial Resume.
              </h1>
            </div>

            <div className="rounded-full border border-gray-200 px-4 py-2 text-sm">
              English · हिंदी
            </div>
          </div>

          <div className="max-w-2xl">
            <p className="text-lg leading-8 text-gray-600">
              Turn the financial evidence already present in your everyday
              life into a financial identity you can understand and build on.
            </p>

            <Link
              href="/identity"
              className="mt-8 inline-flex rounded-xl bg-green-700 px-6 py-3 font-semibold text-white transition hover:bg-green-800"
            >
              Create Your Financial Identity →
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}