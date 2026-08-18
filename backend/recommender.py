"""Reusable loader and API-ready interface for VANTA's hybrid recommender.

The ranking logic in this module is intentionally kept in lockstep with
``notebooks/recommendation_system/hybrid_recommendation.ipynb``.  It only
loads the already-generated artifacts; it never trains or rebuilds them.
"""

from pathlib import Path
from typing import Any

import gzip
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.neighbors import NearestNeighbors


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def _load_semantic_embeddings() -> np.ndarray:
    p_parts = [PROCESSED_DATA_DIR / f"semantic_embeddings_p{i}.npy.gz" for i in range(1, 5)]
    full_p = PROCESSED_DATA_DIR / "semantic_embeddings.npy"
    
    if all(p.exists() for p in p_parts):
        arrays = [np.load(gzip.open(p, "rb")) for p in p_parts]
        return np.vstack(arrays).astype(np.float32)
    elif full_p.exists():
        return np.load(full_p)
    else:
        raise FileNotFoundError("Semantic embeddings matrices missing.")


# Load the persisted artifacts and fit the query indexes once per process.
movies_df = pd.read_csv(PROCESSED_DATA_DIR / "movies_enriched.csv", low_memory=False)
semantic_embeddings = _load_semantic_embeddings()
weighted_tfidf_matrix = sp.load_npz(
    PROCESSED_DATA_DIR / "weighted_tfidf_matrix.npz"
)

semantic_index = NearestNeighbors(metric="cosine", algorithm="brute")
semantic_index.fit(semantic_embeddings)

tfidf_index = NearestNeighbors(metric="cosine", algorithm="brute")
tfidf_index.fit(weighted_tfidf_matrix)


def get_semantic_candidates(movie_index: int, n: int = 20) -> tuple[np.ndarray, np.ndarray]:
    """Return semantic-nearest candidates, excluding the queried movie."""
    distances, indices = semantic_index.kneighbors(
        semantic_embeddings[movie_index].reshape(1, -1),
        n_neighbors=n + 1,
    )
    return indices[0][1:], distances[0][1:]


def get_tfidf_candidates(movie_index: int, n: int = 20) -> tuple[np.ndarray, np.ndarray]:
    """Return weighted-TF-IDF-nearest candidates, excluding the queried movie."""
    distances, indices = tfidf_index.kneighbors(
        weighted_tfidf_matrix[movie_index],
        n_neighbors=n + 1,
    )
    return indices[0][1:], distances[0][1:]


def recommend_movies(movie_title: str, n: int = 10) -> dict[str, Any]:
    """Return the notebook's hybrid recommendations in an API-ready shape.

    Unknown titles return an empty recommendation list instead of raising an
    exception.  The candidate count and hybrid formula intentionally match the
    existing ``hybrid_recommend`` notebook function exactly.
    """
    if not isinstance(movie_title, str) or not movie_title.strip():
        return {
            "movie_title": movie_title,
            "found": False,
            "recommendations": [],
            "message": "A non-empty movie title is required.",
        }

    matches = movies_df[
        movies_df["primaryTitle"].str.lower() == movie_title.lower()
    ]

    if matches.empty:
        return {
            "movie_title": movie_title,
            "found": False,
            "recommendations": [],
            "message": f"Movie '{movie_title}' not found.",
        }

    movie_index = matches.index[0]

    # These calls deliberately use 20, as in hybrid_recommend in the notebook.
    semantic_indices, semantic_distances = get_semantic_candidates(movie_index, n=20)
    tfidf_indices, tfidf_distances = get_tfidf_candidates(movie_index, n=20)

    semantic_scores = {
        idx: 1 - distance
        for idx, distance in zip(semantic_indices, semantic_distances)
    }
    tfidf_scores = {
        idx: 1 - distance
        for idx, distance in zip(tfidf_indices, tfidf_distances)
    }
    candidate_indices = list(set(semantic_indices) | set(tfidf_indices))

    hybrid_scores = {}
    for idx in candidate_indices:
        semantic_score = semantic_scores.get(idx, 0)
        tfidf_score = tfidf_scores.get(idx, 0)
        hybrid_scores[idx] = 0.5 * semantic_score + 0.5 * tfidf_score

    ranked_indices = sorted(hybrid_scores, key=hybrid_scores.get, reverse=True)
    cols = ["primaryTitle", "startYear", "genres", "overview", "poster_path", "backdrop_path", "vote_average", "averageRating"]
    # Filter available columns safely
    available_cols = [c for c in cols if c in movies_df.columns]
    selected_df = movies_df.loc[ranked_indices[:n], available_cols]
    
    recs_list = []
    for _, row in selected_df.iterrows():
        poster_p = str(row.get("poster_path", "")) if pd.notna(row.get("poster_path")) else ""
        if poster_p.startswith("/"):
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_p}"
        elif poster_p.startswith("http"):
            poster_url = poster_p
        else:
            poster_url = None

        backdrop_p = str(row.get("backdrop_path", "")) if pd.notna(row.get("backdrop_path")) else ""
        if backdrop_p.startswith("/"):
            backdrop_url = f"https://image.tmdb.org/t/p/w780{backdrop_p}"
        elif backdrop_p.startswith("http"):
            backdrop_url = backdrop_p
        else:
            backdrop_url = None

        raw_genres = str(row.get("genres", "")) if pd.notna(row.get("genres")) else ""
        genres_list = [g.strip().upper() for g in raw_genres.split(",") if g.strip()] if raw_genres else []

        rating_val = None
        if "vote_average" in row and pd.notna(row["vote_average"]) and float(row["vote_average"]) > 0:
            rating_val = round(float(row["vote_average"]), 1)
        elif "averageRating" in row and pd.notna(row["averageRating"]) and float(row["averageRating"]) > 0:
            rating_val = round(float(row["averageRating"]), 1)

        year_val = None
        if pd.notna(row.get("startYear")):
            try:
                year_val = int(row["startYear"])
            except (ValueError, TypeError):
                year_val = str(row["startYear"])

        recs_list.append({
            "title": str(row.get("primaryTitle", "")),
            "year": year_val,
            "genres": genres_list,
            "overview": str(row.get("overview", "")) if pd.notna(row.get("overview")) else "",
            "poster_url": poster_url,
            "backdrop_url": backdrop_url,
            "rating": rating_val,
        })

    return {
        "movie_title": matches.iloc[0]["primaryTitle"],
        "found": True,
        "recommendations": recs_list,
    }


def get_movie_details(movie_title: str) -> dict[str, Any]:
    """Return comprehensive single movie details from movies_df."""
    if not isinstance(movie_title, str) or not movie_title.strip():
        return {
            "found": False,
            "message": "A non-empty movie title is required.",
        }

    matches = movies_df[
        movies_df["primaryTitle"].str.lower() == movie_title.lower()
    ]

    if matches.empty:
        matches = movies_df[
            movies_df["primaryTitle"].str.contains(movie_title, case=False, regex=False)
        ]

    if matches.empty:
        return {
            "found": False,
            "message": f"Movie '{movie_title}' not found.",
        }

    row = matches.iloc[0]

    poster_p = str(row.get("poster_path", "")) if pd.notna(row.get("poster_path")) else ""
    if poster_p.startswith("/"):
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_p}"
    elif poster_p.startswith("http"):
        poster_url = poster_p
    else:
        poster_url = None

    backdrop_p = str(row.get("backdrop_path", "")) if pd.notna(row.get("backdrop_path")) else ""
    if backdrop_p.startswith("/"):
        backdrop_url = f"https://image.tmdb.org/t/p/w1280{backdrop_p}"
    elif backdrop_p.startswith("http"):
        backdrop_url = backdrop_p
    else:
        backdrop_url = None

    raw_genres = str(row.get("genres", "")) if pd.notna(row.get("genres")) else ""
    genres_list = [g.strip().upper() for g in raw_genres.split(",") if g.strip()] if raw_genres else []

    rating_val = None
    if "vote_average" in row and pd.notna(row["vote_average"]) and float(row["vote_average"]) > 0:
        rating_val = round(float(row["vote_average"]), 1)
    elif "averageRating" in row and pd.notna(row["averageRating"]) and float(row["averageRating"]) > 0:
        rating_val = round(float(row["averageRating"]), 1)

    year_val = None
    if pd.notna(row.get("startYear")):
        try:
            year_val = int(row["startYear"])
        except (ValueError, TypeError):
            year_val = str(row["startYear"])

    runtime_val = None
    if pd.notna(row.get("runtimeMinutes")):
        try:
            total_mins = int(row["runtimeMinutes"])
            hrs = total_mins // 60
            mins = total_mins % 60
            runtime_val = f"{hrs}h {mins}m" if hrs > 0 else f"{mins}m"
        except (ValueError, TypeError):
            runtime_val = str(row["runtimeMinutes"])

    directors = str(row.get("directors", "")) if pd.notna(row.get("directors")) else "Unknown"
    cast = str(row.get("castName", "")) if pd.notna(row.get("castName")) else ""
    cast_list = [c.strip() for c in cast.split(",") if c.strip()] if cast else []

    return {
        "found": True,
        "title": str(row.get("primaryTitle", "")),
        "original_title": str(row.get("originalTitle", "")) if pd.notna(row.get("originalTitle")) else "",
        "year": year_val,
        "runtime": runtime_val,
        "genres": genres_list,
        "overview": str(row.get("overview", "")) if pd.notna(row.get("overview")) else "",
        "poster_url": poster_url,
        "backdrop_url": backdrop_url,
        "rating": rating_val,
        "directors": directors,
        "cast": cast_list[:6],
    }


def get_trending_movies(limit: int = 10) -> dict[str, Any]:
    """Return top trending catalog movies sorted by popularity."""
    if "popularity" in movies_df.columns:
        sorted_df = movies_df.sort_values(by="popularity", ascending=False)
    elif "numVotes" in movies_df.columns:
        sorted_df = movies_df.sort_values(by="numVotes", ascending=False)
    else:
        sorted_df = movies_df

    valid_movies = sorted_df[sorted_df["poster_path"].notna() & (sorted_df["poster_path"] != "")]
    
    seen_posters = set()
    seen_titles = set()
    unique_rows = []
    
    for _, row in valid_movies.iterrows():
        poster_p = str(row.get("poster_path", "")).strip()
        title_p = str(row.get("primaryTitle", "")).strip().lower()
        if not poster_p or poster_p in seen_posters or title_p in seen_titles:
            continue
        seen_posters.add(poster_p)
        seen_titles.add(title_p)
        unique_rows.append(row)
        if len(unique_rows) >= limit:
            break

    trending_list = []
    for row in unique_rows:
        poster_p = str(row.get("poster_path", "")) if pd.notna(row.get("poster_path")) else ""
        if poster_p.startswith("/"):
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_p}"
        elif poster_p.startswith("http"):
            poster_url = poster_p
        else:
            poster_url = None

        raw_genres = str(row.get("genres", "")) if pd.notna(row.get("genres")) else ""
        genres_list = [g.strip().upper() for g in raw_genres.split(",") if g.strip()] if raw_genres else []

        rating_val = None
        if "vote_average" in row and pd.notna(row["vote_average"]) and float(row["vote_average"]) > 0:
            rating_val = round(float(row["vote_average"]), 1)
        elif "averageRating" in row and pd.notna(row["averageRating"]) and float(row["averageRating"]) > 0:
            rating_val = round(float(row["averageRating"]), 1)

        year_val = None
        if pd.notna(row.get("startYear")):
            try:
                year_val = int(row["startYear"])
            except (ValueError, TypeError):
                year_val = str(row["startYear"])

        trending_list.append({
            "title": str(row.get("primaryTitle", "")),
            "year": year_val,
            "genres": genres_list,
            "overview": str(row.get("overview", "")) if pd.notna(row.get("overview")) else "",
            "poster_url": poster_url,
            "rating": rating_val,
        })

    return {"movies": trending_list}



