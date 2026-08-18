# VANTA REST API Specification

The VANTA Backend API is built using **FastAPI** and served via **Uvicorn**.

Base URL: `http://127.0.0.1:8000`

---

## 📡 Endpoints Overview

### 1. Health Check
`GET /health`

Returns service health status.

**Response:**
```json
{
  "status": "ok"
}
```

---

### 2. Live Autocomplete Search
`GET /movies/search`

Provides fast prefix and substring search across the 70,000+ movie catalog.

**Parameters:**
- `query` (string, required): Title query string.
- `limit` (int, default=6): Maximum matches to return.

**Response:**
```json
{
  "matches": [
    "Inception",
    "Interstellar",
    "Inception: The Cobol Job"
  ]
}
```

---

### 3. Trending Movies
`GET /movies/trending`

Returns top popular catalog movies deduplicated by poster artwork and title.

**Parameters:**
- `limit` (int, default=10, min=1, max=20): Number of trending films.

**Response:**
```json
{
  "movies": [
    {
      "title": "Spider-Man: Brand New Day",
      "year": 2026,
      "genres": ["ACTION", "ADVENTURE", "SCI-FI"],
      "overview": "Fighting crime full-time as Spider-Man...",
      "poster_url": "https://image.tmdb.org/t/p/w500/iPOn6DinuVyLY17YM9mKuPofV08.jpg",
      "rating": 7.9
    }
  ]
}
```

---

### 4. Random Library Shortcuts
`GET /movies/random`

Returns distinct random movie titles from the catalog for quick-click shortcuts.

**Parameters:**
- `limit` (int, default=3, min=1, max=12): Number of titles.

**Response:**
```json
{
  "movies": [
    "Arrival",
    "The Matrix",
    "Whiplash"
  ]
}
```

---

### 5. Hybrid Movie Recommendations
`GET /recommend`

Generates 10 nearest-neighbor atmospheric recommendations for a target film based on 50% Dense Transformer Embeddings + 50% Sparse Metadata TF-IDF vectors.

**Parameters:**
- `movie` (string, required): Exact target movie title.
- `limit` (int, default=10, min=1, max=20): Number of recommendations.

**Response:**
```json
{
  "target_movie": "Inception",
  "recommendations": [
    {
      "title": "Interstellar",
      "year": 2014,
      "genres": ["ADVENTURE", "DRAMA", "SCI-FI"],
      "overview": "The adventures of a group of explorers...",
      "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
      "backdrop_url": "https://image.tmdb.org/t/p/w1280/xJHokMbljvjADYdit5fK5VQsSY.jpg",
      "rating": 8.7
    }
  ]
}
```

---

### 6. Full Movie Details
`GET /movie/details`

Retrieves full metadata for a target film including cast, directors, backdrop URL, genres, runtime, and AI mood analysis.

**Parameters:**
- `title` (string, required): Movie title.

**Response:**
```json
{
  "found": true,
  "title": "Inception",
  "original_title": "Inception",
  "year": 2010,
  "runtime": 148,
  "genres": ["ACTION", "ADVENTURE", "SCI-FI"],
  "overview": "Cobb, a skilled thief who steals valuable secrets...",
  "poster_url": "https://image.tmdb.org/t/p/w500/oYuLE1h2CVCdIFvDStmyTeLx9y1.jpg",
  "backdrop_url": "https://image.tmdb.org/t/p/w1280/8ZTVqvKDQ8StS2MsS92GTVsuB3.jpg",
  "rating": 8.4,
  "directors": ["Christopher Nolan"],
  "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"]
}
```
