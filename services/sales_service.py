import io
import csv
from datetime import datetime, date, timedelta
from collections import defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from extensions import db
from models import Sale, CATEGORIES

class SalesService:
    @staticmethod
    def extract_premium_sales(sales, threshold=50000.0):
        """
        High-Value Sales Aggregator Core Method.
        Uses Python list comprehension to extract premium transactions above the threshold.
        """
        return [sale for sale in sales if sale.total_amount >= threshold]

    @staticmethod
    def extract_regular_sales(sales, threshold=50000.0):
        """
        Extract regular transactions below the threshold using list comprehension.
        """
        return [sale for sale in sales if sale.total_amount < threshold]

    @classmethod
    def aggregate_sales(cls, sales, threshold=50000.0):
        """
        Comprehensive financial and metric aggregation.
        """
        total_count = len(sales)
        total_revenue = sum(sale.total_amount for sale in sales)

        # Core list comprehension extraction as requested
        premium_sales = cls.extract_premium_sales(sales, threshold)
        regular_sales = cls.extract_regular_sales(sales, threshold)

        premium_revenue = sum(sale.total_amount for sale in premium_sales)
        regular_revenue = sum(sale.total_amount for sale in regular_sales)
        premium_count = len(premium_sales)
        regular_count = len(regular_sales)

        avg_transaction_value = (total_revenue / total_count) if total_count > 0 else 0.0
        premium_avg_value = (premium_revenue / premium_count) if premium_count > 0 else 0.0
        regular_avg_value = (regular_revenue / regular_count) if regular_count > 0 else 0.0

        highest_sale = max(sales, key=lambda s: s.total_amount) if sales else None
        lowest_sale = min(sales, key=lambda s: s.total_amount) if sales else None

        premium_revenue_pct = (premium_revenue / total_revenue * 100) if total_revenue > 0 else 0.0
        regular_revenue_pct = (regular_revenue / total_revenue * 100) if total_revenue > 0 else 0.0
        premium_volume_pct = (premium_count / total_count * 100) if total_count > 0 else 0.0

        # Sort top transactions
        sorted_by_value = sorted(sales, key=lambda s: s.total_amount, reverse=True)
        top_premium_deals = sorted(premium_sales, key=lambda s: s.total_amount, reverse=True)[:5]
        top_5_all = sorted_by_value[:5]

        # Category breakdown
        category_revenue = defaultdict(float)
        category_counts = defaultdict(int)
        for s in sales:
            category_revenue[s.category] += s.total_amount
            category_counts[s.category] += 1

        # Sorted category summary
        category_summary = [
            {
                'category': cat,
                'revenue': round(rev, 2),
                'count': category_counts[cat],
                'share_pct': round((rev / total_revenue * 100), 1) if total_revenue > 0 else 0.0
            }
            for cat, rev in sorted(category_revenue.items(), key=lambda x: x[1], reverse=True)
        ]

        # Monthly breakdown (last 6-12 months)
        monthly_data = defaultdict(lambda: {'revenue': 0.0, 'count': 0, 'premium_revenue': 0.0})
        for s in sales:
            month_key = s.transaction_date.strftime('%Y-%m')
            monthly_data[month_key]['revenue'] += s.total_amount
            monthly_data[month_key]['count'] += 1
            if s.total_amount >= threshold:
                monthly_data[month_key]['premium_revenue'] += s.total_amount

        sorted_months = sorted(monthly_data.keys())
        monthly_summary = [
            {
                'month': m,
                'label': datetime.strptime(m, '%Y-%m').strftime('%b %Y'),
                'revenue': round(monthly_data[m]['revenue'], 2),
                'premium_revenue': round(monthly_data[m]['premium_revenue'], 2),
                'count': monthly_data[m]['count']
            }
            for m in sorted_months
        ]

        return {
            'total_count': total_count,
            'total_revenue': round(total_revenue, 2),
            'threshold': float(threshold),
            'premium_count': premium_count,
            'premium_revenue': round(premium_revenue, 2),
            'regular_count': regular_count,
            'regular_revenue': round(regular_revenue, 2),
            'avg_transaction_value': round(avg_transaction_value, 2),
            'premium_avg_value': round(premium_avg_value, 2),
            'regular_avg_value': round(regular_avg_value, 2),
            'highest_sale': highest_sale,
            'lowest_sale': lowest_sale,
            'premium_revenue_pct': round(premium_revenue_pct, 1),
            'regular_revenue_pct': round(regular_revenue_pct, 1),
            'premium_volume_pct': round(premium_volume_pct, 1),
            'top_premium_deals': top_premium_deals,
            'top_5_all': top_5_all,
            'category_summary': category_summary,
            'monthly_summary': monthly_summary
        }

    @staticmethod
    def filter_sales(user_id, search_query=None, category=None, date_from=None, date_to=None,
                     sale_type=None, sort_by='date_desc', threshold=50000.0):
        """
        Query and filter user transactions securely with sorting and criteria.
        """
        query = Sale.query.filter_by(user_id=user_id)

        if search_query:
            term = f"%{search_query.strip()}%"
            query = query.filter(
                (Sale.product_name.ilike(term)) |
                (Sale.customer_name.ilike(term)) |
                (Sale.description.ilike(term))
            )

        if category and category != 'All':
            query = query.filter(Sale.category == category)

        if date_from:
            if isinstance(date_from, str):
                try:
                    date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                except ValueError:
                    date_from = None
            if date_from:
                query = query.filter(Sale.transaction_date >= date_from)

        if date_to:
            if isinstance(date_to, str):
                try:
                    date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                except ValueError:
                    date_to = None
            if date_to:
                query = query.filter(Sale.transaction_date <= date_to)

        if sale_type == 'premium':
            query = query.filter(Sale.total_amount >= threshold)
        elif sale_type == 'regular':
            query = query.filter(Sale.total_amount < threshold)

        # Sorting
        if sort_by == 'date_asc':
            query = query.order_by(Sale.transaction_date.asc(), Sale.id.asc())
        elif sort_by == 'amount_desc':
            query = query.order_by(Sale.total_amount.desc())
        elif sort_by == 'amount_asc':
            query = query.order_by(Sale.total_amount.asc())
        elif sort_by == 'name_asc':
            query = query.order_by(Sale.product_name.asc())
        elif sort_by == 'name_desc':
            query = query.order_by(Sale.product_name.desc())
        else: # default date_desc
            query = query.order_by(Sale.transaction_date.desc(), Sale.id.desc())

        return query

    @staticmethod
    def parse_and_import_csv(user_id, file_storage):
        """
        Safely import CSV rows into user's sales table.
        """
        content = file_storage.read().decode('utf-8-sig', errors='replace')
        csv_file = io.StringIO(content)
        reader = csv.DictReader(csv_file)

        imported = 0
        skipped = 0
        errors = []

        # Standard header mappings for flexibility
        header_map = {}
        if reader.fieldnames:
            for field in reader.fieldnames:
                clean = field.strip().lower().replace(' ', '_').replace('-', '_')
                header_map[clean] = field

        for row_num, row in enumerate(reader, start=2):
            try:
                # Helper to extract value flexibly
                def get_val(*keys, default=''):
                    for k in keys:
                        if k in header_map:
                            val = row.get(header_map[k], '')
                            if val:
                                return val.strip()
                        if k in row and row[k]:
                            return row[k].strip()
                    return default

                product_name = get_val('product_name', 'product', 'item', 'title')
                if not product_name:
                    skipped += 1
                    continue

                category = get_val('category', 'type', default='Cloud Infrastructure')
                quantity_str = get_val('quantity', 'qty', default='1')
                unit_price_str = get_val('unit_price', 'price', 'unit_cost', default='0').replace('$', '').replace(',', '')
                total_str = get_val('total_amount', 'total', 'amount', default='').replace('$', '').replace(',', '')
                date_str = get_val('transaction_date', 'date', 'trans_date', default='')
                description = get_val('description', 'notes', 'desc', default='')
                customer_name = get_val('customer_name', 'customer', 'client', default='Enterprise Client')
                status = get_val('status', default='Completed')

                quantity = max(1, int(float(quantity_str))) if quantity_str else 1
                unit_price = max(0.0, float(unit_price_str)) if unit_price_str else 0.0

                if total_str:
                    try:
                        total_amount = float(total_str)
                    except ValueError:
                        total_amount = quantity * unit_price
                else:
                    total_amount = quantity * unit_price

                # Parse date
                trans_date = date.today()
                if date_str:
                    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'):
                        try:
                            trans_date = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            pass

                sale = Sale(
                    user_id=user_id,
                    product_name=product_name[:150],
                    category=category[:80],
                    quantity=quantity,
                    unit_price=round(unit_price, 2),
                    total_amount=round(total_amount, 2),
                    transaction_date=trans_date,
                    description=description,
                    customer_name=customer_name[:120],
                    status=status if status in ['Completed', 'Pending', 'Processing'] else 'Completed'
                )
                db.session.add(sale)
                imported += 1
            except Exception as e:
                skipped += 1
                errors.append(f"Row {row_num}: {str(e)}")

        if imported > 0:
            db.session.commit()

        return {'imported': imported, 'skipped': skipped, 'errors': errors[:5]}

    @staticmethod
    def export_sales_to_csv(sales, threshold=50000.0):
        """
        Generate CSV content with high-value classification flag.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            'Transaction ID',
            'Product Name',
            'Category',
            'Customer Name',
            'Quantity',
            'Unit Price (INR)',
            'Total Amount (INR)',
            'Is High Value (Premium)',
            'Transaction Date',
            'Status',
            'Description'
        ])

        for s in sales:
            writer.writerow([
                s.id,
                s.product_name,
                s.category,
                s.customer_name or 'N/A',
                s.quantity,
                f"{s.unit_price:.2f}",
                f"{s.total_amount:.2f}",
                'YES' if s.total_amount >= threshold else 'NO',
                s.transaction_date.strftime('%Y-%m-%d'),
                s.status,
                s.description or ''
            ])

        output.seek(0)
        return output.getvalue()

    @staticmethod
    def generate_sample_csv():
        """
        Generate standard sample CSV for download with Indian Rupee figures.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'product_name', 'category', 'customer_name', 'quantity', 'unit_price', 'total_amount', 'transaction_date', 'status', 'description'
        ])
        sample_rows = [
            ['Quantum Neural Processing Core', 'Enterprise AI', 'Apex Cybernetics India', 2, '485000.00', '970000.00', date.today().strftime('%Y-%m-%d'), 'Completed', 'Next-gen enterprise inference rack module.'],
            ['Zero-Trust Mesh Gateway V4', 'Cybersecurity', 'Nexus Defense Tech', 4, '125000.00', '500000.00', (date.today() - timedelta(days=2)).strftime('%Y-%m-%d'), 'Completed', 'Edge security endpoint license bundle.'],
            ['Cloud Multi-Region VPC License', 'Cloud Infrastructure', 'Starlight Media Mumbai', 1, '82000.00', '82000.00', (date.today() - timedelta(days=5)).strftime('%Y-%m-%d'), 'Completed', 'Monthly hyperscaler network fabric.'],
            ['SaaS Autonomous Ops Seat Pack', 'SaaS Subscriptions', 'Omni Corp Bangalore', 15, '12000.00', '180000.00', (date.today() - timedelta(days=7)).strftime('%Y-%m-%d'), 'Completed', 'Tier-3 seat expansion.'],
            ['AI Architecture Consulting Sprint', 'Consulting & Services', 'Hyperion Dynamics Delhi', 1, '350000.00', '350000.00', (date.today() - timedelta(days=10)).strftime('%Y-%m-%d'), 'Completed', 'Deep neural fine-tuning engagement.'],
            ['Edge Micro-Sensor Telemetry Pack', 'Hardware & Edge', 'Volt Logistics Pune', 10, '3500.00', '35000.00', (date.today() - timedelta(days=12)).strftime('%Y-%m-%d'), 'Completed', 'IoT fleet monitoring starter pack.']
        ]
        for row in sample_rows:
            writer.writerow(row)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def generate_pdf_report(user, sales, threshold=50000.0):
        """
        Generate executive PDF sales analytics report with ReportLab.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        agg = SalesService.aggregate_sales(sales, threshold)
        styles = getSampleStyleSheet()

        # Custom styles with dark navy / purple / cyan corporate color theme
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=15
        )
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor('#1e1b4b'),
            spaceBefore=14,
            spaceAfter=8
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#334155')
        )
        kpi_label_style = ParagraphStyle(
            'KpiLabel',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#64748b'),
            alignment=1
        )
        kpi_val_style = ParagraphStyle(
            'KpiVal',
            parent=styles['Heading3'],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#0f172a'),
            alignment=1
        )

        elements = []

        # Header section
        elements.append(Paragraph("HIGH VALUE SALES — EXECUTIVE INTELLIGENCE REPORT", title_style))
        curr_label = "INR (Rs)" if user.currency == '₹' else user.currency
        elements.append(Paragraph(
            f"Prepared for: <b>{user.company_name or user.username}</b> &nbsp;|&nbsp; Generated on: {datetime.now().strftime('%B %d, %Y - %H:%M UTC')} &nbsp;|&nbsp; Currency: {user.currency} ({curr_label})",
            subtitle_style
        ))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#6366f1'), spaceAfter=14))

        # KPI Metrics Grid (2 rows x 3 columns)
        curr = user.currency
        kpi_data = [
            [
                Paragraph("TOTAL REVENUE", kpi_label_style),
                Paragraph("PREMIUM REVENUE", kpi_label_style),
                Paragraph("REGULAR REVENUE", kpi_label_style)
            ],
            [
                Paragraph(f"{curr}{agg['total_revenue']:,.2f}", kpi_val_style),
                Paragraph(f"{curr}{agg['premium_revenue']:,.2f} ({agg['premium_revenue_pct']}%)", kpi_val_style),
                Paragraph(f"{curr}{agg['regular_revenue']:,.2f} ({agg['regular_revenue_pct']}%)", kpi_val_style)
            ],
            [
                Paragraph("TOTAL TRANSACTIONS", kpi_label_style),
                Paragraph("HIGH-VALUE DEALS (≥" + f"{curr}{threshold:,.0f})", kpi_label_style),
                Paragraph("AVG TRANSACTION VALUE", kpi_label_style)
            ],
            [
                Paragraph(f"{agg['total_count']:,}", kpi_val_style),
                Paragraph(f"{agg['premium_count']:,} deals ({agg['premium_volume_pct']}%)", kpi_val_style),
                Paragraph(f"{curr}{agg['avg_transaction_value']:,.2f}", kpi_val_style)
            ]
        ]

        kpi_table = Table(kpi_data, colWidths=[180, 180, 180])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 14))

        # Section: High-Value Sales Spotlight
        elements.append(Paragraph(f"Top High-Value Transactions (Threshold ≥ {curr}{threshold:,.2f})", section_style))

        premium_deals = agg['top_premium_deals']
        if premium_deals:
            spotlight_data = [[
                Paragraph("<b>Product / Service</b>", body_style),
                Paragraph("<b>Category</b>", body_style),
                Paragraph("<b>Customer</b>", body_style),
                Paragraph("<b>Date</b>", body_style),
                Paragraph("<b>Amount</b>", body_style)
            ]]
            for deal in premium_deals:
                spotlight_data.append([
                    Paragraph(deal.product_name, body_style),
                    Paragraph(deal.category, body_style),
                    Paragraph(deal.customer_name or 'N/A', body_style),
                    Paragraph(deal.transaction_date.strftime('%Y-%m-%d'), body_style),
                    Paragraph(f"<b>{curr}{deal.total_amount:,.2f}</b>", body_style)
                ])

            spotlight_table = Table(spotlight_data, colWidths=[150, 110, 120, 70, 90])
            spotlight_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ede9fe')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#4338ca')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(spotlight_table)
        else:
            elements.append(Paragraph("<i>No transactions currently meet or exceed the premium threshold.</i>", body_style))

        elements.append(Spacer(1, 14))

        # Section: Category Performance Summary
        elements.append(Paragraph("Category Performance Breakdown", section_style))
        cat_summary = agg['category_summary']
        if cat_summary:
            cat_data = [[
                Paragraph("<b>Category</b>", body_style),
                Paragraph("<b>Transactions</b>", body_style),
                Paragraph("<b>Total Revenue</b>", body_style),
                Paragraph("<b>Revenue Share</b>", body_style)
            ]]
            for c in cat_summary:
                cat_data.append([
                    Paragraph(c['category'], body_style),
                    Paragraph(str(c['count']), body_style),
                    Paragraph(f"{curr}{c['revenue']:,.2f}", body_style),
                    Paragraph(f"{c['share_pct']}%", body_style)
                ])

            cat_table = Table(cat_data, colWidths=[200, 100, 140, 100])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0f2fe')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0369a1')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(cat_table)

        elements.append(Spacer(1, 16))

        # Footer notes
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=8))
        elements.append(Paragraph(
            "Confidential & Proprietary — High Value Sales 3D Intelligence Platform. Powered by Python Flask & Three.js Analytics Engine.",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, textColor=colors.HexColor('#94a3b8'), alignment=1)
        ))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    def seed_demo_data(user_id):
        """
        Populate rich, realistic enterprise sales data in Indian Rupees (INR).
        """
        # Check if user already has data
        existing = Sale.query.filter_by(user_id=user_id).count()
        if existing >= 10:
            return 0

        today = date.today()
        demo_sales = [
            # High-value / Premium deals (>= Rs 50,000)
            ("Quantum Neural Inference Cluster", "Enterprise AI", 2, 450000.0, today - timedelta(days=1), "Apex AI Labs Mumbai", "Completed", "Multi-GPU neural inference node cluster."),
            ("Zero-Trust SASE Cloud Fabric", "Cybersecurity", 5, 120000.0, today - timedelta(days=3), "Fortress Financial Mumbai", "Completed", "Global zero-trust perimeter defense architecture."),
            ("HyperScale Kubernetes Mesh Tier 1", "Cloud Infrastructure", 1, 380000.0, today - timedelta(days=6), "Nebula Telecom Bangalore", "Completed", "Annual tier-1 container orchestration runtime."),
            ("Autonomous Sales Copilot Platform", "Enterprise AI", 12, 45000.0, today - timedelta(days=8), "Aegis Media Global Gurgaon", "Completed", "Seat license expansion for commercial operations."),
            ("Global Threat Detection Suite", "Cybersecurity", 1, 550000.0, today - timedelta(days=12), "Standard Security Group Delhi", "Completed", "Full enterprise telemetry & endpoint defense."),
            ("Bespoke AI Pipeline Implementation", "Consulting & Services", 1, 750000.0, today - timedelta(days=15), "Vanguard BioTech Hyderabad", "Completed", "30-day production neural pipeline deployment."),
            ("High-Frequency Analytics Edge Engine", "Data Analytics", 3, 180000.0, today - timedelta(days=19), "Sigma Quant Capital Chennai", "Completed", "Real-time streaming transaction analysis."),
            ("Titan Industrial IoT Hub Unit", "Hardware & Edge", 4, 95000.0, today - timedelta(days=23), "Helios Energy Pune", "Completed", "Ruggedized telemetry edge gateways."),
            ("Enterprise Sovereign Data Mesh", "Data Analytics", 1, 420000.0, today - timedelta(days=28), "Aura Life Sciences Ahmedabad", "Completed", "Federated data governance engine."),
            ("Dedicated Cloud Engineering Retainer", "Consulting & Services", 1, 350000.0, today - timedelta(days=34), "Zenith Mobility Kolkata", "Completed", "Q4 Cloud architecture consulting."),
            # Regular value sales (< Rs 50,000)
            ("Developer Sandbox Cloud Instance", "Cloud Infrastructure", 3, 6500.0, today - timedelta(days=2), "Starlight Devs Noida", "Completed", "Staging container instances."),
            ("API Security Scanner Seat", "Cybersecurity", 2, 14000.0, today - timedelta(days=4), "Pulse Media Jaipur", "Completed", "Automated code vulnerability scanner."),
            ("Business Intelligence Dashboard Pack", "Data Analytics", 1, 35000.0, today - timedelta(days=7), "Nova Studios Chandigarh", "Completed", "Executive visual telemetry templates."),
            ("SaaS Team Workspace - 10 Seats", "SaaS Subscriptions", 1, 22000.0, today - timedelta(days=10), "Veritas Legal Kochi", "Completed", "Monthly collaborative productivity tier."),
            ("Edge Telemetry Micro-Sensors (x10)", "Hardware & Edge", 2, 12500.0, today - timedelta(days=14), "Grid Logistics Indore", "Completed", "Smart sensor monitoring pack."),
            ("Cloud Storage Snapshot Backup 10TB", "Cloud Infrastructure", 1, 18000.0, today - timedelta(days=17), "Echo Gaming Surat", "Completed", "Cold storage archival backup block."),
            ("Basic SSL & Identity Verification", "Cybersecurity", 4, 4500.0, today - timedelta(days=21), "Blue Ridge App Lucknow", "Completed", "Wildcard domain TLS certification."),
            ("SaaS Customer Support Plugin", "SaaS Subscriptions", 2, 9500.0, today - timedelta(days=26), "Crestline Retail Nagpur", "Completed", "Omnichannel widget integration."),
            ("Data Pipeline Health Audit", "Consulting & Services", 1, 32000.0, today - timedelta(days=31), "Optima Healthcare Bhopal", "Completed", "Single-day architecture performance review."),
            ("Continuous Integration Runner Hours", "Cloud Infrastructure", 5, 4200.0, today - timedelta(days=37), "Kite Mobile Coimbatore", "Completed", "High-throughput build runner quota.")
        ]

        count = 0
        for name, cat, qty, price, dt, cust, status, desc in demo_sales:
            sale = Sale(
                user_id=user_id,
                product_name=name,
                category=cat,
                quantity=qty,
                unit_price=price,
                total_amount=round(qty * price, 2),
                transaction_date=dt,
                customer_name=cust,
                status=status,
                description=desc
            )
            db.session.add(sale)
            count += 1

        db.session.commit()
        return count
