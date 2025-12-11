from flask import Flask
from config import Config
from models import db, Admin, Department
from routes import register_routes
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Register all routes
register_routes(app)

# Database initialization function
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin if not exists
        if not Admin.query.first():
            admin = Admin(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@hospital.com'
            )
            db.session.add(admin)
        
        # Create departments if not exist
        if Department.query.count() == 0:
            departments = [
                Department(name='Cardiology', description='Heart and cardiovascular system care'),
                Department(name='Neurology', description='Brain and nervous system treatment'),
                Department(name='Orthopedics', description='Bone and joint care'),
                Department(name='Pediatrics', description='Child healthcare'),
                Department(name='Dermatology', description='Skin care and treatment'),
                Department(name='General Medicine', description='General health consultation')
            ]
            db.session.add_all(departments)
        
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)