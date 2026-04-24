import streamlit as st
import wikipedia
from speech import generate_pdf
from voice import generate_voice

st.set_page_config(page_title="Wikipedia Search Bot", page_icon="📖", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background-color: #f5f5f5;
}

h1 {
    text-align: center;
    color: #1a1a1a;
    font-size: 2rem !important;
    font-weight: 700;
    margin-bottom: 0.2rem;
}

.tagline {
    text-align: center;
    color: #666;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}

.stTextInput > div > div > input {
    background: #ffffff !important;
    border: 1.5px solid #d0d0d0 !important;
    border-radius: 8px !important;
    color: #1a1a1a !important;
    font-size: 1rem !important;
    padding: 10px 16px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #4a90e2 !important;
    box-shadow: 0 0 0 3px rgba(74,144,226,0.15) !important;
}

.stTextInput > div > div > input::placeholder {
    color: #999 !important;
}

.summary-box {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1.5rem 2rem;
    color: #1a1a1a;
    font-size: 1rem;
    line-height: 1.8;
    margin-top: 1rem;
}

.summary-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.8rem;
    border-bottom: 2px solid #4a90e2;
    padding-bottom: 0.5rem;
}

.error-box {
    background: #fff3f3;
    border: 1px solid #ffcccc;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    color: #cc0000;
    margin-top: 1rem;
}

div[data-testid="stDownloadButton"] > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
    padding: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1>📖 WIKIPEDIA SEARCH BOT</h1>", unsafe_allow_html=True)
st.markdown('<p class="tagline">Search any topic and get a quick summary</p>', unsafe_allow_html=True)
st.divider()

def get_summary(keyword):
    try:
        summary = wikipedia.summary(keyword, sentences=22)
        return keyword.title(), summary
    except wikipedia.exceptions.DisambiguationError as e:
        for option in e.options:
            try:
                summary = wikipedia.summary(option, sentences=22)
                return option, summary
            except (wikipedia.exceptions.DisambiguationError,
                    wikipedia.exceptions.PageError):
                continue
        return None, None
    except wikipedia.exceptions.PageError:
        return None, None

# Search Input
keyword = st.text_input("", placeholder="Enter a keyword... e.g. India, Einstein, Python")

if keyword:
    with st.spinner("Searching..."):
        title, summary = get_summary(keyword)

        if title and summary:
            # Summary card
            st.markdown(f"""
            <div class="summary-box">
                <div class="summary-title">📌 {title}</div>
                {summary}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # PDF and MP3 buttons side by side
            col1, col2 = st.columns(2)

            with col1:
                # Generate PDF
                pdf_file = generate_pdf(title, summary, "output.pdf")
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📄 Download PDF",
                        data=f,
                        file_name=f"{title}.pdf",
                        mime="application/pdf"
                    )

            with col2:
                # Generate MP3
                mp3_file = generate_voice(summary, "output.mp3")
                with open(mp3_file, "rb") as f:
                    st.download_button(
                        label="🎧 Download MP3",
                        data=f,
                        file_name=f"{title}.mp3",
                        mime="audio/mpeg"
                    )

        else:
            st.markdown("""
            <div class="error-box">
                ❌ No page found. Please try a different keyword.
            </div>
            """, unsafe_allow_html=True)