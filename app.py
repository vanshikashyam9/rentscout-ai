import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# ---------------------------------------------------
# LOAD API KEY
# ---------------------------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Vancouver Rental AI",
    page_icon="🏠",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
st.markdown(
    """
    <style>

    .main {
        background-color: #0E1117;
        color: white;
    }

    .hero-box {
        background: linear-gradient(135deg, #1E3A8A, #7C3AED);
        padding: 2rem;
        border-radius: 25px;
        margin-bottom: 2rem;
        box-shadow: 0px 4px 25px rgba(0,0,0,0.3);
    }

    .hero-title {
        font-size: 2.7rem;
        font-weight: 700;
        color: white;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #E5E7EB;
        margin-top: 0.5rem;
    }

    .card {
        background-color: #1F2937;
        padding: 1.2rem;
        border-radius: 18px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .metric-title {
        font-size: 0.9rem;
        color: #9CA3AF;
    }

    .metric-value {
        font-size: 1.7rem;
        font-weight: bold;
        color: white;
    }

    .success-box {
        background-color: rgba(16,185,129,0.15);
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #10B981;
    }

    .warning-box {
        background-color: rgba(245,158,11,0.15);
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #F59E0B;
    }

    .danger-box {
        background-color: rgba(239,68,68,0.15);
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #EF4444;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# HERO SECTION
# ---------------------------------------------------
st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">🏠 Vancouver Rental AI</div>
        <div class="hero-subtitle">
            Your AI-powered newcomer guide for rentals, budgeting,
            neighborhoods, and survival tips in Vancouver.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------
def is_budget_question(text: str) -> bool:
    keywords = [
        "budget", "survive", "enough", "afford",
        "monthly", "$", "income", "salary", "cost"
    ]

    return any(k in text.lower() for k in keywords)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
st.sidebar.title("⚙️ Budget Planner")
st.sidebar.write("Adjust your monthly lifestyle expenses.")

income = st.sidebar.slider("💰 Monthly Income", 1000, 10000, 3000, 100)

rent = st.sidebar.slider("🏠 Rent", 500, 5000, 1800, 50)

food = st.sidebar.slider("🍔 Food", 100, 1500, 400, 50)

transport = st.sidebar.slider("🚇 Transport", 0, 500, 120, 10)

utilities = st.sidebar.slider("⚡ Utilities", 0, 500, 100, 10)

other = st.sidebar.slider("🎯 Other Expenses", 0, 1000, 200, 50)

# ---------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------
total_expenses = rent + food + transport + utilities + other
remaining = income - total_expenses

# ---------------------------------------------------
# STATUS
# ---------------------------------------------------
if remaining > 1000:
    status = "🟢 Comfortable"
    explanation = (
        "You have a strong financial buffer. "
        "This budget is healthy for Vancouver."
    )
    status_class = "success-box"

elif remaining > 0:
    status = "🟡 Tight but survivable"
    explanation = (
        "Vancouver is expensive, and your remaining savings are limited."
    )
    status_class = "warning-box"

else:
    status = "🔴 Budget deficit"
    explanation = (
        "Your expenses exceed your income. "
        "You may need cheaper housing or lower spending."
    )
    status_class = "danger-box"

# ---------------------------------------------------
# BIGGEST EXPENSE
# ---------------------------------------------------
costs = {
    "Rent": rent,
    "Food": food,
    "Transport": transport,
    "Utilities": utilities,
    "Other": other
}

highest_category = max(costs, key=costs.get)
highest_value = costs[highest_category]

# ---------------------------------------------------
# SUGGESTIONS
# ---------------------------------------------------
if highest_category == "Rent":
    suggestion = (
        "Consider shared accommodation or areas like Surrey/Burnaby."
    )

elif highest_category == "Food":
    suggestion = (
        "Cooking at home can significantly reduce food expenses."
    )

elif highest_category == "Transport":
    suggestion = (
        "A monthly transit pass may save money."
    )

else:
    suggestion = (
        "Reducing discretionary spending could improve your savings."
    )

# ---------------------------------------------------
# MAIN DASHBOARD METRICS
# ---------------------------------------------------
st.markdown("## 📊 Financial Snapshot")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-title">Monthly Income</div>
            <div class="metric-value">${income}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-title">Total Expenses</div>
            <div class="metric-value">${total_expenses}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-title">Remaining Balance</div>
            <div class="metric-value">${remaining}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# INSIGHT PANEL
# ---------------------------------------------------
st.markdown("## 🧠 AI Budget Insight")

st.markdown(
    f"""
    <div class="{status_class}">
        <h4>{status}</h4>
        <p>{explanation}</p>
        <p><strong>Biggest Expense:</strong> {highest_category} (${highest_value})</p>
        <p><strong>Suggestion:</strong> {suggestion}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# SYSTEM PROMPTS
# ---------------------------------------------------
BASE_SYSTEM_PROMPT = """
You are a Vancouver rental assistant for newcomers.

You help users with:
1. Finding rentals in Vancouver & Metro Vancouver
2. Explaining neighborhoods
3. Detecting rental scams
4. Giving budget and cost-of-living advice

Be practical, friendly, realistic, and supportive.
"""

BUDGET_SYSTEM_PROMPT = """
You are a Vancouver cost-of-living and budgeting expert.

When answering:
- Break down expenses clearly
- Compare affordability realistically
- Explain why the budget is good or risky
- Suggest practical improvements
"""

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": BASE_SYSTEM_PROMPT}
    ]

# ---------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------
st.markdown("## 💬 AI Assistant")

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------
user_input = st.chat_input(
    "Ask about rentals, survival budget, neighborhoods, or scams..."
)

if user_input:

    st.chat_message("user").write(user_input)

    if is_budget_question(user_input):
        system_prompt = BUDGET_SYSTEM_PROMPT
    else:
        system_prompt = BASE_SYSTEM_PROMPT

    budget_context = f"""
    Current User Budget Snapshot:

    Income: {income}
    Rent: {rent}
    Food: {food}
    Transport: {transport}
    Utilities: {utilities}
    Other: {other}

    Total Expenses: {total_expenses}
    Remaining: {remaining}
    Status: {status}

    Biggest Expense Category:
    {highest_category}: {highest_value}

    Suggestion:
    {suggestion}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": budget_context},
        *st.session_state.messages[1:],
        {"role": "user", "content": user_input}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.6
    )

    reply = response.choices[0].message.content

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    st.chat_message("assistant").write(reply)
