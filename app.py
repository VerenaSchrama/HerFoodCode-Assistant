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

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Simple demo authentication (replace with real auth for production) ---
from streamlit_authenticator import Authenticate
names = ["Demo User"]
usernames = ["demo"]
passwords = ["demo"]
authenticator = Authenticate(names, usernames, passwords, "cookie_name", "signature_key", cookie_expiry_days=30)
name, auth_status, username = authenticator.login("Login", "main")

if auth_status:
    st.success(f"Welcome {name}! 👋")
    user_id = username

    reset_session()

    # Load or initialize profile
    user_data = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
    if not user_data.data:
        supabase.table("profiles").insert({"user_id": user_id, "phase": "", "goal": "", "diet": []}).execute()
        st.info("New profile created. Please personalize your settings.")
    else:
        profile = user_data.data[0]
        st.session_state.phase = profile.get("phase", "")
        st.session_state.support_goal = profile.get("goal", "")
        st.session_state.dietary_preferences = profile.get("diet", [])

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
        }).eq("user_id", user_id).execute()
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
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "question": user_question,
                "response": response
            }).execute()

            add_to_chat_history("user", user_question)
            add_to_chat_history("assistant", response)

        st.markdown("---")
        st.subheader("🕓 Chat History")

        history = supabase.table("chat_history").select("*").eq("user_id", user_id).order("timestamp", desc=True).limit(5).execute()
        for msg in reversed(history.data):
            st.chat_message("user").markdown(msg["question"])
            st.chat_message("assistant").markdown(msg["response"])

    else:
        st.info("✨ Please complete the personalization steps above before asking questions.")

elif auth_status is False:
    st.error("Incorrect username or password")
elif auth_status is None:
    st.warning("Please enter your credentials")
