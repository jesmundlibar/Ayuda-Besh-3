# routes/frontend.py

from flask import Blueprint, render_template
from lib.decorators import token_required

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def home():
    return render_template('home.html')

# ✅ Only handle GET requests (show login form)
@frontend_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@frontend_bp.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@frontend_bp.route('/customer/dashboard')
@token_required
def customer_dashboard():
    return render_template('customer/dashboard.html')

@frontend_bp.route('/provider/dashboard')
@token_required
def provider_dashboard():
    return render_template('provider/dashboard.html')