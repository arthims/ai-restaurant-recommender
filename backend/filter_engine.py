import pandas as pd
import os
from .models import UserPreferences

def load_data() -> pd.DataFrame:
    """Loads the preprocessed parquet dataset."""
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cleaned_zomato.parquet')
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}. Please run data ingestion first.")
    df = pd.read_parquet(file_path)
    
    # Fix rate column which might be like '4.1/5' or 'NEW'
    if 'rate' in df.columns:
        df['rate_float'] = df['rate'].astype(str).str.split('/').str[0].replace(['NEW', '-'], '0')
        df['rate_float'] = pd.to_numeric(df['rate_float'], errors='coerce').fillna(0.0)
    
    # Fix cost column
    cost_col_name = 'approx_cost(for two people)'
    if cost_col_name in df.columns:
        df['cost_float'] = df[cost_col_name].astype(str).str.replace(',', '', regex=False)
        df['cost_float'] = pd.to_numeric(df['cost_float'], errors='coerce').fillna(0.0)
        
    return df

def filter_restaurants(df: pd.DataFrame, prefs: UserPreferences, top_n: int = 15) -> pd.DataFrame:
    """
    Applies hard constraints to narrow down the massive dataset to a Top N candidates
    that will be passed to the LLM.
    """
    filtered = df.copy()

    # 1. Filter by Location
    if prefs.location:
        loc = prefs.location.lower().strip()
        loc_col = 'location' if 'location' in filtered.columns else 'city' if 'city' in filtered.columns else None
        if loc_col:
            # Case insensitive substring match
            loc_mask = filtered[loc_col].str.contains(loc, na=False, case=False)
            filtered = filtered[loc_mask]
    
    # 2. Filter by Budget (Cost for two)
    if 'cost_float' in filtered.columns:
        filtered = filtered[(filtered['cost_float'] >= prefs.min_budget) & (filtered['cost_float'] <= prefs.max_budget)]

    # 3. Filter by Rating
    if 'rate_float' in filtered.columns:
        filtered = filtered[filtered['rate_float'] >= prefs.min_rating]

    # 4. Filter by Cuisine
    if prefs.cuisines:
        cuisine_col = 'cuisines' if 'cuisines' in filtered.columns else 'cuisine' if 'cuisine' in filtered.columns else None
        if cuisine_col:
            masks = [filtered[cuisine_col].str.contains(c.lower().strip(), na=False, case=False) for c in prefs.cuisines]
            combined_mask = masks[0]
            for m in masks[1:]:
                combined_mask = combined_mask | m
            filtered = filtered[combined_mask]

    # 5. Sort to find the "Best" Top N candidates
    sort_cols = []
    ascending_flags = []
    
    if 'rate_float' in filtered.columns:
        sort_cols.append('rate_float')
        ascending_flags.append(False)
        
    votes_col = 'votes' if 'votes' in filtered.columns else None
    if votes_col:
        filtered[votes_col] = pd.to_numeric(filtered[votes_col], errors='coerce').fillna(0)
        sort_cols.append(votes_col)
        ascending_flags.append(False)
        
    if sort_cols:
        filtered = filtered.sort_values(by=sort_cols, ascending=ascending_flags)
        
    return filtered.head(top_n)
