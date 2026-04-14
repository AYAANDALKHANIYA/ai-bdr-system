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
      const response = await fetch("http://127.0.0.1:8000/run-bdr-agent", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResults(data.results);

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
        {results.map((item, index) => (
          <div key={index} className="border p-4 mb-4 rounded">

            <h2 className="font-bold">
              {item.name} ({item.company})
            </h2>

            <p><b>Industry:</b> {item.industry}</p>

            <p><b>Insights:</b> {item.insights}</p>

            <p><b>Email:</b></p>
            <pre className="bg-gray-100 p-2 whitespace-pre-wrap">
              {item.email}
            </pre>

            <p><b>Score:</b> {item.score}</p>

          </div>
        ))}
      </div>
    </div>
  );
}