import os
import pandas as pd

from semantic_search import (
    semantic_search
)

from collaborative_scoring import (
    collaborative_scores,
    normalize_scores
)


# ==========================================
# LOAD MOVIES
# ==========================================

MOVIE_MASTER_PATH = os.getenv("MOVIE_MASTER_PATH")

candidates = []

if MOVIE_MASTER_PATH:
    candidates.append(MOVIE_MASTER_PATH)

# prefer data/ folder
candidates.append(os.path.join("data", "movie_master.csv"))
# fallback to project root
candidates.append("movie_master.csv")

for path in candidates:
    try:
        movie_master = pd.read_csv(path)
        break
    except FileNotFoundError:
        movie_master = None

if movie_master is None:
    raise FileNotFoundError(
        "movie_master.csv not found. Expected at MOVIE_MASTER_PATH or data/movie_master.csv"
    )

movie_lookup = (
    movie_master
    .set_index("tmdb_id")
)

# ==========================================
# HYBRID SEARCH
# ==========================================

def hybrid_search(
    query,
    top_k_semantic=50,
    top_n=10,
    semantic_weight=0.7,
    collaborative_weight=0.3
):

    # ----------------------------------
    # Semantic Retrieval
    # ----------------------------------

    semantic_results = semantic_search(
        query=query,
        top_k=top_k_semantic
    )

    matches = semantic_results.matches

    candidate_movie_ids = [
        int(match.id)
        for match in matches
    ]

    # ----------------------------------
    # Collaborative Scores
    # ----------------------------------

    collab_scores = (
        collaborative_scores(
            candidate_movie_ids
        )
    )

    collab_scores = (
        normalize_scores(
            collab_scores
        )
    )

    # ----------------------------------
    # Semantic Scores
    # ----------------------------------

    semantic_scores = {}

    for match in matches:

        semantic_scores[
            int(match.id)
        ] = float(
            match.score
        )

    semantic_scores = (
        normalize_scores(
            semantic_scores
        )
    )

    # ----------------------------------
    # Final Ranking
    # ----------------------------------

    results = []

    for match in matches:

        movie_id = int(
            match.id
        )

        semantic_score = (
            semantic_scores.get(
                movie_id,
                0
            )
        )

        collab_score = (
            collab_scores.get(
                movie_id,
                0
            )
        )

        final_score = (
            semantic_weight
            * semantic_score
            +
            collaborative_weight
            * collab_score
        )

        metadata = (
            match.metadata
        )

        results.append({

            "tmdb_id":
            movie_id,

            "title":
            metadata.get(
                "title",
                "Unknown"
            ),

            "semantic_score":
            round(
                semantic_score,
                4
            ),

            "collaborative_score":
            round(
                collab_score,
                4
            ),

            "final_score":
            round(
                final_score,
                4
            ),

            "vote_average":
            metadata.get(
                "vote_average",
                0
            ),

            "director":
            metadata.get(
                "director",
                ""
            ),

            "document":
            metadata.get(
                "document",
                ""
            )
        })

    # ----------------------------------
    # Sort
    # ----------------------------------

    results = sorted(
        results,
        key=lambda x: x[
            "final_score"
        ],
        reverse=True
    )

    return results[:top_n]


# ==========================================
# PRETTY PRINT
# ==========================================

def print_results(
    results
):

    print("\n")
    print("=" * 120)

    for idx, movie in enumerate(
        results,
        start=1
    ):

        print(
            f"{idx:02d}. "
            f"{movie['title']}"
        )

        print(
            f"    Semantic Score      : "
            f"{movie['semantic_score']}"
        )

        print(
            f"    Collaborative Score : "
            f"{movie['collaborative_score']}"
        )

        print(
            f"    Final Score         : "
            f"{movie['final_score']}"
        )

        print()

    print("=" * 120)


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    print("hybrid_retrieval module - use hybrid_search(query) from your application.")
    print("To run an end-to-end demo, ensure embeddings/pinecone and neighbor graph are prepared, then run the Streamlit app: streamlit run app.py")