# Folosim imaginea oficială Python
FROM python:3.9

# Setăm directorul de lucru
WORKDIR /app

# Copiem fișierele necesare în container
COPY . /app

# Instalăm dependințele
RUN pip install --no-cache-dir -r requirements.txt

# Expunem portul pe care va rula aplicația
EXPOSE 5000

# Comanda pentru a porni aplicația
CMD ["python", "app.py"]
