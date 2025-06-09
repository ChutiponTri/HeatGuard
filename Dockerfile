# ใช้ base image ที่เป็น Python
FROM python:3.12-slim

# ตั้งค่า working directory
WORKDIR /app

# คัดลอกไฟล์จากเครื่องมาสู่ container
COPY requirements.txt /app/

# Copy the certificate file into the container
COPY cert/emqxsl-ca.crt /app/cert/emqxsl-ca.crt

# ติดตั้ง dependencies
RUN pip install -r requirements.txt

# คัดลอกไฟล์ทั้งหมดจากโปรเจคไปยัง container
COPY . /app/

# รันคำสั่ง collectstatic เพื่อรวบรวม static files
RUN python manage.py collectstatic --noinput

# คำสั่งสำหรับรัน Django
# CMD ["gunicorn", "heatstroke.asgi:application", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
