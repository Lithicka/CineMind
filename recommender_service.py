from hybrid_retrieval import hybrid_search
from llm_explainer import explain_recommendations


def recommend_movies(query: str):

    recommendations = hybrid_search(
        query=query,
        top_n=5
    )

    explanation = explain_recommendations(
        user_query=query,
        recommendations=recommendations
    )

    return {
        "recommendations": recommendations,
        "explanation": explanation
    }