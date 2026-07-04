# CineMind: AI-Powered Hybrid Movie Recommendation System

This repository contains CineMind, an AI-powered hybrid movie recommendation system that combines semantic retrieval (embeddings + vector index) with collaborative scoring.

**Note:** the dataset's original README/license is included as `README.txt`. This `README.md` describes the project architecture, setup, and pipeline.

**Architecture**
- `create_embeddings.py`: builds document text and creates embeddings (Azure OpenAI) and uploads to Pinecone.
- `semantic_search.py`: performs vector-based semantic search against the Pinecone index.
- `collaborative_scoring.py`: loads a precomputed neighbor graph (`movie_neighbors.pkl`) and computes collaborative scores.
- `hybrid_retrieval.py`: combines semantic scores and collaborative scores into final ranking.
- `recommender_service.py` and `app.py`: glue logic and Streamlit UI.

Setup
1. Create and activate a Python virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with the following variables:

- `AZURE_OPENAI_API_KEY` — your Azure OpenAI key
- `AZURE_OPENAI_ENDPOINT` — your Azure endpoint
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` — embedding deployment name
- `PINECONE_API_KEY` — Pinecone API key
- `PINECONE_INDEX_NAME` — Pinecone index name (optional)

Do not commit `.env` — it is listed in `.gitignore`.

Pipeline / Recommended order
1. Run `python clean_dataset.py` to build `data/movie_master.csv` and `data/ratings_master.csv` (use `--dataset-dir` if your raw files are elsewhere).
2. Run preprocessing to build neighbor graph (`movie_neighbors.pkl`) used by collaborative scoring.
3. Run `create_embeddings.py` to build and upload embeddings to Pinecone.
4. Start the UI: `streamlit run app.py`.

Safety notes
- This project uses `pickle` for `movie_neighbors.pkl`. Loading pickles from untrusted sources is a security risk (remote code execution). Regenerate pickles locally from the raw data when possible.

Troubleshooting
- If the app fails with `movie_master.csv not found`, run `python clean_dataset.py` to generate the CSVs into `data/`.
- If Pinecone or Azure errors occur, ensure relevant env vars are set and you can reach the services.

Contact
Feel free to open an issue or ask for help if you want this packaged into a Docker image or CI workflow.
