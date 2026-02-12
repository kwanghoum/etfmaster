import EtfDashboard from "@/components/EtfDashboard";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-[1600px] mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          ETF Master Dashboard
        </h1>
        <EtfDashboard />
      </div>
    </main>
  );
}
