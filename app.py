import re
import html
import streamlit as st

from recommender_service import recommend_movies

st.set_page_config(
    page_title="CineMind",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background:
        radial-gradient(circle at 72% 10%, rgba(217,70,239,0.22), transparent 18%),
        radial-gradient(circle at 88% 22%, rgba(56,189,248,0.14), transparent 24%),
        radial-gradient(circle at 0% 0%, rgba(124,58,237,0.16), transparent 30%),
        #05060d;
    color: #f4f4f8;
}

header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

.block-container {
    max-width: 980px;
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}

.hero {
    position: relative;
    padding: 1.2rem 0 1.2rem 0;
}

.orb {
    position: absolute;
    right: 0rem;
    top: 0.6rem;
    width: 285px;
    height: 285px;
    border-radius: 50%;
    border: 1px solid rgba(217,70,239,0.36);
    background:
        radial-gradient(circle at 65% 30%, rgba(217,70,239,0.26), transparent 35%),
        radial-gradient(circle at 35% 75%, rgba(56,189,248,0.18), transparent 42%);
    box-shadow: 0 0 70px rgba(217,70,239,0.14);
    opacity: 0.75;
}

.orb::after {
    content: "";
    position: absolute;
    left: -70px;
    top: 115px;
    width: 430px;
    height: 105px;
    border: 1px solid rgba(56,189,248,0.16);
    border-radius: 50%;
    transform: rotate(-17deg);
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 610px;
}

.logo {
    font-size: 3.4rem;
    font-weight: 700;
    letter-spacing: -0.06em;
    line-height: 1;
    margin-bottom: 0.85rem;
    background: linear-gradient(95deg, #ffffff 8%, #f0abfc 38%, #8b5cf6 62%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.tagline {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.34em;
    color: #f472ff;
    text-transform: uppercase;
    margin-bottom: 1.7rem;
}

.hero-title {
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.25;
    color: #f3f0ff;
    margin-bottom: 0.85rem;
}

.accent { color: #f045df; }

.hero-copy {
    color: #b7b7c9;
    font-size: 0.98rem;
    line-height: 1.6;
    max-width: 500px;
}

div[data-testid="stHorizontalBlock"] { gap: 0.85rem !important; }

button[data-testid="baseButton-secondary"] {
    height: 62px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(217,70,239,0.40) !important;
    background: rgba(12, 13, 25, 0.96) !important;
    color: #f6f3ff !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    transition: all 0.18s ease;
}

button[data-testid="baseButton-secondary"] p {
    color: #f6f3ff !important;
    font-weight: 600 !important;
}

button[data-testid="baseButton-secondary"]:hover {
    border-color: rgba(217,70,239,0.95) !important;
    background: rgba(25, 16, 36, 0.98) !important;
    box-shadow: 0 0 24px rgba(217,70,239,0.18);
    transform: translateY(-1px);
}

div[data-testid="stTextInput"] label { display: none; }

div[data-testid="stTextInput"] input {
    height: 58px;
    background: rgba(14, 15, 24, 0.96);
    border: 1px solid rgba(208, 213, 224, 0.52);
    border-radius: 14px;
    color: #ffffff;
    padding: 0 1.25rem;
    font-size: 1rem;
}

div[data-testid="stTextInput"] input::placeholder { color: #77778d; }

div[data-testid="stTextInput"] input:focus {
    border-color: rgba(217,70,239,0.95);
    box-shadow: 0 0 0 1px rgba(217,70,239,0.6), 0 0 28px rgba(217,70,239,0.18);
}

button[data-testid="baseButton-primary"] {
    height: 58px !important;
    border-radius: 14px !important;
    border: none !important;
    background: linear-gradient(90deg, #e12bd8 0%, #8b5cf6 48%, #2f80ed 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    box-shadow: 0 0 32px rgba(139,92,246,0.28);
    margin-top: 0.45rem;
}

button[data-testid="baseButton-primary"] p {
    color: white !important;
    font-weight: 700 !important;
}

.section-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 2.2rem 0 1rem 0;
}

.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #f0abfc;
    letter-spacing: 0.22em;
    text-transform: uppercase;
}

.sort-note {
    font-size: 0.8rem;
    color: #85859a;
}

.movie-card {
    display: grid;
    grid-template-columns: 54px 1fr 124px;
    gap: 1.2rem;
    align-items: center;
    background: rgba(9, 10, 20, 0.86);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 18px;
    padding: 1.05rem 1.25rem;
    margin-bottom: 0.85rem;
    transition: all 0.18s ease;
}

.movie-card:hover {
    border-color: rgba(217,70,239,0.42);
    box-shadow: 0 0 36px rgba(217,70,239,0.12);
    transform: translateY(-2px);
}

.rank {
    font-size: 1.45rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(180deg, #f045df, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.movie-title {
    font-size: 1.22rem;
    font-weight: 700;
    color: #f6f3ff;
    margin-bottom: 0.25rem;
}

.movie-meta {
    color: #9b9bad;
    font-size: 0.84rem;
    margin-bottom: 0.78rem;
}

.score-line {
    display: grid;
    grid-template-columns: 124px 1fr 44px;
    gap: 0.6rem;
    align-items: center;
    margin: 0.3rem 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    color: #a2a2b6;
    text-transform: uppercase;
}

.bar {
    height: 5px;
    background: #1b1c28;
    border-radius: 999px;
    overflow: hidden;
}

.fill-semantic {
    height: 5px;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    border-radius: 999px;
}

.fill-collab {
    height: 5px;
    background: linear-gradient(90deg, #ec4899, #f045df);
    border-radius: 999px;
}

.hybrid-box { text-align: right; }

.hybrid-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #a2a2b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.hybrid-score {
    font-size: 1.85rem;
    font-weight: 700;
    line-height: 1;
    background: linear-gradient(180deg, #f045df, #2f80ed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 0.25rem;
}

.hybrid-score span {
    font-size: 0.75rem;
    -webkit-text-fill-color: #77778d;
}

.explain-block {
    background: rgba(9, 10, 20, 0.86);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 18px;
    padding: 1.35rem 1.5rem;
    color: #d6d6e4;
    line-height: 1.7;
    margin-top: 0.3rem;
    font-size: 0.96rem;
}

.explain-block h3 {
    color: #f0abfc;
    margin-top: 1.2rem;
    margin-bottom: 0.45rem;
    font-size: 1.05rem;
}

.explain-block strong {
    color: #ffffff;
}

.explain-block hr {
    border: none;
    border-top: 1px solid rgba(148,163,184,0.14);
    margin: 1.2rem 0;
}

.footer-note {
    text-align: center;
    color: #59596d;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    margin-top: 2rem;
}

@media (max-width: 900px) {
    .orb { display: none; }
    .movie-card { grid-template-columns: 42px 1fr; }
    .hybrid-box {
        grid-column: 2;
        text-align: left;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

if "query_text" not in st.session_state:
    st.session_state.query_text = ""

if "result" not in st.session_state:
    st.session_state.result = None

EXAMPLE_PROMPTS = [
    "💔 Heart-wrenching romance",
    "🌀 Mind-bending sci-fi thriller",
    "☕ Cozy feel-good comedy",
    "🎭 Twisty crime drama",
]


def set_example(prompt: str):
    st.session_state.query_text = (
        prompt.replace("💔 ", "")
        .replace("🌀 ", "")
        .replace("☕ ", "")
        .replace("🎭 ", "")
    )


def clamp_pct(value):
    value = value or 0
    return max(0, min(100, round(value * 100)))


def markdown_to_clean_html(text: str) -> str:
    text = text or ""

    text = re.sub(r"^#{1,6}\s+(.*)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)

    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = text.replace("---", "<hr>")

    paragraphs = []
    for block in text.split("\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("<h3>") or block == "<hr>":
            paragraphs.append(block)
        else:
            paragraphs.append(f"<p>{block}</p>")

    return "\n".join(paragraphs)


st.markdown(
    """
<div class="hero">
    <div class="orb"></div>
    <div class="hero-content">
        <div class="logo">CineMind</div>
        <div class="tagline">Hybrid AI · Retrieval Engine</div>
        <div class="hero-title">
            Tell it the mood.<br>
            We’ll find what <span class="accent">actually</span> fits.
        </div>
        <div class="hero-copy">
            CineMind blends semantic search with collaborative viewer signal
            to surface movies you’ll love.
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

cols = st.columns(4)
for col, prompt in zip(cols, EXAMPLE_PROMPTS):
    with col:
        st.button(
            prompt,
            key=f"chip_{prompt}",
            on_click=set_example,
            args=(prompt,),
            use_container_width=True,
        )

query = st.text_input(
    "Mood",
    key="query_text",
    placeholder="e.g. a slow-burn mystery with an unreliable narrator",
)

go = st.button("✨ Recommend", type="primary", use_container_width=True)

if go:
    if not query.strip():
        st.warning("Type something you're in the mood for first.")
    else:
        with st.spinner("Cross-referencing taste graphs..."):
            st.session_state.result = recommend_movies(query)

result = st.session_state.result

if result:
    recommendations = result.get("recommendations", [])

    if recommendations:
        st.markdown(
            """
<div class="section-head">
    <div class="section-label">✦ Top Matches</div>
    <div class="sort-note">Sorted by hybrid score</div>
</div>
""",
            unsafe_allow_html=True,
        )

        for i, movie in enumerate(recommendations, start=1):
            title = html.escape(str(movie.get("title", "Unknown")))
            director = html.escape(str(movie.get("director") or "Unknown"))
            vote_average = html.escape(str(movie.get("vote_average", "N/A")))

            semantic_pct = clamp_pct(movie.get("semantic_score", 0))
            collab_pct = clamp_pct(movie.get("collaborative_score", 0))
            hybrid_pct = round((semantic_pct * 0.6) + (collab_pct * 0.4))

            card_html = (
                f'<div class="movie-card">'
                f'<div class="rank">{i:02d}</div>'
                f'<div>'
                f'<div class="movie-title">{title}</div>'
                f'<div class="movie-meta">{director} · Rating {vote_average}</div>'
                f'<div class="score-line">'
                f'<div>Semantic</div>'
                f'<div class="bar"><div class="fill-semantic" style="width:{semantic_pct}%;"></div></div>'
                f'<div>{semantic_pct}%</div>'
                f'</div>'
                f'<div class="score-line">'
                f'<div>Viewer signal</div>'
                f'<div class="bar"><div class="fill-collab" style="width:{collab_pct}%;"></div></div>'
                f'<div>{collab_pct}%</div>'
                f'</div>'
                f'</div>'
                f'<div class="hybrid-box">'
                f'<div class="hybrid-label">Hybrid Score</div>'
                f'<div class="hybrid-score">{hybrid_pct}<span>/100</span></div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

        explanation = markdown_to_clean_html(str(result.get("explanation", "")))

        st.markdown(
            """
<div class="section-head">
    <div class="section-label">✦ Why These Picks?</div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
<div class="explain-block">
    {explanation}
</div>
""",
            unsafe_allow_html=True,
        )

    else:
        st.info("No matches came back for that one — try rephrasing or a different mood.")

st.markdown(
    """
<div class="footer-note">
    CINEMIND — SEMANTIC SEARCH + COLLABORATIVE FILTERING, EXPLAINED BY AN LLM
</div>
""",
    unsafe_allow_html=True,
)