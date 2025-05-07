import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import os
from dotenv import load_dotenv

from ui import (
    render_personalization_sidebar,
    render_cycle_questions,
    render_personalization_summary,
)
from utils import reset_session, load_llm_chain, add_to_chat_history
from supabase_auth import register_user, login_user

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Authentication ---
if not st.session_state.get("logged_in"):
    st.title("Your Cycle Nutrition Assistant")
    st.markdown("_Ask your hormonal, PCOS & food questions to science._")

    auth_mode = st.radio("Do you want to log in or register?", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if auth_mode == "Register":
        if st.button("Register"):
            success, msg = register_user(email, password)
            st.success(msg) if success else st.error(f"Registration error: {msg}")
    elif auth_mode == "Login":
        if st.button("Login"):
            success, user_data, msg = login_user(email, password)
            if success:
                st.session_state.user_id = user_data["id"]
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error(f"Login error: {msg}")

    st.stop()

# --- Load or initialize profile ---
user_data = supabase.table("profiles").select("*").eq("user_id", st.session_state.user_id).execute()

if not user_data.data:
    supabase.table("profiles").insert({"user_id": st.session_state.user_id, "phase": "", "goal": "", "diet": []}).execute()
    st.info("New profile created. Please personalize your settings.")
else:
    profile = user_data.data[0]
    st.session_state.phase = profile.get("phase", "")
    st.session_state.support_goal = profile.get("goal", "")
    st.session_state.dietary_preferences = profile.get("diet", [])

# --- App Content ---
st.title("Your Cycle Nutrition Assistant")
st.write("*Ask your hormonal, PCOS & food questions to science.*")

# --- Personalization ---
has_cycle = render_cycle_questions()
render_personalization_sidebar()

if st.sidebar.button("💾 Save Settings"):
    supabase.table("profiles").update({
        "phase": st.session_state.phase,
        "goal": st.session_state.support_goal,
        "diet": st.session_state.dietary_preferences
    }).eq("user_id", st.session_state.user_id).execute()
    st.sidebar.success("Preferences saved!")

# --- Chat interface ---
if st.session_state.personalization_completed:
    render_personalization_summary()

    user_question = st.chat_input("Ask something like: 'What should I eat in my luteal phase?'")
    if user_question:
        qa_chain = load_llm_chain()
        response = qa_chain.run({
            "phase": st.session_state.phase,
            "goal": st.session_state.support_goal,
            "diet": ", ".join(st.session_state.dietary_preferences),
            "question": user_question
        })

        supabase.table("chat_history").insert({
            "user_id": st.session_state.user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "question": user_question,
            "response": response
        }).execute()

        add_to_chat_history("user", user_question)
        add_to_chat_history("assistant", response)

    st.markdown("---")
    st.subheader("🕓 Chat History")

    history = supabase.table("chat_history").select("*").eq("user_id", st.session_state.user_id).order("timestamp", desc=True).limit(5).execute()
    for msg in reversed(history.data):
        st.chat_message("user").markdown(msg["question"])
        st.chat_message("assistant").markdown(msg["response"])
else:
    st.info("✨ Please complete the personalization steps above before asking questions.")

