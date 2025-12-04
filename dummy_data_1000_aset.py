import csv
import random
from datetime import datetime, timedelta

# Data untuk generate dummy
categories = ['Laptop', 'Desktop', 'Server', 'Network', 'Printer', 'Mobile', 'Lainnya']
brands = {
    'Laptop': ['Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'Apple', 'MSI'],
    'Desktop': ['Dell', 'HP', 'Lenovo', 'Acer', 'Custom Build'],
    'Server': ['Dell', 'HP', 'IBM', 'Cisco', 'Supermicro'],
    'Network': ['Cisco', 'TP-Link', 'Ubiquiti', 'Mikrotik', 'D-Link'],
    'Printer': ['HP', 'Canon', 'Epson', 'Brother', 'Xerox'],
    'Mobile': ['Apple', 'Samsung', 'Xiaomi', 'Oppo', 'Vivo'],
    'Lainnya': ['Various', 'Generic', 'Custom']
}
models = {
    'Dell': ['Latitude 5420', 'Latitude 7420', 'OptiPlex 7090', 'PowerEdge R740'],
    'HP': ['EliteBook 840', 'ProBook 450', 'Z2 Tower', 'ProLiant DL380'],
    'Lenovo': ['ThinkPad X1', 'ThinkPad T14', 'ThinkCentre M70', 'ThinkSystem SR650'],
    'Asus': ['ZenBook 14', 'VivoBook 15', 'ROG Strix', 'ExpertBook B9'],
    'Acer': ['Aspire 5', 'Swift 3', 'Predator', 'TravelMate'],
    'Apple': ['MacBook Pro', 'MacBook Air', 'iMac', 'iPhone 14', 'iPhone 13'],
    'MSI': ['Modern 14', 'Prestige 15', 'GF63'],
    'Cisco': ['Catalyst 2960', 'ASR 1000', 'ISR 4000', 'Nexus 9000'],
    'TP-Link': ['Archer AX50', 'TL-SG1024', 'Deco M5'],
    'Ubiquiti': ['UniFi AP AC Pro', 'EdgeRouter X', 'UniFi Dream Machine'],
    'Canon': ['ImageCLASS MF445dw', 'PIXMA G3010', 'imageRUNNER'],
    'Epson': ['EcoTank L3110', 'WorkForce Pro', 'L5190'],
    'Samsung': ['Galaxy S23', 'Galaxy A54', 'Galaxy M14'],
    'Xiaomi': ['Redmi Note 12', 'Poco X5', 'Mi 11'],
    'Custom Build': ['Gaming PC', 'Workstation', 'Office PC'],
    'Various': ['Model A', 'Model B', 'Model C']
}
statuses = ['Aktif', 'Maintenance', 'Rusak', 'Retired']
locations = ['Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Bali', 'Medan', 'Semarang', 'Makassar']
departments = ['IT', 'Finance', 'HR', 'Marketing', 'Sales', 'Operations', 'R&D', 'Customer Service']
first_names = ['Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fitri', 'Gunawan', 'Hani', 'Indra', 'Joko', 
               'Kartika', 'Linda', 'Made', 'Nur', 'Oscar', 'Putri', 'Rudi', 'Sari', 'Tono', 'Wati']
last_names = ['Susanto', 'Wijaya', 'Prasetyo', 'Santoso', 'Kurniawan', 'Hidayat', 'Setiawan', 'Putra', 
              'Hermawan', 'Suharto', 'Rahman', 'Lestari', 'Nuraini', 'Wibowo', 'Permana']

def generate_serial_number():
    """Generate random serial number"""
    return f"SN{random.randint(100000, 999999)}{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}"

def generate_purchase_date():
    """Generate random purchase date within last 5 years"""
    days_ago = random.randint(0, 1825)  # 5 years
    return (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

def generate_warranty_end(purchase_date):
    """Generate warranty end date (1-3 years from purchase)"""
    purchase = datetime.strptime(purchase_date, '%Y-%m-%d')
    warranty_years = random.choice([1, 2, 3])
    warranty_end = purchase + timedelta(days=365 * warranty_years)
    return warranty_end.strftime('%Y-%m-%d')

def generate_price(category):
    """Generate realistic price based on category"""
    price_ranges = {
        'Laptop': (8000000, 25000000),
        'Desktop': (6000000, 20000000),
        'Server': (30000000, 150000000),
        'Network': (1000000, 15000000),
        'Printer': (2000000, 10000000),
        'Mobile': (3000000, 15000000),
        'Lainnya': (500000, 5000000)
    }
    min_price, max_price = price_ranges[category]
    return random.randint(min_price, max_price)

def generate_user_name():
    """Generate random user name"""
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_email(name, department):
    """Generate email based on name and department"""
    first, last = name.split()
    domain = "company.com"
    dept_prefix = department.lower().replace(' ', '')
    email_formats = [
        f"{first.lower()}.{last.lower()}@{domain}",
        f"{first[0].lower()}{last.lower()}@{domain}",
        f"{first.lower()}{last[0].lower()}@{domain}",
        f"{first.lower()}.{last.lower()}@{dept_prefix}.{domain}"
    ]
    return random.choice(email_formats)

def generate_notes(category, status):
    """Generate contextual notes"""
    notes_list = {
        'Aktif': [
            'Kondisi baik, berfungsi normal',
            'Unit baru, garansi aktif',
            'Performa optimal',
            'Sudah dikonfigurasi dan siap pakai',
            'Update software terbaru'
        ],
        'Maintenance': [
            'Sedang dilakukan upgrade RAM',
            'Pembersihan dan pengecekan rutin',
            'Update sistem operasi',
            'Penggantian thermal paste',
            'Kalibrasi dan testing'
        ],
        'Rusak': [
            'Layar rusak, menunggu spare part',
            'Motherboard bermasalah',
            'Hard disk failure',
            'Battery tidak berfungsi',
            'Menunggu keputusan repair/replace'
        ],
        'Retired': [
            'Unit sudah tidak digunakan',
            'Spesifikasi sudah outdated',
            'Diganti dengan unit baru',
            'Akan didonasikan',
            'Menunggu disposal'
        ]
    }
    return random.choice(notes_list.get(status, ['']))

# Generate CSV file
filename = 'dummy_data_1000_assets.csv'

with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Kode Aset', 'Nama', 'Kategori', 'Brand', 'Model', 'Serial Number', 
                  'Status', 'Lokasi', 'Assigned To', 'Email', 'Tanggal Beli', 'Warranty End', 'Harga', 'Notes']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    
    for i in range(1, 1001):
        category = random.choice(categories)
        brand = random.choice(brands[category])
        model = random.choice(models.get(brand, ['Standard Model']))
        status = random.choices(statuses, weights=[70, 15, 10, 5])[0]  # Weighted: more Aktif
        location = random.choice(locations)
        purchase_date = generate_purchase_date()
        warranty_end = generate_warranty_end(purchase_date)
        
        # Generate assigned_to and email based on status
        if status in ['Aktif', 'Maintenance']:
            department = random.choice(departments)
            user_name = generate_user_name()
            assigned_to = f"{user_name} - {department}"
            user_email = generate_email(user_name, department)
        else:
            assigned_to = ''
            user_email = ''
        
        asset_name = f"{brand} {model} - {location}"
        
        writer.writerow({
            'Kode Aset': f'IT-{str(i).zfill(4)}',
            'Nama': asset_name,
            'Kategori': category,
            'Brand': brand,
            'Model': model,
            'Serial Number': generate_serial_number(),
            'Status': status,
            'Lokasi': location,
            'Assigned To': assigned_to,
            'Email': user_email,
            'Tanggal Beli': purchase_date,
            'Warranty End': warranty_end,
            'Harga': generate_price(category),
            'Notes': generate_notes(category, status)
        })

print(f"✅ File '{filename}' berhasil dibuat dengan 1000 data aset!")
print(f"📊 Distribusi Status:")
print(f"   - Aktif: ~700 aset (70%)")
print(f"   - Maintenance: ~150 aset (15%)")
print(f"   - Rusak: ~100 aset (10%)")
print(f"   - Retired: ~50 aset (5%)")
print(f"\n📍 Lokasi: {', '.join(locations)}")
print(f"📦 Kategori: {', '.join(categories)}")
print(f"\n💡 File siap untuk di-import ke aplikasi!")
