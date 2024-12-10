# Instrukcja instalacji aplikacji Email Validator

## 1. Wymagania systemowe

### 1.1. Wymagania oprogramowania
- Python 3.11 z zainstalowanym pip i virtualenv
- Git (do zarządzania kodem)
- Serwer SMTP do walidacji emaili

### 1.2. Wymagania dostępu
- Dostęp SSH do serwera
- Uprawnienia sudo (do instalacji pakietów systemowych)
- Dostęp do panelu zarządzania hostingiem

### 1.3. Wymagane umiejętności
- Podstawowa znajomość obsługi systemu Linux
- Umiejętność korzystania z wiersza poleceń
- Znajomość podstawowych poleceń Git
- Podstawowa znajomość konfiguracji serwerów WWW

### 1.4. Zalecane narzędzia
- Edytor tekstu z obsługą składni Python
- Terminal SSH z obsługą kluczy SSH
- Klient Git

## 2. Konfiguracja parametrów hostingu

### 2.1. Wymagane ustawienia serwera
- System operacyjny: Linux (zalecany Ubuntu 20.04 LTS lub nowszy)
- Minimalna ilość pamięci RAM: 1GB
- Przestrzeń dyskowa: minimum 1GB wolnego miejsca
- Dostęp do portów: 80, 443 (dla HTTPS) i 587 (dla SMTP)
- Skonfigurowany firewall z odpowiednimi regułami:
  - Reguły wejściowe: porty 80, 443 (HTTP/HTTPS)
  - Reguły wyjściowe: port 587 (SMTP)
  - Blokada pozostałych portów

### 2.2. Konfiguracja aplikacji w panelu hostingu
- Python version: 3.11 (wymagane)
- Application root: /home/boguu/domains/app.suseu.studio/public_html
- Application startup file: main.py
- Application Entry point: app:app
- Domena: Skonfiguruj domenę w panelu hostingu
- SSL/HTTPS: Zalecane włączenie dla bezpieczeństwa
- Zmienne środowiskowe: Skonfiguruj zgodnie z sekcją 5
- Automatyczny restart: Włącz po aktualizacji plików
- Monitoring:
  - Włącz monitorowanie użycia zasobów
  - Ustaw powiadomienia o błędach
  - Skonfiguruj rotację logów

### 2.3. Uprawnienia i dostęp
- Upewnij się, że użytkownik serwera ma uprawnienia do:
  - Odczytu i zapisu w katalogu aplikacji
  - Tworzenia i modyfikacji plików w katalogu /tmp
  - Dostępu do logów aplikacji
  - Zarządzania procesami Python
  - Konfiguracji SSL/HTTPS
- Ustaw odpowiednie uprawnienia CHMOD:
  - Katalogi: 755
  - Pliki Python: 644
  - Pliki konfiguracyjne (.env): 600
  - Logi: 644
- Zalecane ustawienia SELinux/AppArmor:
  - Włącz tryb wymuszania (enforcing)
  - Skonfiguruj profile dla aplikacji Python
  - Ogranicz dostęp do katalogu /tmp
  - Ustaw reguły dla połączeń sieciowych

## 3. Instalacja aplikacji

### 3.1. Aktywacja środowiska wirtualnego
```bash
source /home/boguu/virtualenv/domains/app.suseu.studio/public_html/3.11/bin/activate && cd /home/boguu/domains/app.suseu.studio/public_html
```

### 3.2. Instalacja wymaganych pakietów
```bash
pip install flask dnspython email-validator
```

### 3.3. Konfiguracja plików aplikacji
1. Skopiuj wszystkie pliki aplikacji do katalogu głównego:
   - app.py
   - main.py
   - email_validator.py
   - templates/
   - static/

2. Upewnij się, że struktura katalogów jest następująca (zwróć szczególną uwagę na plik .env, który jest kluczowy dla konfiguracji aplikacji):
```
/home/boguu/domains/app.suseu.studio/public_html/
├── app.py
├── main.py
├── email_validator.py
├── .env                # Plik konfiguracyjny ze zmiennymi środowiskowymi
├── templates/
│   ├── base.html
│   └── index.html
└── static/
    ├── css/
    │   └── custom.css
    └── js/
        └── main.js
```

3. Utwórz i skonfiguruj plik `.env` zgodnie z instrukcjami w sekcji 5.

## 4. Konfiguracja serwera SMTP

Do prawidłowego działania walidacji emaili, aplikacja wymaga dostępu do serwera SMTP. Wszystkie parametry połączenia są konfigurowane poprzez zmienne środowiskowe w pliku `.env`, który zostanie szczegółowo opisany w sekcji 5.

Upewnij się, że:
- Masz dostęp do serwera SMTP z obsługą TLS
- Port 587 (SMTP) jest otwarty i dostępny
- Posiadasz poprawne dane uwierzytelniające do serwera SMTP

## 5. Konfiguracja zmiennych środowiskowych

Utwórz plik `.env` w katalogu głównym aplikacji i ustaw odpowiednie uprawnienia:

```bash
touch .env
chmod 600 .env  # Ograniczenie dostępu tylko dla właściciela
```

Dodaj następujące zmienne środowiskowe do pliku `.env`. Każda z nich jest wymagana dla poprawnego działania aplikacji:

```env
# Klucz zabezpieczający sesje Flask
FLASK_SECRET_KEY=twoj_tajny_klucz_sesji

# Konfiguracja SMTP do walidacji adresów email
SMTP_HOST=smtp.twojserwer.pl      # Adres serwera SMTP
SMTP_PORT=587                      # Port SMTP (zazwyczaj 587 dla TLS)
SMTP_USER=twoj_uzytkownik         # Nazwa użytkownika SMTP
SMTP_PASSWORD=twoje_haslo         # Hasło do serwera SMTP
SMTP_USE_TLS=True                 # Użycie TLS (zalecane dla bezpieczeństwa)
SMTP_TIMEOUT=10                   # Timeout w sekundach dla połączeń SMTP

# Limity i ścieżki plików
MAX_CONTENT_LENGTH=16777216       # Maksymalny rozmiar pliku (16MB)
UPLOAD_FOLDER=/tmp               # Katalog na pliki tymczasowe

# Konfiguracja logowania
LOG_LEVEL=DEBUG                  # Poziom szczegółowości logów
LOG_FILE=/home/boguu/domains/app.suseu.studio/logs/app.log
```

### 5.1 Zabezpieczenie danych wrażliwych
- Upewnij się, że plik `.env` jest dodany do `.gitignore`
- Ustaw odpowiednie uprawnienia dla pliku `.env`:
```bash
chmod 600 .env
```
- Nie udostępniaj pliku `.env` osobom nieupoważnionym
- Regularnie zmieniaj hasła i klucze dostępowe
- Wykonaj kopię zapasową pliku .env w bezpiecznym miejscu
- Regularnie monitoruj logi aplikacji pod kątem nieautoryzowanych prób dostępu
- Używaj silnych, unikalnych haseł dla każdego serwera SMTP
- W środowisku produkcyjnym zmień domyślne wartości na bardziej bezpieczne

## 6. Uruchomienie aplikacji

Po wykonaniu wszystkich kroków:

1. W panelu hostingu ustaw parametry:
   - Python version: 3.11
   - Application root: /home/boguu/domains/app.suseu.studio/public_html
   - Application startup file: main.py
   - Application Entry point: app:app
   - Aplikacja będzie dostępna pod adresem URL skonfigurowanym w panelu hostingu

2. Zrestartuj aplikację w panelu hostingu

## 7. Weryfikacja instalacji

1. Otwórz adres URL aplikacji w przeglądarce
2. Przetestuj:
   - Walidację pojedynczego adresu email
   - Walidację wielu adresów z pliku CSV/TXT
   - Pobieranie wyników w formacie CSV i TXT

## 8. Rozwiązywanie problemów

### 8.1. Problemy z SMTP
- Sprawdź wartości zmiennych SMTP_* w pliku .env
- Zweryfikuj dostępność serwera SMTP pod adresem SMTP_HOST
- Upewnij się, że port SMTP (SMTP_PORT) jest otwarty i dostępny
- Sprawdź poprawność danych logowania (SMTP_USER, SMTP_PASSWORD)
- Przejrzyj logi aplikacji w trybie DEBUG dla szczegółowych informacji o błędach SMTP

### 8.2. Problemy z uprawnieniami
- Sprawdź uprawnienia do katalogu /tmp dla plików tymczasowych
- Ustaw odpowiednie uprawnienia dla katalogów aplikacji:
```bash
chmod -R 755 /home/boguu/domains/app.suseu.studio/public_html
```

### 8.3. Debugging
- Włącz debugowanie w main.py:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```
- Sprawdź logi aplikacji w ścieżce określonej w LOG_FILE (domyślnie: /home/boguu/domains/app.suseu.studio/logs/app.log)
- Monitoruj logi błędów serwera w katalogu logs hostingu
- W przypadku problemów z SMTP, sprawdź logi w DEBUG_LEVEL
