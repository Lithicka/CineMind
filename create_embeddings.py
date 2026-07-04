import os
import ast
import math
from pathlib import Path
import pandas as pd

from openai import AzureOpenAI
from pinecone import Pinecone, ServerlessSpec


def load_dotenv(dotenv_path: str = ".env"):
    path = Path(dotenv_path)

    if not path.exists():
        return

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


# =====================================================
# CONFIG
# =====================================================

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION",
    "2024-02-01"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "text-embedding-3-large"
)
EMBEDDING_DIMENSION = int(
    os.getenv("EMBEDDING_DIMENSION", "1536")
)

AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME",
    "movie-semantic-search"
)

MOVIE_MASTER_PATH = os.getenv(
    "MOVIE_MASTER_PATH",
    os.path.join("data", "movie_master.csv")
)

# =====================================================
# CLIENTS
# =====================================================

if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
    raise RuntimeError(
        "Missing Azure OpenAI credentials: set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in your environment or .env"
    )

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
)

pc = Pinecone(
    api_key=PINECONE_API_KEY
)

# Convenience index object exported for other modules (semantic search, etc.)
index = pc.Index(PINECONE_INDEX_NAME)

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
# EMBEDDING
# =====================================================

def get_embeddings_batch(texts):

    texts = [
        str(t).replace("\n", " ")
        for t in texts
    ]

    model_to_use = (
        AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
    )

    # Quick validation: Azure deployment names that target chat models (e.g. gpt-*)
    # do not support embeddings. Detect likely chat deployments and raise
    # a clear error with remediation steps.
    if model_to_use:
        low = str(model_to_use).lower()
        if low.startswith("gpt-") or "gpt-" in low:
            raise RuntimeError(
                f"The selected deployment '{model_to_use}' appears to be a chat/model deployment which does not support embeddings. "
                "Set AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME in .env to an embedding-capable deployment (for example: text-embedding-3-small), "
            )

    response = client.embeddings.create(
        model=model_to_use,
        input=texts,
        dimensions=EMBEDDING_DIMENSION,
    )

    return [
        item.embedding
        for item in response.data
    ]

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