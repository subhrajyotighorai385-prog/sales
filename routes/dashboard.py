from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Sale
from services.sales_service import SalesService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def landing():
    """
    Futuristic 3D Landing Page with WebGL geometric scene, dynamic stats & CTAs.
    """
    # Fetch public or aggregate platform stats for landing page display
    total_platform_sales = Sale.query.count()
    return render_template('index.html', total_platform_sales=total_platform_sales)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Main Executive 3D Analytics Dashboard.
    """
    time_filter = request.args.get('range', 'all')
    threshold = current_user.premium_threshold or 50000.0

    today = date.today()
    date_from = None
    date_to = today

    if time_filter == 'today':
        date_from = today
    elif time_filter == '7days':
        date_from = today - timedelta(days=7)
    elif time_filter == '30days':
        date_from = today - timedelta(days=30)
    elif time_filter == 'this_month':
        date_from = date(today.year, today.month, 1)
    elif time_filter == 'custom':
        custom_from = request.args.get('from')
        custom_to = request.args.get('to')
        if custom_from:
            try:
                date_from = datetime.strptime(custom_from, '%Y-%m-%d').date()
            except ValueError:
                pass
        if custom_to:
            try:
                date_to = datetime.strptime(custom_to, '%Y-%m-%d').date()
            except ValueError:
                pass

    # Fetch user transactions according to date range
    query = Sale.query.filter_by(user_id=current_user.id)
    if date_from:
        query = query.filter(Sale.transaction_date >= date_from)
    if date_to:
        query = query.filter(Sale.transaction_date <= date_to)

    sales = query.order_by(Sale.transaction_date.desc(), Sale.id.desc()).all()

    # Aggregate using Python list comprehension service
    agg = SalesService.aggregate_sales(sales, threshold=threshold)

    # Recent transactions (top 8)
    recent_transactions = sales[:8]

    # Calculate growth comparison (compare current range to prior period if applicable)
    prior_revenue = 0.0
    if date_from:
        delta = (date_to - date_from).days or 1
        prior_from = date_from - timedelta(days=delta)
        prior_to = date_from - timedelta(days=1)
        prior_sales = Sale.query.filter(
            Sale.user_id == current_user.id,
            Sale.transaction_date >= prior_from,
            Sale.transaction_date <= prior_to
        ).all()
        prior_revenue = sum(s.total_amount for s in prior_sales)

    growth_pct = 0.0
    if prior_revenue > 0:
        growth_pct = round(((agg['total_revenue'] - prior_revenue) / prior_revenue) * 100, 1)
    elif agg['total_revenue'] > 0 and date_from:
        growth_pct = 100.0

    return render_template(
        'dashboard.html',
        agg=agg,
        sales=sales,
        recent_transactions=recent_transactions,
        time_filter=time_filter,
        date_from=date_from.strftime('%Y-%m-%d') if date_from else '',
        date_to=date_to.strftime('%Y-%m-%d') if date_to else '',
        growth_pct=growth_pct,
        threshold=threshold
    )


@dashboard_bp.route('/dashboard/load-demo-data', methods=['POST'])
@login_required
def load_demo_data():
    """
    Action to populate or restore interactive enterprise demo data.
    """
    added = SalesService.seed_demo_data(current_user.id)
    if added > 0:
        flash(f"Successfully generated {added} enterprise technology sales transactions!", "success")
    else:
        flash("Enterprise demo transactions are already active on your account.", "info")
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/dashboard/clear-data', methods=['POST'])
@login_required
def clear_data():
    """
    Action to wipe transactions for fresh testing / CSV imports.
    """
    deleted = Sale.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash(f"Cleared {deleted} transactions from your workspace.", "warning")
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/api/analytics')
@login_required
def api_analytics():
    """
    JSON API for live Chart.js and Three.js 3D graphics rendering.
    Uses real database transactions isolated per user.
    """
    threshold = current_user.premium_threshold or 50000.0
    sales = Sale.query.filter_by(user_id=current_user.id).order_by(Sale.transaction_date.asc()).all()

    agg = SalesService.aggregate_sales(sales, threshold=threshold)

    # 3D visualization data points (last 24 transactions or top ones)
    sorted_for_3d = sorted(sales, key=lambda s: s.transaction_date)[-30:]
    bars_3d = []
    for idx, s in enumerate(sorted_for_3d):
        bars_3d.append({
            'id': s.id,
            'product': s.product_name,
            'category': s.category,
            'amount': round(s.total_amount, 2),
            'date': s.transaction_date.strftime('%b %d'),
            'is_premium': s.total_amount >= threshold,
            'height': min(12.0, max(1.5, (s.total_amount / (agg['highest_sale'].total_amount if agg['highest_sale'] else 1.0)) * 10.0))
        })

    return jsonify({
        'status': 'success',
        'currency': current_user.currency,
        'threshold': threshold,
        'kpis': {
            'total_revenue': agg['total_revenue'],
            'total_count': agg['total_count'],
            'premium_revenue': agg['premium_revenue'],
            'premium_count': agg['premium_count'],
            'regular_revenue': agg['regular_revenue'],
            'regular_count': agg['regular_count'],
            'avg_transaction_value': agg['avg_transaction_value'],
            'highest_amount': agg['highest_sale'].total_amount if agg['highest_sale'] else 0.0,
            'premium_revenue_pct': agg['premium_revenue_pct'],
            'regular_revenue_pct': agg['regular_revenue_pct']
        },
        'categories': agg['category_summary'],
        'monthly': agg['monthly_summary'],
        'bars_3d': bars_3d
    })
