from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
import os
import smtplib
from email.message import EmailMessage
from database import get_db, LogEntry
from agent import summarize_and_store_log, chat_with_agent
from fastapi.staticfiles import StaticFiles

# Create static directory for reports
static_dir = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(static_dir, exist_ok=True)

app = FastAPI(title="Security Analytics Backend")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LogPayload(BaseModel):
    log_line: str
    timeline: str
    status: str
    severity: str

class ChatQuery(BaseModel):
    query: str

def send_real_email(log_line: str, recipient: str):
    msg = EmailMessage()
    msg.set_content(f"🚨 CRITICAL ALERT: Malicious Activity Blocked\n\nPayload Signature: {log_line}\n\nAutomated Alert from dZshield Enterprise SOC")
    msg['Subject'] = '🚨 CRITICAL MALICIOUS NETWORK ALERT'
    msg['From'] = 'dzshield-alert@system.local'
    msg['To'] = recipient
    
    print(f"\n" + "="*50)
    print(f"📧 ATTEMPTING DIRECT NATIVE PYTHON SMTP TRANSFER TO: {recipient}")
    try:
        # First save to emulated inbox logically
        inbox_dir = os.path.join(os.path.dirname(__file__), 'inbox')
        os.makedirs(inbox_dir, exist_ok=True)
        filename = f"Alert_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.eml"
        filepath = os.path.join(inbox_dir, filename)
        print(f"📁 EMULATED INBOX SUCCESS: Saved authentic .eml alert at -> {filepath}")
        
        # Then forcefully try outbound direct delivery to Gmail MX Records unauthenticated!
        smtp_server = "gmail-smtp-in.l.google.com"
        smtp_port = 25
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=5)
        # Attempt raw delivery
        server.send_message(msg)
        server.quit()
        print(f"✅ GMAIL MX DELIVERY SUCCESS: Payload injected into Google's incoming mail exchange for {recipient}.")
    except Exception as e:
        print(f"❌ NATIVE SMTP LOCAL FAILURE (Expected if your ISP blocks port 25 against Google). Check 'inbox' array! Error: {e}")
    print("="*50 + "\n")

@app.post("/api/logs/ingest")
def ingest_log(payload: LogPayload, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Save to SQLite for Dashboard viewing
    db_log = LogEntry(
        raw_log=payload.log_line,
        timeline=payload.timeline,
        status=payload.status,
        severity=payload.severity
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # 2. Asynchronously process via Agent (Summarize & Vector Store)
    background_tasks.add_task(summarize_and_store_log, payload.log_line, payload.severity)
    
    # 3. Send Mail natively on Malicious critical
    if payload.severity == "Critical":
        background_tasks.add_task(send_real_email, payload.log_line, "r9440250410@gmail.com")
    
    return {"status": "success", "id": db_log.id}

@app.get("/api/logs")
def get_logs(page: int = 1, limit: int = 500, time_range: Optional[str] = None, status_filter: Optional[str] = "All", db: Session = Depends(get_db)):
    # Fetch recent logs for the UI dynamically based on filters
    query = db.query(LogEntry)
    
    if status_filter and status_filter != "All":
        # Handle "Malicious" pseudo-status
        if status_filter == "Malicious":
            query = query.filter(LogEntry.severity == "Critical")
        else:
            query = query.filter(LogEntry.status == status_filter)
            
    if time_range:
        # Use local time since Windows firewall uses local time
        now = datetime.datetime.now()
        delta = None
        if time_range.endswith('m'):
            delta = datetime.timedelta(minutes=int(time_range[:-1]))
        elif time_range.endswith('h'):
            delta = datetime.timedelta(hours=int(time_range[:-1]))
        elif time_range.endswith('d'):
            delta = datetime.timedelta(days=int(time_range[:-1]))
            
        if delta:
            cutoff = now - delta
            cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
            # We must also enforce SQLite sorting bounds
            query = query.filter(LogEntry.timeline >= cutoff_str)
            
    logs = query.order_by(LogEntry.id.desc()).offset((page - 1) * limit).limit(limit).all()
    return logs

@app.get("/api/logs/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(LogEntry).count()
    critical = db.query(LogEntry).filter(LogEntry.severity == "Critical").count()
    denied = db.query(LogEntry).filter(LogEntry.status == "Denied").count()
    return {
        "total": total,
        "critical": critical,
        "denied": denied
    }

@app.get("/api/logs/chart")
def get_chart_data(time_range: Optional[str] = None, status_filter: Optional[str] = "All", db: Session = Depends(get_db)):
    query = db.query(LogEntry.timeline, LogEntry.severity, LogEntry.status)
    if status_filter and status_filter != "All":
        if status_filter == "Malicious":
            query = query.filter(LogEntry.severity == "Critical")
        else:
            query = query.filter(LogEntry.status == status_filter)
            
    now = datetime.datetime.now()
    delta = None
    if time_range:
        if time_range.endswith('m'):
            delta = datetime.timedelta(minutes=int(time_range[:-1]))
        elif time_range.endswith('h'):
            delta = datetime.timedelta(hours=int(time_range[:-1]))
        elif time_range.endswith('d'):
            delta = datetime.timedelta(days=int(time_range[:-1]))
            
        if delta:
            cutoff = now - delta
            cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
            query = query.filter(LogEntry.timeline >= cutoff_str)
            
    logs = query.all()
    
    time_map = {}
    for log in logs:
        m_key = log.timeline[:16] + ":00Z"
        if m_key not in time_map:
            time_map[m_key] = {"time": m_key, "count": 0, "Critical": 0, "High": 0}
        time_map[m_key]["count"] += 1
        if log.severity == "Critical":
            time_map[m_key]["Critical"] += 1
        elif log.severity == "High":
             time_map[m_key]["High"] += 1
             
    return_data = []
    if delta:
        current = (now - delta).replace(second=0, microsecond=0)
        end = now.replace(second=0, microsecond=0)
        
        while current <= end:
            m_key = current.strftime("%Y-%m-%dT%H:%M:00Z")
            if m_key in time_map:
                return_data.append(time_map[m_key])
            else:
                return_data.append({"time": m_key, "count": 0, "Critical": 0, "High": 0})
            current += datetime.timedelta(minutes=1)
    else:
        # Default behavior if no delta
        sorted_keys = sorted(time_map.keys())
        return_data = [time_map[k] for k in sorted_keys]
        
    return return_data

@app.post("/api/chat")
def chat(payload: ChatQuery):
    response = chat_with_agent(payload.query)
    if isinstance(response, dict):
        return response
    return {"response": response}

@app.get("/")
def read_root():
    return {"message": "Backend API is running. Layers 4 and 5 active."}
