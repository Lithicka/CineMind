import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import pickle

# ---------------------------------
# Load ratings master
# ---------------------------------

ratings = pd.read_csv("ratings_master.csv")

print("Ratings shape:", ratings.shape)

# ---------------------------------
# Optional filtering
# Remove very unpopular movies
# ---------------------------------

movie_rating_counts = (
    ratings.groupby("tmdb_id")
    .size()
    .reset_index(name="rating_count")
)

ratings = ratings.merge(
    movie_rating_counts,
    on="tmdb_id"
)

MIN_RATINGS = 20

ratings = ratings[
    ratings["rating_count"] >= MIN_RATINGS
].copy()

print(
    f"Movies with >= {MIN_RATINGS} ratings:",
    ratings["tmdb_id"].nunique()
)

# ---------------------------------
# Create User-Movie Matrix
# ---------------------------------

user_movie_matrix = ratings.pivot_table(
    index="userId",
    columns="tmdb_id",
    values="rating",
    fill_value=0
)

print(
    "User-Movie Matrix Shape:",
    user_movie_matrix.shape
)

# ---------------------------------
# Convert to Sparse Matrix
# ---------------------------------

sparse_matrix = csr_matrix(
    user_movie_matrix.values
)

# ---------------------------------
# Fit KNN
# ---------------------------------

knn_model = NearestNeighbors(
    metric="cosine",
    algorithm="brute",
    n_neighbors=21
)

knn_model.fit(
    sparse_matrix.T
)

# ---------------------------------
# Build Mapping
# ---------------------------------

movie_ids = list(
    user_movie_matrix.columns
)

movie_neighbors = {}

# ---------------------------------
# Find Similar Movies
# ---------------------------------

for idx, movie_id in enumerate(movie_ids):

    movie_vector = sparse_matrix.T[idx]

    distances, indices = knn_model.kneighbors(
        movie_vector,
        n_neighbors=21
    )

    neighbors = []

    for distance, neighbor_idx in zip(
        distances.flatten()[1:],
        indices.flatten()[1:]
    ):

        neighbor_movie_id = movie_ids[
            neighbor_idx
        ]

        similarity = 1 - distance

        neighbors.append(
            (
                int(neighbor_movie_id),
                round(float(similarity), 4)
            )
        )

    movie_neighbors[
        int(movie_id)
    ] = neighbors

    if idx % 1000 == 0:
        print(
            f"Processed {idx:,}/{len(movie_ids):,}"
        )

# ---------------------------------
# Save
# ---------------------------------

with open(
    "movie_neighbors.pkl",
    "wb"
) as f:

    pickle.dump(
        movie_neighbors,
        f
    )

print(
    f"Saved neighbors for "
    f"{len(movie_neighbors):,} movies"
)