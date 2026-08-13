from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy import text

from pydantic import BaseModel

from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

from database import engine, SessionLocal
from models import Base, WasteBin, Complaint

from ai.prediction import predict_fill_level


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# DATABASE MIGRATION
# =========================================================
# Render already has an older complaints table.
# SQLAlchemy create_all() does NOT add new columns to an
# existing table.
#
# This migration safely adds missing columns without
# deleting existing bins or complaints.
# =========================================================

def migrate_complaints_table():

    try:

        with engine.begin() as connection:

            # Get existing columns
            result = connection.execute(
                text("PRAGMA table_info(complaints)")
            )

            existing_columns = {
                row[1]
                for row in result
            }

            print(
                "Existing Complaint columns:",
                existing_columns
            )

            # Required columns
            required_columns = {

                "latitude":
                    "ALTER TABLE complaints ADD COLUMN latitude FLOAT",

                "longitude":
                    "ALTER TABLE complaints ADD COLUMN longitude FLOAT",

                "bin_id":
                    "ALTER TABLE complaints ADD COLUMN bin_id INTEGER",

                "collection_time":
                    "ALTER TABLE complaints ADD COLUMN collection_time DATETIME"

            }

            # Add only missing columns
            for column_name, sql in required_columns.items():

                if column_name not in existing_columns:

                    print(
                        f"Adding missing column: {column_name}"
                    )

                    connection.execute(
                        text(sql)
                    )

            print(
                "Complaint table migration completed."
            )

    except Exception as e:

        print(
            "Complaint table migration error:",
            str(e)
        )

        raise


# Run migration immediately after create_all()
migrate_complaints_table()


# =========================================================
# INSERT SAMPLE DATA
# =========================================================

db = SessionLocal()

try:

    if db.query(WasteBin).count() == 0:

        bins = [

            WasteBin(
                bin_code="BIN001",
                location="Market Road",
                latitude=17.3850,
                longitude=78.4867,
                fill_level=90,
                status="FULL"
            ),

            WasteBin(
                bin_code="BIN002",
                location="City Park",
                latitude=17.3902,
                longitude=78.4912,
                fill_level=55,
                status="MEDIUM"
            ),

            WasteBin(
                bin_code="BIN003",
                location="Bus Stand",
                latitude=17.3815,
                longitude=78.4804,
                fill_level=20,
                status="EMPTY"
            )
        ]

        db.add_all(bins)

        db.commit()

finally:

    db.close()


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="AI-Enabled Smart City Waste Management System V2"
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================================================
# TEMPLATES
# =========================================================

templates = Jinja2Templates(
    directory="templates"
)


# =========================================================
# DATABASE DEPENDENCY
# =========================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# =========================================================
# HOME PAGE
# =========================================================

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# =========================================================
# GET ALL WASTE BINS
# =========================================================

@app.get("/bins")
def get_bins(
    db: Session = Depends(get_db)
):

    bins = db.query(WasteBin).all()

    result = []

    for bin in bins:

        # Only active complaints
        active_complaint = db.query(Complaint).filter(
            Complaint.bin_id == bin.id,
            Complaint.status.notin_([
                "COLLECTED",
                "KEPT"
            ])
        ).first()

        result.append({

            "id": bin.id,

            "bin_code": bin.bin_code,

            "location": bin.location,

            "latitude": bin.latitude,

            "longitude": bin.longitude,

            "fill_level": bin.fill_level,

            "status": bin.status,

            "complaint_raised": (
                True
                if active_complaint
                else False
            ),

            "complaint_id": (
                active_complaint.id
                if active_complaint
                else None
            ),

            "complaint_type": (
                active_complaint.complaint_type
                if active_complaint
                else None
            )

        })

    return result


# =========================================================
# API BINS FOR MAP / DASHBOARD
# =========================================================

@app.get("/api/bins")
def api_bins(
    db: Session = Depends(get_db)
):

    bins = db.query(WasteBin).all()

    result = []

    for bin in bins:

        result.append({

            "id": bin.id,

            "bin_code": bin.bin_code,

            "location": bin.location,

            "latitude": bin.latitude,

            "longitude": bin.longitude,

            "fill_level": bin.fill_level,

            "status": bin.status

        })

    return result


# =========================================================
# CREATE NEW WASTE BIN
# =========================================================

@app.post("/bins")
def create_bin(

    bin_code: str,

    location: str,

    fill_level: int,

    status: str = "",

    db: Session = Depends(get_db)

):

    # Duplicate check
    existing_bin = db.query(WasteBin).filter(
        WasteBin.bin_code == bin_code
    ).first()

    if existing_bin:

        raise HTTPException(
            status_code=400,
            detail="Bin code already exists"
        )


    # Validate fill level
    if fill_level < 0 or fill_level > 100:

        raise HTTPException(
            status_code=400,
            detail="Fill level must be between 0 and 100"
        )


    # Automatic status
    if fill_level >= 80:

        status = "FULL"

    elif fill_level >= 40:

        status = "MEDIUM"

    else:

        status = "EMPTY"


    # Location coordinates
    location_coordinates = {

        "market road": (17.3855, 78.4869),

        "city park": (17.3900, 78.4800),

        "bus stand": (17.3755, 78.4740),

        "railway station": (17.3850, 78.4870),

        "main street": (17.3920, 78.4820),

        "municipal office": (17.3765, 78.4890),

        "school road": (17.3980, 78.4900),

        "hospital road": (17.3810, 78.4950),

        "shopping mall": (17.3930, 78.4770),

        "shopping mal": (17.3930, 78.4770),

        "temple road": (17.3870, 78.4780),

        "industrial area": (17.3650, 78.5000),

        "airport road": (17.2400, 78.4290)
    }


    location_key = location.strip().lower()


    if location_key in location_coordinates:

        latitude, longitude = location_coordinates[
            location_key
        ]

    else:

        latitude = 17.3850
        longitude = 78.4867


    # Create bin
    new_bin = WasteBin(

        bin_code=bin_code,

        location=location,

        latitude=latitude,

        longitude=longitude,

        fill_level=fill_level,

        status=status

    )

    db.add(new_bin)

    db.commit()

    db.refresh(new_bin)


    return {

        "message": "Bin added successfully",

        "bin": {

            "id": new_bin.id,

            "bin_code": new_bin.bin_code,

            "location": new_bin.location,

            "latitude": new_bin.latitude,

            "longitude": new_bin.longitude,

            "fill_level": new_bin.fill_level,

            "status": new_bin.status

        }

    }


# =========================================================
# UPDATE EXISTING BIN LOCATIONS
# =========================================================

@app.post("/bins/update-existing-locations")
def update_existing_bin_locations(

    db: Session = Depends(get_db)

):

    location_coordinates = {

        "market road": (17.3855, 78.4869),

        "city park": (17.3900, 78.4800),

        "bus stand": (17.3755, 78.4740),

        "railway station": (17.3850, 78.4870),

        "main street": (17.3920, 78.4820),

        "municipal office": (17.3765, 78.4890),

        "school road": (17.3980, 78.4900),

        "hospital road": (17.3810, 78.4950),

        "shopping mall": (17.3930, 78.4770),

        "shopping mal": (17.3930, 78.4770),

        "temple road": (17.3870, 78.4780),

        "industrial area": (17.3650, 78.5000),

        "airport road": (17.2400, 78.4290)

    }


    bins = db.query(WasteBin).all()

    updated = []


    for bin in bins:

        location_key = bin.location.strip().lower()


        if location_key in location_coordinates:

            latitude, longitude = location_coordinates[
                location_key
            ]

            bin.latitude = latitude

            bin.longitude = longitude


            updated.append({

                "bin_code": bin.bin_code,

                "location": bin.location,

                "latitude": latitude,

                "longitude": longitude

            })


    db.commit()


    return {

        "message": "Existing bin locations updated successfully",

        "updated_bins": updated

    }


# =========================================================
# DASHBOARD PAGE
# =========================================================

@app.get("/dashboard")
def dashboard(

    request: Request,

    db: Session = Depends(get_db)

):

    bins = db.query(WasteBin).all()

    total_bins = len(bins)

    full_bins = 0

    medium_bins = 0

    empty_bins = 0

    total_fill = 0


    for bin in bins:

        fill = bin.fill_level or 0

        total_fill += fill


        if fill >= 80:

            full_bins += 1

        elif fill >= 40:

            medium_bins += 1

        else:

            empty_bins += 1


    average_fill = 0


    if total_bins > 0:

        average_fill = round(
            total_fill / total_bins,
            2
        )


    return templates.TemplateResponse(

        request=request,

        name="dashboard.html",

        context={

            "total_bins": total_bins,

            "full_bins": full_bins,

            "medium_bins": medium_bins,

            "empty_bins": empty_bins,

            "average_fill": average_fill

        }

    )


# =========================================================
# DASHBOARD DATA API
# =========================================================

@app.get("/dashboard-data")
def dashboard_data(
    db: Session = Depends(get_db)
):

    # =====================================================
    # GET ALL BINS
    # =====================================================

    bins = db.query(WasteBin).all()

    total_bins = len(bins)

    full_bins = 0
    medium_bins = 0
    empty_bins = 0

    total_fill = 0

    status_count = {
        "FULL": 0,
        "MEDIUM": 0,
        "EMPTY": 0
    }

    # =====================================================
    # CALCULATE BIN STATISTICS
    # =====================================================

    for bin in bins:

        fill = bin.fill_level or 0

        total_fill += fill

        if fill >= 80:

            full_bins += 1
            status_count["FULL"] += 1

        elif fill >= 40:

            medium_bins += 1
            status_count["MEDIUM"] += 1

        else:

            empty_bins += 1
            status_count["EMPTY"] += 1

    # =====================================================
    # AVERAGE FILL
    # =====================================================

    if total_bins > 0:

        average_fill = round(
            total_fill / total_bins,
            2
        )

    else:

        average_fill = 0

    # =====================================================
    # HIGH FILL BINS
    # Dashboard threshold = 75%
    # =====================================================

    high_fill_bins = sorted(

        [
            bin

            for bin in bins

            if (bin.fill_level or 0) >= 75
        ],

        key=lambda x: x.fill_level or 0,

        reverse=True
    )

    top_labels = []

    top_fill_levels = []

    for bin in high_fill_bins:

        top_labels.append(
            bin.bin_code
        )

        top_fill_levels.append(
            bin.fill_level or 0
        )

    # =====================================================
    # GET ALL COMPLAINTS
    # =====================================================

    all_complaints = db.query(
        Complaint
    ).order_by(
        Complaint.id.desc()
    ).all()

    # =====================================================
    # ACTIVE COMPLAINTS
    # =====================================================

    active_complaints_list = [

        complaint

        for complaint in all_complaints

        if complaint.status not in [
            "COLLECTED",
            "KEPT"
        ]

    ]

    active_complaints = len(
        active_complaints_list
    )

    total_complaints = len(
        all_complaints
    )

    # =====================================================
    # COMPLAINT DATA
    # =====================================================

    complaints = []

    for complaint in active_complaints_list:

        bin_data = None

        if complaint.bin_id:

            bin_data = db.query(
                WasteBin
            ).filter(
                WasteBin.id == complaint.bin_id
            ).first()

        complaints.append({

            "id":
                complaint.id,

            "name":
                complaint.name,

            "location":
                complaint.location,

            "latitude":
                complaint.latitude,

            "longitude":
                complaint.longitude,

            "bin_id":
                complaint.bin_id,

            "bin_code": (

                bin_data.bin_code

                if bin_data

                else "N/A"

            ),

            "complaint_type":
                complaint.complaint_type,

            "description":
                complaint.description,

            "status":
                complaint.status,

            "collection_time": (

                complaint.collection_time.isoformat()

                if complaint.collection_time

                else None

            )

        })

    # =====================================================
    # ALERT COUNT
    # BINS >= 75%
    # =====================================================

    alert_count = len(
        high_fill_bins
    )

    # =====================================================
    # RETURN DATA
    # =====================================================

    return {

        "total_bins":
            total_bins,

        "full_bins":
            full_bins,

        "medium_bins":
            medium_bins,

        "empty_bins":
            empty_bins,

        "average_fill":
            average_fill,

        "top_labels":
            top_labels,

        "top_fill_levels":
            top_fill_levels,

        "status":
            status_count,

        "alert_count":
            alert_count,

        "active_complaints":
            active_complaints,

        "total_complaints":
            total_complaints,

        # Kept for compatibility
        "complaint_count":
            active_complaints,

        "complaints":
            complaints

    }
# =========================================================
# MAP PAGE
# =========================================================

@app.get("/map")
def map_page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="map.html",

        context={}

    )


# =========================================================
# COMPLAINT PAGE
# =========================================================

@app.get("/complaints-page")
def complaints_page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="complaints.html",

        context={}

    )


# =========================================================
# AI PREDICTION PAGE
# =========================================================

@app.get("/prediction")
def prediction_page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="ai_prediction.html",

        context={}

    )


# =========================================================
# BIN MANAGEMENT PAGE
# =========================================================

@app.get("/bins-page")
def bins_page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="waste_bins.html",

        context={}

    )


# =========================================================
# AI PREDICTION - GET ALL BINS
# =========================================================

@app.get("/ai/bins")
def ai_bins(

    db: Session = Depends(get_db)

):

    bins = db.query(
        WasteBin
    ).order_by(
        WasteBin.id
    ).all()


    return [

        {

            "id": bin.id,

            "bin_code": bin.bin_code,

            "location": bin.location,

            "fill_level": bin.fill_level,

            "status": bin.status

        }

        for bin in bins

    ]


# =========================================================
# AI PREDICTION
# =========================================================

@app.get("/ai/predict/{bin_id}")
def ai_prediction(

    bin_id: int,

    db: Session = Depends(get_db)

):

    bin_data = db.query(
        WasteBin
    ).filter(

        WasteBin.id == bin_id

    ).first()


    if bin_data is None:

        raise HTTPException(

            status_code=404,

            detail="Bin not found"

        )


    predicted = predict_fill_level(
        bin_data.fill_level
    )


    if predicted >= 80:

        decision = "Collection Required 🚛"

    elif predicted >= 50:

        decision = "Monitor 🟠"

    else:

        decision = "Normal 🟢"


    return {

        "bin_id":
            bin_data.id,

        "location":
            bin_data.location,

        "current_fill":
            bin_data.fill_level,

        "predicted_fill":
            predicted,

        "decision":
            decision

    }


# =========================================================
# COMPLAINT SCHEMA
# =========================================================

class ComplaintCreate(BaseModel):

    name: str

    location: str

    latitude: float

    longitude: float

    complaint_type: str

    description: str


# =========================================================
# DISTANCE CALCULATION
# =========================================================

def calculate_distance(

    lat1,

    lon1,

    lat2,

    lon2

):

    R = 6371.0


    lat1 = radians(lat1)

    lon1 = radians(lon1)

    lat2 = radians(lat2)

    lon2 = radians(lon2)


    dlat = lat2 - lat1

    dlon = lon2 - lon1


    a = (

        sin(dlat / 2) ** 2

        +

        cos(lat1)

        *

        cos(lat2)

        *

        sin(dlon / 2) ** 2

    )


    c = 2 * atan2(

        sqrt(a),

        sqrt(1 - a)

    )


    return R * c


# =========================================================
# CREATE COMPLAINT
# =========================================================

@app.post("/complaints")
def create_complaint(

    name: str = Form(...),

    location: str = Form(...),

    latitude: float = Form(...),

    longitude: float = Form(...),

    complaint_type: str = Form(...),

    description: str = Form(...),

    db: Session = Depends(get_db)

):

    bins = db.query(WasteBin).all()


    if not bins:

        raise HTTPException(

            status_code=404,

            detail="No waste bins available"

        )


    # FIND NEAREST BIN

    nearest_bin = None

    shortest_distance = float("inf")


    for bin in bins:

        distance = calculate_distance(

            latitude,

            longitude,

            bin.latitude,

            bin.longitude

        )


        if distance < shortest_distance:

            shortest_distance = distance

            nearest_bin = bin


    # CREATE COMPLAINT

    complaint = Complaint(

        name=name,

        location=location,

        latitude=latitude,

        longitude=longitude,

        bin_id=nearest_bin.id,

        complaint_type=complaint_type,

        description=description,

        status="Pending"

    )


    db.add(complaint)

    db.commit()

    db.refresh(complaint)


    return {

        "message":
            "Complaint submitted successfully",

        "complaint_id":
            complaint.id,

        "location":
            complaint.location,

        "latitude":
            complaint.latitude,

        "longitude":
            complaint.longitude,

        "nearest_bin": {

            "id":
                nearest_bin.id,

            "bin_code":
                nearest_bin.bin_code,

            "location":
                nearest_bin.location,

            "distance_km":
                round(
                    shortest_distance,
                    3
                )

        },

        "status":
            complaint.status

    }


# =========================================================
# GET COMPLAINTS
# =========================================================

@app.get("/complaints")
def get_complaints(

    db: Session = Depends(get_db)

):

    complaints = db.query(
        Complaint
    ).order_by(

        Complaint.id.desc()

    ).all()


    result = []


    for complaint in complaints:

        bin_data = None


        if complaint.bin_id:

            bin_data = db.query(
                WasteBin
            ).filter(

                WasteBin.id == complaint.bin_id

            ).first()


        result.append({

            "id":
                complaint.id,

            "name":
                complaint.name,

            "location":
                complaint.location,

            "latitude":
                complaint.latitude,

            "longitude":
                complaint.longitude,

            "bin_id":
                complaint.bin_id,

            "bin_code": (

                bin_data.bin_code

                if bin_data

                else None

            ),

            "complaint_type":
                complaint.complaint_type,

            "description":
                complaint.description,

            "status":
                complaint.status,

            "collection_time": (

                complaint.collection_time.isoformat()

                if complaint.collection_time

                else None

            )

        })


    return result


# =========================================================
# MARK COMPLAINT AS COLLECTED
# =========================================================

@app.put("/complaints/{complaint_id}/collect")
def collect_complaint(

    complaint_id: int,

    db: Session = Depends(get_db)

):

    complaint = db.query(
        Complaint
    ).filter(

        Complaint.id == complaint_id

    ).first()


    if complaint is None:

        raise HTTPException(

            status_code=404,

            detail="Complaint not found"

        )


    # Prevent re-collection

    if complaint.status in [
        "COLLECTED",
        "KEPT"
    ]:

        raise HTTPException(

            status_code=400,

            detail="Complaint is already completed"

        )


    # Find associated bin

    bin_data = None


    if complaint.bin_id:

        bin_data = db.query(
            WasteBin
        ).filter(

            WasteBin.id == complaint.bin_id

        ).first()


    # Update complaint

    complaint.status = "COLLECTED"

    complaint.collection_time = datetime.now()


    # Empty associated bin

    if bin_data:

        bin_data.fill_level = 0

        bin_data.status = "EMPTY"


    db.commit()

    db.refresh(complaint)


    return {

        "message":
            "Complaint marked as collected",

        "complaint_id":
            complaint.id,

        "status":
            complaint.status,

        "collection_time": (

            complaint.collection_time.isoformat()

        ),

        "bin": {

            "bin_code": (

                bin_data.bin_code

                if bin_data

                else None

            ),

            "fill_level": (

                bin_data.fill_level

                if bin_data

                else None

            ),

            "status": (

                bin_data.status

                if bin_data

                else None

            )

        }

    }


# =========================================================
# KEEP COMPLETED COMPLAINT
# =========================================================

@app.put("/complaints/{complaint_id}/keep")
def keep_complaint(

    complaint_id: int,

    db: Session = Depends(get_db)

):

    complaint = db.query(
        Complaint
    ).filter(

        Complaint.id == complaint_id

    ).first()


    if complaint is None:

        raise HTTPException(

            status_code=404,

            detail="Complaint not found"

        )


    # Only completed complaints can be kept

    if complaint.status != "COLLECTED":

        raise HTTPException(

            status_code=400,

            detail="Only completed complaints can be kept"

        )


    complaint.status = "KEPT"


    db.commit()

    db.refresh(complaint)


    return {

        "message":
            "Complaint kept in history",

        "complaint_id":
            complaint.id,

        "status":
            complaint.status

    }


# =========================================================
# DELETE COMPLETED COMPLAINT
# =========================================================

@app.delete("/complaints/{complaint_id}")
def delete_complaint(

    complaint_id: int,

    db: Session = Depends(get_db)

):

    complaint = db.query(
        Complaint
    ).filter(

        Complaint.id == complaint_id

    ).first()


    if complaint is None:

        raise HTTPException(

            status_code=404,

            detail="Complaint not found"

        )


    # Only completed complaints can be deleted

    if complaint.status not in [
        "COLLECTED",
        "KEPT"
    ]:

        raise HTTPException(

            status_code=400,

            detail="Only completed complaints can be deleted"

        )


    db.delete(complaint)

    db.commit()


    return {

        "message":
            "Complaint deleted successfully",

        "complaint_id":
            complaint_id

    }