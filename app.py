import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from market_intelligence import get_market_stats
from listing_analyzer import analyze_listing
import pandas as pd
import plotly.express as px
from area_recommender import recommend_areas
from craigslist_scraper import get_craigslist_listings
from listing_analyzer import analyze_listing
import os

# ---------------------------------------------------
# LOAD API KEY
# ---------------------------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------------
# LOAD MARKET DATA
# -----------------------------------

market_df = pd.read_csv(
    "data/processed/cleaned_market_data.csv"
)

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="RENTSCOUT AI - Vancouver Rental Assistant",
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

def detect_area(text):

     # Prevent NoneType error
    if text is None:
        return None

    areas = [
        "Downtown",
        "Burnaby",
        "Richmond",
        "Surrey",
        "Kitsilano",
        "Marpole",
        "New Westminster",
        "Langley",
        "North Vancouver",
        "West Vancouver",
        "Metrotown",
        "Tri-Cities"
    ]

    for area in areas:
        if area.lower() in text.lower():
            return area

    return None

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

# -----------------------------------
# 🚨 LISTING SCAM ANALYZER
# -----------------------------------

st.sidebar.markdown("---")
st.sidebar.markdown("## 🚨 Rental Scam Detector")

listing_input = st.sidebar.text_area(
    "Paste rental listing here",
    height=200
)

analyze_button = st.sidebar.button(
    "Analyze Listing"
)

# -----------------------------------
# RUN ANALYZER
# -----------------------------------

if analyze_button and listing_input:

    result = analyze_listing(listing_input)

    risk_score = result["risk_score"]
    risk_level = result["risk_level"]
    reasons = result["reasons"]

    st.markdown("## 🚨 Scam Analysis Result")

    # -----------------------------------
    # RISK BADGE
    # -----------------------------------

    if risk_level == "HIGH":
        st.error(f"⚠ HIGH RISK ({risk_score}/100)")

    elif risk_level == "MEDIUM":
        st.warning(f"🟡 MEDIUM RISK ({risk_score}/100)")

    else:
        st.success(f"🟢 LOW RISK ({risk_score}/100)")

    # -----------------------------------
    # SCAM SCORE BAR
    # -----------------------------------

    st.progress(min(risk_score / 100, 1.0))
    st.caption(f"Risk Confidence Score: {risk_score}%")

    # -----------------------------------
    # REASONS
    # -----------------------------------

    st.markdown("### 🔍 Why this was flagged")

    for reason in reasons:
        st.write(f"• {reason}")

    # -----------------------------------
    # SAFETY TIPS
    # -----------------------------------

    st.markdown("### 🛡 Safety Tips")

    st.write("""
    - Never send deposits before viewing
    - Verify landlord identity
    - Avoid rushed payments
    - Compare prices with market averages
    - Be cautious of unrealistic deals
    """)
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
# RENTAL SCAM DETECTOR
# ---------------------------------------------------

st.markdown("---")
st.markdown("## 🔍 Rental Listing Analyzer")

listing_text = st.text_area(
    "Paste a rental listing here for scam analysis:",
    height=200,
    placeholder="Example:\n1 bedroom downtown Vancouver for $700..."
)

if st.button("Analyze Listing"):

    if listing_text.strip() == "":
        st.warning("Please paste a rental listing first.")

    else:

        scam_prompt = f"""
You are an expert rental scam detection AI.

Analyze the following Vancouver rental listing.

Return:
1. Scam Risk Level (Low / Medium / High)
2. Scam Score out of 100
3. Red flags detected
4. Recommendation for the user

Rental Listing:
{listing_text}
"""

        with st.spinner("Analyzing listing..."):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a rental scam detection expert."
                    },
                    {
                        "role": "user",
                        "content": scam_prompt
                    }
                ],
                temperature=0.3
            )

            analysis = response.choices[0].message.content

        st.markdown("### 🚨 Scam Analysis")

        st.write(analysis)

# ---------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------
user_input = st.chat_input(
    "Ask about rentals, survival budget, neighborhoods, or scams..."
)

if user_input:

    st.chat_message("user").write(user_input)

# -----------------------------------
# MARKET INTELLIGENCE
# -----------------------------------

market_context = ""

detected_area = detect_area(user_input)

if detected_area:

    market_data = get_market_stats(detected_area)

    if market_data:

        market_context = f"""
        MARKET INTELLIGENCE DATA:

        Area: {market_data['area']}
        Historical Average Vacancy Rate:
        {market_data['average_vacancy']}%

        Latest Year:
        {market_data['latest_year']}

        Latest Vacancy Rate:
        {market_data['latest_vacancy']}%

        Lower vacancy rates indicate
        a more competitive rental market.
        """

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
    {"role": "system", "content": market_context},
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

# ===================================
# 📊 MARKET INTELLIGENCE DASHBOARD
# ===================================

st.markdown("---")
st.markdown("# 📊 RentScout Market Dashboard")

st.write(
    "Historical CMHC rental market intelligence for Metro Vancouver."
)

# -----------------------------------
# AREA SELECTOR
# -----------------------------------

areas = sorted(market_df["Zone"].unique())

selected_area = st.selectbox(
    "Select Area",
    areas
)

# -----------------------------------
# FILTER DATA
# -----------------------------------

filtered_df = market_df[
    market_df["Zone"] == selected_area
]

# -----------------------------------
# METRICS
# -----------------------------------

latest_year = filtered_df["Year"].max()

latest_data = filtered_df[
    filtered_df["Year"] == latest_year
]

latest_vacancy = latest_data["Vacancy_Rate"].mean()

avg_vacancy = filtered_df[
    "Vacancy_Rate"
].mean()

# -----------------------------------
# METRIC CARDS
# -----------------------------------

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Latest Vacancy Rate",
        f"{latest_vacancy:.2f}%"
    )

with col2:
    st.metric(
        "Historical Average",
        f"{avg_vacancy:.2f}%"
    )

# -----------------------------------
# TREND CHART
# -----------------------------------

fig = px.line(
    filtered_df,
    x="Year",
    y="Vacancy_Rate",
    markers=True,
    title=f"Vacancy Trend — {selected_area}"
)

fig.update_xaxes(
    dtick=1
)

st.plotly_chart(
    fig,
    use_container_width=True
)
# ===================================
# 📈 MULTI-AREA COMPARISON
# ===================================

st.markdown("## 📈 Compare Multiple Areas")

multi_areas = st.multiselect(
    "Choose areas to compare",
    areas,
    default=[
        "City of Vancouver (Zones 1-10)",
        "Burnaby (Zones 12-14)",
        "Zone 21 - Surrey"
    ]
)

if multi_areas:

    compare_df = market_df[
        market_df["Zone"].isin(multi_areas)
    ]

    compare_fig = px.line(
        compare_df,
        x="Year",
        y="Vacancy_Rate",
        color="Zone",
        markers=True,
        title="Metro Vancouver Vacancy Comparison"
    )

    # cleaner x-axis
    compare_fig.update_xaxes(
        dtick=1
    )

    st.plotly_chart(
        compare_fig,
        use_container_width=True
    )
# -----------------------------------
# MARKET INSIGHT
# -----------------------------------

st.markdown("## 🧠 AI Market Insight")

if latest_vacancy < 1:
    st.error(
        "Extremely competitive rental market."
    )

elif latest_vacancy < 2:
    st.warning(
        "Rental market is competitive."
    )

elif latest_vacancy < 4:
    st.info(
        "Moderate rental availability."
    )

else:
    st.success(
        "Higher rental availability than historical norms."
    )

# -----------------------------------
# RAW DATA
# -----------------------------------

with st.expander("📄 View Raw Market Data"):
    st.dataframe(filtered_df)
# ===================================
# 🏠 AREA RECOMMENDATION ENGINE
# ===================================

st.markdown("---")
st.markdown("# 🏠 Smart Area Recommendations")

st.write(
    "Find the best Metro Vancouver areas based on your budget."
)

# -----------------------------------
# USER INPUT
# -----------------------------------

user_budget = st.slider(
    "Monthly Housing Budget ($)",
    800,
    5000,
    1800,
    100
)

# -----------------------------------
# RUN RECOMMENDER
# -----------------------------------

if st.button("Find Best Areas"):

    recommendations = recommend_areas(
        user_budget
    )

    st.markdown("## 🎯 Recommended Areas")

    for rec in recommendations:

        area = rec["area"]
        vacancy = rec["vacancy_rate"]
        score = rec["score"]

        # -----------------------------------
        # AREA CARD
        # -----------------------------------

        with st.container():

            st.markdown(f"### 📍 {area}")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Vacancy Rate",
                    f"{vacancy:.1f}%"
                )

            with col2:
                st.metric(
                    "Recommendation Score",
                    score
                )

            # -----------------------------------
            # MARKET INTERPRETATION
            # -----------------------------------

            if vacancy >= 4:
                st.success(
                    "High rental availability. Easier to find housing."
                )

            elif vacancy >= 2:
                st.info(
                    "Moderate competition in this area."
                )

            else:
                st.warning(
                    "Highly competitive rental market."
                )

            st.markdown("---")

# ===================================
# 🏠 LIVE RENTAL LISTINGS
# ===================================

st.markdown("---")
st.markdown("# 🏠 Live Vancouver Rentals")

st.write(
    "Latest rental listings from Craigslist Vancouver."
)

if st.button("Load Live Listings"):

    listings = get_craigslist_listings()

    for listing in listings:

        st.markdown("### 📍 " + listing["title"])

        # -----------------------------------
        # SCAM ANALYSIS
        # -----------------------------------
        analysis = analyze_listing(
            listing["title"],
            listing["price"]
            )

        risk = analysis["risk_level"]
        score = analysis["risk_score"]

        if risk == "HIGH":
            st.error(
                f"🚨 HIGH SCAM RISK ({score}/100)"
            )

        elif risk == "MEDIUM":
            st.warning(
                f"⚠ MEDIUM SCAM RISK ({score}/100)"
                )
            
        else:
            st.success(
                f"✅ LOW SCAM RISK ({score}/100)"
                )
            
        if analysis["reasons"]:
            with st.expander("See Scam Analysis"):
                for reason in analysis["reasons"]:
                    st.write("•", reason)

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                f"💰 Price: {listing['price']}"
            )

        with col2:
            st.write(
                f"📌 Location: {listing['location']}"
            )

        st.markdown(
            f"[View Listing]({listing['link']})"
        )

        st.markdown("---")