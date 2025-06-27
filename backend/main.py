import pandas as pd
from joblib import load
from thefuzz import process
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os 
from pydantic import BaseModel, Field
from typing import Optional


BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
MODEL_PATH = os.path.join(BASE_DIR, "football_predictor_advanced.joblib")
DATA_PATH = os.path.join(BASE_DIR, "Matches.csv")

app = FastAPI(title="Football Match Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def find_closest_team(name, team_list):
    best_match = process.extractOne(name, team_list)
    return best_match[0] if best_match and best_match[1] > 80 else None

def get_head_to_head(team1, team2, df):
    h2h_matches = df[((df['home_team_name'] == team1) & (df['away_team_name'] == team2)) | ((df['home_team_name'] == team2) & (df['away_team_name'] == team1))]
    if h2h_matches.empty: return {"summary": "No historical matches found.", "last_5": []}
    
    team1_wins, team2_wins, draws = 0, 0, 0
    for _, row in h2h_matches.iterrows():
        result = row.get('FTResult', '')
        if (result == 'H' and row['home_team_name'] == team1) or (result == 'A' and row['away_team_name'] == team1): team1_wins += 1
        elif result == 'D': draws += 1
        else: team2_wins += 1
            
    last_5 = h2h_matches.sort_values(by='local_date', ascending=False).head(5)
    last_5_list = [f"{row['local_date'].strftime('%Y-%m-%d')}: {row['home_team_name']} {int(row.get('home_team_score',0))}-{int(row.get('away_team_score',0))} {row['away_team_name']}" for _, row in last_5.iterrows()]

    return {"summary": f"{team1} Wins: {team1_wins} | {team2} Wins: {team2_wins} | Draws: {draws}", "last_5": last_5_list}

resources = {}

@app.on_event("startup")
def load_resources():
    print("Loading model and data resources...")
    if not os.path.exists(MODEL_PATH) or not os.path.exists(DATA_PATH):
        print(f"FATAL ERROR: Could not find model at '{MODEL_PATH}' or data at '{DATA_PATH}'")
        resources["model"] = None
        return

    try:
        model, predictors = load(MODEL_PATH)
        matches_df = pd.read_csv(DATA_PATH, index_col=0, low_memory=False)
        matches_df.rename(columns={'HomeTeam': 'home_team_name', 'AwayTeam': 'away_team_name', 'FTHome': 'home_team_score', 'FTAway': 'away_team_score', 'MatchDate': 'local_date'}, inplace=True)
        matches_df['local_date'] = pd.to_datetime(matches_df['local_date'], errors='coerce')
        
        processed_matches = []
        for _, row in matches_df.iterrows():
             for venue in ['Home', 'Away']:
                opponent_venue = "away" if venue == "Home" else "home"
                if pd.isna(row[f'{venue.lower()}_team_name']): continue
                
                if venue == 'Home':
                    if row['home_team_score'] > row['away_team_score']: result = 'W'
                    elif row['home_team_score'] < row['away_team_score']: result = 'L'
                    else: result = 'D'
                else: 
                    if row['away_team_score'] > row['home_team_score']: result = 'W'
                    elif row['away_team_score'] < row['home_team_score']: result = 'L'
                    else: result = 'D'

                processed_matches.append({
                    'team': row[f'{venue.lower()}_team_name'], 'opponent': row[f'{opponent_venue}_team_name'],
                    'venue': venue, 'date': row['local_date'], 'elo_for': row.get(f'{venue}Elo'),
                    'elo_against': row.get(f'{opponent_venue.capitalize()}Elo'), 'form_for': row.get(f'Form5{venue}'),
                    'odds_for': row.get(f'Odd{venue}'), 'odds_draw': row.get('OddDraw'),
                    'odds_against': row.get(f'Odd{opponent_venue.capitalize()}'), 'result': result
                })
        
        matches_processed = pd.DataFrame(processed_matches)
        matches_processed["team_code"] = matches_processed["team"].astype("category").cat.codes
        matches_processed["opponent_code"] = matches_processed["opponent"].astype("category").cat.codes
        
        resources["model"] = model
        resources["predictors"] = predictors
        resources["original_df"] = matches_df
        resources["processed_df"] = matches_processed
        resources["all_teams"] = list(matches_processed['team'].unique())
        print("Resources loaded successfully.")
        
    except Exception as e:
        print(f"An error occurred during resource loading: {e}")
        resources["model"] = None

class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    odds_home: Optional[float] = Field(default=0.0)
    odds_draw: Optional[float] = Field(default=0.0)
    odds_away: Optional[float] = Field(default=0.0)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Football Predictor API"}

@app.post("/predict/")
def handle_prediction(request: PredictionRequest):
    if not resources.get("model"):
        raise HTTPException(status_code=503, detail="Model is not loaded. The server is unavailable.")

    home_team = find_closest_team(request.home_team, resources["all_teams"])
    away_team = find_closest_team(request.away_team, resources["all_teams"])
    if not home_team or not away_team:
        raise HTTPException(status_code=404, detail="One or both team names could not be found.")

    h2h_stats = get_head_to_head(home_team, away_team, resources["original_df"])

    try:
        model = resources["model"]
        predictors = resources["predictors"]
        processed_df = resources["processed_df"]

        home_team_latest = processed_df[processed_df['team'] == home_team].sort_values('date', ascending=False).iloc[0]
        away_team_latest = processed_df[processed_df['team'] == away_team].sort_values('date', ascending=False).iloc[0]

        prediction_data = {
            "team_code": home_team_latest['team_code'], "opponent_code": away_team_latest['team_code'],
            "venue_code": 1, "day_code": 5, "elo_for": home_team_latest['elo_for'],
            "elo_against": away_team_latest['elo_for'], "form_for": home_team_latest['form_for'],
            "odds_for": request.odds_home, "odds_draw": request.odds_draw, "odds_against": request.odds_away
        }
        prediction_df = pd.DataFrame([prediction_data], columns=predictors)
        
        probabilities = model.predict_proba(prediction_df)[0]
        classes = model.classes_
        prob_map = dict(zip(classes, probabilities))

        return {
            "found_home_team": home_team, "found_away_team": away_team,
            "prediction": { "home_team_win_prob": prob_map.get('W', 0), "draw_prob": prob_map.get('D', 0), "away_team_win_prob": prob_map.get('L', 0) },
            "head_to_head": h2h_stats,
        }
    except (IndexError, ValueError):
        raise HTTPException(status_code=400, detail="Could not make prediction. A team may not have enough historical data.")