from flask import Blueprint, render_template

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def home():
    """Home/Landing page"""
    return render_template('home.html')

@frontend_bp.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@frontend_bp.route('/signup')
def signup():
    """Signup page"""
    return render_template('signup.html')

@frontend_bp.route('/customer/dashboard')
def customer_dashboard():
    """Customer dashboard"""
    return render_template('customer/dashboard.html')

@frontend_bp.route('/provider/dashboard')
def provider_dashboard():
    """Provider dashboard"""
    return render_template('provider/dashboard.html')

