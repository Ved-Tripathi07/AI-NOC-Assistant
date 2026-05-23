import streamlit as st
import asyncio

from masterAgent import master_agent


# --------------------------------
# PAGE CONFIG
# --------------------------------
st.set_page_config(
    page_title="AI Network Operations Center",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------
# CUSTOM CSS
# --------------------------------
st.markdown("""
<style>

/* Main App */
.stApp {
    background-color: #0f172a;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1f2937;
}

/* Main Header */
.main-title {
    font-size: 42px;
    font-weight: 700;
    color: #38bdf8;
    margin-bottom: 0px;
}

.sub-title {
    font-size: 16px;
    color: #94a3b8;
    margin-top: -10px;
    margin-bottom: 30px;
}

/* Chat Cards */
.chat-container {
    margin-bottom: 20px;
}

.user-chat {
    background: linear-gradient(
        135deg,
        #2563eb,
        #1d4ed8
    );
    padding: 16px;
    border-radius: 16px;
    color: white;
    font-size: 15px;
}

.assistant-chat {
    background-color: #1e293b;
    border: 1px solid #334155;
    padding: 16px;
    border-radius: 16px;
    color: #e2e8f0;
    font-size: 15px;
}

/* Chat Input */
.stChatInput textarea {
    background-color: #1e293b !important;
    color: white !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}

/* Spinner Text */
.stSpinner > div {
    color: white !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 10px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------
# SIDEBAR
# --------------------------------
with st.sidebar:

    st.markdown("## 🌐 AI NOC Dashboard")

    st.markdown("---")

    st.markdown("""
### Features
- ServiceNow Incident Analysis
- Cisco Diagnostics
- Multi-Agent Orchestration
- MCP Tool Execution
- RCA Assistance
""")

    st.markdown("---")

    st.markdown("""
### Example Queries
- Investigate INC0976270
- Diagnose router CPU issue
- Analyze interface flapping
- Fetch incident details
""")


# --------------------------------
# HEADER
# --------------------------------
st.markdown(
    """
    <div class="main-title">
        🌐 AI Network Operations Center
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="sub-title">
        ServiceNow + Cisco Multi-Agent AI System
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------
# SESSION STATE
# --------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------
for message in st.session_state.messages:

    if message["role"] == "human":

        st.markdown(
            f"""
            <div class="chat-container">
                <div class="user-chat">
                    🧑‍💻 <b>You</b><br><br>
                    {message["content"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="chat-container">
                <div class="assistant-chat">
                    🤖 <b>AI NOC Assistant</b><br><br>
                    {message["content"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# --------------------------------
# USER INPUT
# --------------------------------
prompt = st.chat_input(
    "Ask about incidents, diagnostics, RCA..."
)


# --------------------------------
# ASYNC HELPER
# --------------------------------
def run_async(coro):

    loop = asyncio.new_event_loop()

    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    finally:
        loop.close()


# --------------------------------
# RUN MASTER AGENT
# --------------------------------
async def run_agent():

    formatted_messages = []

    for msg in st.session_state.messages:

        role = "human" if msg["role"] == "human" else "assistant"

        formatted_messages.append(
            (role, msg["content"])
        )

    response = await master_agent.ainvoke({
        "messages": formatted_messages
    })

    return response["messages"][-1].content


# --------------------------------
# HANDLE USER PROMPT
# --------------------------------
if prompt:

    # Save User Message
    st.session_state.messages.append({
        "role": "human",
        "content": prompt
    })

    # Show User Message
    st.markdown(
        f"""
        <div class="chat-container">
            <div class="user-chat">
                🧑‍💻 <b>You</b><br><br>
                {prompt}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Generate AI Response
    with st.spinner("🔍 Investigating network issue..."):

        try:

            ai_response = run_async(
                run_agent()
            )

            # Display AI Response
            st.markdown(
                f"""
                <div class="chat-container">
                    <div class="assistant-chat">
                        🤖 <b>AI NOC Assistant</b><br><br>
                        {ai_response}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Save AI Response
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response
            })

        except Exception as e:

            error_msg = f"❌ Error: {str(e)}"

            st.error(error_msg)

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })