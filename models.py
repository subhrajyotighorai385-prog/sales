from datetime import datetime, timezone, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager

CATEGORIES = [
    'Cloud Infrastructure',
    'Enterprise AI',
    'Cybersecurity',
    'SaaS Subscriptions',
    'Consulting & Services',
    'Hardware & Edge',
    'Data Analytics',
    'Other'
]

STATUSES = ['Completed', 'Pending', 'Processing']

def get_utc_now():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    company_name = db.Column(db.String(120), default='Aura Enterprise')
    currency = db.Column(db.String(8), default='₹')
    premium_threshold = db.Column(db.Float, default=50000.0)
    theme_accent = db.Column(db.String(32), default='cyan')
    created_at = db.Column(db.DateTime, default=get_utc_now)

    sales = db.relationship('Sale', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def avatar_initials(self):
        if self.username:
            parts = self.username.strip().split()
            if len(parts) >= 2:
                return (parts[0][0] + parts[1][0]).upper()
            return self.username[:2].upper()
        return 'U'

    def __repr__(self):
        return f'<User {self.username}>'


class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    product_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80), nullable=False, default='General')
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    transaction_date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.Text, nullable=True)
    customer_name = db.Column(db.String(120), default='Direct Client')
    status = db.Column(db.String(32), default='Completed')
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def is_premium(self, threshold=50000.0):
        t = threshold if threshold is not None else 50000.0
        return self.total_amount >= t

    def to_dict(self, threshold=50000.0, currency='₹'):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'category': self.category,
            'quantity': self.quantity,
            'unit_price': round(float(self.unit_price), 2),
            'total_amount': round(float(self.total_amount), 2),
            'currency': currency,
            'transaction_date': self.transaction_date.strftime('%Y-%m-%d'),
            'description': self.description or '',
            'customer_name': self.customer_name or '',
            'status': self.status,
            'is_premium': self.is_premium(threshold)
        }

    def __repr__(self):
        return f'<Sale {self.id}: {self.product_name} (₹{self.total_amount})>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

