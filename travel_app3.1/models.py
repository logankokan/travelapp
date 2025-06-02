from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    points = db.relationship('RoutePoint', backref='route', lazy=True, order_by="RoutePoint.id")
    expenses = db.relationship('Expense', backref='route', lazy=True)


class RoutePoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    date = db.Column(db.String(50))
    note = db.Column(db.Text)
    image_filename = db.Column(db.String(100))
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    amount = db.Column(db.Float)
    date = db.Column(db.String(50))
    description = db.Column(db.Text)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
