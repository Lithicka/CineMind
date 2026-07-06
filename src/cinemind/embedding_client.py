import os
from pathlib import Path

from openai import AzureOpenAI
from pinecone import Pinecone


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


def get_embeddings_batch(texts):
    texts = [str(t).replace("\n", " ") for t in texts]
    model_to_use = AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
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
