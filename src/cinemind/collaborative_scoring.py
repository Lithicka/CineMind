import pickle
import os
import warnings


# ==========================================
# LOAD NEIGHBOR GRAPH
# =========================================

# Load the neighbors pickle if present. If it's missing, continue with
# an empty neighbor graph and surface a friendly warning. Note: untrusted
# pickle files can execute arbitrary code — do not run this on files
# from unknown sources. Prefer regenerating `movie_neighbors.pkl` from
# the provided data processing pipeline.

movie_neighbors = {}
neighbors_path = os.getenv("MOVIE_NEIGHBORS_PATH", "movie_neighbors.pkl")

if os.path.exists(neighbors_path):
    try:
        with open(neighbors_path, "rb") as f:
            movie_neighbors = pickle.load(f)
    except Exception as e:
        warnings.warn(
            f"Failed to load movie neighbors from {neighbors_path}: {e}. Continuing with empty neighbor graph."
        )
        movie_neighbors = {}
else:
    warnings.warn(
        f"Neighbor graph not found at {neighbors_path}. Run the preprocessing pipeline to generate movie_neighbors.pkl."
    )


# ==========================================
# SINGLE MOVIE SCORE
# ==========================================

def collaborative_score(
    candidate_movie_id,
    reference_movie_ids
):
    """
    Computes how strongly a candidate movie
    is connected to a list of reference movies.

    Parameters
    ----------
    candidate_movie_id : int

    reference_movie_ids : list[int]

    Returns
    -------
    float
    """

    neighbors = movie_neighbors.get(
        int(candidate_movie_id),
        []
    )

    if not neighbors:
        return 0.0

    neighbor_dict = {
        movie_id: similarity
        for movie_id, similarity in neighbors
    }

    score = 0.0

    for movie_id in reference_movie_ids:

        score += neighbor_dict.get(
            int(movie_id),
            0.0
        )

    return score


# ==========================================
# BATCH SCORING
# ==========================================

def collaborative_scores(
    candidate_movie_ids
):
    """
    Compute collaborative scores
    for all candidate movies.

    Parameters
    ----------
    candidate_movie_ids : list[int]

    Returns
    -------
    dict
    """

    scores = {}

    candidate_set = set(
        candidate_movie_ids
    )

    for movie_id in candidate_movie_ids:

        reference_movies = list(
            candidate_set - {movie_id}
        )

        scores[movie_id] = collaborative_score(
            movie_id,
            reference_movies
        )

    return scores


# ==========================================
# NORMALIZATION
# ==========================================

def normalize_scores(
    score_dict
):
    """
    Min-max normalization
    """

    if not score_dict:
        return {}

    values = list(
        score_dict.values()
    )

    min_score = min(values)
    max_score = max(values)

    if max_score == min_score:

        return {
            k: 1.0
            for k in score_dict
        }

    normalized = {}

    for movie_id, score in score_dict.items():

        normalized[movie_id] = (
            score - min_score
        ) / (
            max_score - min_score
        )

    return normalized