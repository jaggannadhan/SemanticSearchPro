import traceback
import streamlit as st
import pandas as pd
from services.email_service import send_email


def sidebar():
    with st.sidebar:
        
        st.header("SemanticSearchPro - Search like no other!" , divider="red")

        st.text("""ⓘ A robust semantic search engine designed to intelligently match user queries with relevant FAQ entries using state-of-the-art natural language processing techniques. 
                """)
        
        if st.button("🤔 How to use?"):
            how_to()
        
        if st.button("""🤩 We encourage your feedback!"""):
            feedback()
        else:
            show_feedback_response()

        st.divider()

        st.text("""  😎 Author: Jaggannadhan Venugopal""")
        st.page_link("https://www.linkedin.com/in/jvenu94/", label="Follow me on: Linkedin")
        st.page_link("https://www.github.com/jaggannadhan", label="Work with me on: GitHub")
        st.page_link("https://www.buymeacoffee.com/jaggannadhan", label="(or) Just Buy Me Protein 💪🏼")
        


@st.dialog("Give us your Feedback!")
def feedback():
    st.write("Liked iSage? What can we improve on? Let us know!")
    your_email = st.text_input("Your Email")
    subject = st.text_input("Subject")
    message = st.text_area("Message")
    if st.button("Submit"):
        success, reason = send_email(your_email, subject, message)            
        if not ("cannot be empty" in reason):
            st.session_state.feedback = {"success": success, "reason": reason}    
            st.rerun()
        
        
def show_feedback_response():
    try:
        if "feedback" in st.session_state: 
            email_resp = st.session_state.feedback
            resp_status = email_resp.get("success")
            if resp_status:
                st.balloons()
                st.toast("Feedback submitted!", icon="✅")
            else:
                st.toast("Unable to submit feedback, pls try later!", icon="❌")
            st.session_state.pop("feedback")
    except Exception:
        print(traceback.format_exc())


@st.dialog("🤔 How to use?")
def how_to():
    st.write("""1) SemanticSearchPro is engineered to identify a single question that matches the user query from a FAQ DB.""")
    st.write("""2) Kindly use the feedback feature to submit your queries/concerns to me. I will take up most raised bugs during my weekends to work on.""")
    st.write("""3) I use a hashmap-based caching setup to address repeated questions. So feel free to ask the same questions again if your session is lost or if you need to refresh your memory. But for new questions please try to keep it to less than 5 questions per session.""")
    st.write("""4) Please refrain from using profanity. We understand that student life can be frustrating, foul language will not make it better.""")
    

def search_FAQ():
    pass