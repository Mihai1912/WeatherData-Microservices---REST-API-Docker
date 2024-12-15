# SCD - Tema 2 - Microservicii & Docker

### Popescu Mihai-Costel 343C3

## Docker Compose

Acest fișier `docker-compose.yml` definește o configurație pentru a lansa un mediu de dezvoltare cu trei servicii interconectate: un API REST, o bază de date PostgreSQL și un instrument de administrare a bazei de date, pgAdmin.

---

## Servicii

### 1. **API REST**

Acest serviciu implementează un API REST, construit cu Flask.

#### Configurare:

- **Build**: Directorul `./api` este folosit pentru a construi imaginea Docker a serviciului.
- **Porturi**: Expune portul 5000 din container pe portul 5000 al host-ului.
- **Variabile de mediu**:
  - `DATABASE_URL`: Definiția URL-ului de conectare la baza de date PostgreSQL. Formatul este `postgresql://user:password@db/mydb`, unde `user` și `password` sunt credențialele bazei de date, `db` este numele serviciului de bază de date, iar `mydb` este numele bazei de date.
  - `FLASK_ENV`: Setează mediul de dezvoltare pentru aplicația Flask.
- **Volume**:
  - `./api:/app`: Montează directorul local `./api` în container la `/app`, astfel încât modificările făcute în aplicație pe host se reflectă imediat în container.
- **Depends_on**: Asigură că serviciul de API se va lansa doar după ce baza de date (serviciul `db`) este disponibilă.

### 2. **PostgreSQL**

Acest serviciu rulează o instanță PostgreSQL, care este utilizată ca bază de date pentru aplicația API.

#### Configurare:

- **Imagine**: Folosește imaginea oficială `postgres:13`.
- **Variabile de mediu**:
  - `POSTGRES_DB`: Numele bazei de date care va fi creată la pornirea containerului (în acest caz, `mydb`).
  - `POSTGRES_USER`: Numele de utilizator pentru accesul la baza de date (în acest caz, `user`).
  - `POSTGRES_PASSWORD`: Parola pentru utilizatorul `user` (în acest caz, `password`).
- **Volume**:
  - `db_data:/var/lib/postgresql/data`: Montează un volum Docker pentru a persista datele bazei de date, astfel încât acestea să nu se piardă la oprirea containerului.
  - `./init.sql:/docker-entrypoint-initdb.d/init.sql`: Montează fișierul local `init.sql` în container pentru a-l executa automat la prima inițializare a bazei de date, pentru a crea tabelele.

### 3. **pgAdmin**

pgAdmin este un instrument web pentru administrarea bazelor de date PostgreSQL, oferind o interfață grafică pentru vizualizarea și manipularea datelor.

#### Configurare:

- **Imagine**: Folosește imaginea oficială `dpage/pgadmin4`.
- **Variabile de mediu**:
  - `PGADMIN_DEFAULT_EMAIL`: Setează adresa de email de autentificare (în acest caz, `admin@example.com`).
  - `PGADMIN_DEFAULT_PASSWORD`: Setează parola de autentificare pentru pgAdmin (în acest caz, `adminpassword`).
- **Porturi**: Expune portul 80 din container pe portul 8081 al host-ului, astfel încât pgAdmin să fie accesibil la `http://localhost:8081`.
- **Depends_on**: Asigură că pgAdmin se va lansa doar după ce serviciul de bază de date (`db`) este disponibil.

---

## Volumes

- **db_data**: Un volum Docker care stochează datele persistente ale bazei de date PostgreSQL, astfel încât acestea să nu se piardă la oprirea sau recrearea containerelor.

---

## Descriere REST API

### 1. **GET /**

- Răspunde cu mesajul "Hello, World!".

### 2. **POST /api/countries**

- Adaugă o țară nouă în baza de date.
- Parametri necesari: `nume`, `lat`, `lon` (latitudine și longitudine).
- Răspunde cu ID-ul noii țări sau eroare dacă există deja.

### 3. **GET /api/countries**

- Obține toate țările din baza de date.
- Răspunde cu o listă de țări (ID, nume, latitudine, longitudine).

### 4. **PUT /api/countries/<int:id>**

- Actualizează o țară existentă (după ID).
- Parametri necesari: `nume`, `lat`, `lon`.
- Răspunde cu un mesaj de succes sau eroare (ex: dacă țara nu există).

### 5. **DELETE /api/countries/<int:id>**

- Șterge o țară din baza de date (după ID).
- Răspunde cu un mesaj de succes sau eroare (dacă țara nu există).

### 6. **POST /api/cities**

- Adaugă un oraș nou într-o țară.
- Parametri necesari: `nume`, `lat`, `lon`, `idTara` (ID-ul țării asociate).
- Răspunde cu ID-ul noii orașe sau eroare dacă există deja.

### 7. **GET /api/cities**

- Obține toate orașele din baza de date.
- Răspunde cu o listă de orașe (ID, nume, latitudine, longitudine, ID țară).

### 8. **GET /api/cities/country/<int:id>**

- Obține orașele dintr-o anumită țară (după ID-ul țării).
- Răspunde cu o listă de orașe asociate țării respective.

### 9. **PUT /api/cities/<int:id>**

- Actualizează un oraș existent (după ID).
- Parametri necesari: `nume`, `lat`, `lon`, `idTara`.
- Răspunde cu un mesaj de succes sau eroare.

### 10. **DELETE /api/cities/<int:id>**

- Șterge un oraș din baza de date (după ID).
- Răspunde cu un mesaj de succes sau eroare (dacă orașul nu există).

### 11. **POST /api/temperatures**

- Adaugă o temperatură pentru un oraș.
- Parametri necesari: `idOras` (ID oraș), `valoare` (temperatura).
- Răspunde cu ID-ul noii temperaturi sau eroare (ex: dacă orașul nu există).

### 12. **GET /api/temperatures**

- Obține temperaturile din toate orașele.
- Poate fi filtrat după latitudine, longitudine, și intervalul de timp (datele `from` și `until`).
- Răspunde cu o listă de temperaturi.

### 13. **GET /api/temperatures/cities/<int:idOras>**

- Obține temperaturile pentru un oraș specific (după ID-ul orașului).
- Poate fi filtrat după intervalul de timp (datele `from` și `until`).

### 14. **GET /api/temperatures/countries/<int:idTara>**

- Obține temperaturile pentru toate orașele dintr-o țară (după ID-ul țării).
- Poate fi filtrat după intervalul de timp (datele `from` și `until`).

### 15. **PUT /api/temperatures/<int:id>**

- Actualizează temperatura pentru o înregistrare existentă (după ID).
- Parametru necesar: `valoare` (noua temperatură).
- Răspunde cu un mesaj de succes sau eroare (dacă temperatura nu există).

### 16. **DELETE /api/temperatures/<int:id>**

- Șterge o temperatură din baza de date (după ID).
- Răspunde cu un mesaj de succes sau eroare (dacă temperatura nu există).

---

### Dockerfile

În esență, acest **Dockerfile** definește cum să construiești o imagine Docker pentru o aplicație Python Flask:

1. Utilizează o imagine de bază Python 3.9.
2. Setează directorul de lucru al containerului la `/app`.
3. Copiază fișierele aplicației tale în container.
4. Instalează toate dependențele din fișierul `requirements.txt` folosind `pip`.
5. Expune portul 5000 (unde Flask va asculta).
6. Rulează aplicația Flask (`app.py`) atunci când containerul este pornit.
