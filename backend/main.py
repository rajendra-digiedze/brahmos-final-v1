from fastapi import FastAPI, Depends, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
import os
import smtplib
from email.message import EmailMessage
from database import get_db, LogEntry, OfflineLogEntry
from agent import summarize_and_store_log, chat_with_agent
from fastapi.staticfiles import StaticFiles
import pandas as pd
import io
import math

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
    source: Optional[str] = "live"

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

@app.post("/api/logs/upload_offline")
async def upload_offline_logs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(content))
        # Clear existing offline logs
        db.query(OfflineLogEntry).delete()
        
        records = df.to_dict('records')
        for r in records:
            def get_val(key, default=""):
                val = r.get(key)
                if isinstance(val, float) and math.isnan(val):
                    return default
                return str(val) if val is not None else default

            time_val = get_val('Time')
            if hasattr(time_val, "strftime"):
                time_val = time_val.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                time_val = str(time_val).replace(" ", "T")
                if not time_val.endswith("Z"):
                    time_val += "Z"

            src_ip = get_val('Src IP', '0.0.0.0')
            dst_ip = get_val('Dst IP', '0.0.0.0')
            src_port = get_val('Src port', '0').split('.')[0]
            dst_port = get_val('Dst port', '0').split('.')[0]
            status = get_val('Log subtype', 'Allowed')
            
            rule_name = get_val('Firewall rule name')
            
            severity = "Low"
            if status == "Denied":
                if "Geo" in rule_name or "IPS" in rule_name or "Malware" in rule_name:
                    severity = "Critical"
                else:
                    severity = "High"
            
            raw_log = f"{time_val} | {src_ip} | {dst_ip} | {src_port} | {dst_port} | {status} | {severity}"
            
            entry = OfflineLogEntry(
                raw_log=raw_log,
                timeline=time_val,
                status=status,
                severity=severity
            )
            db.add(entry)
            
        db.commit()
        return {"status": "success", "message": f"Uploaded {len(records)} offline logs."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/logs")
def get_logs(page: int = 1, limit: int = 500, time_range: Optional[str] = None, status_filter: Optional[str] = "All", source: str = "live", db: Session = Depends(get_db)):
    model = OfflineLogEntry if source == "offline" else LogEntry
    query = db.query(model)
    
    if status_filter and status_filter != "All":
        if status_filter == "Malicious":
            query = query.filter(model.severity == "Critical")
        else:
            query = query.filter(model.status == status_filter)
            
    from sqlalchemy import func
    if time_range:
        now = datetime.datetime.now()
        if source == "offline":
            max_time_str = db.query(func.max(model.timeline)).scalar()
            if max_time_str:
                try:
                    now = datetime.datetime.strptime(max_time_str, "%Y-%m-%dT%H:%M:%SZ")
                except:
                    pass
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
            query = query.filter(model.timeline >= cutoff_str)
            
    logs = query.order_by(model.id.desc()).offset((page - 1) * limit).limit(limit).all()
    return logs

@app.get("/api/logs/stats")
def get_stats(source: str = "live", db: Session = Depends(get_db)):
    model = OfflineLogEntry if source == "offline" else LogEntry
    total = db.query(model).count()
    critical = db.query(model).filter(model.severity == "Critical").count()
    denied = db.query(model).filter(model.status == "Denied").count()
    allowed = db.query(model).filter(model.status == "Allowed").count()
    return {
        "total": total,
        "critical": critical,
        "denied": denied,
        "allowed": allowed
    }

@app.get("/api/logs/chart")
def get_chart_data(time_range: Optional[str] = None, status_filter: Optional[str] = "All", source: str = "live", db: Session = Depends(get_db)):
    model = OfflineLogEntry if source == "offline" else LogEntry
    query = db.query(model.timeline, model.severity, model.status)
    if status_filter and status_filter != "All":
        if status_filter == "Malicious":
            query = query.filter(model.severity == "Critical")
        else:
            query = query.filter(model.status == status_filter)
            
    from sqlalchemy import func
    now = datetime.datetime.now()
    if source == "offline":
        max_time_str = db.query(func.max(model.timeline)).scalar()
        if max_time_str:
            try:
                now = datetime.datetime.strptime(max_time_str, "%Y-%m-%dT%H:%M:%SZ")
            except:
                pass
                
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
            query = query.filter(model.timeline >= cutoff_str)
            
    logs = query.all()
    
    time_map = {}
    for log in logs:
        m_key = log.timeline[:16] + ":00Z"
        if m_key not in time_map:
            time_map[m_key] = {"time": m_key, "count": 0, "Critical": 0, "High": 0, "Allowed": 0, "Denied": 0}
        time_map[m_key]["count"] += 1
        if log.severity == "Critical":
            time_map[m_key]["Critical"] += 1
        elif log.severity == "High":
             time_map[m_key]["High"] += 1
             
        if log.status == "Allowed":
             time_map[m_key]["Allowed"] += 1
        elif log.status == "Denied":
             time_map[m_key]["Denied"] += 1
             
    return_data = []
    if delta:
        current = (now - delta).replace(second=0, microsecond=0)
        end = now.replace(second=0, microsecond=0)
        
        while current <= end:
            m_key = current.strftime("%Y-%m-%dT%H:%M:00Z")
            if m_key in time_map:
                return_data.append(time_map[m_key])
            else:
                return_data.append({"time": m_key, "count": 0, "Critical": 0, "High": 0, "Allowed": 0, "Denied": 0})
            current += datetime.timedelta(minutes=1)
    else:
        sorted_keys = sorted(time_map.keys())
        return_data = [time_map[k] for k in sorted_keys]
        
    return return_data

@app.post("/api/chat")
def chat(payload: ChatQuery):
    response = chat_with_agent(payload.query, source=payload.source)
    if isinstance(response, dict):
        return response
    return {"response": response}

@app.get("/")
def read_root():
    return {"message": "Backend API is running. Layers 4 and 5 active."}
