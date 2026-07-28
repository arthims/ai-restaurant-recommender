"""
AI Restaurant Recommender - Single File Version
All logic is self-contained to avoid any ImportError on Streamlit Cloud.
"""
import streamlit as st
import pandas as pd
import os
import sys
import json

# ─────────────────────────────────────────────────────────
# 1. PAGE CONFIG (must be first Streamlit call)
# ─────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Restaurant Recommender", page_icon="🍽️", layout="wide")

# ─────────────────────────────────────────────────────────
# 2. DATA LOADING & INGESTION
# ─────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'cleaned_zomato.parquet')

@st.cache_resource(show_spinner="Loading restaurant data...")
def load_data():
    if not os.path.exists(DATA_PATH):
        st.info("First-time setup: Downloading dataset from Hugging Face...")
        _ingest_data()
    df = pd.read_parquet(DATA_PATH)
    # Fix rate column (e.g. '4.1/5' or 'NEW')
    if 'rate' in df.columns:
        df['rate_float'] = df['rate'].astype(str).str.split('/').str[0].replace(['NEW', '-', 'nan'], '0')
        df['rate_float'] = pd.to_numeric(df['rate_float'], errors='coerce').fillna(0.0)
    # Fix cost column
    cost_col = 'approx_cost(for two people)' if 'approx_cost(for two people)' in df.columns else \
               'approx cost(for two people)' if 'approx cost(for two people)' in df.columns else None
    if cost_col:
        df['cost_float'] = df[cost_col].astype(str).str.replace(',', '', regex=False)
        df['cost_float'] = pd.to_numeric(df['cost_float'], errors='coerce').fillna(0.0)
    return df

def _ingest_data():
    try:
        from datasets import load_dataset
        dataset = load_dataset("ManikaSaini/zomato-restaurant-recommendation", split="train")
        heavy_cols = ['reviews_list', 'menu_item', 'dish_liked', 'url', 'phone', 'address']
        cols_to_remove = [c for c in heavy_cols if c in dataset.column_names]
        if cols_to_remove:
            dataset = dataset.remove_columns(cols_to_remove)
        df = dataset.to_pandas()
        df.columns = [col.lower() for col in df.columns]
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        df.to_parquet(DATA_PATH, index=False)
    except Exception as e:
        st.error(f"Failed to download dataset: {e}")
        st.stop()

# ─────────────────────────────────────────────────────────
# 3. FILTERING LOGIC
# ─────────────────────────────────────────────────────────
def filter_restaurants(df, location, cuisines, min_budget, max_budget, min_rating, top_n=15):
    filtered = df.copy()
    # Filter by Location
    if location:
        loc = location.lower().strip()
        loc_col = next((c for c in ['location', 'city'] if c in filtered.columns), None)
        if loc_col:
            filtered = filtered[filtered[loc_col].str.contains(loc, na=False, case=False)]
    # Filter by Budget
    if 'cost_float' in filtered.columns:
        filtered = filtered[(filtered['cost_float'] >= min_budget) & (filtered['cost_float'] <= max_budget)]
    # Filter by Rating
    if 'rate_float' in filtered.columns:
        filtered = filtered[filtered['rate_float'] >= min_rating]
    # Filter by Cuisine
    if cuisines:
        cuisine_col = next((c for c in ['cuisines', 'cuisine'] if c in filtered.columns), None)
        if cuisine_col:
            mask = filtered[cuisine_col].str.lower().str.contains('|'.join([c.lower() for c in cuisines]), na=False)
            filtered = filtered[mask]
    # Sort by rating then votes
    sort_cols, asc = [], []
    if 'rate_float' in filtered.columns:
        sort_cols.append('rate_float'); asc.append(False)
    if 'votes' in filtered.columns:
        filtered['votes'] = pd.to_numeric(filtered['votes'], errors='coerce').fillna(0)
        sort_cols.append('votes'); asc.append(False)
    if sort_cols:
        filtered = filtered.sort_values(by=sort_cols, ascending=asc)
    return filtered.head(top_n)

# ─────────────────────────────────────────────────────────
# 4. LLM RECOMMENDATION
# ─────────────────────────────────────────────────────────
def generate_recommendations(df, prefs_dict):
    groq_key = None
    # Try Streamlit secrets first, then env variable
    try:
        groq_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        groq_key = os.environ.get("GROQ_API_KEY")

    candidates = df.to_dict(orient="records")
    candidates_str = json.dumps(candidates[:15], indent=2, default=str)

    if groq_key:
        try:
            from langchain_groq import ChatGroq
            from langchain_core.prompts import PromptTemplate
            from langchain_core.output_parsers import JsonOutputParser

            llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7, api_key=groq_key)
            template = """You are an expert food critic and AI Restaurant Recommender.
User Preferences: {prefs}
Top Restaurant Candidates: {candidates}
Select the best 3-5 restaurants that match the user preferences and rank them.
Output ONLY a JSON object:
{{
    "summary": "A brief welcoming intro sentence.",
    "recommendations": [
        {{"rank": 1, "name": "Restaurant Name", "explanation": "Why it is a great choice..."}}
    ]
}}"""
            prompt = PromptTemplate(template=template, input_variables=["prefs", "candidates"])
            chain = prompt | llm | JsonOutputParser()
            return chain.invoke({"prefs": json.dumps(prefs_dict), "candidates": candidates_str})
        except Exception as e:
            st.warning(f"AI ranking unavailable ({e}). Showing top matches by rating.")

    # Fallback: top 5 by rating
    top_recs = []
    for i, row in enumerate(df.head(5).to_dict(orient="records")):
        name_val = row.get("name") or row.get("restaurant name") or "Unknown"
        rating = row.get("rate_float", row.get("rate", "N/A"))
        top_recs.append({
            "rank": i + 1,
            "name": name_val,
            "explanation": f"⭐ Rating: {rating} | 💰 Cost for two: ₹{row.get('cost_float', 'N/A')} | 🍽️ Cuisines: {row.get('cuisines', 'N/A')}"
        })
    return {
        "summary": "Top restaurants matching your criteria (sorted by rating):",
        "recommendations": top_recs
    }

# ─────────────────────────────────────────────────────────
# 5. CUSTOM CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.restaurant-card {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    border-left: 5px solid #ff4b4b;
    transition: transform 0.2s ease;
}
.restaurant-name {
    color: #ff6b6b;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 8px;
}
.restaurant-explanation { font-size: 15px; color: #cdd6f4; line-height: 1.6; }
.rank-badge {
    background: linear-gradient(135deg, #ff4b4b, #ff6b35);
    color: white;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: bold;
    margin-right: 10px;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# 6. UI LAYOUT
# ─────────────────────────────────────────────────────────
st.title("🍽️ AI-Powered Restaurant Recommender")
st.markdown("Find the perfect place to eat based on your unique preferences! Powered by **Groq** and **LangChain**.")

st.sidebar.header("🎯 Your Preferences")

# City fixed to Bangalore (dataset only covers Bangalore)
st.sidebar.markdown("🏙️ **City: Bangalore**")

bangalore_areas = [
    "Banashankari", "BTM", "Koramangala", "Indiranagar", "Jayanagar",
    "JP Nagar", "Marathahalli", "HSR Layout", "Whitefield", "Malleshwaram",
    "Electronic City", "Hebbal", "Yelahanka", "Rajajinagar", "Bellandur",
    "Sarjapur", "Basavanagudi", "Frazer Town", "MG Road", "Brigade Road"
]

selected_area = st.sidebar.selectbox("📍 Area", options=bangalore_areas)
location = selected_area

cuisines_list = ["North Indian", "South Indian", "Chinese", "Italian", "Mexican",
                 "Cafe", "Desserts", "Continental", "Fast Food", "Biryani", "Seafood", "Pizza"]
selected_cuisines = st.sidebar.multiselect("🍕 Cuisine(s)", options=cuisines_list)

budget_range = st.sidebar.slider("💰 Budget (Cost for Two ₹)", min_value=100, max_value=5000, value=(300, 1500), step=100)
min_rating = st.sidebar.slider("⭐ Minimum Rating", min_value=3.5, max_value=5.0, value=4.0, step=0.1)

submit = st.sidebar.button("🔍 Find Restaurants", use_container_width=True)

# ─────────────────────────────────────────────────────────
# 7. MAIN LOGIC
# ─────────────────────────────────────────────────────────
if submit:
    df = load_data()

    col1, col2, col3 = st.columns(3)
    col1.metric("📍 Area", selected_area)
    col2.metric("⭐ Min Rating", min_rating)
    col3.metric("💰 Budget", f"₹{budget_range[0]}–₹{budget_range[1]}")

    with st.spinner("Filtering restaurants..."):
        filtered_df = filter_restaurants(
            df, location, selected_cuisines,
            budget_range[0], budget_range[1], min_rating
        )

    if filtered_df.empty:
        st.warning("😕 No restaurants found matching your criteria. Try lowering the rating or expanding the budget.")
        st.info(f"**Debug info:** Searched for '{location}' in dataset. Total rows in dataset: {len(df)}")
        # Show sample locations in dataset for debugging
        loc_col = next((c for c in ['location', 'city'] if c in df.columns), None)
        if loc_col:
            sample_locs = df[loc_col].dropna().unique()[:20]
            st.write("**Sample locations in dataset:**", list(sample_locs))
    else:
        st.success(f"✅ Found **{len(filtered_df)}** matching restaurants! AI is ranking the best ones...")

        prefs_dict = {
            "location": location,
            "cuisines": selected_cuisines,
            "min_budget": budget_range[0],
            "max_budget": budget_range[1],
            "min_rating": min_rating
        }

        with st.spinner("AI is reasoning and ranking..."):
            recommendations = generate_recommendations(filtered_df, prefs_dict)

        if 'summary' in recommendations:
            st.markdown(f"### ✨ {recommendations['summary']}")

        if recommendations.get('recommendations'):
            for rec in recommendations['recommendations']:
                st.markdown(f"""
                <div class="restaurant-card">
                    <div class="restaurant-name">
                        <span class="rank-badge">#{rec.get('rank', '-')}</span> {rec.get('name', 'Unknown')}
                    </div>
                    <div class="restaurant-explanation">
                        {rec.get('explanation', 'No explanation provided.')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Failed to generate recommendations.")
else:
    st.info("👈 Select your city, area, cuisine, and budget in the sidebar, then click **Find Restaurants**!")
