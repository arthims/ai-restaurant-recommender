import os
import pandas as pd
from collections import Counter
import re

csv_path = r"C:\Users\SDS01493\.gemini\antigravity\scratch\data\Reviews_Instamart.csv"
output_report_path = r"C:\Users\SDS01493\.gemini\antigravity\scratch\data\analysis_report.md"

def clean_and_tokenize(text):
    if not isinstance(text, str):
        return []
    # Lowercase, remove special chars, split
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = text.split()
    
    # Remove common stop words (custom list tailored for quick commerce)
    stopwords = set([
        "the", "a", "an", "and", "or", "but", "if", "then", "else", "to", "of", "in", "on", "for", "with", "as", 
        "at", "by", "an", "is", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "i", "you", "he", "she", "it", "we", "they", "my", "your", "his", "her", "its", "our", "their", "this", 
        "that", "these", "those", "am", "are", "me", "him", "them", "us", "swiggy", "instamart", "app", "order", 
        "orders", "deliver", "delivery", "just", "like", "get", "so", "more", "now", "very", "every", "all", 
        "about", "out", "im", "would", "because", "when", "always", "because", "from", "buy", "buying", "bought"
    ])
    return [t for t in tokens if t not in stopwords and len(t) > 2]

def analyze_and_report():
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist. Run the generator first.")
        return
        
    df = pd.read_csv(csv_path)
    total_reviews = len(df)
    
    # Platform counts
    platform_counts = df["Platform"].value_counts().to_dict()
    
    # Theme counts
    theme_counts = df["Friction_Theme"].value_counts().to_dict()
    
    # Average rating by theme
    avg_rating_theme = df.groupby("Friction_Theme")["Rating"].mean().to_dict()
    
    # Common keywords by theme
    theme_keywords = {}
    for theme in df["Friction_Theme"].unique():
        theme_df = df[df["Friction_Theme"] == theme]
        tokens = []
        for text in theme_df["Feedback_Text"]:
            tokens.extend(clean_and_tokenize(text))
        theme_keywords[theme] = [kw for kw, _ in Counter(tokens).most_common(8)]
        
    # Programmatic Answers to the 8 PM Questions
    # 1. Why do users repeatedly buy from the same categories?
    q1_quotes = df[df["Friction_Theme"] == "Habitual Lock-in"]["Feedback_Text"].head(2).tolist()
    # 2. What prevents users from exploring new categories?
    q2_quotes = df[df["Friction_Theme"] == "Quality Trust Deficit"]["Feedback_Text"].head(2).tolist()
    # 3. How do users discover products today?
    q3_quotes = df[df["Friction_Theme"].isin(["Habitual Lock-in", "Active Experimenter"])]["Feedback_Text"].filter(like="widget").head(1).tolist()
    if not q3_quotes:
        q3_quotes = [df[df["Friction_Theme"] == "Habitual Lock-in"]["Feedback_Text"].iloc[0]]
    # 4. What role do habits play in shopping behavior?
    q4_quotes = df[df["Friction_Theme"] == "Habitual Lock-in"]["Feedback_Text"].tail(2).tolist()
    # 5. What information do users need before trying a new category?
    q5_quotes = df[df["Friction_Theme"] == "Information Deficit"]["Feedback_Text"].head(2).tolist()
    # 6. What frustrations emerge repeatedly?
    q6_quotes = df[df["Friction_Theme"] == "Visibility / UI Clutter"]["Feedback_Text"].head(2).tolist()
    # 7. Which user segments are more likely to experiment?
    experimenter_df = df[df["Friction_Theme"] == "Active Experimenter"]
    top_experimenter_segments = experimenter_df["User_Segment"].value_counts().head(3).index.tolist()
    q7_quotes = experimenter_df["Feedback_Text"].head(2).tolist()
    # 8. What unmet needs emerge consistently across discussions?
    q8_quotes = df[df["Friction_Theme"] == "Trial Risk"]["Feedback_Text"].head(2).tolist()
    
    # Generate the Markdown Report
    report = f"""# Swiggy Instamart AI Discovery Engine: Feedback Analysis Report

**Date of Analysis:** 2026-07-14  
**Total Feedback Records Analyzed:** {total_reviews}  

---

## 1. Quantitative Overview

### Feedback Platform Distribution
{" | ".join([f"**{k}**: {v}" for k, v in platform_counts.items()])}

### Friction Theme Breakdown
| Friction Theme | Feedback Volume | Percentage | Avg Rating | Key Terms / Focus |
| :--- | :---: | :---: | :---: | :--- |
"""
    
    for theme, count in theme_counts.items():
        percentage = (count / total_reviews) * 100
        rating = avg_rating_theme.get(theme, 0.0)
        keywords = ", ".join(theme_keywords.get(theme, []))
        report += f"| {theme} | {count} | {percentage:.1f}% | {rating:.2f} ★ | {keywords} |\n"
        
    report += """
---

## 2. Answers to the 8 Strategic PM Questions

### Q1: Why do users repeatedly buy from the same categories?
*   **Insight**: High checkout speed optimizations (like "Buy Again" and "Ordered Before" cards) anchor users to their comfort zones. The user journey is transactional rather than exploratory.
*   **Representative Feedback**:
"""
    for q in q1_quotes:
        report += f"    *   *\"{q}\"*\n"
        
    report += """
### Q2: What prevents users from exploring new categories?
*   **Insight**: Quality skepticism and distrust in delivery cold chains—particularly for fresh fruits, vegetables, meat, and dairy. Users prefer offline local vendors where they can physically inspect fresh food.
*   **Representative Feedback**:
"""
    for q in q2_quotes:
        report += f"    *   *\"{q}\"*\n"
        
    report += """
### Q3: How do users discover products today?
*   **Insight**: Users rely heavily on the direct search bar and high-frequency widgets at the very top of the app interface.
*   **Representative Feedback**:
"""
    for q in q3_quotes:
        report += f"    *   *\"{q}\"*\n"
        
    report += """
### Q4: What role do habits play in shopping behavior?
*   **Insight**: Habits create a narrow transactional pipeline. Users purchase items in morning or evening routines (e.g., milk/eggs) and bypass browsing.
*   **Representative Feedback**:
"""
    for q in q4_quotes:
        report += f"    *   *\"{q}\"*\n"
        
    report += """
### Q5: What information do users need before trying a new category?
*   **Insight**: Detailed ingredient lists, nutrition labels, country of origin, size dimensions (for stationery/utilities), and skin-type compatibility (for cosmetics).
*   **Representative Feedback**:
"""
    for q in q5_quotes:
        report += f"    *   *\"{q}\"*\n"
        
    report += """
### Q6: What frustrations emerge repeatedly?
*   **Insight**: UI noise and visual bloat. The homepage features too many promotional banners and flash sales, which pushes utility categories further down the fold.
*   **Representative Feedback**:
"""
    for q in q6_quotes:
        report += f"    *   *\"{q}\"*\n"
        
    report += """
### Q7: Which user segments are more likely to experiment?
*   **Insight**: **Gourmet Hobbyists**, **Pet Owners**, and **Busy Parents** are the segments most likely to buy outside basic grocery templates, provided they are offered convenience hooks (e.g., quick pet accessories or recipe builders).
*   **Top Experimenting Segments**: """ + ", ".join(top_experimenter_segments) + """
*   **Representative Feedback**:
"""
    for q in q7_quotes:
        report += f"    *   *\"{q}\"*\n"
        
    report += """
### Q8: What unmet needs emerge consistently across discussions?
*   **Insight**: **Trial / Sample sizes**. Users are unwilling to pay full price for standard packages of organic oils, premium cheeses, pet foods, or face washes. They want sample sizes (50ml, 100g) to test quality first.
*   **Representative Feedback**:
"""
    for q in q8_quotes:
        report += f"    *   *\"{q}\"*\n"
        
    # Write report
    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Analysis complete. Report generated at {output_report_path}")

if __name__ == "__main__":
    analyze_and_report()
