import os
import requests
import streamlit as st

# ==============================================================================
# Page Configuration & Styling
# ==============================================================================
st.set_page_config(
    page_title="AI vs AI Debate Simulator",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished, modern look
st.markdown(
    """
    <style>
    .main-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .main-subtitle {
        color: #64748B;
        font-size: 1.05rem;
    }
    .topic-card {
        background-color: rgba(99, 102, 241, 0.08);
        border-left: 4px solid #4F46E5;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin: 1rem 0 1.5rem 0;
    }
    .verdict-box {
        background-color: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-top: 1.5rem;
    }
    .for-badge {
        background-color: #10B981;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .against-badge {
        background-color: #EF4444;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stButton>button {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Backend API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


# ==============================================================================
# Session State Initialization
# ==============================================================================
if "debate_result" not in st.session_state:
    st.session_state.debate_result = None

if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""

if "last_rounds" not in st.session_state:
    st.session_state.last_rounds = 3


def reset_debate():
    """Clear the current debate session state."""
    st.session_state.debate_result = None
    st.session_state.last_topic = ""
    st.session_state.last_rounds = 3


# ==============================================================================
# Sidebar
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Simulator Controls")
    st.markdown(
        """
        Welcome to the **AI vs AI Debate Simulator**!
        
        Two AI agents debate opposing sides of any resolution across multiple structured rounds. Once the debate concludes, an impartial AI judge determines the winner with reasoned analysis.
        """
    )

    st.markdown("---")
    st.markdown("#### 💡 Example Topics")
    example_topics = [
        "Social media does more harm than good to society.",
        "Artificial Intelligence will create more jobs than it destroys.",
        "Space exploration is worth the high financial cost.",
        "Remote work is superior to in-office work for productivity.",
        "Universal basic income should be implemented globally.",
    ]

    selected_example = st.selectbox(
        "Choose an example topic to fill:",
        options=["Select an example topic..."] + example_topics,
        index=0,
    )

    st.markdown("---")
    st.markdown("#### 📡 Backend Connection")
    backend_endpoint = st.text_input(
        "FastAPI Backend URL",
        value=BACKEND_URL,
        help="URL of the running FastAPI backend server",
    )

    # Simple health check helper
    if st.button("Check Backend Status", use_container_width=True):
        try:
            res = requests.get(f"{backend_endpoint}/", timeout=3)
            if res.status_code == 200:
                st.success("✅ Backend is reachable & healthy!")
            else:
                st.warning(f"⚠️ Backend responded with status {res.status_code}")
        except Exception:
            st.error("❌ Cannot connect to backend server.")


# ==============================================================================
# Header & Instructions
# ==============================================================================
st.markdown(
    """
    <div class="main-header">
        <div class="main-title">⚔️ AI vs AI Debate Simulator</div>
        <div class="main-subtitle">Two AI debaters enter the arena. One judge decides the victor.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 1. User Inputs & Layout
# ==============================================================================
with st.container():
    col_input, col_config = st.columns([3, 1])

    with col_input:
        default_val = ""
        if selected_example and selected_example != "Select an example topic...":
            default_val = selected_example
        elif st.session_state.last_topic:
            default_val = st.session_state.last_topic

        topic_input = st.text_input(
            "🎯 Debate Topic / Resolution",
            value=default_val,
            placeholder="e.g., Artificial general intelligence poses an existential risk to humanity.",
            help="Enter any statement or debate topic for the AI agents to argue.",
        )

    with col_config:
        # Strictly restricted to 2 or 3 rounds per SPEC
        num_rounds = st.radio(
            "🔁 Rounds",
            options=[2, 3],
            index=1 if st.session_state.last_rounds == 3 else 0,
            horizontal=True,
            help="Select strictly 2 or 3 debate rounds (FOR and AGAINST exchange arguments each round).",
        )

    btn_col1, btn_col2, _ = st.columns([1.5, 1.2, 3])

    with btn_col1:
        start_button = st.button("🚀 Start Debate", type="primary", use_container_width=True)

    with btn_col2:
        reset_button = st.button("🔄 New Debate", on_click=reset_debate, use_container_width=True)


# ==============================================================================
# 2. Backend API Integration & Execution
# ==============================================================================
if start_button:
    # 5. Error Handling: check empty topic
    if not topic_input or not topic_input.strip():
        st.warning("⚠️ Please enter a debate topic before starting the debate.")
    else:
        cleaned_topic = topic_input.strip()
        st.session_state.last_topic = cleaned_topic
        st.session_state.last_rounds = num_rounds

        # 3. UX & Loading States
        with st.spinner("🤖 Debaters FOR and AGAINST are arguing round-by-round and the Judge is deliberating... Please wait."):
            payload = {
                "topic": cleaned_topic,
                "num_rounds": num_rounds,
            }
            api_endpoint = f"{backend_endpoint.rstrip('/')}/debate"

            try:
                response = requests.post(api_endpoint, json=payload, timeout=120)
                
                if response.status_code == 200:
                    st.session_state.debate_result = response.json()
                else:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        error_detail = error_json.get("detail", response.text)
                    except Exception:
                        pass
                    st.error(f"⚠️ Backend returned error (Status {response.status_code}): {error_detail}")

            except requests.exceptions.ConnectionError:
                st.error(
                    f"❌ **Connection Error**: Unable to reach backend server at `{backend_endpoint}`.\n\n"
                    "**To fix this:**\n"
                    "1. Make sure your FastAPI backend is running:\n"
                    "   ```bash\n"
                    "   uvicorn backend.main:app --reload\n"
                    "   ```\n"
                    "2. Check that the port is `8000` and you have a valid `GEMINI_API_KEY` in your `.env` file."
                )
            except requests.exceptions.Timeout:
                st.error("⏳ **Request Timed Out**: The LLM response took longer than 120 seconds. Please try again.")
            except Exception as e:
                st.error(f"❌ **Unexpected Error**: {str(e)}")


# ==============================================================================
# 4. Formatted Results Display
# ==============================================================================
if st.session_state.debate_result:
    result = st.session_state.debate_result
    topic = result.get("topic", topic_input)
    turns = result.get("turns", [])
    winner = result.get("winner", "UNDECIDED").upper()
    reasoning = result.get("reasoning", "No justification provided.")

    st.markdown("---")
    st.markdown(
        f"""
        <div class="topic-card">
            <h4 style="margin: 0; color: #1E293B;">📜 Resolution: <em>"{topic}"</em></h4>
            <span style="font-size: 0.9rem; color: #64748B;">Total Rounds: {len(set(t.get('round') for t in turns))}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("💬 Debate Transcript")

    # Group turns by round
    rounds_dict = {}
    for turn in turns:
        r_num = turn.get("round", 1)
        if r_num not in rounds_dict:
            rounds_dict[r_num] = []
        rounds_dict[r_num].append(turn)

    for r_num in sorted(rounds_dict.keys()):
        st.markdown(f"#### 🥊 Round {r_num}")

        for turn in rounds_dict[r_num]:
            speaker = turn.get("speaker", "UNKNOWN").upper()
            text = turn.get("text", "")

            if speaker == "FOR":
                with st.chat_message("user", avatar="🟢"):
                    st.markdown(
                        "<span class='for-badge'>PROPOSITION — FOR</span>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(text)
            elif speaker == "AGAINST":
                with st.chat_message("assistant", avatar="🔴"):
                    st.markdown(
                        "<span class='against-badge'>OPPOSITION — AGAINST</span>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(text)
            else:
                with st.chat_message("system", avatar="⚠️"):
                    st.markdown(f"**{speaker}:**")
                    st.markdown(text)

        st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # Final Judge Verdict (Prominently separated at the bottom)
    # --------------------------------------------------------------------------
    st.markdown("---")
    st.subheader("🧑‍⚖️ Official Judge's Verdict")

    if winner == "FOR":
        winner_display = "🟢 PROPOSITION (FOR)"
        banner_type = st.success
    elif winner == "AGAINST":
        winner_display = "🔴 OPPOSITION (AGAINST)"
        banner_type = st.error
    else:
        winner_display = f"⚖️ {winner}"
        banner_type = st.info

    banner_type(f"### 🏆 WINNER: {winner_display}")

    with st.container():
        st.markdown("#### 📝 Reasoned Justification")
        st.info(reasoning)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    with c1:
        st.button("🔄 Start Another Debate", on_click=reset_debate, type="secondary", use_container_width=True)
