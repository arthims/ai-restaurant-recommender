import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def generate_recommendations(df, user_prefs: dict):
    if df.empty:
        return {"summary": "No candidates found to recommend.", "recommendations": []}
        
    try:
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7)
        
        # Format the dataframe into a string of candidates
        candidates = df.to_dict(orient="records")
        candidates_str = json.dumps(candidates, indent=2, default=str)
        
        template = """
        You are an expert food critic and AI Restaurant Recommender.
        
        User Preferences:
        {prefs}
        
        Top Restaurant Candidates (pre-filtered):
        {candidates}
        
        Task: 
        Analyze the candidates and select the best 3-5 restaurants that match the user's preferences.
        Rank them and provide a brief, engaging explanation for each as to why they are a perfect fit.
        
        Output your response ONLY as a JSON object matching this schema:
        {{
            "summary": "A brief, welcoming intro sentence.",
            "recommendations": [
                {{
                    "rank": 1,
                    "name": "Restaurant Name",
                    "explanation": "Why it's a great choice..."
                }}
            ]
        }}
        """
        
        prompt = PromptTemplate(template=template, input_variables=["prefs", "candidates"])
        chain = prompt | llm | JsonOutputParser()
        
        result = chain.invoke({"prefs": json.dumps(user_prefs), "candidates": candidates_str})
        return result
        
    except Exception as e:
        print(f"LLM generation failed: {e}")
        # Fallback to simple top 3 extraction if API fails
        top_recs = []
        for i, row in enumerate(df.head(3).to_dict(orient="records")):
            name_val = row.get("name") or row.get("restaurant name") or "Unknown"
            top_recs.append({
                "rank": i + 1,
                "name": name_val,
                "explanation": "AI personalized explanations are currently unavailable. Selected based on highest ratings and votes."
            })
        return {
            "summary": "Here are the top matches based on your filters (AI personalized explanations are currently unavailable).",
            "recommendations": top_recs
        }
