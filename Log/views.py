from .models import User
from flask import request, jsonify
from Log import app, db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        required_fields = ['email', 'name', 'mobile', 'city', 'password']
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({'error': f'Missing fields: {", ".join(missing_fields)} are required'}), 400
        
        # Validate email and mobile uniqueness
        existing_user = User.query.filter((User.email == data['email']) | (User.mobile == data['mobile'])).first()
        if existing_user:
            if existing_user.email == data['email']:
                return jsonify({'message': 'Email already exists'}), 400
            if existing_user.mobile == data['mobile']:
                return jsonify({'error': 'Mobile number already exists'}), 400
        
        # Additional input validation
        if '@' not in data['email'] or '.' not in data['email']:
            return jsonify({'error': 'Invalid email format'}), 400
        if not data['mobile'].isdigit() or len(data['mobile']) != 10:
            return jsonify({'error': 'Invalid mobile number: Must be 10 digits'}), 400
        if len(data['password']) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400

        # Create new user
        user = User(
            email=data['email'],
            name=data['name'],
            mobile=data['mobile'],
            city=data['city'],
            password_hash=generate_password_hash(data['password']),
            referral_code=str(uuid.uuid4())[:10]
        )

        # Handle referral
        if referral_code := data.get('referral_code'):
            referrer = User.query.filter_by(referral_code=referral_code).first()
            if not referrer:
                return jsonify({'error': 'Invalid referral code'}), 400
            user.referrer_id = referrer.id

        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'referral_code': user.referral_code,
            'user_id': user.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
            
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'message': 'Invalid credentials'}), 401
            
        return jsonify({
            'user_id': user.id,
            'email': user.email,
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/referrals/<int:user_id>', methods=['GET'])
def get_referrals(user_id):
    try:
        # Fetch the user by ID
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get all referees (users who used this user's referral code)
        referees = user.referees.all()
        
        # Format the response with explicit date and time
        result = [{
            'name': referee.name,
            'email': referee.email,
            'registration_date': referee.registered_at.strftime('%Y-%m-%d'),  # Date only
            'registration_time': referee.registered_at.strftime('%H:%M:%S'),  # Time only
        } for referee in referees]
        
        # Return the response with referral details and count
        return jsonify({
            'referrals': result,
            'total_referrals': len(result),
            'message': f'Referral details for user ID {user_id}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error fetching referrals: {str(e)}'}), 500

#  -------- Extra API's ---------------

@app.route('/users', methods=['GET'])
def get_all_users():
    # Query all users from the database
    users = User.query.all()
    users_list = [
        {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'referral_code': user.referral_code
        }
        for user in users
    ]
    return jsonify({'users': users_list}), 200