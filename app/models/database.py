from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Property(Base):
    __tablename__ = "properties"
    
    property_id = Column(Integer, primary_key=True)
    property_name = Column(String)
    address = Column(String)
    units = relationship("Unit", back_populates="property")

class Unit(Base):
    __tablename__ = "units"
    
    unit_id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"))
    unit_number = Column(String)
    size = Column(Integer, nullable=True)
    type = Column(String, nullable=True)
    property = relationship("Property", back_populates="units")
    leases = relationship("Lease", back_populates="unit")

class Lease(Base):
    __tablename__ = "leases"
    
    lease_id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey("units.unit_id"))
    tenant_id = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    unit = relationship("Unit", back_populates="leases") 