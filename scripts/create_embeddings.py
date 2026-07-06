import os
import ast
import math
import pandas as pd

from pinecone import ServerlessSpec

from src.cinemind.embedding_client import (
    client,
    pc,
    index,
    get_embeddings_batch,
    EMBEDDING_DIMENSION,
    PINECONE_INDEX_NAME,
)


# =====================================================
# CONFIG
# =====================================================

MOVIE_MASTER_PATH = os.getenv(
    "MOVIE_MASTER_PATH",
    os.path.join("data", "movie_master.csv")
)

# =====================================================
# CREATE INDEX
# =====================================================

def create_index():

    existing = [
        idx.name
        for idx in pc.list_indexes()
    ]

    if PINECONE_INDEX_NAME not in existing:

        print(
            f"Creating index: "
            f"{PINECONE_INDEX_NAME}"
        )

        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    else:

        print(
            f"Index already exists: "
            f"{PINECONE_INDEX_NAME}"
        )

# =====================================================
# HELPERS
# =====================================================

def safe_list(value):

    if pd.isna(value):
        return []

    try:
        return ast.literal_eval(value)
    except:
        return []

# =====================================================
# DOCUMENT CREATION
# =====================================================

def build_document(row):

    genres = ", ".join(
        safe_list(row["genre_list"])
    )

    keywords = ", ".join(
        safe_list(row["keyword_list"])
    )

    cast = ", ".join(
        safe_list(row["cast_list"])
    )

    return f"""
Title: {row['title']}

Genres: {genres}

Keywords: {keywords}

Director: {row['director']}

Cast: {cast}

Overview:
{row['overview']}
""".strip()

# =====================================================
# LOAD DATA
# =====================================================

def load_movies():

    df = pd.read_csv(
        MOVIE_MASTER_PATH
    )

    df["document"] = df.apply(
        build_document,
        axis=1
    )

    return df

# =====================================================
# PINECONE INGESTION
# =====================================================

def upload_movies():

    df = load_movies()

    print(
        f"Movies loaded: "
        f"{len(df):,}"
    )

    index = pc.Index(
        PINECONE_INDEX_NAME
    )

    BATCH_SIZE = 100

    total_batches = math.ceil(
        len(df) / BATCH_SIZE
    )

    for start in range(
        0,
        len(df),
        BATCH_SIZE
    ):

        end = start + BATCH_SIZE

        batch = df.iloc[start:end]

        docs = batch[
            "document"
        ].tolist()

        embeddings = get_embeddings_batch(
            docs
        )

        vectors = []

        for row, embedding in zip(
            batch.itertuples(),
            embeddings
        ):

            metadata = {

                "tmdb_id":
                int(row.tmdb_id),

                "title":
                str(row.title),

                "director":
                str(row.director),

                "language":
                str(
                    row.original_language
                ),

                "vote_average":
                float(
                    row.vote_average
                )
                if pd.notna(
                    row.vote_average
                )
                else 0.0,

                "popularity":
                float(
                    row.popularity
                )
                if pd.notna(
                    row.popularity
                )
                else 0.0,

                "document":
                row.document
            }

            vectors.append(
                (
                    str(row.tmdb_id),
                    embedding,
                    metadata
                )
            )

        index.upsert(
            vectors=vectors
        )

        batch_num = (
            start // BATCH_SIZE
        ) + 1

        print(
            f"Uploaded batch "
            f"{batch_num}/{total_batches}"
        )

    print(
        "\nIngestion complete!"
    )

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    create_index()

    upload_movies()