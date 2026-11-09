from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from forms import LoginForm, RegisterForm, ProfileForm
from services.sales_service import SalesService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user_identifier = form.username.data.strip()
        # Find by username or email
        user = User.query.filter(
            (User.username.ilike(user_identifier)) | (User.email.ilike(user_identifier))
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.username}! Accessing 3D Sales Matrix...", "success")
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash("Invalid username/email or password. Please verify your credentials.", "danger")

    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data.strip()).first()
        if existing_user:
            flash("Username is already taken. Please choose another.", "warning")
            return render_template('register.html', form=form)

        existing_email = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if existing_email:
            flash("Email is already registered. Please log in.", "warning")
            return render_template('register.html', form=form)

        new_user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            company_name=form.company_name.data.strip() or 'Aura Enterprise'
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        # Seed sample interactive data if checked
        if form.seed_sample_data.data:
            SalesService.seed_demo_data(new_user.id)

        login_user(new_user)
        flash("Account initialized successfully! Welcome to High Value Sales Intelligence.", "success")
        return redirect(url_for('dashboard.index'))

    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Session terminated securely. You have been logged out.", "info")
    return redirect(url_for('dashboard.landing'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Check username uniqueness if changed
        if form.username.data.strip() != current_user.username:
            chk = User.query.filter_by(username=form.username.data.strip()).first()
            if chk:
                flash("Username is already taken by another user.", "warning")
                return render_template('profile.html', form=form)
            current_user.username = form.username.data.strip()

        # Check email uniqueness if changed
        if form.email.data.strip().lower() != current_user.email:
            chk = User.query.filter_by(email=form.email.data.strip().lower()).first()
            if chk:
                flash("Email is already registered by another user.", "warning")
                return render_template('profile.html', form=form)
            current_user.email = form.email.data.strip().lower()

        current_user.company_name = form.company_name.data.strip() if form.company_name.data else ''
        current_user.currency = form.currency.data
        current_user.premium_threshold = float(form.premium_threshold.data)
        current_user.theme_accent = form.theme_accent.data

        if form.new_password.data:
            current_user.set_password(form.new_password.data)
            flash("Password updated successfully.", "info")

        db.session.commit()
        flash("Profile and analytics configuration updated successfully!", "success")
        return redirect(url_for('auth.profile'))

    return render_template('profile.html', form=form)
