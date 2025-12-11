**Hospitals need efficient systems to manage patients, doctors, appointments, and treatments. Currently, many hospitals use manual registers or disconnected software, which makes it difficult to manage records, avoid scheduling conflicts, and track patient history.**
**We build a Hospital Management System, an one stop web application that allows Admins, Doctors, and Patients to interact with the system based on their roles.**

# Roles & Functionalities

1. Admin (Hospital Staff)
   
-- Admin is the pre-existing superuser of the application
   
-- Can add, update, and delete doctor profiles (name, specialization, availability).

-- Can view and manage all appointments.

-- Can search for patients or doctors by name/specialization.

2. Doctor
   
-- Can log in to view assigned appointments.
   
-- Can mark a patient’s visit as completed and enter diagnosis & treatment notes.

-- Can view patient history (previous diagnoses & prescriptions).
   
3. Patient
   
-- Can register, log in, and update their profile.
   
-- Can search for doctors by specialization and availability.

-- Can book, reschedule, or cancel an appointment.

-- Can view their own appointment history and treatment details.
   
# Key Terminologies

-- Admin (Hospital Staff): A user with the highest level of access who manages doctors, appointments, and overall hospital data.

-- Doctor: A medical professional registered in the system who interacts with patients via the app.

-- Patient: A user who seeks medical care and interacts with doctors via the system.

-- Appointment: A scheduled meeting between a patient and a doctor for consultation or treatment.
**Attributes:**
* Patient ID
* Doctor ID
* Date
* Time
* Status (Booked/Completed/Cancelled).

-- Treatment: A record of medical care provided to a patient during an appointment.
**Attributes:**
* Appointment ID
* Diagnosis
* Prescription
* Notes.

  
-- Department/Specialization: A field of medical science in which a particular doctor is specialized in
**Attributes:**
* Department ID
* Department Name
* Description
* Doctors_registered

# Core Features

-- Admin functionalities:
* Admin dashboard must display total number of doctors, patients, and appointments.
* Admin should pre-exist in the app i.e. it must be created programmatically after the creation of the database. [No admin registration allowed]
* Admin can add/update doctor profiles.
* Admin can view all upcoming and past appointments.
* Admin can search for patients or doctors and view their details.
* Admin can edit doctor details such as name, specialization etc., and also patient info if needed.
* Admin can remove/blacklist doctors and patients from the system.
  
-- Doctor functionalities:
* Doctor’s dashboard must display upcoming appointments for the day/week.
* Doctor’s dashboard must show list of patients assigned to the doctor.
* Doctor's dashboard must have the option to mark appointments as Completed or Cancelled.
* Doctors can provide their availability for the next 7 days.
* Doctors can update patient treatment history like provide diagnosis, treatment and prescriptions.
  
-- Patient functionalities:
* Patients can register and login themselves on the app.
* Patients’ Dashboard must display all available specialization/departments
* Patients’ Dashboard must display availability of doctors for the coming 7 days (1 week) and patients can read doctors profiles.
* It must display upcoming appointments and their status.
* It must show past appointment history with diagnosis and prescriptions.
* Patients can edit their profile.
* Patients can book as well as cancel appointments with doctors.
  
-- Other core functionalities:
* Prevent multiple appointments at the same date and time for the same doctor.
* Update appointment status dynamically (Booked → Completed → Cancelled).
* Admin and Patient should be able to search for a specialization or by a doctor’s name
* Admin should be able to search patients by name, ID, or contact information.
* Store all completed appointment records for each patient.
* Include diagnosis, prescriptions, and doctor notes for each visit.
* Allow patients to view their own treatment history.
* Allow doctors to view the full history of their patients for informed consultation.
