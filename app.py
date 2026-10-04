# app.py 
import os
import joblib
import streamlit as st
from checks import run_checks

st.set_page_config(page_title="JobScam Guard", page_icon="")


@st.cache_resource(show_spinner="Training the model on first start (about a minute)...")
def load_model():
    import zipfile
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline

    if os.path.exists("scam_model.joblib"):
        return joblib.load("scam_model.joblib")

    if os.path.exists("fake_job_postings.zip"):
        with zipfile.ZipFile("fake_job_postings.zip") as z:
            names = [n for n in z.namelist()
                     if n.endswith("fake_job_postings.csv") and "__MACOSX" not in n]
            with z.open(names[0]) as f:
                df = pd.read_csv(f)
    else:
        df = pd.read_csv("fake_job_postings.csv")

    cols = ["title", "company_profile", "description", "requirements", "benefits"]
    df["text"] = df[cols].fillna("").agg(" ".join, axis=1)
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=50000, ngram_range=(1, 2),
                                  stop_words="english", sublinear_tf=True)),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000)),
    ])
    pipe.fit(df["text"], df["fraudulent"])
    return pipe


def get_setting(name):
    val = os.getenv(name)
    if val:
        return val
    try:
        return st.secrets[name]
    except Exception:
        return None


def fallback_explanation(result):
    if not result["flags"]:
        return "No rule-based red flags were found, but always verify the company yourself."
    items = "; ".join(f["name"].lower() for f in result["flags"])
    return f"Red flags found: {items}. Verify the employer through their official website before replying."


def llm_explain(text, prob, result):
    key = get_setting("LLM_API_KEY")
    base_url = get_setting("LLM_BASE_URL")
    model = get_setting("LLM_MODEL")
    if not (key and base_url and model):
        return fallback_explanation(result)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key, base_url=base_url)
        flags = "\n".join(f"- {f['name']} (evidence: {f['evidence']})" for f in result["flags"]) or "- none"
        prompt = (
            "You help students spot fake job offers. Write 3-4 plain sentences explaining "
            "the risk. Use ONLY the evidence below. Do not claim certainty.
