from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.property import (
    PropertyOccupancyResponse, QuarterlyOccupancy,
    PropertyLeaseDurationResponse
)
from app import queries

app = FastAPI(title="Property Management API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Property Management API"}

@app.get("/property/{property_id}/occupancy", response_model=PropertyOccupancyResponse)
def get_property_occupancy(property_id: int, db: Session = Depends(get_db)):
    """Get quarterly occupancy rates for a specified property"""
    results = queries.get_quarterly_occupancy_rates(db, property_id)
    
    if not results:
        raise HTTPException(status_code=404, detail=f"Property with ID {property_id} not found")
    
    # Process the first row to get property details
    property_id = results[0][0]
    property_name = results[0][1]
    
    quarterly_rates = []
    for row in results:
        quarterly_rates.append(QuarterlyOccupancy(
            quarter=row[2],
            occupancy_rate=float(row[3])
        ))
    
    return PropertyOccupancyResponse(
        property_id=property_id,
        property_name=property_name,
        quarterly_rates=quarterly_rates
    )

@app.get("/property/{property_id}/lease-duration", response_model=PropertyLeaseDurationResponse)
def get_property_lease_duration(property_id: int, db: Session = Depends(get_db)):
    """Get average lease duration for a specified property"""
    results = queries.get_average_lease_duration(db, property_id)
    
    if not results:
        raise HTTPException(status_code=404, detail=f"Property with ID {property_id} not found")
    
    result = results[0]
    
    return PropertyLeaseDurationResponse(
        property_id=result[0],
        property_name=result[1],
        average_lease_duration_days=float(result[2])
    )

# For completeness, adding these endpoints to get the other analysis data
@app.get("/analysis/units-never-leased")
def get_units_never_leased(db: Session = Depends(get_db)):
    """Get units that have never been leased"""
    units = queries.find_units_never_leased(db)
    return {"count": len(units), "units": [{"unit_id": u.unit_id, "unit_number": u.unit_number} for u in units]}

@app.get("/analysis/units-with-future-leases")
def get_units_with_future_leases(db: Session = Depends(get_db)):
    """Get units with future leases"""
    units = queries.find_units_with_future_leases(db)
    return {"count": len(units), "units": [{"unit_id": u.unit_id, "unit_number": u.unit_number} for u in units]}

@app.get("/analysis/units-with-multiple-active-leases")
def get_units_with_multiple_active_leases(db: Session = Depends(get_db)):
    """Get units with multiple active leases"""
    units = queries.find_units_with_multiple_active_leases(db)
    return {"count": len(units), "units": [{"unit_id": u.unit_id, "unit_number": u.unit_number} for u in units]}

@app.get("/analysis/duplicate-leases")
def get_duplicate_leases(db: Session = Depends(get_db)):
    """Get duplicate leases"""
    leases = queries.find_duplicate_leases(db)
    return {"count": len(leases), "leases": [{"lease_id": l.lease_id, "unit_id": l.unit_id, "tenant_id": l.tenant_id} for l in leases]}