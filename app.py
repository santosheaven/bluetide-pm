from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bluetide_pm.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    condition = db.Column(db.String(50), default='Good')
    photo_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    description = db.Column(db.Text)
    requested_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    
    # Relationships
    service = db.relationship('Service', backref='requests')
    property = db.relationship('Property', backref='service_requests')
    requester = db.relationship('User', backref='requests')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent service requests
    if current_user.is_admin:
        recent_requests = ServiceRequest.query.order_by(ServiceRequest.requested_date.desc()).limit(10).all()
    else:
        recent_requests = ServiceRequest.query.filter_by(requester_id=current_user.id).order_by(ServiceRequest.requested_date.desc()).limit(10).all()
    
    # Get unread notifications
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return render_template('dashboard.html', 
                         recent_requests=recent_requests,
                         unread_notifications=unread_notifications)

@app.route('/services')
@login_required
def services():
    services = Service.query.filter_by(is_active=True).all()
    return render_template('services.html', services=services)

@app.route('/request_service/<int:service_id>')
@login_required
def request_service_form(service_id):
    service = Service.query.get_or_404(service_id)
    properties = Property.query.filter_by(owner_id=current_user.id).all() if not current_user.is_admin else Property.query.all()
    return render_template('request_service.html', service=service, properties=properties)

@app.route('/submit_service_request', methods=['POST'])
@login_required
def submit_service_request():
    service_id = request.form['service_id']
    property_id = request.form['property_id']
    description = request.form['description']
    priority = request.form.get('priority', 'medium')
    
    service_request = ServiceRequest(
        service_id=service_id,
        property_id=property_id,
        requester_id=current_user.id,
        description=description,
        priority=priority
    )
    
    db.session.add(service_request)
    
    # Create notification for admins
    admins = User.query.filter_by(is_admin=True).all()
    for admin in admins:
        notification = Notification(
            user_id=admin.id,
            title='New Service Request',
            message=f'New {priority} priority service request from {current_user.username}'
        )
        db.session.add(notification)
    
    db.session.commit()
    flash('Service request submitted successfully!')
    return redirect(url_for('my_requests'))

@app.route('/my_requests')
@login_required
def my_requests():
    if current_user.is_admin:
        requests = ServiceRequest.query.order_by(ServiceRequest.requested_date.desc()).all()
    else:
        requests = ServiceRequest.query.filter_by(requester_id=current_user.id).order_by(ServiceRequest.requested_date.desc()).all()
    
    return render_template('my_requests.html', requests=requests)

@app.route('/inventory')
@login_required
def inventory():
    properties = Property.query.filter_by(owner_id=current_user.id).all() if not current_user.is_admin else Property.query.all()
    return render_template('inventory.html', properties=properties)

@app.route('/property/<int:property_id>/spaces')
@login_required
def property_spaces(property_id):
    property_obj = Property.query.get_or_404(property_id)
    spaces = Space.query.filter_by(property_id=property_id).all()
    return render_template('spaces.html', property=property_obj, spaces=spaces)

@app.route('/space/<int:space_id>/items')
@login_required
def space_items(space_id):
    space = Space.query.get_or_404(space_id)
    items = InventoryItem.query.filter_by(space_id=space_id).all()
    return render_template('items.html', space=space, items=items)

@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)

# Admin routes
@app.route('/admin/update_request_status', methods=['POST'])
@login_required
def update_request_status():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    request_id = request.form['request_id']
    new_status = request.form['status']
    
    service_request = ServiceRequest.query.get_or_404(request_id)
    service_request.status = new_status
    
    if new_status == 'completed':
        service_request.completed_date = datetime.utcnow()
    
    db.session.commit()
    
    # Notify requester
    notification = Notification(
        user_id=service_request.requester_id,
        title='Service Request Updated',
        message=f'Your service request status has been updated to: {new_status}'
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Request status updated successfully!')
    return redirect(url_for('my_requests'))

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@bluetide.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            
            # Create sample owner
            owner = User(
                username='owner1',
                email='owner1@example.com',
                password_hash=generate_password_hash('owner123'),
                is_admin=False
            )
            db.session.add(owner)
            
            db.session.commit()
            
            # Create sample property
            property1 = Property(
                name='Sunset Apartments',
                address='123 Main St, City, State 12345',
                owner_id=owner.id
            )
            db.session.add(property1)
            db.session.commit()
            
            # Create sample spaces
            spaces = [
                Space(name='Apartment 101', property_id=property1.id, description='2-bedroom unit'),
                Space(name='Lobby', property_id=property1.id, description='Main entrance lobby'),
                Space(name='Parking Garage', property_id=property1.id, description='Underground parking')
            ]
            
            for space in spaces:
                db.session.add(space)
            
            # Create sample services
            services = [
                Service(name='Plumbing Repair', category='Maintenance', description='Fix leaks, unclog drains, repair pipes'),
                Service(name='Electrical Work', category='Maintenance', description='Electrical repairs and installations'),
                Service(name='HVAC Service', category='Maintenance', description='Heating and cooling system maintenance'),
                Service(name='Cleaning Service', category='Cleaning', description='Professional cleaning services'),
                Service(name='Landscaping', category='Outdoor', description='Lawn care and garden maintenance'),
            ]
            
            for service in services:
                db.session.add(service)
            
            db.session.commit()
            
            # Create sample inventory items
            sample_items = [
                InventoryItem(
                    name='Sofa', 
                    description='Brown leather 3-seater sofa',
                    space_id=spaces[0].id,
                    condition='Good'
                ),
                InventoryItem(
                    name='Coffee Table', 
                    description='Glass top coffee table',
                    space_id=spaces[0].id,
                    condition='Excellent'
                ),
                InventoryItem(
                    name='Front Desk', 
                    description='Reception desk with drawers',
                    space_id=spaces[1].id,
                    condition='Good'
                ),
                InventoryItem(
                    name='Security Camera', 
                    description='CCTV camera in lobby',
                    space_id=spaces[1].id,
                    condition='Good'
                ),
                InventoryItem(
                    name='Parking Gate', 
                    description='Automated parking barrier',
                    space_id=spaces[2].id,
                    condition='Fair'
                ),
            ]
            
            for item in sample_items:
                db.session.add(item)
            
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)