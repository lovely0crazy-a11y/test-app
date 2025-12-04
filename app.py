# app.py - IT Inventory Management System
from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import qrcode
import io
import csv
from io import StringIO, BytesIO
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    status = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    assigned_to = db.Column(db.String(200))
    user_email = db.Column(db.String(200))
    purchase_date = db.Column(db.Date)
    warranty_end = db.Column(db.Date)
    price = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'assetCode': self.asset_code,
            'name': self.name,
            'category': self.category,
            'brand': self.brand,
            'model': self.model,
            'serialNumber': self.serial_number,
            'status': self.status,
            'location': self.location,
            'assignedTo': self.assigned_to,
            'userEmail': self.user_email,
            'purchaseDate': self.purchase_date.isoformat() if self.purchase_date else None,
            'warrantyEnd': self.warranty_end.isoformat() if self.warranty_end else None,
            'price': self.price,
            'notes': self.notes
        }

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(50), nullable=False)
    asset_code = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    user = db.Column(db.String(100), default='Admin')
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'action': self.action,
            'assetCode': self.asset_code,
            'details': self.details,
            'user': self.user
        }

# Initialize database
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/assets', methods=['GET'])
def get_assets():
    search = request.args.get('search', '')
    category = request.args.get('category', 'all')
    status = request.args.get('status', 'all')
    
    query = Asset.query
    
    if search:
        query = query.filter(
            db.or_(
                Asset.asset_code.contains(search),
                Asset.name.contains(search),
                Asset.serial_number.contains(search),
                Asset.assigned_to.contains(search)
            )
        )
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    assets = query.all()
    return jsonify([asset.to_dict() for asset in assets])

@app.route('/api/assets', methods=['POST'])
def create_asset():
    data = request.json
    
    # Generate asset code if not provided
    if not data.get('assetCode'):
        last_asset = Asset.query.order_by(Asset.id.desc()).first()
        next_id = (last_asset.id + 1) if last_asset else 1
        data['assetCode'] = f"IT-{str(next_id).zfill(4)}"
    
    asset = Asset(
        asset_code=data['assetCode'],
        name=data['name'],
        category=data['category'],
        brand=data.get('brand', ''),
        model=data.get('model', ''),
        serial_number=data.get('serialNumber', ''),
        status=data['status'],
        location=data.get('location', ''),
        assigned_to=data.get('assignedTo', ''),
        user_email=data.get('userEmail', ''),
        purchase_date=datetime.fromisoformat(data['purchaseDate']) if data.get('purchaseDate') else None,
        warranty_end=datetime.fromisoformat(data['warrantyEnd']) if data.get('warrantyEnd') else None,
        price=float(data.get('price', 0)) if data.get('price') else None,
        notes=data.get('notes', '')
    )
    
    db.session.add(asset)
    db.session.commit()
    
    # Add audit log
    log = AuditLog(
        action='CREATE',
        asset_code=asset.asset_code,
        details=f"Created new asset: {asset.name}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(asset.to_dict()), 201

@app.route('/api/assets/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    data = request.json
    
    old_name = asset.name
    
    asset.asset_code = data.get('assetCode', asset.asset_code)
    asset.name = data.get('name', asset.name)
    asset.category = data.get('category', asset.category)
    asset.brand = data.get('brand', asset.brand)
    asset.model = data.get('model', asset.model)
    asset.serial_number = data.get('serialNumber', asset.serial_number)
    asset.status = data.get('status', asset.status)
    asset.location = data.get('location', asset.location)
    asset.assigned_to = data.get('assignedTo', asset.assigned_to)
    asset.user_email = data.get('userEmail', asset.user_email)
    asset.purchase_date = datetime.fromisoformat(data['purchaseDate']) if data.get('purchaseDate') else asset.purchase_date
    asset.warranty_end = datetime.fromisoformat(data['warrantyEnd']) if data.get('warrantyEnd') else asset.warranty_end
    asset.price = float(data.get('price', 0)) if data.get('price') else asset.price
    asset.notes = data.get('notes', asset.notes)
    
    db.session.commit()
    
    # Add audit log
    log = AuditLog(
        action='UPDATE',
        asset_code=asset.asset_code,
        details=f"Updated asset from {old_name} to {asset.name}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(asset.to_dict())

@app.route('/api/assets/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    
    asset_code = asset.asset_code
    asset_name = asset.name
    
    db.session.delete(asset)
    db.session.commit()
    
    # Add audit log
    log = AuditLog(
        action='DELETE',
        asset_code=asset_code,
        details=f"Deleted asset: {asset_name}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Asset deleted successfully'}), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total = Asset.query.count()
    active = Asset.query.filter_by(status='Aktif').count()
    maintenance = Asset.query.filter_by(status='Maintenance').count()
    broken = Asset.query.filter_by(status='Rusak').count()
    
    # Warranty alerts
    today = datetime.now().date()
    thirty_days = today + timedelta(days=30)
    alerts = Asset.query.filter(
        Asset.warranty_end.between(today, thirty_days)
    ).all()
    
    return jsonify({
        'total': total,
        'active': active,
        'maintenance': maintenance,
        'broken': broken,
        'warrantyAlerts': len(alerts)
    })

@app.route('/api/charts', methods=['GET'])
def get_chart_data():
    categories = ['Laptop', 'Desktop', 'Server', 'Network', 'Printer', 'Mobile', 'Lainnya']
    statuses = ['Aktif', 'Maintenance', 'Rusak', 'Retired']
    locations = ['Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Bali']
    
    # Category distribution
    category_data = {}
    for cat in categories:
        category_data[cat] = Asset.query.filter_by(category=cat).count()
    
    # Status distribution
    status_data = {}
    for status in statuses:
        status_data[status] = Asset.query.filter_by(status=status).count()
    
    # Location distribution
    location_data = {}
    for loc in locations:
        location_data[loc] = Asset.query.filter_by(location=loc).count()
    
    # Value by category
    value_data = {}
    for cat in categories:
        assets = Asset.query.filter_by(category=cat).all()
        total = sum([a.price for a in assets if a.price])
        value_data[cat] = total
    
    return jsonify({
        'category': category_data,
        'status': status_data,
        'location': location_data,
        'value': value_data
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return jsonify([log.to_dict() for log in logs])

@app.route('/api/qrcode/<int:asset_id>', methods=['GET'])
def generate_qrcode(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    
    qr_data = f"Asset: {asset.asset_code}\nName: {asset.name}\nSerial: {asset.serial_number}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

@app.route('/api/export', methods=['GET'])
def export_csv():
    assets = Asset.query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Kode Aset', 'Nama', 'Kategori', 'Brand', 'Model', 
        'Serial Number', 'Status', 'Lokasi', 'Assigned To', 'Email',
        'Tanggal Beli', 'Warranty End', 'Harga', 'Notes'
    ])
    
    # Data
    for asset in assets:
        writer.writerow([
            asset.asset_code,
            asset.name,
            asset.category,
            asset.brand,
            asset.model,
            asset.serial_number,
            asset.status,
            asset.location,
            asset.assigned_to,
            asset.user_email,
            asset.purchase_date.isoformat() if asset.purchase_date else '',
            asset.warranty_end.isoformat() if asset.warranty_end else '',
            asset.price if asset.price else '',
            asset.notes
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='inventory_export.csv'
    )

@app.route('/api/import', methods=['POST'])
def import_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be CSV'}), 400
    
    stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.DictReader(stream)
    
    imported = 0
    for row in csv_reader:
        try:
            asset = Asset(
                asset_code=row.get('Kode Aset', ''),
                name=row.get('Nama', 'Unknown'),
                category=row.get('Kategori', 'Lainnya'),
                brand=row.get('Brand', ''),
                model=row.get('Model', ''),
                serial_number=row.get('Serial Number', ''),
                status=row.get('Status', 'Aktif'),
                location=row.get('Lokasi', ''),
                assigned_to=row.get('Assigned To', ''),
                user_email=row.get('Email', ''),
                purchase_date=datetime.fromisoformat(row['Tanggal Beli']) if row.get('Tanggal Beli') else None,
                warranty_end=datetime.fromisoformat(row['Warranty End']) if row.get('Warranty End') else None,
                price=float(row.get('Harga', 0)) if row.get('Harga') else None,
                notes=row.get('Notes', '')
            )
            
            if not asset.asset_code:
                last_asset = Asset.query.order_by(Asset.id.desc()).first()
                next_id = (last_asset.id + 1) if last_asset else 1
                asset.asset_code = f"IT-{str(next_id).zfill(4)}"
            
            db.session.add(asset)
            
            # Add audit log
            log = AuditLog(
                action='IMPORT',
                asset_code=asset.asset_code,
                details=f"Imported from CSV: {asset.name}"
            )
            db.session.add(log)
            
            imported += 1
        except Exception as e:
            print(f"Error importing row: {e}")
            continue
    
    db.session.commit()
    
    return jsonify({'message': f'Successfully imported {imported} assets'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
