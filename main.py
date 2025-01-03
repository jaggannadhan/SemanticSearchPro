import streamlit as st
from services.streamlit_service import *
from services.FAQ_list import FAQ_list
from services.semantic_search_service import SemanticSearchEngine
import time, math
from services.weighted_keywords import weighted_keywords

@st.cache_resource()
def init_search_engine():
    return SemanticSearchEngine()

def main():
    st.set_page_config(
        page_title="SemanticSearchPro",
        page_icon="./images/favico.png",
        layout="wide"
    )

    sidebar()
    st.subheader("SemanticSearchPro" , divider="red")
    query = st.text_input("Ask me anything", placeholder="Type your query")

    col1, col2 = st.columns(2)
    with col1:
        diplay_questions = FAQ_list
        search_engine = init_search_engine()

        if query:
            with st.spinner("Searching..."):
                start = time.time()
                match = search_engine.find_match(query)
                end = time.time()

                if match:
                    score = 1 if match[1] > 1 else match[1]
                    score *= 100

                    diplay_questions = [{
                        "Match": match[0],
                        "Score": f"{round(score, 4)}%",
                        "Time": f"{round(end-start, 4)} seconds"
                    }]
                else:
                    diplay_questions = ["Query not found"]
    
        else:
            diplay_questions = FAQ_list

        with st.container(height=500, border=True):
            for question in diplay_questions:
                st.write(question)
    
    with col2:
        selected_keywords = {}

        with st.container(height=500, border=True):
            st.write("Weighted Keywords")
            for keyword, idx in weighted_keywords.items():
                st.checkbox(keyword, value=True, disabled=True)
    

# st.cache_resource.clear()

if __name__ == "__main__":
    main()