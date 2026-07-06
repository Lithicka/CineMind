import os
import argparse
import pandas as pd
import ast


def clean_numeric_id(df, col):
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=[col])
    df[col] = df[col].astype(int)
    return df


def parse_json_column(value):
    if pd.isna(value):
        return []

    try:
        return ast.literal_eval(value)
    except Exception:
        return []


def extract_keywords(x):
    items = parse_json_column(x)
    return [
        item["name"]
        for item in items
        if isinstance(item, dict) and "name" in item
    ]


def extract_genres(x):
    items = parse_json_column(x)
    return [
        item["name"]
        for item in items
        if isinstance(item, dict) and "name" in item
    ]


def extract_director(crew_text):
    crew = parse_json_column(crew_text)
    for person in crew:
        if isinstance(person, dict) and person.get("job") == "Director":
            return person.get("name")
    return None


def extract_cast(cast_text, top_n=5):
    cast = parse_json_column(cast_text)
    return [
        person["name"]
        for person in cast[:top_n]
        if isinstance(person, dict) and "name" in person
    ]


def build_master(dataset_dir: str, out_dir: str):
    # Build cross-platform paths
    movies_path = os.path.join(dataset_dir, "movies_metadata.csv")
    keywords_path = os.path.join(dataset_dir, "keywords.csv")
    credits_path = os.path.join(dataset_dir, "credits.csv")
    ratings_path = os.path.join(dataset_dir, "ratings.csv")
    links_path = os.path.join(dataset_dir, "links.csv")

    movies = pd.read_csv(movies_path, low_memory=False)
    keywords = pd.read_csv(keywords_path)
    credits = pd.read_csv(credits_path)

    ratings = pd.read_csv(ratings_path)
    links = pd.read_csv(links_path)

    movies = clean_numeric_id(movies, "id")
    keywords = clean_numeric_id(keywords, "id")
    credits = clean_numeric_id(credits, "id")

    links["tmdbId"] = pd.to_numeric(links["tmdbId"], errors="coerce")
    links = links.dropna(subset=["tmdbId"])  # drop rows without tmdbId
    links["tmdbId"] = links["tmdbId"].astype(int)

    keywords["keyword_list"] = keywords["keywords"].apply(extract_keywords)
    movies["genre_list"] = movies["genres"].apply(extract_genres)

    credits["director"] = credits["crew"].apply(extract_director)
    credits["cast_list"] = credits["cast"].apply(extract_cast)

    movie_master = (
        movies
        .merge(keywords[["id", "keyword_list"]], on="id", how="left")
        .merge(credits[["id", "director", "cast_list"]], on="id", how="left")
    )

    movie_master = movie_master.rename(columns={"id": "tmdb_id"})

    cols = [
        "tmdb_id",
        "title",
        "overview",
        "genre_list",
        "keyword_list",
        "director",
        "cast_list",
        "release_date",
        "vote_average",
        "vote_count",
        "popularity",
        "runtime",
        "original_language",
    ]

    movie_master = movie_master[cols]

    ratings_master = ratings.merge(
        links[["movieId", "tmdbId"]], on="movieId", how="inner"
    )

    ratings_master = ratings_master.rename(columns={"tmdbId": "tmdb_id"})
    ratings_master = ratings_master.drop(columns=["movieId"])
    ratings_master = ratings_master[["userId", "tmdb_id", "rating", "timestamp"]]

    os.makedirs(out_dir, exist_ok=True)

    movie_master_path = os.path.join(out_dir, "movie_master.csv")
    ratings_master_path = os.path.join(out_dir, "ratings_master.csv")

    movie_master.to_csv(movie_master_path, index=False)
    ratings_master.to_csv(ratings_master_path, index=False)

    print(f"Wrote: {movie_master_path}")
    print(f"Wrote: {ratings_master_path}")


def main():
    parser = argparse.ArgumentParser(description="Clean raw dataset and build master CSVs")
    parser.add_argument(
        "--dataset-dir",
        default=os.path.join("data", "movie_dataset"),
        help="Directory containing the raw dataset CSVs"
    )
    parser.add_argument(
        "--out-dir",
        default="data",
        help="Output directory for generated master CSVs"
    )

    args = parser.parse_args()
    build_master(args.dataset_dir, args.out_dir)


if __name__ == "__main__":
    main()

