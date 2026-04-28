import streamlit as st
import wikipediaapi
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from gtts import gTTS

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wikipedia Bot",
    page_icon="📖",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }

    .main-header p {
        color: #6b7280;
        font-size: 1.1rem;
        margin-top: 0;
    }

    .summary-box {
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        border: 1px solid #e0e7ff;
        border-left: 4px solid #667eea;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin: 1.5rem 0;
        line-height: 1.8;
        color: #1f2937;
        font-size: 1rem;
    }

    .topic-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .action-header {
        text-align: center;
        font-size: 1.1rem;
        font-weight: 600;
        color: #374151;
        margin: 2rem 0 1rem 0;
    }

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
    }

    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e7ff;
        padding: 0.6rem 1rem;
        font-size: 1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    }

    .stSelectbox > div > div {
        border-radius: 10px;
    }

    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #f3f4f6;
    }

    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def fetch_wikipedia_summary(topic: str, lang: str = "en", sentences: int = 5) -> dict:
    """Fetch Wikipedia summary for a topic."""
    wiki = wikipediaapi.Wikipedia(
        language=lang,
        user_agent="WikipediaBot/1.0 (streamlit-app)"
    )
    page = wiki.page(topic)

    if not page.exists():
        return {"found": False, "topic": topic}

    # Get first N sentences from summary
    full_summary = page.summary
    sentences_list = full_summary.replace("! ", ". ").replace("? ", ". ").split(". ")
    short_summary = ". ".join(sentences_list[:sentences]).strip()
    if not short_summary.endswith("."):
        short_summary += "."

    return {
        "found": True,
        "topic": page.title,
        "summary": short_summary,
        "full_summary": full_summary,
        "url": page.fullurl,
    }


def generate_pdf(topic: str, summary: str) -> bytes:
    """Generate a styled PDF from the summary."""
    from io import BytesIO
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#667eea"),
        spaceAfter=8,
        fontName="Helvetica-Bold",
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#9ca3af"),
        spaceAfter=20,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=12,
        leading=20,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=12,
    )

    source_style = ParagraphStyle(
        "Source",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#6b7280"),
        spaceAfter=4,
    )

    story = [
        Paragraph(topic, title_style),
        Paragraph("Wikipedia Summary", subtitle_style),
        Spacer(1, 0.1 * inch),
        Paragraph(summary, body_style),
        Spacer(1, 0.3 * inch),
        Paragraph("─" * 80, source_style),
        Paragraph("Source: Wikipedia — The Free Encyclopedia", source_style),
    ]

    doc.build(story)
    return buffer.getvalue()


def generate_voice(text: str, lang: str = "en") -> bytes:
    """Generate TTS audio using gTTS."""
    from io import BytesIO
    tts = gTTS(text=text, lang=lang, slow=False)
    buffer = BytesIO()
    tts.write_to_fp(buffer)
    return buffer.getvalue()


# ── Language maps ─────────────────────────────────────────────────────────────
LANG_OPTIONS = {
    "English": ("en", "en"),
    "Hindi": ("hi", "hi"),
    "Marathi": ("mr", "mr"),
    "French": ("fr", "fr"),
    "Spanish": ("es", "es"),
    "German": ("de", "de"),
    "Japanese": ("ja", "ja"),
}

SENTENCES_OPTIONS = {
    "Short (3 sentences)": 3,
    "Medium (5 sentences)": 5,
    "Long (8 sentences)": 8,
    "Full Summary": 999,
}


# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>📖 Wikipedia Bot</h1>
    <p>Search any topic · Get a summary · Export as PDF or Voice</p>
</div>
""", unsafe_allow_html=True)

# Search controls
col1, col2 = st.columns([2, 1])
with col1:
    topic = st.text_input(
        "🔍 Enter a topic",
        placeholder="e.g. Artificial Intelligence, India, Black Hole...",
        label_visibility="collapsed",
    )
with col2:
    lang_label = st.selectbox(
        "Language",
        options=list(LANG_OPTIONS.keys()),
        label_visibility="collapsed",
    )

col3, col4 = st.columns([2, 1])
with col3:
    summary_length = st.selectbox(
        "Summary Length",
        options=list(SENTENCES_OPTIONS.keys()),
        index=1,
        label_visibility="collapsed",
    )
with col4:
    search_btn = st.button("🔎 Search", use_container_width=True, type="primary")

# ── Session State ─────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None

if search_btn and topic.strip():
    wiki_lang, _ = LANG_OPTIONS[lang_label]
    n_sentences = SENTENCES_OPTIONS[summary_length]

    with st.spinner(f"Searching Wikipedia for **{topic}**..."):
        result = fetch_wikipedia_summary(topic.strip(), lang=wiki_lang, sentences=n_sentences)
        st.session_state.result = result

# ── Display Result ────────────────────────────────────────────────────────────
result = st.session_state.result

if result:
    if not result["found"]:
        st.error(f"❌ No Wikipedia article found for **\"{result['topic']}\"**. Try a different spelling or topic.")
    else:
        # Summary display
        st.markdown(f'<div class="topic-badge">📌 {result["topic"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-box">{result["summary"]}</div>', unsafe_allow_html=True)
        st.markdown(f"🔗 [Read full article on Wikipedia]({result['url']})", unsafe_allow_html=False)

        # Export options
        st.markdown('<div class="action-header">⬇️ Export Options</div>', unsafe_allow_html=True)

        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            with st.spinner("Preparing PDF..."):
                pdf_bytes = generate_pdf(result["topic"], result["summary"])
            st.download_button(
                label="📄 Download as PDF",
                data=pdf_bytes,
                file_name=f"{result['topic'].replace(' ', '_')}_summary.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        with exp_col2:
            _, tts_lang = LANG_OPTIONS[lang_label]
            with st.spinner("Generating voice..."):
                try:
                    audio_bytes = generate_voice(result["summary"], lang=tts_lang)
                    st.download_button(
                        label="🔊 Download as Audio",
                        data=audio_bytes,
                        file_name=f"{result['topic'].replace(' ', '_')}_voice.mp3",
                        mime="audio/mpeg",
                        use_container_width=True,
                    )
                    # Also play inline
                    st.audio(audio_bytes, format="audio/mp3")
                except Exception as e:
                    st.warning(f"Voice generation failed: {e}")

elif search_btn and not topic.strip():
    st.warning("⚠️ Please enter a topic to search.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Made with ❤️ using Streamlit + Wikipedia API · Powered by gTTS &amp; ReportLab
</div>
""", unsafe_allow_html=True)