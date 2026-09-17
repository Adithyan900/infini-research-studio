from html import escape

import streamlit as st
from google.genai import errors

from planner import add_research_plan, generate_research_plan


st.set_page_config(page_title="Infini | Research Studio", page_icon="✦", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(ellipse at top right,
            rgba(69, 136, 117, 0.14), transparent 50%), #0B111A;
    }
    .block-container { max-width: 900px; padding-top: 3rem; padding-bottom: 3rem; }
    .brand { color: #9FE8CD; font-size: 13px; letter-spacing: 0.23em;
        font-weight: 600; margin-bottom: 26px; }
    .hero { font-size: clamp(36px, 6vw, 58px); font-weight: 650;
        line-height: 1.12; letter-spacing: -0.045em; color: #EDF2F7; margin-bottom: 18px; }
    .intro { color: #A9B6C6; font-size: 17px; line-height: 1.7;
        max-width: 580px; margin-bottom: 30px; }
    .question-card { background: linear-gradient(130deg, #182635, #121C28);
        border: 1px solid #2A3B4B; border-radius: 18px; padding: 23px; margin: 12px 0; }
    .question-number { color: #9FE8CD; font-size: 12px;
        letter-spacing: 0.12em; margin-bottom: 10px; }
    .question-text { color: #EDF2F7; font-size: 17px;
        line-height: 1.65; overflow-wrap: anywhere; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="brand">✦ INFINI / RESEARCH STUDIO</div>', unsafe_allow_html=True)
st.markdown('<div class="hero">Big questions.<br>Clear next steps.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="intro">Turn your curiosity into a focused research plan. '
    'Start with a question. Find three directions worth exploring.</div>',
    unsafe_allow_html=True,
)

if "plans" not in st.session_state:
    st.session_state.plans = []

with st.expander("Need a starting point?"):
    st.write("How can machine learning predict high CPU usage?")
    st.write("How can RAG improve answers from company documents?")
    st.write("What makes an AI research assistant reliable?")

st.caption("Planning workspace · Questions generated with Gemini")
st.caption("Use public topics only: your question is sent to Google. Document search is not connected yet.")

if st.session_state.plans:
    if st.button("Clear conversation"):
        st.session_state.plans = []
        st.rerun()


def display_plan(plan, index):
    with st.chat_message("user"):
        st.write(plan["question"])
    with st.chat_message("assistant"):
        st.markdown("**Your research plan**")
        for number, question in enumerate(plan["subquestions"], start=1):
            st.markdown(
                f'<div class="question-card">'
                f'<div class="question-number">DIRECTION {number:02d}</div>'
                f'<div class="question-text">{escape(question)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.caption("Review these questions before gathering evidence.")
        download_text = (
            plan["question"] + "\n\n"
            + "\n".join(
                f"{n}. {question}"
                for n, question in enumerate(plan["subquestions"], start=1)
            )
        )
        st.download_button(
            "Download plan ↓", data=download_text,
            file_name="infini-research-plan.txt", mime="text/plain",
            key=f"download_{index}",
        )


for index, plan in enumerate(st.session_state.plans):
    display_plan(plan, index)

topic = st.chat_input("What would you like to research?", max_chars=2000)

if topic and topic.strip():
    topic = topic.strip()
    try:
        with st.spinner("Turning your question into a research plan..."):
            subquestions = generate_research_plan(topic)
            research = {
                "question": topic, "status": "created", "subquestions": [],
                "findings": [], "report": None,
            }
            research = add_research_plan(research, subquestions)
    except errors.APIError as error:
        if error.code == 503:
            st.error("Gemini is busy. Please submit your question again later.")
        elif error.code == 429:
            st.error("The API usage limit was reached. Check your quota.")
        else:
            st.error(f"Gemini could not complete this request ({error.code}).")
    except ValueError:
        st.error("Could not create a valid plan. Check your setup or try again.")
    except Exception:
        st.error("The request could not finish. Check your connection and retry.")
    else:
        st.session_state.plans.append(research)
        st.rerun()
