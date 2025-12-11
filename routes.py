from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from models import db, Admin, Department, Doctor, Patient, DoctorAvailability, Appointment, Treatment

# Decorator for login requirements
def login_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != role:
                flash('Please login to access this page', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def register_routes(app):
    """Register all application routes"""
    
    # Home and Authentication Routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')
            
            if role == 'admin':
                user = Admin.query.filter_by(email=email).first()
                if user and check_password_hash(user.password, password):
                    session['user_id'] = user.id
                    session['username'] = user.username
                    session['role'] = 'admin'
                    flash('Login successful!', 'success')
                    return redirect(url_for('admin_dashboard'))
            
            elif role == 'doctor':
                user = Doctor.query.filter_by(email=email, is_active=True).first()
                if user and check_password_hash(user.password, password):
                    session['user_id'] = user.id
                    session['username'] = user.name
                    session['role'] = 'doctor'
                    flash('Login successful!', 'success')
                    return redirect(url_for('doctor_dashboard'))
            
            elif role == 'patient':
                user = Patient.query.filter_by(email=email, is_active=True).first()
                if user and check_password_hash(user.password, password):
                    session['user_id'] = user.id
                    session['username'] = user.name
                    session['role'] = 'patient'
                    flash('Login successful!', 'success')
                    return redirect(url_for('patient_dashboard'))
            
            flash('Invalid credentials or account inactive', 'danger')
        
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            phone = request.form.get('phone')
            age = request.form.get('age')
            gender = request.form.get('gender')
            address = request.form.get('address')
            
            if Patient.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))
            
            new_patient = Patient(
                name=name,
                email=email,
                password=generate_password_hash(password),
                phone=phone,
                age=age,
                gender=gender,
                address=address
            )
            db.session.add(new_patient)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out successfully', 'success')
        return redirect(url_for('index'))

    # Admin Routes
    @app.route('/admin/dashboard')
    @login_required('admin')
    def admin_dashboard():
        total_doctors = Doctor.query.filter_by(is_active=True).count()
        total_patients = Patient.query.filter_by(is_active=True).count()
        total_appointments = Appointment.query.count()
        upcoming_appointments = Appointment.query.filter(
            Appointment.date >= datetime.now().date(),
            Appointment.status == 'Booked'
        ).order_by(Appointment.date, Appointment.time).limit(10).all()
        
        return render_template('admin/dashboard.html',
                             total_doctors=total_doctors,
                             total_patients=total_patients,
                             total_appointments=total_appointments,
                             upcoming_appointments=upcoming_appointments)

    @app.route('/admin/doctors')
    @login_required('admin')
    def admin_doctors():
        doctors = Doctor.query.filter_by(is_active=True).all()
        return render_template('admin/doctors.html', doctors=doctors)

    @app.route('/admin/doctor/add', methods=['GET', 'POST'])
    @login_required('admin')
    def admin_add_doctor():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            phone = request.form.get('phone')
            department_id = request.form.get('department_id')
            experience_years = request.form.get('experience_years')
            
            if Doctor.query.filter_by(email=email).first():
                flash('Email already exists', 'danger')
                return redirect(url_for('admin_add_doctor'))
            
            new_doctor = Doctor(
                name=name,
                email=email,
                password=generate_password_hash(password),
                phone=phone,
                department_id=department_id,
                experience_years=experience_years
            )
            db.session.add(new_doctor)
            db.session.commit()
            
            flash('Doctor added successfully!', 'success')
            return redirect(url_for('admin_doctors'))
        
        departments = Department.query.all()
        return render_template('admin/add_doctor.html', departments=departments)

    @app.route('/admin/doctor/edit/<int:id>', methods=['GET', 'POST'])
    @login_required('admin')
    def admin_edit_doctor(id):
        doctor = Doctor.query.get_or_404(id)
        
        if request.method == 'POST':
            doctor.name = request.form.get('name')
            doctor.phone = request.form.get('phone')
            doctor.department_id = request.form.get('department_id')
            doctor.experience_years = request.form.get('experience_years')
            
            db.session.commit()
            flash('Doctor updated successfully!', 'success')
            return redirect(url_for('admin_doctors'))
        
        departments = Department.query.all()
        return render_template('admin/edit_doctor.html', doctor=doctor, departments=departments)

    @app.route('/admin/doctor/delete/<int:id>')
    @login_required('admin')
    def admin_delete_doctor(id):
        doctor = Doctor.query.get_or_404(id)
        doctor.is_active = False
        db.session.commit()
        flash('Doctor removed successfully!', 'success')
        return redirect(url_for('admin_doctors'))

    @app.route('/admin/patients')
    @login_required('admin')
    def admin_patients():
        patients = Patient.query.filter_by(is_active=True).all()
        return render_template('admin/patients.html', patients=patients)

    @app.route('/admin/patient/edit/<int:id>', methods=['GET', 'POST'])
    @login_required('admin')
    def admin_edit_patient(id):
        patient = Patient.query.get_or_404(id)
        
        if request.method == 'POST':
            patient.name = request.form.get('name')
            patient.phone = request.form.get('phone')
            patient.age = request.form.get('age')
            patient.gender = request.form.get('gender')
            patient.address = request.form.get('address')
            
            db.session.commit()
            flash('Patient updated successfully!', 'success')
            return redirect(url_for('admin_patients'))
        
        return render_template('admin/edit_patient.html', patient=patient)

    @app.route('/admin/patient/delete/<int:id>')
    @login_required('admin')
    def admin_delete_patient(id):
        patient = Patient.query.get_or_404(id)
        patient.is_active = False
        db.session.commit()
        flash('Patient removed successfully!', 'success')
        return redirect(url_for('admin_patients'))

    @app.route('/admin/appointments')
    @login_required('admin')
    def admin_appointments():
        appointments = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
        return render_template('admin/appointments.html', appointments=appointments)

    @app.route('/admin/search', methods=['GET', 'POST'])
    @login_required('admin')
    def admin_search():
        if request.method == 'POST':
            search_type = request.form.get('search_type')
            search_query = request.form.get('search_query')
            
            results = []
            if search_type == 'doctor':
                results = Doctor.query.filter(
                    (Doctor.name.contains(search_query)) |
                    (Doctor.department.has(Department.name.contains(search_query)))
                ).filter_by(is_active=True).all()
            elif search_type == 'patient':
                results = Patient.query.filter(
                    (Patient.name.contains(search_query)) |
                    (Patient.phone.contains(search_query))
                ).filter_by(is_active=True).all()
            
            return render_template('admin/search.html', results=results, search_type=search_type, search_query=search_query)
        
        return render_template('admin/search.html')
    
    @app.route('/admin/patient/history/<int:id>')
    @login_required('admin')
    def admin_patient_history(id):
        patient = Patient.query.get_or_404(id)
        completed_appointments = Appointment.query.filter_by(
            patient_id=id,
            status='Completed'
        ).order_by(Appointment.date.desc()).all()
        
        return render_template('admin/patient_history.html', patient=patient, appointments=completed_appointments)

    # Doctor Routes
    @app.route('/doctor/dashboard')
    @login_required('doctor')
    def doctor_dashboard():
        doctor_id = session['user_id']
        today = datetime.now().date()
        week_later = today + timedelta(days=7)
        
        upcoming_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date >= today,
            Appointment.date <= week_later,
            Appointment.status == 'Booked'
        ).order_by(Appointment.date, Appointment.time).all()
        
        patients = Patient.query.join(Appointment).filter(
            Appointment.doctor_id == doctor_id
        ).distinct().all()
        
        return render_template('doctor/dashboard.html',
                             upcoming_appointments=upcoming_appointments,
                             patients=patients)

    @app.route('/doctor/appointments')
    @login_required('doctor')
    def doctor_appointments():
        doctor_id = session['user_id']
        appointments = Appointment.query.filter_by(doctor_id=doctor_id).order_by(
            Appointment.date.desc(), Appointment.time.desc()
        ).all()
        return render_template('doctor/appointments.html', appointments=appointments)

    @app.route('/doctor/appointment/complete/<int:id>', methods=['GET', 'POST'])
    @login_required('doctor')
    def doctor_complete_appointment(id):
        appointment = Appointment.query.get_or_404(id)
        
        if request.method == 'POST':
            diagnosis = request.form.get('diagnosis')
            prescription = request.form.get('prescription')
            notes = request.form.get('notes')
            
            appointment.status = 'Completed'
            
            treatment = Treatment(
                appointment_id=appointment.id,
                diagnosis=diagnosis,
                prescription=prescription,
                notes=notes
            )
            db.session.add(treatment)
            db.session.commit()
            
            flash('Appointment completed and treatment recorded!', 'success')
            return redirect(url_for('doctor_appointments'))
        
        return render_template('doctor/complete_appointment.html', appointment=appointment)

    @app.route('/doctor/appointment/cancel/<int:id>')
    @login_required('doctor')
    def doctor_cancel_appointment(id):
        appointment = Appointment.query.get_or_404(id)
        appointment.status = 'Cancelled'
        db.session.commit()
        flash('Appointment cancelled!', 'success')
        return redirect(url_for('doctor_appointments'))

    @app.route('/doctor/patient/<int:id>')
    @login_required('doctor')
    def doctor_patient_history(id):
        patient = Patient.query.get_or_404(id)
        appointments = Appointment.query.filter_by(
            patient_id=id,
            doctor_id=session['user_id'],
            status='Completed'
        ).order_by(Appointment.date.desc()).all()
        
        return render_template('doctor/patient_history.html', patient=patient, appointments=appointments)

    @app.route('/doctor/availability', methods=['GET', 'POST'])
    @login_required('doctor')
    def doctor_availability():
        doctor_id = session['user_id']
        
        if request.method == 'POST':
            today = datetime.now().date()
            DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doctor_id,
                DoctorAvailability.date >= today
            ).delete()
            
            for i in range(7):
                date_field = f'date_{i}'
                start_time_field = f'start_time_{i}'
                end_time_field = f'end_time_{i}'
                available_field = f'available_{i}'
                
                if request.form.get(available_field):
                    availability_date = datetime.strptime(request.form.get(date_field), '%Y-%m-%d').date()
                    start_time = request.form.get(start_time_field)
                    end_time = request.form.get(end_time_field)
                    
                    availability = DoctorAvailability(
                        doctor_id=doctor_id,
                        date=availability_date,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True
                    )
                    db.session.add(availability)
            
            db.session.commit()
            flash('Availability updated successfully!', 'success')
            return redirect(url_for('doctor_dashboard'))
        
        today = datetime.now().date()
        next_7_days = [today + timedelta(days=i) for i in range(7)]
        
        existing_availability = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date >= today
        ).all()
        
        availability_dict = {av.date: av for av in existing_availability}
        
        return render_template('doctor/availability.html',
                             next_7_days=next_7_days,
                             availability_dict=availability_dict)

    # Patient Routes
    @app.route('/patient/dashboard')
    @login_required('patient')
    def patient_dashboard():
        departments = Department.query.all()
        patient_id = session['user_id']
        
        today = datetime.now().date()
        upcoming_appointments = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.date >= today,
            Appointment.status == 'Booked'
        ).order_by(Appointment.date, Appointment.time).all()
        
        return render_template('patient/dashboard.html',
                             departments=departments,
                             upcoming_appointments=upcoming_appointments)
    
    @app.route('/patient/search')
    @login_required('patient')
    def patient_search():
        query = request.args.get('query', '').strip()
        results = []
        searched = False
        
        if query:
            searched = True
            results = Doctor.query.filter(
                (Doctor.name.contains(query)) |
                (Doctor.department.has(Department.name.contains(query)))
            ).filter_by(is_active=True).all()
        
        return render_template('patient/search.html', results=results, query=query, searched=searched)

    @app.route('/patient/doctors/<int:department_id>')
    @login_required('patient')
    def patient_doctors(department_id):
        department = Department.query.get_or_404(department_id)
        doctors = Doctor.query.filter_by(department_id=department_id, is_active=True).all()
        
        today = datetime.now().date()
        week_later = today + timedelta(days=7)
        
        doctor_availability = {}
        for doctor in doctors:
            availability = DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doctor.id,
                DoctorAvailability.date >= today,
                DoctorAvailability.date <= week_later,
                DoctorAvailability.is_available == True
            ).all()
            doctor_availability[doctor.id] = availability
        
        return render_template('patient/doctors.html',
                            department=department,
                            doctors=doctors,
                            doctor_availability=doctor_availability,
                            now=datetime.now(),
                            timedelta=timedelta)

    @app.route('/patient/book/<int:doctor_id>', methods=['GET', 'POST'])
    @login_required('patient')
    def patient_book_appointment(doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        
        if request.method == 'POST':
            date_str = request.form.get('date')
            time = request.form.get('time')
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check 1: If doctor slot is already booked at this specific time
            existing_doctor_time = Appointment.query.filter_by(
                doctor_id=doctor_id,
                date=appointment_date,
                time=time,
                status='Booked'
            ).first()
            
            if existing_doctor_time:
                flash('This doctor slot is already booked at this time. Please choose another time.', 'danger')
                return redirect(url_for('patient_book_appointment', doctor_id=doctor_id))
            
            # Check 2: If patient already has an appointment at this time (with any doctor)
            existing_patient_time = Appointment.query.filter_by(
                patient_id=session['user_id'],
                date=appointment_date,
                time=time,
                status='Booked'
            ).first()
            
            if existing_patient_time:
                flash('You already have an appointment at this time with another doctor. Please choose a different time.', 'danger')
                return redirect(url_for('patient_book_appointment', doctor_id=doctor_id))
            
            # Check 3: If patient already has an appointment with this doctor on this date (any time)
            existing_patient_doctor_date = Appointment.query.filter_by(
                patient_id=session['user_id'],
                doctor_id=doctor_id,
                date=appointment_date,
                status='Booked'
            ).first()
            
            if existing_patient_doctor_date:
                flash('You already have an appointment with this doctor on this date. Please choose a different date or cancel your existing appointment.', 'danger')
                return redirect(url_for('patient_book_appointment', doctor_id=doctor_id))
            
            # All checks passed - create the appointment
            new_appointment = Appointment(
                patient_id=session['user_id'],
                doctor_id=doctor_id,
                date=appointment_date,
                time=time,
                status='Booked'
            )
            db.session.add(new_appointment)
            db.session.commit()
            
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('patient_dashboard'))
        
        # GET request - get selected date from query parameter
        selected_date_str = request.args.get('selected_date')
        selected_slot = None
        time_slots = []
        
        today = datetime.now().date()
        week_later = today + timedelta(days=7)
        
        availability = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date >= today,
            DoctorAvailability.date <= week_later,
            DoctorAvailability.is_available == True
        ).all()
        
        # If a date is selected, generate time slots for that date
        if selected_date_str and availability:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            for slot in availability:
                if slot.date == selected_date:
                    selected_slot = slot
                    
                    # Generate 30-minute time slots
                    start_parts = slot.start_time.split(':')
                    end_parts = slot.end_time.split(':')
                    start_hour = int(start_parts[0])
                    start_min = int(start_parts[1]) if len(start_parts) > 1 else 0
                    end_hour = int(end_parts[0])
                    end_min = int(end_parts[1]) if len(end_parts) > 1 else 0
                    
                    current_hour = start_hour
                    current_min = start_min
                    
                    while current_hour < end_hour or (current_hour == end_hour and current_min < end_min):
                        time_24 = f"{current_hour:02d}:{current_min:02d}"
                        
                        # Convert to 12-hour format
                        if current_hour == 0:
                            display_time = f"12:{current_min:02d} AM"
                        elif current_hour < 12:
                            display_time = f"{current_hour}:{current_min:02d} AM"
                        elif current_hour == 12:
                            display_time = f"12:{current_min:02d} PM"
                        else:
                            display_time = f"{current_hour - 12}:{current_min:02d} PM"
                        
                        time_slots.append({'value': time_24, 'display': display_time})
                        
                        # Add 30 minutes
                        current_min += 30
                        if current_min >= 60:
                            current_min = 0
                            current_hour += 1
                    
                    break
        
        return render_template('patient/book_appointment.html', 
                            doctor=doctor, 
                            availability=availability,
                            selected_date=selected_date_str,
                            time_slots=time_slots)

    @app.route('/patient/appointments')
    @login_required('patient')
    def patient_appointments():
        patient_id = session['user_id']
        appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
            Appointment.date.desc(), Appointment.time.desc()
        ).all()
        return render_template('patient/appointments.html', appointments=appointments)

    @app.route('/patient/appointment/cancel/<int:id>')
    @login_required('patient')
    def patient_cancel_appointment(id):
        appointment = Appointment.query.get_or_404(id)
        
        if appointment.patient_id != session['user_id']:
            flash('Unauthorized access', 'danger')
            return redirect(url_for('patient_dashboard'))
        
        appointment.status = 'Cancelled'
        db.session.commit()
        flash('Appointment cancelled successfully!', 'success')
        return redirect(url_for('patient_appointments'))

    @app.route('/patient/history')
    @login_required('patient')
    def patient_history():
        patient_id = session['user_id']
        completed_appointments = Appointment.query.filter_by(
            patient_id=patient_id,
            status='Completed'
        ).order_by(Appointment.date.desc()).all()
        
        return render_template('patient/history.html', appointments=completed_appointments)

    @app.route('/patient/profile', methods=['GET', 'POST'])
    @login_required('patient')
    def patient_profile():
        patient = Patient.query.get_or_404(session['user_id'])
        
        if request.method == 'POST':
            patient.name = request.form.get('name')
            patient.phone = request.form.get('phone')
            patient.age = request.form.get('age')
            patient.gender = request.form.get('gender')
            patient.address = request.form.get('address')
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('patient_profile'))
        
        return render_template('patient/profile.html', patient=patient)
