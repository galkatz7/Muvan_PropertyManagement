from sqlalchemy import text, func
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models import Property, Unit, Lease

def find_units_never_leased(db: Session):
    """Find and count units that have never been leased"""
    query = db.query(Unit).filter(
        ~Unit.unit_id.in_(db.query(Lease.unit_id).distinct())
    ).all()
    return query

def find_units_with_future_leases(db: Session):
    """Find all units with future leases"""
    today = date.today()
    query = db.query(Unit).join(Lease).filter(
        Lease.start_date > today
    ).distinct().all()
    return query

def find_units_with_multiple_active_leases(db: Session):
    """Find any units with multiple active leases as of today"""
    today = date.today()
    query = db.query(Unit).join(Lease).filter(
        Lease.start_date <= today,
        Lease.end_date >= today
    ).group_by(Unit.unit_id).having(
        func.count(Lease.lease_id) > 1
    ).all()
    return query

def find_duplicate_leases(db: Session):
    """Find duplicated leases without deleting them"""
    duplicate_lease_ids = db.query(Lease.lease_id)\
        .group_by(Lease.lease_id)\
        .having(func.count() > 1)\
        .scalar_subquery()  # Use scalar_subquery() instead of subquery()
    
    query = db.query(Lease)\
        .filter(Lease.lease_id.in_(duplicate_lease_ids))\
        .all()
    return query

def get_quarterly_occupancy_rates(db: Session, property_id: int = None):
    """
    Get quarterly occupancy rates for each property for the previous year
    If property_id is provided, filter by that property
    """
    today = date.today()
    last_year = today.replace(year=today.year - 1)
    
    # Raw SQL for complex query
    sql = text("""
    WITH quarters AS (
        SELECT 
            p.property_id, 
            p.property_name,
            CASE 
                WHEN strftime('%m', date('now', '-1 year')) <= '03' THEN 'Q1'
                WHEN strftime('%m', date('now', '-1 year')) <= '06' THEN 'Q2'
                WHEN strftime('%m', date('now', '-1 year')) <= '09' THEN 'Q3'
                ELSE 'Q4'
            END AS quarter,
            date('now', '-1 year') AS start_date,
            date('now') AS end_date
    FROM 
        properties p
    ),
    unit_counts AS (
        SELECT 
            p.property_id,
            COUNT(u.unit_id) AS total_units
        FROM 
            properties p
        JOIN 
            units u ON p.property_id = u.property_id
        GROUP BY 
            p.property_id
    ),
    occupied_units AS (
        SELECT 
            p.property_id,
            q.quarter,
            COUNT(DISTINCT u.unit_id) AS occupied
        FROM 
            properties p
        JOIN 
            units u ON p.property_id = u.property_id
        JOIN 
            leases l ON u.unit_id = l.unit_id
        JOIN 
            quarters q ON p.property_id = q.property_id
        WHERE 
            l.start_date <= q.end_date AND
            l.end_date >= q.start_date
        GROUP BY 
            p.property_id, q.quarter
    )
    SELECT 
        p.property_id,
        p.property_name,
        q.quarter,
        COALESCE(CAST(o.occupied AS FLOAT) / uc.total_units, 0) AS occupancy_rate
    FROM 
        properties p
    JOIN 
        quarters q ON p.property_id = q.property_id
    JOIN 
        unit_counts uc ON p.property_id = uc.property_id
    LEFT JOIN 
        occupied_units o ON p.property_id = o.property_id AND q.quarter = o.quarter
    """)
    
    if property_id:
        sql = text(f"{sql} WHERE p.property_id = :property_id")
        result = db.execute(sql, {"property_id": property_id}).fetchall()
    else:
        result = db.execute(sql).fetchall()
    
    return result

def get_average_lease_duration(db: Session, property_id: int = None):
    """
    Calculate the average lease duration (in days) per property
    If property_id is provided, filter by that property
    """
    query = db.query(
        Property.property_id,
        Property.property_name,
        func.avg(func.julianday(Lease.end_date) - func.julianday(Lease.start_date)).label('avg_duration')
    ).join(Unit, Property.property_id == Unit.property_id
    ).join(Lease, Unit.unit_id == Lease.unit_id)
    
    if property_id:
        query = query.filter(Property.property_id == property_id)
    
    result = query.group_by(Property.property_id).all()
    return result