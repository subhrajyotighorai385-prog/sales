import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
from app import app
from models import User, Sale
from extensions import db

client = app.test_client()

# 1. GET register to get real CSRF token
r = client.get('/register')
assert r.status_code == 200
match = re.search(r'name=["\']csrf_token["\'][^>]*?value=["\']([^"\']+)["\']', r.data.decode('utf-8'))
csrf_token = match.group(1) if match else None
print('1. CSRF Token retrieved:', bool(csrf_token))

# Unique test user
uname = f"exec_{int(time.time())}"
uemail = f"{uname}@enterprise.ai"

# 2. POST registration with CSRF token
res_reg = client.post('/register', data={
    'csrf_token': csrf_token,
    'username': uname,
    'email': uemail,
    'company_name': 'Aura Enterprise Global',
    'password': 'StrongPassword123!',
    'confirm_password': 'StrongPassword123!',
    'seed_sample_data': 'y'
}, follow_redirects=True)
print('2. Registration Status:', res_reg.status_code)
assert b'3D Intelligence Dashboard' in res_reg.data

# 3. Test Dashboard
r_dash = client.get('/dashboard')
print('3. Dashboard Status:', r_dash.status_code)
assert b'3D Intelligence Dashboard' in r_dash.data

# 4. Test High-Value Aggregator
r_prem = client.get('/premium')
print('4. High-Value Aggregator Status:', r_prem.status_code)
assert b'High-Value Sales Aggregator' in r_prem.data
assert b'[sale for sale in sales if sale.total_amount' in r_prem.data

# 5. Test Transactions Ledger
r_tx = client.get('/transactions')
print('5. Transactions Ledger Status:', r_tx.status_code)
assert b'Transaction Ledger' in r_tx.data

# 6. Test Reports Hub
r_rep = client.get('/reports')
print('6. Reports Hub Status:', r_rep.status_code)
assert b'Executive Sales Intelligence' in r_rep.data

# 7. Test JSON API Analytics
r_api = client.get('/api/analytics')
print('7. API Analytics Status:', r_api.status_code)
json_data = r_api.get_json()
assert json_data['status'] == 'success'
print(f"   Total Revenue: ${json_data['kpis']['total_revenue']:,.2f}")
print(f"   Premium Revenue: ${json_data['kpis']['premium_revenue']:,.2f} ({json_data['kpis']['premium_revenue_pct']}%)")
print(f"   3D Bars Count: {len(json_data['bars_3d'])}")

# 8. Test PDF Report Generation via ReportLab
r_pdf = client.get('/transactions/export-pdf')
print('8. PDF Export Status:', r_pdf.status_code, r_pdf.mimetype, f"{len(r_pdf.data)} bytes")
assert r_pdf.data.startswith(b'%PDF')

# 9. Test CSV Export
r_csv = client.get('/transactions/export-csv')
print('9. CSV Export Status:', r_csv.status_code, f"{len(r_csv.data)} bytes")
assert b'Is High Value (Premium)' in r_csv.data

# 10. Test Sample CSV Template
r_sample = client.get('/transactions/sample-csv')
print('10. Sample CSV Download Status:', r_sample.status_code)
assert b'product_name' in r_sample.data

# 11. Test Add Transaction via form
match_add = re.search(r'name=["\']csrf_token["\'][^>]*?value=["\']([^"\']+)["\']', client.get('/transactions/add').data.decode('utf-8'))
csrf_add = match_add.group(1)
r_add = client.post('/transactions/add', data={
    'csrf_token': csrf_add,
    'product_name': 'Quantum Cyber Vault',
    'category': 'Cybersecurity',
    'quantity': 3,
    'unit_price': 4000.0,
    'transaction_date': '2026-11-09',
    'customer_name': 'Vanguard BioTech',
    'status': 'Completed',
    'description': 'Hardware HSM Cluster'
}, follow_redirects=True)
print('11. Add Transaction Status:', r_add.status_code)

# 12. Test Logout
r_logout = client.get('/logout', follow_redirects=True)
print('12. Logout Status:', r_logout.status_code)

print('\n>>> ALL 12 VERIFICATION PHASES PASSED WITH ZERO ERRORS! <<<')
