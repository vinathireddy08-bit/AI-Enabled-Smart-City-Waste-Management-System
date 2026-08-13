from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


# =========================================================
# WASTE BIN MODEL
# =========================================================

class WasteBin(Base):

    __tablename__ = "waste_bins"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    bin_code = Column(
        String,
        unique=True,
        nullable=False
    )

    location = Column(
        String,
        nullable=False
    )

    latitude = Column(
        Float,
        nullable=False
    )

    longitude = Column(
        Float,
        nullable=False
    )

    fill_level = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String,
        nullable=True
    )


# =========================================================
# COMPLAINT MODEL
# =========================================================

class Complaint(Base):

    __tablename__ = "complaints"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    location = Column(
        String,
        nullable=False
    )

    # =====================================================
    # GPS LOCATION
    # =====================================================

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    # =====================================================
    # ASSOCIATED WASTE BIN
    # =====================================================

    bin_id = Column(
        Integer,
        nullable=True
    )

    complaint_type = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    # =====================================================
    # COMPLAINT STATUS
    # =====================================================

    status = Column(
        String,
        default="Pending"
    )

    # =====================================================
    # COLLECTION TIME
    # =====================================================

    collection_time = Column(
        DateTime,
        nullable=True
    )