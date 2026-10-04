# JobScam Guard

Live demo: https://jobscam-guard-wsvlpzukzeknxhhhwpyk6b.streamlit.app/ 

An AI tool that helps students check job posts and recruiter messages for scam signs.
Built for ForgeHacks 2026, AI + Cybersecurity track.

## Problem
Students and job seekers are targeted by fake job offers: fake checks, upfront fees, requests for personal data, and pressure to move to private chat apps. Most people have no quick way to check a message before they respond.

## Target users
Students and early-career job seekers.

## What it does
1. Recognize: a text classifier trained on about 17,880 job postings gives a scam probability.
2. Verify: rule checks look for red flags such as payment requests, fake-check schemes, free email addresses, a sender domain that does not match the company, and moves to private chat apps.
3. Explain: plain-language reasons for the risk level. An optional LLM can rewrite the explanation.
4. Respond: next steps, reporting links, and a safe reply the user can send.

## Technical approach
- Model: TF-IDF (1-2 word n-grams) + Logistic Regression with class weighting for the imbalanced data (about 4.8% fake).
- Rules: regex-based checks in checks.py, each with a weight and a plain reason.
- Final risk: a blend of model probability and rule score. Strong rule evidence alone can set HIGH.
- App: Streamlit. The model trains on first start from the dataset in the repo.

## Results (held-out test set, 20%)
Fake class: precision 0.84, recall 0.91, F1 0.87.
Confusion matrix: 157 fake caught, 16 missed, 31 real flagged as fake, 3372 real correct.
Accuracy alone is misleading here because most postings are real.

## Limitations (honest)
- The dataset is older and has a specific style. The model may do worse on short modern recruiter texts.
- Some learned terms reflect dataset quirks, not scam behavior, and may unfairly flag legitimate roles such as data entry.
- Rules can be avoided by a careful scammer.
- The tool gives a risk signal, not proof. Users should always verify the employer on the official website.

## Real-world impact
Gives students a fast first check, plus clear next steps and a safe reply, which lowers the chance of losing money or personal data.

## Files
- app.py: Streamlit app
- checks.py: rule-based verification
- requirements.txt: dependencies
- fake_job_postings zip: public dataset (Kaggle, Real / Fake Job Posting Prediction)

## Run locally
    pip install -r requirements.txt
    streamlit run app.py
