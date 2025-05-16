from pydantic import BaseModel
from typing import List
from datetime import date

class QuarterlyOccupancy(BaseModel):
    quarter: str
    occupancy_rate: float

class PropertyOccupancyResponse(BaseModel):
    property_id: int
    property_name: str
    quarterly_rates: List[QuarterlyOccupancy]

class PropertyLeaseDurationResponse(BaseModel):
    property_id: int
    property_name: str
    average_lease_duration_days: float 