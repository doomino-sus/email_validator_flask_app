# Użyj obrazu Python jako bazy
FROM python:3.10-slim

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj wszystkie pliki aplikacji do katalogu roboczego w kontenerze
COPY . /app

# Zainstaluj zależności aplikacji
RUN pip install --no-cache-dir -r requirements.txt

# Otwórz porty dla aplikacji webowej i SMTP (25, 465, 587)
EXPOSE 5001 25 465 587

# Ustaw zmienną środowiskową dla aplikacji Flask
ENV FLASK_APP=main.py

# Uruchom aplikację
CMD ["python", "main.py"]

# docker build -t APP_NAME-BUILD .

# sudo docker run -d \
#  -p 5001:5000 \
#  -p 25:25 \
#  -p 465:465 \
#  -p 587:587 \
#  --env-file .env \
#  --name APP_NAME-BUILD APP_NAME

# TRZEBA ZMIENIĆ ZMIENNE W PLIKU .env
# docker exec -it APP_NAME bash
# cd /app
# apt-get update
# apt-get install nano
# nano .env
# docker restart APP_NAME

