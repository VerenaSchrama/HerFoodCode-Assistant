# app.py
import streamlit as st
from utils import reset_session, load_llm_chain, add_to_chat_history
from ui import render_personalization_sidebar, render_cycle_questions, render_personalization_summary

# Initialize session state
reset_session()

st.title("🌸 Your Cycle-Aware Nutrition Assistant")
st.write("Let's personalize your experience first before you ask questions.")

# Personalization flow
has_cycle = render_cycle_questions()
render_personalization_sidebar()

# If user personalization is complete
if st.session_state.personalization_completed:
    render_personalization_summary()

    user_question = st.chat_input("Ask something like: 'What should I eat in my luteal phase?'")
    if user_question:
        st.write(f"🧠 Thinking based on your cycle phase ({st.session_state.phase}) and dietary needs...")

        qa_chain = load_llm_chain()

        response = qa_chain.run({
            "phase": st.session_state.phase,
            "goal": st.session_state.support_goal,
            "diet": ", ".join(st.session_state.dietary_preferences),
            "question": user_question
        })

        add_to_chat_history("user", user_question)
        add_to_chat_history("assistant", response)

    st.markdown("---")
    st.subheader("📝 Chat History")

    if st.session_state.chat_history:
        for speaker, message in st.session_state.chat_history:
            if speaker == "user":
                with st.chat_message("user"):
                    st.markdown(message)
            elif speaker == "assistant":
                with st.chat_message("assistant"):
                    st.markdown(message)
    else:
        st.info("No chat history yet. Start by asking a question!")
else:
    st.info("✨ Please complete the personalization steps above before asking questions.")