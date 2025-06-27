# ⚽ AI Football Match Predictor

A full-stack web application that uses a machine learning model to predict the outcome of football matches. The project features a Python backend powered by FastAPI and a modern, responsive frontend built with Next.js and Tailwind CSS.

---

## ✨ Features

- **Probabilistic Predictions**: Get the percentage chance for a home win, draw, or away win — not just a single outcome.
- **Advanced Statistical Model**: Trained on historical data including Elo ratings, recent form, and betting odds.
- **Historical Context**: Displays head-to-head stats and last 5 matches of each team.
- **Intelligent Name Matching**: Uses fuzzy matching to find the correct team even with typos (e.g., `"Real Madrid"` vs. `"real madrid"`).
- **Efficient Backend**: Trained model is saved and reloaded on startup — no need to retrain each time.
- **Interactive Odds Input**: Users can input live betting odds for more accurate predictions.
- **Modern & Responsive UI**: Built with Next.js and Tailwind CSS, optimized for all screen sizes.

---

## 🛠️ Tech Stack

### **Backend**
- **Python**
- **FastAPI** – High-performance API framework
- **scikit-learn** – For training the Random Forest ML model
- **pandas** – Data manipulation and analysis
- **joblib** – Model serialization
- **Uvicorn** – ASGI server for running FastAPI

### **Frontend**
- **Next.js** (React framework)
- **TypeScript**
- **Tailwind CSS** – Utility-first styling

---

## 📂 Project Structure
```
/Soccer-Match-Predictor/
├── backend/
│ ├── main.py # FastAPI server
│ ├── football_predictor_advanced.joblib # Saved ML model
│ ├── Matches.csv # Training dataset
│ └── requirements.txt # Python dependencies
│
├── frontend/
│ ├── app/
│ │ ├── page.tsx # Main UI component
│ │ └── globals.css # Global Tailwind styles
│ ├── next.config.js
│ ├── package.json
│ └── tailwind.config.ts
│
└── README.md # This file
```
---

## 🚀 Getting Started (Local Development)

### 🔧 Prerequisites

- Python 3.9+
- Node.js 18.17+ and npm
---

### 🔹 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate     # On Windows

# Install Python packages
pip install -r requirements.txt

# Start the backend server (auto-trains model on first run)
uvicorn main:app --reload
```
### 🔹 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install frontend dependencies
npm install

# Start development server
npm run dev
```
