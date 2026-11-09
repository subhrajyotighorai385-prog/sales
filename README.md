# High Value Sales — 3D Sales Intelligence Platform

> A futuristic, premium 3D Sales & Financial Intelligence Web Platform built with Python Flask, SQLAlchemy, Three.js, Chart.js, and GSAP.

---

## ✦ Platform Overview

**High Value Sales** is an enterprise-grade financial analytics and transaction intelligence platform designed with a luxury cyberpunk dark navy aesthetic (`#070913`), frosted glassmorphism, glowing neon accents (cyan, cyber purple, golden amber), and hardware-accelerated 3D WebGL data visualizations.

The platform is powered by an algorithmic **High-Value Sales Aggregator** using Python list comprehension to instantly extract, classify, and compare premium enterprise contracts against regular sales volume.

---

## 🚀 Key Features

### 1. 3D WebGL Landing Page
- Interactive 3D financial crystal (faceted icosahedron) with glowing outer wireframe cage.
- Dual orbiting orbital rings (torus) and rotating golden telemetry data nodes.
- 450-node particle constellation reacting to mouse movement with depth parallax.
- Graceful 2D fallback for non-WebGL environments and reduced-motion preferences.
- Animated platform statistics counters and smooth hero transitions.

### 2. High-Value Sales Aggregator (Core Feature)
- Dedicated Python list comprehension pipeline:
  ```python
  premium_sales = [sale for sale in sales if sale.total_amount >= threshold]
  regular_sales = [sale for sale in sales if sale.total_amount < threshold]
  ```
- **Dynamic Threshold Testing**: Test custom thresholds ($500, $1,000, $5,000, etc.) in real time.
- Instant automatic calculation of:
  - High-Value Revenue & Yield Share (%)
  - Regular Revenue & Yield Share (%)
  - Deal Count Split & Ratio Bar
  - Average Deal Size Comparison (Premium vs Regular)
  - Highest-Value Deal Spotlight & Ranking

### 3. Interactive 3D Spatial Sales Matrix (Dashboard)
- Real-time Three.js 3D bar matrix representing actual database transactions.
- Golden hexagonal prisms represent high-value deals with crown markers; cyan/purple prisms represent regular sales.
- **Raycasting Interaction**: Hovering over any 3D bar scales it up, enhances emissive glow, and opens a floating futuristic HTML tooltip showing product name, category, VIP status, and revenue amount.
- Drag-to-rotate, auto-rotation toggle, and perspective reset controls.

### 4. Advanced 2D Financial Charts (Chart.js)
- **Revenue Timeline**: Line chart with smooth bezier curves and cyan/purple gradient fill comparing gross revenue vs high-value sales trajectory.
- **Premium vs Regular Split**: Doughnut chart showing yield percentages.
- **Category Vertical Yield**: Horizontal bar chart breaking down sales across high-ticket verticals.
- **Monthly Volume & Revenue**: Dual-axis bar & line chart comparing monthly revenue against deal count.

### 5. Complete Transaction Management
- **Add Transaction**: Real-time auto-calculation of `Total Amount = Quantity × Unit Price` with instant dynamic VIP deal badge preview.
- **Edit & Update**: Modify existing transactions with immediate database synchronization.
- **Secure Deletion**: CSRF-protected deletion with confirmation dialogs.
- **Detail Modal**: Interactive AJAX telemetry modal for full deal inspection.
- **Search & Filters**: Search by keywords (product, client, notes), filter by category, filter by deal type (All, High-Value, Regular), filter by date ranges, and sort (date, amount, product name).
- **Pagination**: Scalable paginated ledger view.

### 6. Bulk CSV & PDF Report Engine
- **Bulk CSV Import**: Flexible parser that automatically detects headers, cleans currency symbols, computes totals, and handles dates.
- **Sample CSV Generator**: One-click download of standardized CSV import templates.
- **CSV Export**: Exports filtered transactions with a dedicated `Is High Value (Premium)` column flag.
- **ReportLab PDF Generator**: Compiles an executive PDF sales intelligence report with corporate dark-cyan tables, KPI summary boxes, and high-value transaction highlights.

### 7. Security & Isolation
- User-specific isolation: each user only accesses their own transactions.
- Password hashing using Werkzeug.
- CSRF protection across all forms and state-changing actions.
- SQLite database stored permanently in the `instance/` directory.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.14+, Flask 3.1+, Flask-SQLAlchemy 3.1+, Flask-Login 0.6+, Flask-WTF 1.3+, WTForms, ReportLab 5.1+ |
| **Database** | SQLite (via SQLAlchemy ORM) |
| **Frontend** | HTML5, CSS3 Glassmorphism, Vanilla JS, Three.js (r128), Chart.js (v4.4), GSAP (3.12) |
| **Fonts** | Plus Jakarta Sans, Space Grotesk |
| **Testing** | pytest 9.2+ |

---

## 📂 Project Structure

```
Sales_Intelligence_3D/
│
├── app.py                      # Flask Application Factory & Server Entry
├── config.py                   # Configuration & Environment Settings
├── extensions.py               # Database, Login Manager & CSRF Extensions
├── models.py                   # User & Sale SQLAlchemy Models
├── forms.py                    # Flask-WTF Validation Forms
├── requirements.txt            # Python Dependencies
├── README.md                   # Documentation
├── run.bat                     # Windows One-Click Launch Script
│
├── instance/
│   └── sales_intelligence.db   # Permanent SQLite Database
│
├── routes/
│   ├── auth.py                 # Login, Registration, Logout & Profile
│   ├── dashboard.py            # Main Dashboard & 3D Analytics APIs
│   └── transactions.py         # CRUD, Aggregator, CSV & PDF Exports
│
├── services/
│   └── sales_service.py        # Python List Comprehension Aggregator & PDF Engine
│
├── templates/
│   ├── base.html               # Master Layout with Cyber Nav & Scripts
│   ├── index.html              # 3D WebGL Landing Page
│   ├── login.html              # 3D Glassmorphism Login
│   ├── register.html           # 3D Registration with Demo Data Option
│   ├── dashboard.html          # Executive Dashboard & 3D Sales Matrix
│   ├── transactions.html       # Transaction Ledger with Filters & Modals
│   ├── add_transaction.html    # Add Transaction with Live Calculator
│   ├── edit_transaction.html   # Edit Transaction
│   ├── premium.html            # High-Value Sales Aggregator Showcase
│   ├── profile.html            # Settings & Custom Threshold Config
│   ├── reports.html            # Executive Reports Hub & Print View
│   ├── 404.html                # Cyberpunk 404 Page
│   └── 500.html                # Error 500 Page
│
├── static/
│   ├── css/
│   │   └── style.css           # Futuristic Glassmorphism Stylesheet
│   └── js/
│       ├── main.js             # UI Interactions, GSAP, Modals & Calculators
│       ├── charts.js           # Chart.js Dynamic Database Feeds
│       └── 3d-scene.js         # Three.js WebGL 3D Matrix & Particle Scene
│
└── tests/
    └── test_app.py             # 8 Automated Unit & Integration Tests
```

---

## 🏁 Quickstart & Installation

### Option 1: Run via `run.bat` (Windows)
Double-click `run.bat` or run:
```cmd
run.bat
```

### Option 2: Run via Terminal
1. Install dependencies (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```
2. Start the Flask application:
   ```bash
   python app.py
   ```
3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 🧪 Running Automated Tests

Run the full pytest suite:
```bash
pytest
```
All 8 test suites verify:
- Registration, password hashing, and authentication
- Python list comprehension high-value aggregator accuracy
- Multi-user data isolation
- Transaction CRUD operations
- CSV export & import validation
- ReportLab PDF generation (valid `%PDF` binary header)
- JSON Analytics API payload validation
