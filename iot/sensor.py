import random
import time
import sys
import os


# Add project root path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from database import SessionLocal
from models import WasteBin


def update_sensor_data():

    db = SessionLocal()


    bins = db.query(WasteBin).all()


    for bin in bins:

        change = random.randint(1,10)

        new_level = bin.fill_level + change


        if new_level > 100:

            new_level = random.randint(10,30)


        bin.fill_level = new_level



        if new_level > 80:

            bin.status = "FULL"


        elif new_level > 40:

            bin.status = "MEDIUM"


        else:

            bin.status = "EMPTY"



        print(
            "Bin:",
            bin.id,
            "Fill Level:",
            bin.fill_level,
            "%"
        )


    db.commit()

    db.close()





while True:

    update_sensor_data()

    time.sleep(10)