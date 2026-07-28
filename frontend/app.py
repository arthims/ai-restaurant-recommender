import streamlit as st
import pandas as pd
import sys
import os

# Ensure we can import from backend and llm folders
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import UserPreferences
from backend.filter_engine import load_data, filter_restaurants
from llm.recommender import generate_recommendations
from src.data_ingestion import ingest_data

# Ensure dataset exists before starting (crucial for Streamlit Cloud deployment)
data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'cleaned_zomato.parquet')
if not os.path.exists(data_path):
    st.info("First-time setup: Downloading dataset from Hugging Face... (This takes a minute)")
    ingest_data()
    st.success("Dataset downloaded!")

# Set up page config
st.set_page_config(page_title="AI Restaurant Recommender", page_icon="🍽️", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .restaurant-card {
        background-color: #1e1e2e;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #ff4b4b;
    }
    .restaurant-name {
        color: #ff4b4b;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .restaurant-explanation {
        font-size: 16px;
        color: #cccccc;
    }
    .rank-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🍽️ AI-Powered Restaurant Recommender")
st.markdown("Find the perfect place to eat based on your unique preferences! Powered by **Groq** and **LangChain**.")

# Sidebar for inputs
st.sidebar.header("🎯 Your Preferences")

# 1. Location Input
city_areas = {
    "Bangalore": ["Banashankari", "BTM", "Koramangala", "Indiranagar", "Jayanagar", "JP Nagar", "Marathahalli", "HSR", "Whitefield", "Malleshwaram"],
    "Chennai": ["T Nagar", "Adyar", "Velachery", "Anna Nagar", "Nungambakkam"],
    "Hyderabad": ["Banjara Hills", "Jubilee Hills", "Gachibowli", "Madhapur", "Kondapur"],
    "Delhi": ["Connaught Place", "Hauz Khas", "Rajouri Garden", "Saket", "Vasant Kunj"],
    "Mumbai": ["Bandra", "Andheri", "Colaba", "Juhu", "Powai"]
}

selected_city = st.sidebar.selectbox("🏙️ City", options=list(city_areas.keys()))

if selected_city != "Bangalore":
    st.sidebar.warning("Note: The current dataset only contains Zomato data for Bangalore! Searches in other cities will return 0 results.")

selected_area = st.sidebar.selectbox("📍 Area", options=city_areas[selected_city])
location = selected_area

# 2. Cuisine Input
# Standard cuisines found in the dataset
cuisines_list = ["North Indian", "South Indian", "Chinese", "Italian", "Mexican", "Cafe", "Desserts", "Continental", "Fast Food", "Biryani"]
selected_cuisines = st.sidebar.multiselect("🍕 Cuisine(s)", options=cuisines_list)

# 3. Budget Input (Cost for Two)
budget_range = st.sidebar.slider("💰 Budget (Cost for Two)", min_value=100, max_value=5000, value=(500, 2000), step=100)

# 4. Rating Input
min_rating = st.sidebar.slider("⭐ Minimum Rating", min_value=3.5, max_value=5.0, value=4.0, step=0.1)

# Submit Button
submit = st.sidebar.button("🔍 Find Restaurants", use_container_width=True)

# Main Page Content
if submit:
    if not location:
        st.warning("Please enter a Location/City to begin.")
    else:
        with st.spinner("Loading dataset and filtering candidates..."):
            try:
                df = load_data()
            except Exception as e:
                st.error(f"Error loading data: {e}")
                st.stop()
                
            # Build user preferences model
            prefs = UserPreferences(
                location=location,
                cuisines=selected_cuisines,
                min_budget=budget_range[0],
                max_budget=budget_range[1],
                min_rating=min_rating,
                additional_prefs=""
            )
            
            # Phase 2: Hard Filtering
            filtered_df = filter_restaurants(df, prefs, top_n=15)
            
        if filtered_df.empty:
            st.warning("No restaurants found matching your exact strict criteria. Try lowering the rating or expanding the budget.")
        else:
            with st.spinner(f"Found {len(filtered_df)} strong candidates. AI is reasoning and ranking the best options..."):
                # Prepare prefs dict for LLM context
                prefs_dict = prefs.model_dump()
                
                # Phase 3: AI Recommendations
                recommendations = generate_recommendations(filtered_df, prefs_dict)
                
            # Display results
            st.success("Analysis Complete!")
            
            if 'summary' in recommendations:
                st.markdown(f"### ✨ {recommendations['summary']}")
                
            if 'recommendations' in recommendations and recommendations['recommendations']:
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
                st.error("Failed to generate intelligent recommendations.")
                st.dataframe(filtered_df[['name', 'location', 'cuisines', 'rate', 'approx cost(for two people)']].head())
                
else:
    st.info("👈 Please enter your preferences in the sidebar and click **Find Restaurants**.")
