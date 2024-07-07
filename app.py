from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flask import send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

current_directory = os.path.dirname(os.path.abspath(__file__))
upload_folder = os.path.join(current_directory, 'static', 'img')
app.config['UPLOAD_FOLDER'] = upload_folder

if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

# Модели
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    source_connections = db.relationship(
        'Connection', 
        foreign_keys='Connection.source_id', 
        back_populates='source', 
        lazy='dynamic'
    )
    destination_connections = db.relationship(
        'Connection', 
        foreign_keys='Connection.destination_id', 
        back_populates='destination', 
        lazy='dynamic'
    )


class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    connection_type_id = db.Column(db.Integer, db.ForeignKey('connection_type.id'))  
    connection_type = db.relationship('ConnectionType') 

    source = db.relationship('Device', foreign_keys=[source_id], back_populates='source_connections')
    destination = db.relationship('Device', foreign_keys=[destination_id], back_populates='destination_connections')


class ConnectionType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<ConnectionType {self.name}>'


# routes
@app.route('/')
def index():
    devices = Device.query.all()
    return render_template('index.html', devices=devices)


@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
    if request.method == 'POST':
        filename = None  
        file = request.files.get('device_image', None) 

        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print("File saved to:", file_path)
        
        new_device = Device(
            name=request.form['name'],
            device_type=request.form['device_type'],
            image_filename=filename  
        )
        db.session.add(new_device)
        db.session.commit()
        print("Device added:", new_device.name)
        return redirect(url_for('index'))  

    devices = Device.query.all()
    return render_template('add_form.html', devices=devices)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/connect', methods=['GET', 'POST'])
def connect_devices():
    devices = Device.query.all()
    connection_types = ConnectionType.query.all()
    if request.method == 'POST':
        source_id = request.form['source_id']
        destination_id = request.form['destination_id']
        connection_type_id = request.form['connection_type_id']  
        connection = Connection(
            source_id=source_id,
            destination_id=destination_id,
            connection_type_id=connection_type_id  
        )
        db.session.add(connection)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('connect.html', devices=devices, connection_types=connection_types)


@app.route('/add_connection_type', methods=['GET', 'POST'])
def add_connection_type():
    if request.method == 'POST':
        type_name = request.form['type_name']
        if type_name:
            new_type = ConnectionType(name=type_name)
            db.session.add(new_type)
            db.session.commit()
            return redirect(url_for('add_connection_type'))
    return render_template('add_connection_type.html')


@app.route('/delete_device_n', methods=['GET', 'POST'])
def delete_device_n():
    devices = Device.query.all()
    return render_template('delete_device_n.html', devices=devices)


@app.route('/delete_device/<int:device_id>', methods=['GET', 'POST'])
def delete_device(device_id):
    device_to_delete = Device.query.get_or_404(device_id)
    if request.method == 'POST':
        db.session.delete(device_to_delete)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('confirm_delete.html', device=device_to_delete)


@app.route('/data')
def data():
    devices = Device.query.all()
    connections = Connection.query.all()

    nodes = [
        {
            'id': device.id,
            'label': device.name,
            'group': device.device_type,
            'image': url_for('static', filename='img/' + device.image_filename) if device.image_filename else None,
            'shape': 'image' if device.image_filename else 'dot'
        }
        for device in devices
    ]

    edges = [
        {
            'from': connection.source_id,
            'to': connection.destination_id,
            'label': connection.connection_type.name if connection.connection_type else "Undefined" 
        }
        for connection in connections
    ]

    return jsonify({'nodes': nodes, 'edges': edges})


if __name__ == '__main__':
    app.run(debug=True)
