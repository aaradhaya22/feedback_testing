# Teacher Feedback System (TFS)

🟢 **Live Production App:** [View on Vercel](https://anonymous-feedback-i46i.vercel.app/)

A comprehensive Teacher Feedback System built with a **Django** backend and a **Next.js** frontend. This system allows for efficient collection, management, and analysis of student feedback for teachers.

## Project Structure

The repository is divided into two main components:

- **`Backend/`**: Django-based REST API.
- **`frontend-next/`**: Next.js-based web application.

---

## Tech Stack

### Backend
- **Framework**: Django 5.1+, Django REST Framework (DRF)
- **Database**: PostgreSQL (psycopg 3)
- **Authentication**: JWT (SimpleJWT)
- **Server**: Gunicorn, Whitenoise (for static files)
- **Tools**: python-dotenv, django-cors-headers

### Frontend
- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS, Framer Motion
- **UI Components**: Radix UI, Lucide Icons
- **Data Fetching**: Axios
- **Charts**: Recharts
- **PDF Generation**: jsPDF, jsPDF-AutoTable

---

## Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (running locally, e.g. PostgreSQL 18)

---

### 1. Backend Setup

```bash
cd Backend
```

#### Create & activate a virtual environment

The virtual environment lives in `Backend/venv`. If it does not exist yet, create it:

```bash
python -m venv venv
```

Activate it (must be done in every new terminal before running Django commands):

| OS | Command |
| --- | --- |
| Windows (PowerShell) | `.\venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.\venv\Scripts\activate.bat` |
| macOS / Linux | `source venv/bin/activate` |

> **Tip:** If `Activate.ps1` is blocked on Windows PowerShell, run
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then retry.

You should see `(venv)` at the start of your prompt.

#### Install dependencies

```bash
pip install -r requirements.txt
```

#### Configure environment variables

Copy the example file and edit the values:

```bash
cp .env.example .env
# Windows:
# copy .env.example .env
```

Then edit `.env` and set your real PostgreSQL credentials. See [Required Environment Variables](#required-environment-variables) below.

#### Run migrations

```bash
python manage.py migrate
```

> All Django commands must be run with the virtual environment active so they use the correct Python interpreter. You can also invoke it directly without activating: `.\venv\Scripts\python manage.py migrate`.

#### Start the backend server

```bash
python manage.py runserver
```

The API will be available at [http://localhost:8000](http://localhost:8000).

---

### 2. Frontend Setup

```bash
cd frontend-next
```

#### Install dependencies

```bash
npm install
```

#### Configure environment variables

```bash
cp .env.example .env
```

#### Start the frontend server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### Required Environment Variables

#### Backend (`Backend/.env`)

| Variable | Description | Example |
| --- | --- | --- |
| `DEBUG` | Django debug mode (`True` for development) | `True` |
| `DB_NAME` | PostgreSQL database name | `feedback_db` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `your_postgres_password` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DATABASE_URL` | *(Optional)* Full database URL. If set, overrides the `DB_*` variables above. | `postgres://postgres:pass@localhost:5432/feedback_db` |

#### Frontend (`frontend-next/.env`)

| Variable | Description | Example |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Base URL of the Django API | `http://localhost:8000` |

---

### Common Troubleshooting

- **`venv` is missing** — Run `python -m venv venv` inside `Backend/`, then activate it and run `pip install -r requirements.txt`.
- **`ModuleNotFoundError: No module named 'django'`** — The virtual environment is not active or is missing dependencies. Activate it (`.\venv\Scripts\Activate.ps1` on Windows, `source venv/bin/activate` on macOS/Linux) and run `pip install -r requirements.txt`.
- **`'python' is not recognized` / wrong Python used** — Use the venv interpreter directly: `.\Backend\venv\Scripts\python.exe manage.py ...` on Windows.
- **PostgreSQL connection issues** (`could not connect to server`, `password authentication failed`) —
  1. Make sure the PostgreSQL service is running (Windows: `Get-Service postgresql-x64-*`).
  2. Verify the host/port in `.env` match your install (default `localhost:5432`).
  3. Confirm `DB_USER`/`DB_PASSWORD` are correct. Reset the password if needed (see below).
  4. If `DATABASE_URL` is set in `.env`, it overrides `DB_*` — remove it unless intended.
- **PostgreSQL password reset** — Temporarily set auth to `trust` in `pg_hba.conf`, restart the service, run `ALTER USER postgres PASSWORD 'new_password';` via `psql`, restore `scram-sha-256`, and restart the service again (requires admin rights).
- **Database does not exist** — Create it: `createdb -U postgres feedback_db` (or run `python create_db.py` after configuring `.env`).
- **Port already in use** — `runserver` on 8000: `python manage.py runserver 8001`. Next.js on 3000: `npm run dev -- -p 3001`.
- **CORS / API not reachable from the frontend** — Make sure `NEXT_PUBLIC_API_URL` points to the running Django server (default `http://localhost:8000`) and that `http://localhost:3000` is in `CORS_ALLOWED_ORIGINS` in `Backend/feedbacksystem/settings.py`.
- **`npm install` fails** — Delete `node_modules` and `package-lock.json`, then run `npm install` again.

---

## Key Features & Analytics Engine

This platform includes a built-in **Data Science Engine** to ensure evaluations are driven by mathematical consensus rather than strict averages.

*   **Robust Statistics:** Utilizes a **Trimmed-Mean Estimator** to mathematically eliminate troll spam and rating biases.
*   **Variance Scoring:** Calculates dataset **Standard Deviation ($\sigma$)** to dynamically cap grades for unstable or highly polarized teachers.
*   **Unsupervised Anomaly Detection:** Establishes dynamic thresholds ($\mu - \sigma$) to automatically flag underperforming outliers relative to the college population.
*   **Data Reliability Gating:** Enforces **Statistical Significance** checks to discard low-volume, misleading datasets.
*   **Automated Reporting:** Real-time visual dashboards and automated PDF executive summaries using `jsPDF`.

---

## License

[Add License Information Here, e.g., MIT]
