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
      const response = await fetch(
        "https://ai-bdr-system.onrender.com/run-bdr-agent",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Backend error");
      }

      const data = await response.json();

      // ✅ Wrap single response into array
      setResults([data]);

    } catch (error) {
      console.error(error);
      alert("Error connecting to backend");
    }

    setLoading(false);
  };

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold mb-6">
        🚀 AI BDR Agent
      </h1>

      {/* Upload */}
      <input
        type="file"
        accept=".csv"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />

      <br />

      <button
        onClick={handleUpload}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        {loading ? "Running..." : "Run Agent"}
      </button>

      {/* Results */}
      <div className="mt-10">
        {results.length > 0 && results.map((item, index) => (
          <div key={index} className="border p-4 mb-4 rounded shadow">

            <h2 className="font-bold text-lg mb-2">
              Lead Analysis Result
            </h2>

            <p className="mb-2">
              <b>Insights:</b><br />
              {item.insights}
            </p>

            <p className="mb-2">
              <b>Email:</b>
            </p>
            <pre className="bg-gray-100 p-3 whitespace-pre-wrap rounded mb-2">
              {item.email}
            </pre>

            <p>
              <b>Score:</b> {item.score}
            </p>

          </div>
        ))}
      </div>
    </div>
  );
}