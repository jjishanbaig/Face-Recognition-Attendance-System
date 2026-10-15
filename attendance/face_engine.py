import cv2, numpy as np
from django.conf import settings
from django.utils import timezone
from .models import Employee, AttendanceRecord
FACE_DIR=settings.MEDIA_ROOT/"faces"
MODEL_DIR=settings.BASE_DIR/"trained_model"
MODEL_PATH=MODEL_DIR/"lbph.yml"
LABELS_PATH=MODEL_DIR/"labels.npy"
def detector():
    d=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
    if d.empty(): raise RuntimeError("OpenCV Haar cascade could not be loaded.")
    return d
def save_sample(code, raw):
    img=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
    if img is None: raise ValueError("Invalid camera image.")
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces=detector().detectMultiScale(gray,1.2,5,minSize=(90,90))
    if not len(faces): raise ValueError("No face detected. Improve lighting and move closer.")
    x,y,w,h=max(faces,key=lambda b:b[2]*b[3]); crop=cv2.resize(gray[y:y+h,x:x+w],(200,200))
    folder=FACE_DIR/code; folder.mkdir(parents=True,exist_ok=True)
    p=folder/f"face_{len(list(folder.glob('*.jpg')))+1:04d}.jpg"
    if not cv2.imwrite(str(p),crop): raise RuntimeError("Could not save sample.")
    return len(list(folder.glob("*.jpg")))
def train():
    if not hasattr(cv2,"face"): raise RuntimeError("LBPH unavailable: install opencv-contrib-python, not opencv-python.")
    images=[]; labels=[]; mapping={}
    for e in Employee.objects.all():
        folder=FACE_DIR/e.employee_id
        for p in (list(folder.glob("*.jpg")) if folder.exists() else []):
            img=cv2.imread(str(p),cv2.IMREAD_GRAYSCALE)
            if img is not None: images.append(cv2.resize(img,(200,200))); labels.append(e.pk); mapping[e.pk]=e.employee_id
    if len(images)<2 or not labels: raise ValueError("Capture at least two face samples before training.")
    model=cv2.face.LBPHFaceRecognizer_create(); model.train(images,np.array(labels,dtype=np.int32))
    MODEL_DIR.mkdir(parents=True,exist_ok=True); model.write(str(MODEL_PATH)); np.save(LABELS_PATH,mapping)
    return len(images),len(mapping)
def recognize(raw):
    if not MODEL_PATH.exists(): raise ValueError("Train the model first.")
    img=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
    if img is None: raise ValueError("Invalid camera image.")
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY); faces=detector().detectMultiScale(gray,1.2,5,minSize=(90,90))
    model=cv2.face.LBPHFaceRecognizer_create(); model.read(str(MODEL_PATH)); mapping=np.load(LABELS_PATH,allow_pickle=True).item()
    out=[]
    for x,y,w,h in faces:
        label,dist=model.predict(cv2.resize(gray[y:y+h,x:x+w],(200,200)))
        code=mapping.get(int(label)); emp=Employee.objects.filter(employee_id=code).first() if code else None
        if emp and dist<=72:
            rec,created=AttendanceRecord.objects.get_or_create(employee=emp,date=timezone.localdate(),defaults={"time":timezone.localtime().time().replace(microsecond=0)})
            out.append({"name":emp.full_name,"employee_id":emp.employee_id,"distance":round(float(dist),1),"status":"Attendance marked" if created else "Already marked today"})
        else: out.append({"name":"Unknown","employee_id":"","distance":round(float(dist),1),"status":"Not recognized"})
    if not out: out=[{"name":"No face detected","employee_id":"","distance":None,"status":"Move into camera view"}]
    return out
