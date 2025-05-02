import streamlit as st
from datetime import datetime

def render_cycle_questions():
    has_cycle = st.radio("Do you have a (regular) menstrual cycle?", ("Yes", "No"))

    # Optional manual override
    phase_override = st.selectbox("Choose your current cycle phase manually ⬇️", ["", "Menstrual", "Follicular", "Ovulatory", "Luteal"], index=0)

    if has_cycle == "Yes":
        today = datetime.now().date()
        st.session_state.second_last_period = st.date_input("Second most recent period start date", value=today)
        st.session_state.last_period = st.date_input("Most recent period start date", value=today)

        if st.session_state.last_period and st.session_state.second_last_period:
            if st.session_state.second_last_period > st.session_state.last_period:
                st.session_state.second_last_period, st.session_state.last_period = st.session_state.last_period, st.session_state.second_last_period

            if st.session_state.last_period != today and st.session_state.second_last_period != today:
                cycle_length = (st.session_state.last_period - st.session_state.second_last_period).days
                if cycle_length <= 10:
                    st.error("Your periods seem too close together. Please check the entered dates.")
                else:
                    st.session_state.cycle_length = cycle_length
                    days_since_last = (today - st.session_state.last_period).days

                    if days_since_last <= 5:
                        detected_phase = "Menstrual"
                    elif days_since_last <= 14:
                        detected_phase = "Follicular"
                    elif days_since_last <= 21:
                        detected_phase = "Ovulatory"
                    else:
                        detected_phase = "Luteal"

                    st.session_state.phase = phase_override if phase_override else detected_phase
                    if not phase_override:
                        st.success(f"Based on your data, you are likely in the **{st.session_state.phase}** phase.")
                    st.session_state.personalization_completed = True

    else:
        st.subheader("🚫 No active menstrual cycle detected.")
        pseudo_choice = st.radio("Would you like:", ("🌿 Get general energetic advice", "🌙 Start with a pseudo-cycle based on a 28-day rhythm"))

        if pseudo_choice:
            if pseudo_choice == "🌿 Get general energetic advice":
                st.session_state.phase = "General"
            else:
                st.session_state.phase = "Menstrual"
                st.session_state.cycle_length = 28
            st.success(f"Selected: {pseudo_choice}")
            st.session_state.personalization_completed = True

    # Manual override sets phase regardless of other conditions
    if phase_override and phase_override in ["Menstrual", "Follicular", "Ovulatory", "Luteal"]:
        st.session_state.phase = phase_override
        st.success(f"You selected: **{phase_override}** phase manually.")
        st.session_state.personalization_completed = True

    return has_cycle

def render_personalization_sidebar():
    st.sidebar.header("Personal settings")
    support_options = ["Nothing specific", "Hormonal balance", "Energy", "Acne", "Digestive health", "Metabolism boost"]
    st.session_state.support_goal = st.sidebar.selectbox("What would you like support with? ℹ️", support_options)

    dietary_options = ["Vegan", "Vegetarian", "Nut allergy", "Gluten free", "Lactose intolerance"]
    st.session_state.dietary_preferences = st.sidebar.multiselect("Do you follow any dietary guidelines? ℹ️", dietary_options)

    if st.session_state.support_goal and st.session_state.dietary_preferences and st.session_state.phase:
        st.session_state.personalization_completed = True

def render_suggested_questions():
    st.markdown("### 💬 Suggested questions you can ask:")
    questions = [
        ("🧬 What foods are best for my current cycle phase?", "suggestion_q1"),
        ("🌿 How can I support my hormones with food?", "suggestion_q2"),
        ("🧼 Why is organic or clean eating important?", "suggestion_q3"),
        (f"📆 How do I support the {st.session_state.phase} phase nutritionally?", "suggestion_q4")
    ]
    for label, key in questions:
        if st.button(label, key=key):
            st.session_state.user_question = label.split(" ", 1)[1]

def render_personalization_summary():
    st.markdown("---")
    st.header("Your Personalization Summary")
    st.markdown(f"**Cycle phase:** {st.session_state.phase}")
    st.markdown(f"**Support goal:** {st.session_state.support_goal}")
    if st.session_state.dietary_preferences:
        st.markdown(f"**Dietary preferences:** {', '.join(st.session_state.dietary_preferences)}")
    else:
        st.markdown("**Dietary preferences:** None")
    st.markdown("---")

    # Show example questions here
    render_suggested_questions()
