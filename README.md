# OrgoLife — Organ Donation Platform

A full-stack organ donation platform built with **FastAPI** (Python) + **MongoDB** (Motor) + a single-file HTML/CSS/JS frontend.

---

## Quick Start (Local)

### Prerequisites
- **Python 3.9+**
- **MongoDB** running locally on port `27017`  
  _or_ a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) free cluster URI

### Run in one command
```bash
cd orgolife
bash start.sh
```

Then open **http://localhost:8000** in your browser.

- Frontend SPA → `http://localhost:8000/`
- Swagger API Docs → `http://localhost:8000/api/docs`
- Health check → `http://localhost:8000/health`

---

## Manual Setup

```bash
cd orgolife

# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env .env.local         # Edit MONGODB_URL and JWT_SECRET_KEY

# 4. Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## MongoDB Atlas (Cloud)

Edit `.env` and set:
```
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=organ_donation_db
```

---

## Environment Variables (`.env`)

| Variable | Default | Description |
|---|---|---|
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection URI |
| `DATABASE_NAME` | `organ_donation_db` | Database name |
| `JWT_SECRET_KEY` | _(dev placeholder)_ | **Change in production!** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | JWT refresh token lifetime |
| `UPLOAD_DIR` | `uploads` | Directory for uploaded files |
| `MAX_FILE_SIZE_MB` | `5` | Max upload size per file |

---

## API Routes

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/register/admin` | — | Register hospital admin |
| POST | `/api/v1/auth/login/donor` | — | Donor login |
| POST | `/api/v1/auth/login/receiver` | — | Receiver login |
| POST | `/api/v1/auth/login/admin` | — | Admin login |
| POST | `/api/v1/auth/refresh` | — | Refresh access token |
| GET | `/api/v1/auth/me` | Bearer | Current user profile |
| POST | `/api/v1/donors/register` | — | Register donor + upload docs |
| POST | `/api/v1/donors/organs` | Donor | Register organ (step 2) |
| GET | `/api/v1/donors/profile` | Donor | Get donor profile |
| GET | `/api/v1/donors/documents` | Donor | Get document URLs |
| POST | `/api/v1/receivers/register` | — | Register receiver + upload docs |
| POST | `/api/v1/receivers/search` | Receiver | Search verified donors |
| GET | `/api/v1/receivers/profile` | Receiver | Get receiver profile |
| GET | `/api/v1/admin/hospital/profile` | Admin | Hospital profile |
| GET | `/api/v1/admin/donors` | Admin | List all donors (paginated) |
| GET | `/api/v1/admin/donors/{id}` | Admin | Full donor detail |
| POST | `/api/v1/admin/donors/approve` | Admin | Approve donor |
| POST | `/api/v1/admin/donors/reject` | Admin | Reject donor |

---

## Project Structure

```
orgolife/
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment config
├── start.sh                   # One-shot startup script
├── frontend/
│   └── index.html             # Single-page frontend (no build step)
├── uploads/                   # Uploaded documents (auto-created)
└── app/
    ├── api/routes/            # Route handlers
    ├── core/                  # Config, security, dependencies
    ├── db/                    # MongoDB connection + indexes
    ├── middleware/            # Error handler, request logger
    ├── models/                # MongoDB document factories
    ├── schemas/               # Pydantic request/response schemas
    ├── services/              # Business logic
    └── utils/                 # JWT, password, masking, pagination
```

---

## Roles

| Role | Portal | Capabilities |
|---|---|---|
| **Donor** | `/` → Donor tab | Register, upload docs, register organs, view profile |
| **Receiver** | `/` → Receiver tab | Register, search verified donors by organ/blood/location |
| **Hospital Admin** | `/` → Hospital tab | Register hospital, view all donors, approve/reject |
