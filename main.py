from fastapi import FastAPI, Depends, Request,Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from pydantic import BaseModel


from database import engine, SessionLocal
from models import Base, WasteBin, Complaint


from ai.prediction import predict_fill_level



# Create Database Tables

Base.metadata.create_all(bind=engine)
# ===============================
# Insert Sample Data
# ===============================

db = SessionLocal()

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

db.close()



app = FastAPI(
    title="AI-Enabled Smart City Waste Management System V2"
)





# Static Files

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)



templates = Jinja2Templates(directory="templates")





# Database Connection

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()








# ===============================
# Home
# ===============================


@app.get("/")
def home():

    return {

        "message":
        "Smart City Waste Management System Running"

    }









# ===============================
# Get Waste Bins
# ===============================


@app.get("/bins")
def get_bins(
    db: Session = Depends(get_db)
):

    return db.query(WasteBin).all()







# ===============================
# API Waste Bins
# ===============================


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







# ===============================
# Dashboard
# ===============================


@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):

    bins = db.query(WasteBin).all()
    complaints = db.query(Complaint).all()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "bins": bins,
            "complaints": complaints
        }
    )







# ===============================
# AI Prediction
# ===============================


@app.get("/ai/predict/{bin_id}")

def ai_prediction(

    bin_id:int,

    db:Session = Depends(get_db)

):


    bin_data = db.query(WasteBin).filter(

        WasteBin.id == bin_id

    ).first()



    if bin_data is None:

        return {

            "error":"Bin not found"

        }





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


        "bin_id":bin_data.id,


        "location":bin_data.location,


        "current_fill":bin_data.fill_level,


        "predicted_fill":predicted,


        "decision":decision


    }









# ===============================
# Complaint Schema
# ===============================


class ComplaintCreate(BaseModel):

    name:str

    location:str

    complaint_type:str

    description:str







# ===============================
# Create Complaint
# ===============================


@app.post("/complaints")

def create_complaint(

    complaint_data:ComplaintCreate,

    db:Session = Depends(get_db)

):


    complaint = Complaint(


        name = complaint_data.name,


        location = complaint_data.location,


        complaint_type = complaint_data.complaint_type,


        description = complaint_data.description,


        status = "Pending"


    )



    db.add(complaint)


    db.commit()


    db.refresh(complaint)



    return complaint









# ===============================
# Get Complaints
# ===============================


@app.get("/complaints")

def get_complaints(

    db:Session = Depends(get_db)

):


    return db.query(Complaint).all()









# ===============================
# Update Complaint Status
# ===============================


@app.put("/complaints/{complaint_id}")

def update_complaint(

    complaint_id:int,

    status:str,

    db:Session = Depends(get_db)

):


    complaint = db.query(Complaint).filter(

        Complaint.id == complaint_id

    ).first()



    if complaint is None:


        return {

            "error":"Complaint not found"

        }





    complaint.status = status



    db.commit()


    db.refresh(complaint)



    return complaint
# ===============================
# Add New Waste Bin
# ===============================

class WasteBinCreate(BaseModel):

    bin_code: str
    location: str
    latitude: float
    longitude: float
    fill_level: int
    status: str



@app.post("/add-bin")
def add_bin(
    bin_code: str = Form(...),
    location: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    fill_level: int = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):

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
        "message": "Waste Bin Added Successfully"
    }