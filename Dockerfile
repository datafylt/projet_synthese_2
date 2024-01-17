FROM python:3.11.2

LABEL authors="Seedoo Ricardo"

WORKDIR /app

# Install libGL dependencies for OpenCV
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "./app.py"]