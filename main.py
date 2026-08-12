from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, SessionLocal
from models import Base, WasteBin, Complaint

from ai.prediction import predict_fill_level


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


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

    return db.query(WasteBin).all()


# =========================================================
# API BINS FOR MAP
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

    # =====================================================
    # CHECK WHETHER BIN CODE ALREADY EXISTS
    # =====================================================

    existing_bin = db.query(WasteBin).filter(
        WasteBin.bin_code == bin_code
    ).first()

    if existing_bin:

        raise HTTPException(
            status_code=400,
            detail="Bin code already exists"
        )


    # =====================================================
    # VALIDATE FILL LEVEL
    # =====================================================

    if fill_level < 0 or fill_level > 100:

        raise HTTPException(
            status_code=400,
            detail="Fill level must be between 0 and 100"
        )


    # =====================================================
    # AUTOMATICALLY DETERMINE STATUS
    # =====================================================

    if fill_level >= 80:

        status = "FULL"

    elif fill_level >= 40:

        status = "MEDIUM"

    else:

        status = "EMPTY"


    # =====================================================
    # LOCATION → LATITUDE / LONGITUDE
    # =====================================================

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


    # =====================================================
    # CONVERT LOCATION TO LOWERCASE
    # =====================================================

    location_key = location.strip().lower()


    # =====================================================
    # GET COORDINATES
    # =====================================================

    if location_key in location_coordinates:

        latitude, longitude = location_coordinates[
            location_key
        ]

    else:

        # Default Hyderabad location

        latitude = 17.3850
        longitude = 78.4867


    # =====================================================
    # CREATE NEW BIN
    # =====================================================

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


    # =====================================================
    # RETURN RESULT
    # =====================================================

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


    average_fill = 0


    if total_bins > 0:

        average_fill = round(

            total_fill / total_bins,

            2

        )


    # =====================================================
    # HIGH FILL BINS
    # =====================================================

    high_fill_bins = sorted(

        [

            bin

            for bin in bins

            if (bin.fill_level or 0) >= 80

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


    return {

        "total_bins": total_bins,

        "full_bins": full_bins,

        "medium_bins": medium_bins,

        "empty_bins": empty_bins,

        "average_fill": average_fill,

        "top_labels": top_labels,

        "top_fill_levels": top_fill_levels,

        "status": status_count

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

    bins = db.query(WasteBin).order_by(

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

    bin_data = db.query(WasteBin).filter(

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

        "bin_id": bin_data.id,

        "location": bin_data.location,

        "current_fill": bin_data.fill_level,

        "predicted_fill": predicted,

        "decision": decision

    }


# =========================================================
# COMPLAINT SCHEMA
# =========================================================

class ComplaintCreate(BaseModel):

    name: str

    location: str

    complaint_type: str

    description: str


# =========================================================
# CREATE COMPLAINT
# =========================================================

@app.post("/complaints")
def create_complaint(

    name: str = Form(...),

    location: str = Form(...),

    complaint_type: str = Form(...),

    description: str = Form(...),

    db: Session = Depends(get_db)

):

    complaint = Complaint(

        name=name,

        location=location,

        complaint_type=complaint_type,

        description=description,

        status="Pending"

    )


    db.add(complaint)

    db.commit()

    db.refresh(complaint)


    return {

        "message": "Complaint submitted successfully"

    }


# =========================================================
# GET COMPLAINTS
# =========================================================

@app.get("/complaints")
def get_complaints(

    db: Session = Depends(get_db)

):

    return db.query(Complaint).all()