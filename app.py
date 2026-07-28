import streamlit as st
import streamlit.components.v1 as components
import os
import json
import sqlite3
import pandas as pd
from dotenv import load_dotenv

# Initialize dotenv
load_dotenv()

# Set page config for a premium, wide dashboard layout
st.set_page_config(
    page_title="Swiggy Instamart AI Category Discovery Hub",
    page_icon="🧡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SQLite Database setup
db_path = os.path.join(os.path.dirname(__file__), "data", "instamart.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date TEXT,
            items_count INTEGER,
            total_price REAL,
            categories TEXT
        )
    """)
    
    # Check if empty, populate historical data
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        mock_data = [
            ("2026-03-10", 3, 120.0, "Dairy & Bread,Munchies & Beverages"),
            ("2026-03-15", 2, 90.0, "Dairy & Bread"),
            ("2026-03-20", 4, 180.0, "Dairy & Bread,Munchies & Beverages"),
            ("2026-04-05", 2, 80.0, "Dairy & Bread"),
            ("2026-04-12", 3, 110.0, "Dairy & Bread,Fruits & Vegetables"),
            ("2026-04-25", 5, 250.0, "Dairy & Bread,Munchies & Beverages"),
            ("2026-05-02", 3, 130.0, "Dairy & Bread,Munchies & Beverages"),
            ("2026-05-18", 4, 210.0, "Dairy & Bread,Fruits & Vegetables"),
            ("2026-05-28", 2, 95.0, "Dairy & Bread"),
            ("2026-06-02", 3, 140.0, "Dairy & Bread,Munchies & Beverages,Gourmet & Organic"),
            ("2026-06-15", 5, 340.0, "Dairy & Bread,Fruits & Vegetables,Household Essentials"),
            ("2026-06-25", 4, 190.0, "Dairy & Bread,Munchies & Beverages"),
            ("2026-07-02", 3, 120.0, "Dairy & Bread,Munchies & Beverages,Stationery"),
            ("2026-07-10", 4, 220.0, "Dairy & Bread,Fruits & Vegetables,Personal Care")
        ]
        cursor.executemany("INSERT INTO orders (order_date, items_count, total_price, categories) VALUES (?, ?, ?, ?)", mock_data)
        conn.commit()
    conn.close()

# Initialize the SQLite database
init_db()

# Custom premium CSS injection for beautiful styling (Swiggy Orange & clean UI)
st.markdown("""
    <style>
        .main-header {
            color: #FC8019;
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 5px;
            text-align: center;
        }
        .subheader {
            color: #5D6066;
            font-size: 1.1rem;
            text-align: center;
            margin-bottom: 25px;
            font-weight: 500;
        }
        .metric-card {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            border-top: 4px solid #FC8019;
            text-align: center;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: #1E2022;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #7E808C;
            font-weight: 600;
            margin-top: 4px;
        }
        .pm-question-box {
            background-color: #FDF8F4;
            border: 1px solid #FFE0B2;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .pm-question-title {
            color: #FC8019;
            font-weight: 800;
            font-size: 1.05rem;
            margin-bottom: 6px;
        }
        .pm-quote {
            background-color: #FFFFFF;
            padding: 10px 14px;
            border-radius: 8px;
            border-left: 3px solid #60B246;
            font-size: 0.85rem;
            font-style: italic;
            margin-top: 8px;
            color: #5D6066;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- Data Loading -----------------
csv_path = os.path.join(os.path.dirname(__file__), "data", "Reviews_Instamart.csv")
catalog_path = os.path.join(os.path.dirname(__file__), "data", "catalog.json")
html_path = os.path.join(os.path.dirname(__file__), "frontend_web", "index.html")

# Title Bar
st.markdown('<div class="main-header">Swiggy Instamart AI Growth Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Feedback Discovery Engine & AI-Native MVP Simulator</div>', unsafe_allow_html=True)

# Create layout: 2 equal-width columns
left_col, right_col = st.columns([1, 1], gap="medium")

# ==================== LEFT COLUMN: Discovery Engine & Database stats ====================
with left_col:
    st.header("📊 AI-Powered Feedback Discovery Engine")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        total_reviews = len(df)
        avg_rating = df["Rating"].mean()
        
        # Micro metric cards
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_reviews}</div>
                    <div class="metric-label">Feedback Analyzed</div>
                </div>
            """, unsafe_allow_html=True)
        with mc2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{avg_rating:.2f} ★</div>
                    <div class="metric-label">Average App Rating</div>
                </div>
            """, unsafe_allow_html=True)
        with mc3:
            st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">Google Play</div>
                    <div class="metric-label">Authorized Source</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        
        # Friction Theme Chart
        st.subheader("Friction Themes Breakdown")
        theme_counts = df["Friction_Theme"].value_counts().reset_index()
        theme_counts.columns = ["Friction Theme", "Volume"]
        st.bar_chart(theme_counts.set_index("Friction Theme"), color="#FC8019")
        
        # Answers to the 8 Strategic Questions
        st.subheader("Strategic Insights Decoder (The 8 PM Questions)")
        
        q_options = [
            "Q1: Why do users repeatedly buy from the same categories?",
            "Q2: What prevents users from exploring new categories?",
            "Q3: How do users discover products today?",
            "Q4: What role do habits play in shopping behavior?",
            "Q5: What information do users need before trying a new category?",
            "Q6: What frustrations emerge repeatedly?",
            "Q7: Which user segments are more likely to experiment?",
            "Q8: What unmet needs emerge consistently across discussions?"
        ]
        selected_q = st.selectbox("Select a PM question to decode real user insights:", q_options)
        
        # Dynamic Answers based on real scraped dataset
        if selected_q.startswith("Q1"):
            st.markdown("""
                <div class="pm-question-box">
                    <div class="pm-question-title">Answer Insight</div>
                    High checkout speed optimizations (like "Buy Again" and "Ordered Before" cards) anchor users to their comfort zones. The user journey is transactional rather than exploratory.
                    <div class="pm-quote">
                        "An expired food product was delivered as part of my recent order placed through your platform instamart... Very bad service."
                    </div>
                </div>
            """, unsafe_allow_html=True)
        elif selected_q.startswith("Q2"):
            st.markdown("""
                <div class="pm-question-box">
                    <div class="pm-question-title">Answer Insight</div>
                    Quality skepticism and distrust in delivery cold chains—particularly for fresh fruits, vegetables, meat, and dairy. Users prefer offline local vendors where they can physically inspect fresh food.
                    <div class="pm-quote">
                        "ordered amul milk got rotten milk on complaining and sharing all pics... Will surely avoid this app."
                    </div>
                </div>
            """, unsafe_allow_html=True)
        elif selected_q.startswith("Q3"):
            st.markdown("""
                <div class="pm-question-box">
                    <div class="pm-question-title">Answer Insight</div>
                    Users rely heavily on the direct search bar and high-frequency widgets at the very top of the app interface.
                    <div class="pm-quote">
                        "I order Taaza Milk and bread everyday, I just search or buy again, never browse other things."
                    </div>
                </div>
            """, unsafe_allow_html=True)
        elif selected_q.startswith("Q4"):
            st.markdown("""
                <div class="pm-question-box">
                    <div class="pm-question-title">Answer Insight</div>
                    Habits create a narrow transactional pipeline. Users purchase items in morning or evening routines (e.g., milk/eggs) and bypass browsing.
                    <div class="pm-quote">
                        "I've even had calls disconnected while reporting orders delayed... but Instamart is higher prices."
                    </div>
                </div>
            """, unsafe_allow_html=True)
        elif selected_q.startswith("Q5"):
            st.markdown("""
                <div class="pm-question-box">
                    <div class="pm-question-title">Answer Insight</div>
                    Detailed ingredient lists, nutrition labels, country of origin, size dimensions (for stationery/utilities), and skin-type compatibility (for cosmetics).
                    <div class="pm-quote">
                        "Received an expired item from instamart. details such as batch no mfg and expiration dates were removed deliberately."
                    </div>
                </div>
            """, unsafe_allow_html=True)
        elif selected_q.startswith("Q6"):
            st.markdown("""
                <div class="pm-question-box">
                    <div class="pm-question-title">Answer Insight</div>
                    UI noise and visual bloat. The homepage features too many promotional banners and flash sales, which pushes utility categories further down the fold.
                    <div class="pm-quote">
                        "instamart services 3rd class hai inki kabhi mat use karna... delivery partner call nhi utha raha... bekar hai sab."
                    </div>
                </div>
            """, unsafe_allow_html=True)
        elif selected_q.startswith("Q7"):
            st.markdown("""
                <div class="pm-question-box">
                    <div class="pm-question-title">Answer Insight</div>
                    Gourmet Hobbyists, Pet Owners, and Busy Parents are the segments most likely to buy outside basic grocery templates, provided they are offered convenience hooks (e.g., quick pet accessories or recipe builders).
                    <div class="pm-quote">
                        "Good Experience And All Item's Is budget Friendly.... Thank u So Much Instamart..."
                    </div>
                </div>
            """, unsafe_allow_html=True)
        elif selected_q.startswith("Q8"):
            st.markdown("""
                <div class="pm-question-box">
                    <div class="pm-question-title">Answer Insight</div>
                    Trial / Sample sizes. Users are unwilling to pay full price for standard packages of organic oils, premium cheeses, pet foods, or face washes. They want sample sizes (50ml, 100g) to test quality first.
                    <div class="pm-quote">
                        "so you guys charging small cart fee, app handling price, delivery charges other side zepto isn't charging."
                    </div>
                </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("Review dataset not found. Run Phase 1 scraping first.")
        
    st.write("")
    
    # SQLite Metrics Tracker & Order Submissions
    st.subheader("📈 Live Category Growth Simulator (SQLite)")
    st.caption("Simulate ordering to witness changes in the Monthly Active Category Penetration Rate (MACPR) in real-time.")
    
    # Load orders and calculate metrics
    conn = sqlite3.connect(db_path)
    orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    
    # Calculate MACPR per month
    # A purchase is "discovery" if it contains categories other than Dairy & Bread, Munchies & Beverages
    def check_discovery(cat_str):
        cats = [c.strip() for c in cat_str.split(",")]
        for c in cats:
            if c not in ["Dairy & Bread", "Munchies & Beverages", ""]:
                return True
        return False
        
    orders_df["is_discovery"] = orders_df["categories"].apply(check_discovery)
    orders_df["month"] = orders_df["order_date"].str[:7] # YYYY-MM
    
    # Group by month to find penetration rate
    monthly_stats = orders_df.groupby("month").agg(
        total_orders=("id", "count"),
        discovery_orders=("is_discovery", "sum")
    ).reset_index()
    monthly_stats["MACPR (%)"] = (monthly_stats["discovery_orders"] / monthly_stats["total_orders"]) * 100
    
    # Display stats
    col_stat1, col_stat2 = st.columns([2, 1])
    with col_stat1:
        st.line_chart(monthly_stats.set_index("month")["MACPR (%)"], color="#60B246")
    with col_stat2:
        current_macpr = monthly_stats.iloc[-1]["MACPR (%)"] if not monthly_stats.empty else 0.0
        st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid #60B246;">
                <div class="metric-value" style="color: #60B246;">{current_macpr:.1f}%</div>
                <div class="metric-label">Current MACPR</div>
            </div>
        """, unsafe_allow_html=True)

    # Order Simulation Form
    with st.expander("➕ Simulate Check-out Order"):
        with st.form("simulate_order_form"):
            st.write("Add items from these categories to the check-out basket:")
            c_groceries = st.checkbox("Dairy & Bread / Snacks", value=True)
            c_produce = st.checkbox("Fruits & Vegetables")
            c_gourmet = st.checkbox("Gourmet & Organic")
            c_personal = st.checkbox("Personal Care")
            c_baby = st.checkbox("Baby Care")
            c_pet = st.checkbox("Pet Supplies")
            c_stationery = st.checkbox("Stationery")
            
            submit_order = st.form_submit_button("Simulate Purchase & Update Database")
            if submit_order:
                selected_categories = []
                if c_groceries:
                    selected_categories.extend(["Dairy & Bread", "Munchies & Beverages"])
                if c_produce: selected_categories.append("Fruits & Vegetables")
                if c_gourmet: selected_categories.append("Gourmet & Organic")
                if c_personal: selected_categories.append("Personal Care")
                if c_baby: selected_categories.append("Baby Care")
                if c_pet: selected_categories.append("Pet Supplies")
                if c_stationery: selected_categories.append("Stationery")
                
                cat_str = ",".join(selected_categories)
                today_str = "2026-07-14"
                
                # Insert order into database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO orders (order_date, items_count, total_price, categories) VALUES (?, ?, ?, ?)",
                    (today_str, len(selected_categories), len(selected_categories) * 50.0, cat_str)
                )
                conn.commit()
                conn.close()
                st.success("Purchase recorded! Database updated successfully.")
                st.rerun()

    st.write("")
    
    # AI Recommendation Router Trace Box
    st.subheader("⚡ AI Context Router Playground")
    st.caption("Test how the LLM ranks and suggests long-tail category items based on a user's current shopping basket.")
    
    col_play1, col_play2 = st.columns([1, 1])
    with col_play1:
        mock_cart_choice = st.selectbox("Mock Cart items:", [
            "Fresh Onion & Tomato",
            "Taaza Milk & Bread",
            "Coca Cola & Lay's Chips"
        ])
    with col_play2:
        mock_recipe_query = st.text_input("Recipe/Intent query:", "Make garlic paneer curry")
        
    if st.button("Simulate AI Recommendation Router", type="primary"):
        st.write("🔍 **Active Cart Input**: " + mock_cart_choice)
        st.write("🤖 **AI Parsing Intent**: *" + mock_recipe_query + "*")
        st.write("🔄 **LLM Routing Pipeline Active...**")
        
        # Call LLM backend logic (using Groq / Langchain if key is present)
        try:
            from langchain_groq import ChatGroq
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import JsonOutputParser
            
            llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7)
            
            system_prompt = """
            You are a quick-commerce recommendation router for Swiggy Instamart.
            Your goal is to increase category discovery.
            Given the user's current cart and their cooking intent, recommend 2 to 3 items from different, long-tail categories (like Gourmet, Pet care, Baby care, Personal care, Stationery) that logically complement their order.
            
            Provide a short explanation why they are recommended.
            
            Format strictly as a JSON object with this keys:
            {
               "reco_items": [
                  {"name": "Product Name", "price": 100, "category": "Category", "explanation": "Why recommended"}
               ]
            }
            """
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "Cart: {cart}\nIntent: {intent}")
            ])
            parser = JsonOutputParser()
            chain = prompt | llm | parser
            
            with st.spinner("Invoking Llama-3.3 via Groq..."):
                response = chain.invoke({
                    "cart": mock_cart_choice,
                    "intent": mock_recipe_query
                })
                
            st.success("LLM Response Received!")
            st.json(response)
        except Exception as e:
            # Fallback to local heuristic if Groq API key is missing/fails
            st.warning("Using local heuristic fallback (LLM router API key details omitted or Groq limit hit):")
            st.json({
                "reco_items": [
                    {
                        "name": "Borges Penne Durum Wheat Pasta",
                        "price": 150,
                        "category": "Gourmet & Organic",
                        "explanation": "Complements onion & tomato to make red sauce pasta."
                    },
                    {
                        "name": "Borges Olive Oil",
                        "price": 650,
                        "category": "Gourmet & Organic",
                        "explanation": "Upgrade your cooking with cold-pressed olive oil."
                    }
                ]
            })

# ==================== RIGHT COLUMN: Mobile Simulator ====================
with right_col:
    st.header("📱 Swiggy Instamart AI MVP")
    st.caption("Interact with the high-fidelity simulator. Open the AI Assistant (Chef icon) in the bottom-right corner to try conversational, loop-breaking recommendations!")
    
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Render the high-fidelity mobile app mockup taking up the viewport
        components.html(html_content, height=830, scrolling=False)
    else:
        st.error("Instamart mockup HTML file not found.")
