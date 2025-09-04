import React, { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError("Please enter a question.");
      return;
    }

    setIsLoading(true);
    setAnswer("");
    setError("");

    try {
      const response = await fetch("http://localhost:5000/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error("Something went wrong with the API request.");
      }

      const data = await response.json();
      setAnswer(data.answer);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>RAG Q&A 📚</h1>
        <p>Ask a question about the Centauri-5 Laptop document.</p>

        <form onSubmit={handleSubmit} className="query-form">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., What kind of display does the laptop have?"
            rows="3"
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Thinking..." : "Ask Question"}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {answer && (
          <div className="answer-result">
            <h2>Answer:</h2>
            <p>{answer}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
