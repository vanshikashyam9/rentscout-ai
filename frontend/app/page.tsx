"use client";

import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [area, setArea] = useState("");
  const [marketStats, setMarketStats] = useState<any>(null);

  const [budget, setBudget] = useState("");
  const [areas, setAreas] = useState<any[]>([]);

  const [income, setIncome] = useState("");
  const [rent, setRent] = useState("");
  const [food, setFood] = useState("");
  const [transport, setTransport] = useState("");
  const [utilities, setUtilities] = useState("");
  const [other, setOther] = useState("");
  const [budgetResult, setBudgetResult] = useState<any>(null);

  const API = "http://127.0.0.1:8000";

  const getMarketStats = async () => {
    const res = await axios.get(
      `${API}/market-stats?area=${area}`
    );

    setMarketStats(res.data);
  };

  const getRecommendations = async () => {
    const res = await axios.get(
      `${API}/areas/recommend?budget=${budget}`
    );

    setAreas(res.data.recommendations);
  };

  const analyzeBudget = async () => {
    const res = await axios.post(
      `${API}/budget-analysis`,
      {
        income: Number(income),
        rent: Number(rent),
        food: Number(food),
        transport: Number(transport),
        utilities: Number(utilities),
        other: Number(other)
      }
    );

    setBudgetResult(res.data);
  };

  return (
    <main style={{ padding: "40px" }}>
      <h1>🏠 RentScout AI</h1>

      <hr />

      <h2>Market Statistics</h2>

      <input
        placeholder="Burnaby"
        value={area}
        onChange={(e) => setArea(e.target.value)}
      />

      <button onClick={getMarketStats}>
        Check Market
      </button>

      {marketStats && (
        <pre>
          {JSON.stringify(marketStats, null, 2)}
        </pre>
      )}

      <hr />

      <h2>Area Recommendations</h2>

      <input
        placeholder="Budget"
        value={budget}
        onChange={(e) => setBudget(e.target.value)}
      />

      <button onClick={getRecommendations}>
        Find Areas
      </button>

      {areas.map((area, index) => (
        <div key={index}>
          <h4>{area.area}</h4>
          <p>Score: {area.score}</p>
          <p>Vacancy: {area.vacancy_rate}%</p>
        </div>
      ))}

      <hr />

      <h2>Budget Analyzer</h2>

      <input
        placeholder="Income"
        value={income}
        onChange={(e) => setIncome(e.target.value)}
      />

      <input
        placeholder="Rent"
        value={rent}
        onChange={(e) => setRent(e.target.value)}
      />

      <input
        placeholder="Food"
        value={food}
        onChange={(e) => setFood(e.target.value)}
      />

      <input
        placeholder="Transport"
        value={transport}
        onChange={(e) => setTransport(e.target.value)}
      />

      <input
        placeholder="Utilities"
        value={utilities}
        onChange={(e) => setUtilities(e.target.value)}
      />

      <input
        placeholder="Other"
        value={other}
        onChange={(e) => setOther(e.target.value)}
      />

      <br />
      <br />

      <button onClick={analyzeBudget}>
        Analyze Budget
      </button>

      {budgetResult && (
        <pre>
          {JSON.stringify(budgetResult, null, 2)}
        </pre>
      )}
    </main>
  );
}