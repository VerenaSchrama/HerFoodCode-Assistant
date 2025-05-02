import streamlit as st
from utils import reset_session, load_llm_chain, add_to_chat_history
from ui import (
    render_personalization_sidebar,
    render_cycle_questions,
    render_personalization_summary,
)

# Initialize session state
reset_session()

st.title("Your Cycle Nutrition Assistant")
st.write("Ask your hormonal, PCOS & food questions to science.")
st.write("Let's personalize your experience first before you ask questions.")

# Personalization flow
has_cycle = render_cycle_questions()
render_personalization_sidebar()

# If user personalization is complete
if st.session_state.personalization_completed:
    render_personalization_summary()

    user_question = st.chat_input("Ask something like: 'What should I eat in my luteal phase?'")

    # Check if a suggested question was triggered
    if st.session_state.get("question_triggered") and st.session_state.get("user_question"):
        user_question = st.session_state.user_question
        st.session_state.question_triggered = False  # Reset trigger

    if user_question:
        st.write(f"\U0001F9E0 Thinking based on your cycle phase ({st.session_state.phase}) and dietary needs...")

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
    st.subheader("\U0001F4DD Chat History")

    if st.session_state.chat_history:
        for speaker, message in st.session_state.chat_history:
            with st.chat_message(speaker):
                st.markdown(message)
    else:
        st.info("No chat history yet. Start by asking a question!")
else:
    st.info("\u2728 Please complete the personalization steps above before asking questions.")
