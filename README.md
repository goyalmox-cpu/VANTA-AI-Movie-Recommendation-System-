# VANTA — AI-Powered Cinematic Recommendation Engine

> **Powered by AI. Guided by taste.**

VANTA is a hybrid movie recommendation platform that blends **dense semantic embeddings** (`SentenceTransformers`) with **weighted sparse metadata vectors** across **70,000+ movies**, wrapped in an aesthetic nocturnal glassmorphism interface.

---

## 🌟 Key Features

- **🧠 Hybrid Vector Recommendation Engine**:
  Combines 384-dimensional sentence transformer embeddings ($50\%$) with weighted TF-IDF plot & metadata vectors ($50\%$) to recommend films based on visual atmosphere, narrative tone, and cinematic cadence.
- **🎠 Floating Trending Marquee**:
  Infinite scrolling 3:4 poster marquee featuring popular catalog films with glowing light borders and interactive hover scale animations.
- **🧭 Atmospheric Recommendations Grid**:
  Dedicated 10-movie grid page (`discover.html`) displaying similarity scores, TMDB poster artwork, ratings, and genre badges.
- **🎬 Deep Movie Details & Bento Bento**:
  Comprehensive film details page (`movie.html`) featuring high-res backdrop hero images, director & cast cards, AI mood analysis bento block, and direct **YouTube Official Trailer** integration.
- **🔒 Private Watchlist Vault**:
  Persistent browser-saved collection (`watchlist.html`) with animated card removals, count badges, and one-click vault clear capabilities.
- **📡 RESTful FastAPI Backend**:
  Asynchronous Python API server with CORS enabled and fast live-search autocomplete.

---

## 📁 Repository Structure

```
VANTA/
├── backend/                  # FastAPI REST server & recommendation engine
│   ├── app/main.py           # REST endpoints (/health, /movies/search, /movies/trending, /recommend, /movie/details)
│   ├── recommender.py        # Hybrid nearest-neighbor vector search & catalog index
│   └── __init__.py
├── frontend/                 # Web application interface
│   ├── index.html            # Hero landing page with floating trending marquee & nav
│   ├── discover.html         # 10-movie recommendation grid layout
│   ├── discover.js           # Recommendation fetch & card rendering logic
│   ├── movie.html            # Movie details, cast bento, AI mood, and trailer button
│   ├── movie.js              # Details API fetcher & YouTube trailer builder
│   ├── watchlist.html        # Private Watchlist Vault layout
│   ├── watchlist.js          # LocalStorage persistence & exit animations
│   ├── styles.css            # Dark mode glassmorphism design system & marquee keyframes
│   ├── app.js                # Landing page search form, autocomplete & trending loader
│   └── server.js             # Static file development HTTP server (Port 5173)
├── data/                     # Dataset storage pipeline
│   ├── raw/                  # Original IMDB dataset dumps
│   ├── interim/              # Filtered interim CSVs
│   └── processed/            # movies_enriched.csv & precomputed vector indices
├── notebooks/                # Jupyter Notebooks for dataset building & ML research
│   └── recommendation_system/
│       ├── dataset_builder.ipynb
│       └── hybrid_recommendation.ipynb
├── docs/                     # Technical documentation suite
│   ├── API.md                # REST API specification & schemas
│   └── ARCHITECTURE.md       # ML vector model & UI system architecture
├── assets/                   # Static project assets & badges
├── package.json              # Frontend package manifest & scripts
├── requirements.txt          # Python dependency specifications
├── .env.example              # Environment variables template
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+**

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/Arceaus/VANTA.git
cd VANTA

# Copy environment template
cp .env.example .env
```

### 3. Launch Backend API Server (Port 8000)
```bash
# Windows PowerShell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Launch Frontend Web Server (Port 5173)
```bash
npm start
# OR
node frontend/server.js
```

Open your browser at **[http://127.0.0.1:5173](http://127.0.0.1:5173)** to experience VANTA!

---

## 📡 API Overview

| Endpoint | Method | Description |
|---|---|---|
| `/health` | `GET` | Returns server health status |
| `/movies/search` | `GET` | Live autocomplete search across catalog titles |
| `/movies/trending` | `GET` | Deduplicated top trending catalog movies |
| `/movies/random` | `GET` | Sample library shortcuts |
| `/recommend` | `GET` | Hybrid vector nearest-neighbor recommendations |
| `/movie/details` | `GET` | Full movie details, cast, directors, & AI mood |

See **[docs/API.md](docs/API.md)** for full request/response JSON schemas.

---

## 👤 Author & Socials

Created by **Sarthak Maurya**

- 🐱 **GitHub**: [github.com/Arceaus](https://github.com/Arceaus)
- 💼 **LinkedIn**: [linkedin.com/in/sarthak-maurya-59b82a366](https://www.linkedin.com/in/sarthak-maurya-59b82a366)

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
