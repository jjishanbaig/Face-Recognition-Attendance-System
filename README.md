# Face Recognition Attendance System
Local-first Django + OpenCV attendance project. Features: admin login, employee CRUD, browser webcam face enrollment, LBPH training, webcam attendance recognition, daily duplicate prevention, attendance filters, CSV export.

## Windows setup
Python 3.10–3.13 recommended; Python 3.14 depends on compatible OpenCV wheels. OpenCV is constrained to 4.x because the face detector requires its packaged Haar cascade files.
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations attendance
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000, sign in, add employee, capture 10–20 samples, train model, then use Attendance Camera.
SQLite is configured by default to make local setup easy; MySQL can be added later.

## Important
This is an educational prototype, not production biometric security. LBPH accuracy varies with lighting, pose, and camera; no liveness detection is included, so a photo may fool it. Obtain informed consent, restrict access, and securely delete biometric samples when no longer needed. Keep db.sqlite3, media/, and trained_model/ private.
