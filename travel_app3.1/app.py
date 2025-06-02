from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from models import db, Route, RoutePoint, Expense
from flask import make_response
from weasyprint import HTML
from flask import render_template_string  # если нужно сгенерировать HTML вручную
import pdfkit
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable

geolocator = Nominatim(user_agent="travel_app")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SECRET_KEY'] = 'secret'

db.init_app(app)

@app.route('/')
def index():
    routes = Route.query.all()
    return render_template('index.html', routes=routes)


@app.route('/route/<int:route_id>')
def view_route(route_id):
    route = Route.query.get_or_404(route_id)
    return render_template('route.html', route=route)

@app.route('/add_route', methods=['POST'])
def add_route():
    title = request.form['title']
    description = request.form['description']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    route = Route(title=title, description=description, start_date=start_date, end_date=end_date)
    db.session.add(route)
    db.session.commit()
    return redirect(url_for('index'))





@app.route('/add_point', methods=['POST'])
#@login_required
def add_point():
    route_id = request.form.get('route_id')
    location_name = request.form.get('location_name')
    note = request.form.get('note')

    try:
        # Геокодирование: преобразуем название в координаты
        location = geolocator.geocode(location_name)
        if not location:
            flash(f"Не удалось найти координаты для: {location_name}", "danger")
            return redirect(url_for('view_route', route_id=route_id))

        point = RoutePoint(
            route_id=route_id,
            lat=location.latitude,
            lon=location.longitude,
            name=location_name,
            note=note
        )
        db.session.add(point)
        db.session.commit()
        flash("Точка успешно добавлена!", "success")
    except GeocoderUnavailable:
        flash("Ошибка геокодирования. Попробуйте позже.", "danger")

    return redirect(url_for('view_route', route_id=route_id))




@app.route('/route/<int:route_id>/add_expense', methods=['POST'])
def add_expense(route_id):
    category = request.form['category']
    amount = float(request.form['amount'])
    date = request.form['date']
    description = request.form['description']
    expense = Expense(category=category, amount=amount, date=date, description=description, route_id=route_id)
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for('view_route', route_id=route_id))




@app.route('/point/<int:point_id>/delete', methods=['POST'])
def delete_point(point_id):
    point = RoutePoint.query.get_or_404(point_id)
    route_id = point.route_id
    db.session.delete(point)
    db.session.commit()
    flash('Точка удалена')
    return redirect(url_for('view_route', route_id=route_id))

@app.route('/point/<int:point_id>/edit', methods=['GET', 'POST'])
def edit_point(point_id):
    point = RoutePoint.query.get_or_404(point_id)
    if request.method == 'POST':
        point.name = request.form['name']
        point.lat = float(request.form['lat'])
        point.lon = float(request.form['lon'])
        point.date = request.form['date']
        point.note = request.form['note']
        image = request.files['image']
        if image and image.filename:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            point.image_filename = image_filename
        db.session.commit()
        flash('Точка обновлена')
        return redirect(url_for('view_route', route_id=point.route_id))
    return render_template('edit_point.html', point=point)


@app.route('/create_route', methods=['GET'])
def create_route():
    return render_template('create_route.html')




@app.route('/route/<int:route_id>/export_pdf')
def export_pdf(route_id):
    route = Route.query.get_or_404(route_id)
    rendered = render_template('pdf_template.html', route=route)
    pdf = pdfkit.from_string(rendered, False)  # False — возвращает PDF в байтах

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=route_{route.id}.pdf'
    return response


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
