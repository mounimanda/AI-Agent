"""Streamlit UI for the stateful agent workflow."""

from __future__ import annotations

import json

import streamlit as st

from agentic_ai.agent import AgricultureResearchAgent
from agentic_ai.config import settings


st.set_page_config(page_title="Agentic AI - Agriculture Papers", layout="wide")
st.title("Agentic AI: Agriculture Research Paper Finder")

user_id = st.text_input("User ID", value="demo-user")
goal = st.text_area(
    "Goal",
    value="Find the top 3 recent AI research papers on agriculture, summarize them, and store output.",
)

if st.button("Run Agent"):
    with st.spinner("Running autonomous workflow..."):
        agent = AgricultureResearchAgent(settings)
        report = agent.run(user_id=user_id, goal=goal)
    st.success("Completed")
    st.subheader("Structured Output")
    st.json(report)
    st.download_button(
        "Download JSON",
        data=json.dumps(report, indent=2),
        file_name=f"{report['job_id']}.json",
        mime="application/json",
    )
