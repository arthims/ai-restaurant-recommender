from pydantic import BaseModel, Field
from typing import List, Optional

class UserPreferences(BaseModel):
    location: Optional[str] = Field(None, description="City or specific location")
    cuisines: List[str] = Field(default_factory=list, description="List of preferred cuisines")
    min_budget: int = Field(0, description="Minimum cost for two")
    max_budget: int = Field(5000, description="Maximum cost for two")
    min_rating: float = Field(1.0, description="Minimum restaurant rating")
    additional_prefs: Optional[str] = Field(None, description="Any extra unstructured preferences like 'family-friendly'")
