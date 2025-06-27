'use client';

import { useState, type FormEvent, type ChangeEvent } from 'react';

interface PredictionResponse {
  prediction: {
    home_team_win_prob: number;
    draw_prob: number;
    away_team_win_prob: number;
  };
  found_home_team: string;
  found_away_team: string;
}

const Spinner = () => (
  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
);

export default function Home() {
  const [homeTeam, setHomeTeam] = useState<string>('');
  const [awayTeam, setAwayTeam] = useState<string>('');
  const [oddsHome, setOddsHome] = useState<string>('');
  const [oddsDraw, setOddsDraw] = useState<string>('');
  const [oddsAway, setOddsAway] = useState<string>('');
  
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await fetch('http://localhost:8000/predict/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          home_team: homeTeam,
          away_team: awayTeam,
          odds_home: oddsHome ? parseFloat(oddsHome) : 0,
          odds_draw: oddsDraw ? parseFloat(oddsDraw) : 0,
          odds_away: oddsAway ? parseFloat(oddsAway) : 0,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Prediction request failed.');
      }
      const data: PredictionResponse = await response.json();
      setPrediction(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (setter: React.Dispatch<React.SetStateAction<string>>) => 
    (e: ChangeEvent<HTMLInputElement>) => {
      setter(e.target.value);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 to-blue-900 p-4">
      <main className="w-full max-w-lg">
        <div className="bg-white/10 backdrop-blur-lg rounded-xl shadow-2xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white">⚽ Match Predictor</h1>
            <p className="text-blue-200">Enter teams and optional odds for AI-powered predictions</p>
          </div>

          <form onSubmit={handlePredict} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <input type="text" value={homeTeam} onChange={handleInputChange(setHomeTeam)} placeholder="Home Team" required className="input-style" />
              <input type="text" value={awayTeam} onChange={handleInputChange(setAwayTeam)} placeholder="Away Team" required className="input-style" />
            </div>

            <div>
              <label className="block text-sm font-medium text-blue-200 mb-2">Betting Odds (Optional)</label>
              <div className="grid grid-cols-3 gap-4">
                <input type="number" step="0.01" value={oddsHome} onChange={handleInputChange(setOddsHome)} placeholder="Home" className="input-style text-center" />
                <input type="number" step="0.01" value={oddsDraw} onChange={handleInputChange(setOddsDraw)} placeholder="Draw" className="input-style text-center" />
                <input type="number" step="0.01" value={oddsAway} onChange={handleInputChange(setOddsAway)} placeholder="Away" className="input-style text-center" />
              </div>
            </div>

            <button type="submit" className="w-full flex justify-center items-center gap-2 text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 font-semibold rounded-lg text-md px-5 py-3 transition-all duration-300" disabled={isLoading}>
              {isLoading && <Spinner />}
              {isLoading ? 'Calculating...' : 'Predict Outcome'}
            </button>
          </form>

          {error && <p className="mt-6 text-center text-red-400 bg-red-900/50 p-3 rounded-lg">{error}</p>}
          
          {prediction && (
            <div className="mt-8 text-white">
              <h2 className="text-2xl font-semibold text-center mb-4">Prediction Results</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">

                <div className="bg-blue-500/30 p-4 rounded-lg border border-blue-400">
                  <div className="text-sm font-semibold">{prediction.found_home_team} Win</div>
                  <div className="text-4xl font-bold my-2">
                    {(prediction.prediction.home_team_win_prob * 100).toFixed(1)}%
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2.5">
                    <div className="bg-blue-400 h-2.5 rounded-full" style={{ width: `${prediction.prediction.home_team_win_prob * 100}%` }}></div>
                  </div>
                </div>
                <div className="bg-gray-500/30 p-4 rounded-lg border border-gray-400">
                  <div className="text-sm font-semibold">Draw</div>
                  <div className="text-4xl font-bold my-2">
                    {(prediction.prediction.draw_prob * 100).toFixed(1)}%
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2.5">
                    <div className="bg-gray-400 h-2.5 rounded-full" style={{ width: `${prediction.prediction.draw_prob * 100}%` }}></div>
                  </div>
                </div>
                <div className="bg-red-500/30 p-4 rounded-lg border border-red-400">
                  <div className="text-sm font-semibold">{prediction.found_away_team} Win</div>
                  <div className="text-4xl font-bold my-2">
                    {(prediction.prediction.away_team_win_prob * 100).toFixed(1)}%
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2.5">
                    <div className="bg-red-400 h-2.5 rounded-full" style={{ width: `${prediction.prediction.away_team_win_prob * 100}%` }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        <style jsx>{`
          .input-style {
            @apply bg-white/10 border border-white/20 rounded-lg py-2 px-4 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all duration-300;
          }
        `}</style>
      </main>
    </div>
  );
}