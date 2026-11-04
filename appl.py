import streamlit as st
import docx
import spacy
import re
import pandas as pd
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP
from hdbscan import HDBSCAN

st.set_page_config(
    page_title="Textometrics & Semantic Concept Mapping",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 1. Linguistic Preprocessing with spaCy
# -------------------------------------------------------------
@st.cache_resource
def load_spacy_model():
    return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

# Expanded filler words common in spoken qualitative interviews
CUSTOM_STOP_WORDS = [
    "yeah", "um", "uh", "you know", "like", "okay", "right", 
    "think", "said", "say", "folks", "guy", "guys"
]

def clean_speech_artifacts(text: str) -> str:
    """Removes stray quotation marks, excessive whitespace, and speech fillers."""
    text = re.sub(r'["“”\'’]', '', text)
    for filler in CUSTOM_STOP_WORDS:
        text = re.sub(rf'\b{filler}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_content_from_docx(file):
    """
    Parses any Word document format:
    - Filters out section headings and interviewer questions.
    - Extracts both body paragraphs and embedded tables.
    - Segments long responses into discrete sentences.
    """
    doc = docx.Document(file)
    extracted_assertions = []

    raw_blocks = []
    
    # 1. Extract paragraphs
    for para in doc.paragraphs:
        txt = para.text.strip()
        if not txt:
            continue
            
        # Skip section markers and standard question lines
        if re.match(r'^(section\s*\d+|interview response|q[:\d]|question[:\d])', txt, re.IGNORECASE):
            continue
        if txt.endswith("?"):
            continue
            
        # Detect bolded text acting as questions
        runs_bold = [run.bold for run in para.runs if run.text.strip()]
        if runs_bold and all(runs_bold):
            continue
            
        raw_blocks.append(txt)

    # 2. Extract table cells
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                cell_txt = cell.text.strip()
                if cell_txt and not cell_txt.endswith("?"):
                    raw_blocks.append(cell_txt)

    # 3. Sentence parsing & semantic cleaning
    for block in raw_blocks:
        spacy_doc = nlp(block)
        for sent in spacy_doc.sents:
            cleaned = clean_speech_artifacts(sent.text)
            # Minimum word threshold: retain meaningful assertions
            if len(cleaned.split()) >= 4:
                extracted_assertions.append(cleaned)

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for item in extracted_assertions:
        if item.lower() not in seen:
            seen.add(item.lower())
            deduped.append(item)

    return deduped

# -------------------------------------------------------------
# 2. UI Layout & Controls
# -------------------------------------------------------------
st.title("Qualitative Semantic Analysis & Concept Mapping")
st.caption("BERTopic + spaCy Academic Engine for Diverse Interview Transcripts")

with st.sidebar:
    st.header("⚙️ Model Parameters")
    min_topic_size = st.slider(
        "Min Cluster Size",
        min_value=2,
        max_value=15,
        value=2,
        help="Use 2 for single interviews/smaller quote sets. Increase for full multi-interview corpora."
    )
    n_gram_range = st.selectbox(
        "N-Gram Range",
        options=[(1, 1), (1, 2), (1, 3)],
        format_func=lambda x: f"{x[0]}-{x[1]} words (captures phrases like 'mental burnout' or 'business model')",
        index=1
    )

uploaded_file = st.file_uploader("Upload Feedback Document (.docx)", type=["docx"])

if uploaded_file is not None:
    with st.spinner("Parsing document and segmenting assertions via spaCy..."):
        sentences = extract_content_from_docx(uploaded_file)

    st.success(f"Parsed and extracted **{len(sentences)}** distinct analytical statements.")

    with st.expander("Preview Extracted Statements for Verification", expanded=False):
        for i, s in enumerate(sentences, 1):
            st.write(f"**{i}.** {s}")

    if st.button("Run Semantic Topic Extraction", type="primary"):
        with st.spinner("Computing contextual embeddings, UMAP projection, and c-TF-IDF..."):
            
            # Calibrate UMAP and HDBSCAN parameters dynamically to dataset size
            n_samples = len(sentences)
            n_neighbors = min(15, max(2, n_samples - 1))
            
            umap_model = UMAP(
                n_neighbors=n_neighbors, 
                n_components=5, 
                min_dist=0.0, 
                metric='cosine', 
                random_state=42
            )
            hdbscan_model = HDBSCAN(
                min_cluster_size=min_topic_size, 
                metric='euclidean', 
                prediction_data=True
            )
            
            vectorizer_model = CountVectorizer(
                stop_words="english",
                ngram_range=n_gram_range,
                min_df=1
            )

            topic_model = BERTopic(
                umap_model=umap_model,
                hdbscan_model=hdbscan_model,
                vectorizer_model=vectorizer_model,
                min_topic_size=min_topic_size,
                verbose=False
            )

            topics, probs = topic_model.fit_transform(sentences)
            
            st.session_state["topic_model"] = topic_model
            st.session_state["sentences"] = sentences
            st.session_state["topics"] = topics

# -------------------------------------------------------------
# 3. Interactive Visualizations & Metrics
# -------------------------------------------------------------
if "topic_model" in st.session_state:
    topic_model = st.session_state["topic_model"]
    sentences = st.session_state["sentences"]
    topics = st.session_state["topics"]
    topic_info = topic_model.get_topic_info()

    st.divider()
    st.subheader("Discovered Themes & Clusters")
    st.dataframe(topic_info, use_container_width=True)

    tab1, tab2, tab3 = st.tabs([
        "c-TF-IDF Keyword Scores", 
        "2D Semantic Distance Map", 
        "Hierarchical Clustering Dendrogram"
    ])

    with tab1:
        st.markdown("**Core Lexical Weights:** Shows the defining terms and n-grams per theme.")
        try:
            fig_barchart = topic_model.visualize_barchart(top_n_topics=6, n_words=6)
            st.plotly_chart(fig_barchart, use_container_width=True)
        except Exception as e:
            st.info("Additional data points are needed to render the bar chart view.")

    with tab2:
        st.markdown("**Intertopic Distance Map:** Shows geometric separation between clusters.")
        try:
            fig_topics = topic_model.visualize_topics()
            st.plotly_chart(fig_topics, use_container_width=True)
        except Exception as e:
            st.info("At least 3 distinct non-outlier clusters are needed to project the 2D plane.")

    with tab3:
        st.markdown("**Hierarchical Similarity Heatmap:** Dendrogram displaying conceptual convergence.")
        try:
            fig_heatmap = topic_model.visualize_heatmap()
            st.plotly_chart(fig_heatmap, use_container_width=True)
        except Exception as e:
            st.info("At least 2 clusters are required to generate similarity trees.")

    # ---------------------------------------------------------
    # 4. Academic Exports
    # ---------------------------------------------------------
    st.subheader("📥 Export Analyzed Data")
    
    detailed_df = pd.DataFrame({
        "Assertion_Text": sentences,
        "Cluster_ID": topics,
        "Assigned_Topic_Label": [topic_model.get_topic_info(t)["Name"].values[0] if t != -1 else "Outlier / Unclustered" for t in topics]
    })

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download Classified Sentences (CSV)",
            data=detailed_df.to_csv(index=False).encode('utf-8'),
            file_name="classified_assertions.csv",
            mime="text/csv",
        )
    with col2:
        st.download_button(
            label="Download Topic Summary (CSV)",
            data=topic_info.to_csv(index=False).encode('utf-8'),
            file_name="thematic_summary.csv",
            mime="text/csv",
        )