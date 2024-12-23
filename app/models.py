""" from app import db

class ParkingLot(db.Model):
    __tablename__ = "parking_lots"

    id = db.Column(db.Integer, primary_key=True)
    park_name = db.Column(db.String(255), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    empty_capacity = db.Column(db.Integer, nullable=False)
    park_type = db.Column(db.String(50), nullable=False)
    is_open = db.Column(db.Boolean, nullable=False)
    work_hours = db.Column(db.String(50), nullable=False)
    free_time = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<ParkingLot {self.park_name}>"

    @classmethod
    def update_or_insert(cls, data):
       
        for park in data:
            existing_park = cls.query.filter_by(park_name=park["parkName"]).first()
            if existing_park:
                existing_park.lat = park["lat"]
                existing_park.lng = park["lng"]
                existing_park.capacity = park["capacity"]
                existing_park.empty_capacity = park["emptyCapacity"]
                existing_park.park_type = park["parkType"]
                existing_park.is_open = bool(park["isOpen"])
                existing_park.work_hours = park["workHours"]
                existing_park.free_time = park["freeTime"]
            else:
                new_park = cls(
                    park_name=park["parkName"],
                    lat=park["lat"],
                    lng=park["lng"],
                    capacity=park["capacity"],
                    empty_capacity=park["emptyCapacity"],
                    park_type=park["parkType"],
                    is_open=bool(park["isOpen"]),
                    work_hours=park["workHours"],
                    free_time=park["freeTime"],
                )
                db.session.add(new_park)

        db.session.commit()
 """