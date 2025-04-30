# ui.py
import streamlit as st
from datetime import datetime

def render_cycle_questions():
    has_cycle = st.radio("Do you have a (regular) menstrual cycle?", ("Yes", "No"))

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
                        st.session_state.phase = "Menstrual"
                    elif days_since_last <= 14:
                        st.session_state.phase = "Follicular"
                    elif days_since_last <= 21:
                        st.session_state.phase = "Ovulatory"
                    else:
                        st.session_state.phase = "Luteal"

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

    return has_cycle

def render_personalization_sidebar():
    st.sidebar.header("🌸 Personalization")
    support_options = ["Nothing specific", "Hormonal balance", "Energy", "Digestive health", "Metabolism boost"]
    st.session_state.support_goal = st.sidebar.selectbox("What would you like support with? ℹ️", support_options)

    dietary_options = ["Vegan", "Vegetarian", "Nut allergy", "Gluten free", "Lactose intolerance"]
    st.session_state.dietary_preferences = st.sidebar.multiselect("Do you follow any dietary guidelines? ℹ️", dietary_options)

    if st.session_state.support_goal and st.session_state.dietary_preferences:
        st.session_state.personalization_completed = True

def render_personalization_summary():
    st.markdown("---")
    st.header("✅ Your Personalization Summary")
    st.markdown(f"**Cycle phase:** {st.session_state.phase}")
    st.markdown(f"**Support goal:** {st.session_state.support_goal}")
    if st.session_state.dietary_preferences:
        st.markdown(f"**Dietary preferences:** {', '.join(st.session_state.dietary_preferences)}")
    else:
        st.markdown("**Dietary preferences:** None")
    st.markdown("---")
