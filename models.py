from sqlalchemy import Column, Integer, String, Float

from database import Base


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

    complaint_type = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="Pending"
    )