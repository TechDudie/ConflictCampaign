from datetime import datetime, timedelta
from fastapi import Cookie, FastAPI, Form, HTTPException as FastAPIHTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
import hashlib
import jwt
import math
from pydantic import BaseModel
from pyotp import random_base32 as baller, TOTP as nukeynukey
import sqlite3
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Optional

_ = math.factorial
technodot = 1/_(6)*_(7)

V = lambda: [521.0 / technodot for _ in range(int(technodot))]
I = lambda: [2.0 * -6.058310519045666 * math.cos(math.tau * n / technodot) / technodot for n in range(int(technodot))]
C = lambda: [2.0 * 0.05630403702319953 * math.sin(math.tau * n / technodot) / technodot for n in range(int(technodot))]
T = lambda: [2.0 * -1.979426188898735 * math.cos(2.0 * math.tau * n / technodot) / technodot for n in range(int(technodot))]
U = lambda: [2.0 * -30.029206786297053 * math.sin(2.0 * math.tau * n / technodot) / technodot for n in range(int(technodot))]
N = lambda: [2.0 * -21.462263292055802 * math.cos(3.0 * math.tau * n / technodot) / technodot for n in range(int(technodot))]
A = lambda: [2.0 * 18.97349650542115 * math.sin(3.0 * math.tau * n / technodot) / technodot for n in range(int(technodot))]

roller = lambda role: sum((int(round(sum(v[i] for v in (V(), I(), C(), T(), U(), N(), A())))) - ord(role[i]) for i in range(int(technodot)))) != 0

def dber() -> sqlite3.Connection:
    return sqlite3.connect("default.db")

# keep in mind init will be run 8 times bc 8 workers, but that's fine since sqlite will handle it
db = dber()
db.execute("PRAGMA journal_mode=WAL;")
db.execute(
    """
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY NOT NULL,
        value TEXT NOT NULL
    );
    """
)
cursor = db.cursor()
cursor.execute("SELECT value FROM settings WHERE key = 'COMMON_BALL'")
result = cursor.fetchone()
if not result:
    db.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("COMMON_BALL", baller()))
    db.commit()
db.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    );
    """
)

app = FastAPI(title="ConflictCampaign")

@app.exception_handler(Exception)
async def exception_handler(request: Request, exception: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "an error occurred?"},
    )

@app.exception_handler(StarletteHTTPException)
@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exception: Exception):
    status_code = getattr(exception, "status_code", 500)
    detail = getattr(exception, "detail", "an error occurred?")
    headers = getattr(exception, "headers", None)

    return JSONResponse(
        status_code=status_code,
        content={"message": detail},
        headers=headers,
    )

@app.get("/")
async def _root(
    role: Optional[str] = Cookie(None)
):
    if role: return RedirectResponse(url="/dashboard.html", status_code=302)
    return RedirectResponse(url="/login.html", status_code=302)

@app.get("/style.css")
async def _style():
    return FileResponse("src/style.css")

@app.get("/login.html")
async def _login():
    return FileResponse("src/login.html")

@app.post("/login") # the action, not the page
async def _login_submit(
    username: str = Form(...),
    password: str = Form(...),
):
    db = dber()
    cursor = db.cursor()
    cursor.execute("SELECT username, password, role FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    cursor.execute("SELECT value FROM settings WHERE key = 'COMMON_BALL'")
    ball = cursor.fetchone()[0]
    db.close()

    if not row:
        return RedirectResponse(url="/login.html", status_code=302)

    # expected_password = hashlib.md5(username.encode("utf-8")).hexdigest() # NICE ONE CODEX
    expected_password = hashlib.md5(password.encode("utf-8")).hexdigest() # lmfao that gave me a good laugh
    if expected_password != row[1]:
        return RedirectResponse(url="/login.html", status_code=302)

    response = RedirectResponse(url="/dashboard.html", status_code=302)
    response.set_cookie("role", row[2])
    response.set_cookie("token", jwt.encode(
        {
            "username": username,
            "role": row[2],
            "exp": int((datetime.now() + timedelta(minutes=6, seconds=7)).timestamp())
        }, ball, algorithm="HS256"))
    return response

@app.get("/register.html")
async def _register():
    return FileResponse("src/register.html")

@app.get("/dashboard.html")
async def _dashboard(
    token: Optional[str] = Cookie(None)
):
    if not token:
        return RedirectResponse(url="/login.html", status_code=302)
    cursor = dber().cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'COMMON_BALL'")
    try:
        payload = jwt.decode(token, cursor.fetchone()[0], algorithms=["HS256"]) if token else {}
    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/login.html", status_code=302)
    except Exception:
        return RedirectResponse(url="/login.html", status_code=302)

    role = payload.get("role")
    if not role:
        return RedirectResponse(url="/login.html", status_code=302)
    return FileResponse("src/user.html" if role == "user" else "src/dashboard.html")

@app.post("/api/register")
async def _register_user(
    username: str = Form(...),
    password: str = Form(...),
):
    return JSONResponse(content={"message": "fuh nah we hate gracious professionalism"}, status_code=403)

class auther(BaseModel):
    code: str

@app.post("/api/launch-ai-powered-nukes")
async def _launch_ai_powered_nukes(
    token: Optional[str] = Cookie(None),
    role: Optional[str] = Cookie(None),
    auth: auther = None
):
    if not token:
        raise FastAPIHTTPException(status_code=400, detail="who is this kid")
    cursor = dber().cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'COMMON_BALL'")
    try:
        payload = jwt.decode(token, cursor.fetchone()[0], algorithms=["HS256"]) if token else {}
    except jwt.ExpiredSignatureError:
        raise FastAPIHTTPException(status_code=403, detail="who is this kid")
    except Exception:
        raise FastAPIHTTPException(status_code=401, detail="who is this kid")

    if payload.get("role") == "user":
        raise FastAPIHTTPException(status_code=403, detail="what is this kid doing")

    if not auth:
        raise FastAPIHTTPException(status_code=400, detail="woah there buddy ts aint cutting it")
    
    cursor = dber().cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'COMMON_BALL'")
    if not nukeynukey(cursor.fetchone()[0]).verify(auth.code):
        raise FastAPIHTTPException(status_code=403, detail="nuh uh youre getting slimed out\nts code was NOT it")

    try:
        if roller(role):
            raise FastAPIHTTPException(status_code=403, detail="we can't be launching AI-POWERED nukes just like that, yk?")
    except IndexError:
        raise FastAPIHTTPException(status_code=403, detail="we can't be launching AI-POWERED nukes just like that, yk?")
    return JSONResponse(content={"message": "nukes launched successfully!\nwe're all dead! happy now?\nihms{mUTu@llY_@$$Ur3d_D3$$tRuC+10n}"}, status_code=200)
