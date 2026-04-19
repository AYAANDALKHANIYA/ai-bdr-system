"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please upload a CSV file");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("https://ai-bdr-system.onrender.com/run-bdr-agent", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error(error);
      alert("Error connecting to backend");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white">

      {/* HERO */}
      <div className="flex flex-col items-center justify-center text-center py-20 px-4">
        <h1 className="text-5xl font-bold mb-4">
          AI BDR Agent 🚀
        </h1>

        <p className="text-gray-400 max-w-xl">
          Upload a CSV and let AI research, enrich, generate emails,
          and score your leads automatically.
        </p>

        {/* Upload Card */}
        <div className="mt-10 bg-white/10 backdrop-blur-lg border border-white/20 p-6 rounded-2xl shadow-lg w-full max-w-md">

          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            className="mb-4 w-full text-sm"
          />

          <button
            onClick={handleUpload}
            className="w-full bg-blue-500 hover:bg-blue-600 transition px-4 py-2 rounded-lg font-semibold"
          >
            {loading ? "Running AI..." : "Run AI Agent"}
          </button>

        </div>
      </div>

      {/* RESULTS */}
      <div className="max-w-5xl mx-auto px-4 pb-20">

        {results.length > 0 && (
          <h2 className="text-2xl font-semibold mb-6">
            Results
          </h2>
        )}

        {results.map((item, index) => (
          <div
            key={index}
            className="bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-2xl mb-6 shadow-md hover:scale-[1.01] transition"
          >

            <h3 className="text-xl font-bold mb-2">
              {item.name} — {item.company}
            </h3>

            <p className="text-gray-400 mb-2">
              <b>Industry:</b> {item.industry}
            </p>

            <p className="mb-3">
              <b>Insights:</b> {item.insights}
            </p>

            <div className="bg-black/40 p-3 rounded-lg mb-3">
              <b>Email:</b>
              <pre className="whitespace-pre-wrap text-sm mt-2">
                {item.email}
              </pre>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">
                Lead Score
              </span>

              <span className="bg-green-500 px-3 py-1 rounded-full text-sm font-semibold">
                {item.score}
              </span>
            </div>

          </div>
        ))}

      </div>

    </div>
  );
}