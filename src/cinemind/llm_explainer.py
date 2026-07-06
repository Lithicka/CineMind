import os
from pathlib import Path

from openai import AzureOpenAI

from src.cinemind.hybrid_retrieval import hybrid_search


# =====================================================
# LOAD ENV
# =====================================================

def load_dotenv(dotenv_path=".env"):

    path = Path(dotenv_path)

    if not path.exists():
        return

    with open(path, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if (
                not line
                or line.startswith("#")
                or "=" not in line
            ):
                continue

            key, value = line.split("=", 1)

            if key not in os.environ:

                os.environ[key] = (
                    value
                    .strip()
                    .strip('"')
                    .strip("'")
                )


load_dotenv()


# =====================================================
# CONFIG
# =====================================================

client = AzureOpenAI(

    api_key=os.getenv(
        "AZURE_OPENAI_API_KEY"
    ),

    azure_endpoint=os.getenv(
        "AZURE_OPENAI_ENDPOINT"
    ),

    api_version=os.getenv(
        "AZURE_OPENAI_API_VERSION"
    )
)

CHAT_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"
)


# =====================================================
# BUILD CONTEXT
# =====================================================

def build_context(recommendations):

    context = ""

    for i, movie in enumerate(
        recommendations,
        start=1
    ):

        context += f"""
Movie {i}

Title:
{movie['title']}

Director:
{movie['director']}

Rating:
{movie['vote_average']}

Movie Description:
{movie['document']}

----------------------------------
"""

    return context


# =====================================================
# GENERATE RESPONSE
# =====================================================

def explain_recommendations(
    user_query,
    recommendations
):

    context = build_context(
        recommendations
    )

    system_prompt = """
You are an expert movie recommendation assistant.

You MUST ONLY use the retrieved movies provided.

Never recommend movies that are not in the retrieved context.

Explain naturally why each recommendation matches the user's request.

Rank recommendations based on how well they match.

Mention trade-offs where appropriate.

Be conversational.

Do not invent facts.

If the context is insufficient, say so.
"""

    user_prompt = f"""
User Query:

{user_query}


Retrieved Movies:

{context}


Instructions:

Recommend the best movies for the user.

For each movie explain:

- Why it matches
- What type of viewer would enjoy it
- Mention any limitations

Finish with a short overall recommendation.
"""

    response = client.chat.completions.create(

        model=CHAT_DEPLOYMENT,

        temperature=0.4,

        messages=[

            {
                "role": "system",
                "content": system_prompt
            },

            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return (
        response
        .choices[0]
        .message
        .content
    )


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    query = input("Enter your movie query: ")

    recommendations = hybrid_search(
        query=query,
        top_n=5
    )

    answer = explain_recommendations(
        user_query=query,
        recommendations=recommendations
    )

    print("\n")
    print("=" * 80)
    print(answer)