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
        .having(func.count(Lease.lease_id) > 1)\
        .scalar_subquery()
    
    query = db.query(Lease)\
        .filter(Lease.lease_id.in_(duplicate_lease_ids))\
        .all()
    return query

def get_quarterly_occupancy_rates(db: Session, property_id: int = None):
    """
    Get quarterly occupancy rates for each property for the previous year.
    If property_id is provided, filter by that property.
    """
    sql = text("""
WITH quarters AS (
    SELECT 
        p.property_id,
        p.property_name,
        strftime('%Y', q.start_date) || '-Q' || q.quarter AS quarter,
        q.start_date,
        q.end_date
    FROM properties p
    JOIN (
        SELECT 
            1 AS quarter,
            date(strftime('%Y-01-01', 'now', '-1 year')) AS start_date,
            date(strftime('%Y-03-31', 'now', '-1 year')) AS end_date
        UNION ALL
        SELECT 
            2,
            date(strftime('%Y-04-01', 'now', '-1 year')) AS start_date,
            date(strftime('%Y-06-30', 'now', '-1 year')) AS end_date
        UNION ALL
        SELECT 
            3,
            date(strftime('%Y-07-01', 'now', '-1 year')) AS start_date,
            date(strftime('%Y-09-30', 'now', '-1 year')) AS end_date
        UNION ALL
        SELECT 
            4,
            date(strftime('%Y-10-01', 'now', '-1 year')) AS start_date,
            date(strftime('%Y-12-31', 'now', '-1 year')) AS end_date
    ) q ON 1 = 1
),
unit_counts AS (
    SELECT 
        property_id,
        COUNT(*) AS total_units
    FROM units
    GROUP BY property_id
),
occupied_units AS (
    SELECT 
        p.property_id,
        q.quarter,
        COUNT(DISTINCT u.unit_id) AS occupied
    FROM leases l
    JOIN units u ON l.unit_id = u.unit_id
    JOIN properties p ON u.property_id = p.property_id
    JOIN quarters q ON p.property_id = q.property_id
    WHERE l.start_date <= q.end_date AND l.end_date >= q.start_date
    GROUP BY p.property_id, q.quarter
)
SELECT 
    q.property_id,
    q.property_name,
    q.quarter,
    COALESCE(1.0 * o.occupied / uc.total_units, 0) AS occupancy_rate
FROM quarters q
JOIN unit_counts uc ON q.property_id = uc.property_id
LEFT JOIN occupied_units o ON q.property_id = o.property_id AND q.quarter = o.quarter
""" + ("""
WHERE q.property_id = :property_id
""" if property_id else "") + """
ORDER BY q.property_id, q.quarter
""")

    params = {"property_id": property_id} if property_id else {}
    result = db.execute(sql, params).fetchall()
    return result


def get_average_lease_duration(db: Session, property_id: int = None):
    """
    Calculate the average lease duration (in days) per property.
    If property_id is provided, filter by that property.
    """
    query = db.query(
        Property.property_id,
        Property.property_name,
        func.round(func.avg(func.julianday(Lease.end_date) - func.julianday(Lease.start_date)), 2).label('avg_duration')
    ).join(Unit, Property.property_id == Unit.property_id
    ).join(Lease, Unit.unit_id == Lease.unit_id)
    
    if property_id:
        query = query.filter(Property.property_id == property_id)
    
    result = query.group_by(Property.property_id, Property.property_name).all()
    return result
