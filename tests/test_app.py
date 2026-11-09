import io
import pytest
from datetime import date, timedelta
from app import create_app
from config import TestConfig
from extensions import db
from models import User, Sale
from services.sales_service import SalesService

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    user = User(username='testpilot', email='pilot@quantum.ai', company_name='Quantum Pilot Inc')
    user.set_password('Secret123!')
    user.premium_threshold = 1000.0
    db.session.add(user)
    db.session.commit()
    return user

def login(client, username='testpilot', password='Secret123!'):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

def test_password_hashing(test_user):
    assert test_user.check_password('Secret123!') is True
    assert test_user.check_password('WrongPassword') is False
    assert test_user.password_hash != 'Secret123!'

def test_registration_and_login(client, app):
    # Register new user
    res = client.post('/register', data={
        'username': 'cyberadmin',
        'email': 'admin@cyber.ai',
        'password': 'StrongPassword99',
        'confirm_password': 'StrongPassword99',
        'company_name': 'Cyber Shield',
        'seed_sample_data': 'y'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome" in res.data or b"Dashboard" in res.data or b"cyberadmin" in res.data

    with app.app_context():
        u = User.query.filter_by(username='cyberadmin').first()
        assert u is not None
        # Verify demo sales were seeded
        seeded_count = Sale.query.filter_by(user_id=u.id).count()
        assert seeded_count > 0

    # Logout
    res_logout = client.get('/logout', follow_redirects=True)
    assert res_logout.status_code == 200
    assert b"logged out" in res_logout.data.lower() or b"sign in" in res_logout.data.lower()

def test_high_value_sales_aggregator_list_comprehension(app, test_user):
    today = date.today()
    sales_data = [
        Sale(user_id=test_user.id, product_name="Enterprise AI Cluster", category="Enterprise AI", quantity=1, unit_price=4500.0, total_amount=4500.0, transaction_date=today),
        Sale(user_id=test_user.id, product_name="Cloud Security Mesh", category="Cybersecurity", quantity=2, unit_price=1200.0, total_amount=2400.0, transaction_date=today),
        Sale(user_id=test_user.id, product_name="Team SaaS Seats", category="SaaS Subscriptions", quantity=1, unit_price=450.0, total_amount=450.0, transaction_date=today),
        Sale(user_id=test_user.id, product_name="Developer API Pack", category="Cloud Infrastructure", quantity=1, unit_price=250.0, total_amount=250.0, transaction_date=today),
        Sale(user_id=test_user.id, product_name="Micro-Gateway", category="Hardware & Edge", quantity=1, unit_price=1000.0, total_amount=1000.0, transaction_date=today)
    ]
    db.session.add_all(sales_data)
    db.session.commit()

    all_sales = Sale.query.filter_by(user_id=test_user.id).all()
    assert len(all_sales) == 5

    # Run Aggregator with threshold = 1000.0
    agg = SalesService.aggregate_sales(all_sales, threshold=1000.0)

    # 4500, 2400, 1000 >= 1000 -> 3 premium sales
    # 450, 250 < 1000 -> 2 regular sales
    assert agg['premium_count'] == 3
    assert agg['regular_count'] == 2
    assert agg['total_count'] == 5
    assert agg['premium_revenue'] == 4500.0 + 2400.0 + 1000.0  # 7900.0
    assert agg['regular_revenue'] == 450.0 + 250.0            # 700.0
    assert agg['total_revenue'] == 8600.0
    assert agg['highest_sale'].product_name == "Enterprise AI Cluster"
    assert agg['highest_sale'].total_amount == 4500.0

    # Test list comprehension helper directly
    prem_list = SalesService.extract_premium_sales(all_sales, threshold=1000.0)
    assert len(prem_list) == 3
    reg_list = SalesService.extract_regular_sales(all_sales, threshold=1000.0)
    assert len(reg_list) == 2

def test_user_data_isolation(app, client):
    # Create User 1
    u1 = User(username='user_alpha', email='alpha@test.com')
    u1.set_password('Pass123!')
    # Create User 2
    u2 = User(username='user_beta', email='beta@test.com')
    u2.set_password('Pass123!')
    db.session.add_all([u1, u2])
    db.session.commit()

    # User 1 adds a confidential sale
    s1 = Sale(user_id=u1.id, product_name="Alpha Secret Project", category="Enterprise AI", quantity=1, unit_price=9999.0, total_amount=9999.0, transaction_date=date.today())
    # User 2 adds their own sale
    s2 = Sale(user_id=u2.id, product_name="Beta Public Module", category="Cloud Infrastructure", quantity=1, unit_price=500.0, total_amount=500.0, transaction_date=date.today())
    db.session.add_all([s1, s2])
    db.session.commit()

    # Log in as User 2
    login(client, 'user_beta', 'Pass123!')

    # Access transactions page
    res = client.get('/transactions')
    assert res.status_code == 200
    assert b"Beta Public Module" in res.data
    # Ensure User 1's secret sale is NOT visible to User 2
    assert b"Alpha Secret Project" not in res.data

    # User 2 attempts to edit User 1's transaction
    res_edit = client.get(f'/transactions/{s1.id}/edit')
    assert res_edit.status_code == 404

def test_transaction_crud(app, client, test_user):
    login(client, 'testpilot', 'Secret123!')

    # 1. Add Transaction
    res_add = client.post('/transactions/add', data={
        'product_name': 'Neural Quantum Engine',
        'category': 'Enterprise AI',
        'quantity': 2,
        'unit_price': 3000.0,
        'transaction_date': date.today().strftime('%Y-%m-%d'),
        'customer_name': 'Titan Dynamics',
        'status': 'Completed',
        'description': 'Production AI Cluster'
    }, follow_redirects=True)
    assert res_add.status_code == 200

    with app.app_context():
        sale = Sale.query.filter_by(product_name='Neural Quantum Engine').first()
        assert sale is not None
        assert sale.total_amount == 6000.0
        assert sale.is_premium(threshold=1000.0) is True

        # 2. Edit Transaction
        sale_id = sale.id

    res_edit = client.post(f'/transactions/{sale_id}/edit', data={
        'product_name': 'Neural Quantum Engine V2',
        'category': 'Enterprise AI',
        'quantity': 3,
        'unit_price': 3500.0,
        'transaction_date': date.today().strftime('%Y-%m-%d'),
        'customer_name': 'Titan Dynamics',
        'status': 'Completed',
        'description': 'Upgraded order'
    }, follow_redirects=True)
    assert res_edit.status_code == 200

    with app.app_context():
        updated_sale = db.session.get(Sale, sale_id)
        assert updated_sale.product_name == 'Neural Quantum Engine V2'
        assert updated_sale.total_amount == 10500.0

        # 3. Delete Transaction
        res_del = client.post(f'/transactions/{sale_id}/delete', follow_redirects=True)
        assert res_del.status_code == 200
        assert db.session.get(Sale, sale_id) is None

def test_csv_export_and_import(app, client, test_user):
    login(client, 'testpilot', 'Secret123!')

    # Seed 2 transactions
    s1 = Sale(user_id=test_user.id, product_name="Test Tool Alpha", category="Cybersecurity", quantity=1, unit_price=1500.0, total_amount=1500.0, transaction_date=date.today())
    db.session.add(s1)
    db.session.commit()

    # Test CSV Export
    res_export = client.get('/transactions/export-csv')
    assert res_export.status_code == 200
    assert b"Test Tool Alpha" in res_export.data
    assert b"YES" in res_export.data  # High value flag

    # Test CSV Import
    csv_content = b"product_name,category,quantity,unit_price,transaction_date,customer_name\nImported Micro Node,Hardware & Edge,5,200.00,2026-05-10,Volt Labs\n"
    data = {
        'csv_file': (io.BytesIO(csv_content), 'import.csv')
    }
    res_import = client.post('/transactions/import-csv', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert res_import.status_code == 200

    with app.app_context():
        imported_sale = Sale.query.filter_by(product_name='Imported Micro Node').first()
        assert imported_sale is not None
        assert imported_sale.total_amount == 1000.0

def test_reportlab_pdf_generation(app, client, test_user):
    login(client, 'testpilot', 'Secret123!')

    # Add a sale
    s = Sale(user_id=test_user.id, product_name="VIP Contract Alpha", category="Enterprise AI", quantity=1, unit_price=8000.0, total_amount=8000.0, transaction_date=date.today())
    db.session.add(s)
    db.session.commit()

    res_pdf = client.get('/transactions/export-pdf')
    assert res_pdf.status_code == 200
    assert res_pdf.mimetype == 'application/pdf'
    # Check PDF magic bytes '%PDF'
    assert res_pdf.data.startswith(b'%PDF')

def test_api_analytics_endpoint(client, test_user):
    login(client, 'testpilot', 'Secret123!')
    res = client.get('/api/analytics')
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['status'] == 'success'
    assert 'kpis' in json_data
    assert 'bars_3d' in json_data
    assert 'monthly' in json_data
