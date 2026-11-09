from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response, send_file
from flask_login import login_required, current_user
from extensions import db
from models import Sale, CATEGORIES
from forms import TransactionForm
from services.sales_service import SalesService

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions')
@login_required
def index():
    """
    Transaction Management Directory with search, filters, sorting, and pagination.
    """
    page = request.args.get('page', 1, type=int)
    per_page = 12

    search_query = request.args.get('q', '').strip()
    category = request.args.get('category', 'All')
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    sale_type = request.args.get('type', 'all') # 'all', 'premium', 'regular'
    sort_by = request.args.get('sort', 'date_desc')

    threshold = current_user.premium_threshold or 50000.0

    query = SalesService.filter_sales(
        user_id=current_user.id,
        search_query=search_query,
        category=category,
        date_from=date_from,
        date_to=date_to,
        sale_type=sale_type,
        sort_by=sort_by,
        threshold=threshold
    )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    sales = pagination.items

    # Quick counters for current filter view
    all_user_sales = Sale.query.filter_by(user_id=current_user.id).all()
    user_agg = SalesService.aggregate_sales(all_user_sales, threshold=threshold)

    return render_template(
        'transactions.html',
        pagination=pagination,
        sales=sales,
        categories=['All'] + CATEGORIES,
        current_category=category,
        search_query=search_query,
        date_from=date_from,
        date_to=date_to,
        sale_type=sale_type,
        sort_by=sort_by,
        threshold=threshold,
        agg=user_agg
    )


@transactions_bp.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Create a new transaction record.
    """
    form = TransactionForm()
    threshold = current_user.premium_threshold or 50000.0

    if form.validate_on_submit():
        qty = form.quantity.data
        price = form.unit_price.data
        total_amount = round(qty * price, 2)

        sale = Sale(
            user_id=current_user.id,
            product_name=form.product_name.data.strip(),
            category=form.category.data,
            quantity=qty,
            unit_price=round(price, 2),
            total_amount=total_amount,
            transaction_date=form.transaction_date.data,
            customer_name=form.customer_name.data.strip() if form.customer_name.data else 'Enterprise Client',
            status=form.status.data,
            description=form.description.data.strip() if form.description.data else ''
        )
        db.session.add(sale)
        db.session.commit()

        is_prem = sale.total_amount >= threshold
        if is_prem:
            flash(f"High-Value Transaction recorded! ({current_user.currency}{sale.total_amount:,.2f}) — Classified as Premium Sale.", "success")
        else:
            flash(f"Transaction for '{sale.product_name}' successfully added.", "success")

        return redirect(url_for('transactions.index'))

    return render_template('add_transaction.html', form=form, threshold=threshold)


@transactions_bp.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit an existing transaction.
    """
    sale = Sale.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = TransactionForm(obj=sale)
    threshold = current_user.premium_threshold or 50000.0

    if form.validate_on_submit():
        sale.product_name = form.product_name.data.strip()
        sale.category = form.category.data
        sale.quantity = form.quantity.data
        sale.unit_price = round(form.unit_price.data, 2)
        sale.total_amount = round(sale.quantity * sale.unit_price, 2)
        sale.transaction_date = form.transaction_date.data
        sale.customer_name = form.customer_name.data.strip() if form.customer_name.data else 'Enterprise Client'
        sale.status = form.status.data
        sale.description = form.description.data.strip() if form.description.data else ''

        db.session.commit()
        flash(f"Transaction #{sale.id} updated successfully.", "success")
        return redirect(url_for('transactions.index'))

    return render_template('edit_transaction.html', form=form, sale=sale, threshold=threshold)


@transactions_bp.route('/transactions/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    Securely delete a transaction.
    """
    sale = Sale.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(sale)
    db.session.commit()
    flash(f"Transaction #{id} has been permanently deleted.", "info")
    return redirect(request.referrer or url_for('transactions.index'))


@transactions_bp.route('/transactions/<int:id>/json')
@login_required
def details_json(id):
    """
    JSON API for interactive detail modal.
    """
    sale = Sale.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return jsonify({
        'status': 'success',
        'sale': sale.to_dict(threshold=current_user.premium_threshold or 50000.0, currency=current_user.currency)
    })


@transactions_bp.route('/premium')
@login_required
def premium_aggregator():
    """
    Dedicated High-Value Sales Aggregator page showcasing list-comprehension based aggregation,
    dynamic threshold testing, and premium deal metrics.
    """
    # Allow temporary threshold query parameter for interactive dynamic simulation
    custom_threshold = request.args.get('threshold', type=float)
    threshold = custom_threshold if custom_threshold is not None else (current_user.premium_threshold or 1000.0)

    all_sales = Sale.query.filter_by(user_id=current_user.id).order_by(Sale.total_amount.desc()).all()

    # Core High-Value Aggregation via SalesService list comprehension
    agg = SalesService.aggregate_sales(all_sales, threshold=threshold)

    return render_template(
        'premium.html',
        agg=agg,
        threshold=threshold,
        user_threshold=current_user.premium_threshold or 50000.0
    )


@transactions_bp.route('/transactions/import-csv', methods=['POST'])
@login_required
def import_csv():
    """
    Upload and parse CSV file of sales transactions.
    """
    if 'csv_file' not in request.files:
        flash("No CSV file selected. Please choose a valid file.", "warning")
        return redirect(url_for('transactions.index'))

    file = request.files['csv_file']
    if file.filename == '':
        flash("No file was selected for upload.", "warning")
        return redirect(url_for('transactions.index'))

    if not file.filename.lower().endswith('.csv'):
        flash("Only standard .csv files are supported.", "danger")
        return redirect(url_for('transactions.index'))

    try:
        result = SalesService.parse_and_import_csv(current_user.id, file)
        if result['imported'] > 0:
            flash(f"Success! Imported {result['imported']} transactions into your dataset.", "success")
        if result['skipped'] > 0:
            flash(f"Skipped {result['skipped']} invalid or empty rows.", "info")
    except Exception as e:
        flash(f"Error processing CSV: {str(e)}", "danger")

    return redirect(url_for('transactions.index'))


@transactions_bp.route('/transactions/sample-csv')
def sample_csv():
    """
    Download sample template CSV for bulk importing.
    """
    content = SalesService.generate_sample_csv()
    return Response(
        content,
        mimetype='text/csv',
        headers={"Content-disposition": "attachment; filename=high_value_sales_sample_template.csv"}
    )


@transactions_bp.route('/transactions/export-csv')
@login_required
def export_csv():
    """
    Export current user's sales data to CSV with high-value classification flag.
    """
    category = request.args.get('category')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    sale_type = request.args.get('type')
    sort_by = request.args.get('sort', 'date_desc')

    threshold = current_user.premium_threshold or 50000.0

    sales = SalesService.filter_sales(
        user_id=current_user.id,
        category=category,
        date_from=date_from,
        date_to=date_to,
        sale_type=sale_type,
        sort_by=sort_by,
        threshold=threshold
    ).all()

    csv_data = SalesService.export_sales_to_csv(sales, threshold=threshold)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={"Content-disposition": f"attachment; filename=sales_export_{timestamp}.csv"}
    )


@transactions_bp.route('/transactions/export-pdf')
@login_required
def export_pdf():
    """
    Export executive intelligence PDF sales report.
    """
    threshold = current_user.premium_threshold or 50000.0
    sales = Sale.query.filter_by(user_id=current_user.id).order_by(Sale.transaction_date.desc()).all()

    if not sales:
        flash("No transactions found to generate report. Please add or load demo sales first.", "warning")
        return redirect(url_for('transactions.index'))

    pdf_buffer = SalesService.generate_pdf_report(current_user, sales, threshold=threshold)
    timestamp = datetime.now().strftime('%Y%m%d')

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"HighValueSales_Report_{current_user.username}_{timestamp}.pdf",
        mimetype='application/pdf'
    )


@transactions_bp.route('/reports')
@login_required
def reports():
    """
    Executive Reporting & Intelligence Hub.
    """
    threshold = current_user.premium_threshold or 50000.0
    sales = Sale.query.filter_by(user_id=current_user.id).order_by(Sale.transaction_date.desc()).all()
    agg = SalesService.aggregate_sales(sales, threshold=threshold)

    return render_template('reports.html', agg=agg, threshold=threshold)
