with open(r'agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Update chat_with_agent PDF time generation block
code = code.replace('''            if min_match:
                cutoff = now - datetime.timedelta(minutes=int(min_match.group(1)))
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime('%Y-%m-%dT%H:%M:%SZ'))
            elif hour_match:
                cutoff = now - datetime.timedelta(hours=int(hour_match.group(1)))
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime('%Y-%m-%dT%H:%M:%SZ'))''', '''            if source == "live":
                if min_match:
                    cutoff = now - datetime.timedelta(minutes=int(min_match.group(1)))
                    query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime('%Y-%m-%dT%H:%M:%SZ'))
                elif hour_match:
                    cutoff = now - datetime.timedelta(hours=int(hour_match.group(1)))
                    query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime('%Y-%m-%dT%H:%M:%SZ'))''')

# Update agent block for normal chat cutoff
code = code.replace('''            if cutoff:
                cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff_str)
                limit_count = 500''', '''            if cutoff and source == "live":
                cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff_str)
                limit_count = 500
            elif source == "offline":
                limit_count = 500''')
                
code = code.replace('''        if min_match:
            cutoff = now - datetime.timedelta(minutes=int(min_match.group(1)))
            query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"))
        elif hour_match:
            cutoff = now - datetime.timedelta(hours=int(hour_match.group(1)))
            query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"))''', '''        if source == "live":
            if min_match:
                cutoff = now - datetime.timedelta(minutes=int(min_match.group(1)))
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"))
            elif hour_match:
                cutoff = now - datetime.timedelta(hours=int(hour_match.group(1)))
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"))''')

# Add explicit stats query to DB returning offline context correctly.
if 't_count = db.query(ModelClass).count()' not in code:
    code = code.replace('''    combined_context = f"=== EXACT SYSTEM LOGS MATCHING QUERY ===\\n{sql_context if sql_context else 'No exact logs matched in the relational DB.'}\\n\\n=== RECENT HIGH/CRITICAL EVENT SUMMARIES ===\\n{rag_context}"''', 
'''    try:
        db = SessionLocal()
        ModelClass = OfflineLogEntry if source == "offline" else LogEntry
        t_count = db.query(ModelClass).count()
        c_count = db.query(ModelClass).filter(ModelClass.severity == "Critical").count()
        d_count = db.query(ModelClass).filter(ModelClass.status == "Denied").count()
        a_count = db.query(ModelClass).filter(ModelClass.status == "Allowed").count()
        stats_str = f"Database Contains - Total Logs: {t_count}, Allowed: {a_count}, Denied: {d_count}, Critical: {c_count}."
    except Exception:
        stats_str = ""
    finally:
        db.close()

    combined_context = f"=== EXACT SYSTEM LOGS MATCHING QUERY ===\\n{sql_context if sql_context else 'No exact logs matched in the relational DB.'}\\n\\n=== RECENT HIGH/CRITICAL EVENT SUMMARIES ===\\n{rag_context}\\n\\n=== DATABASE STATS ===\\n{stats_str}"''')

# Fix "give me logs" query which had standard filtering but dropped cutoff
code = code.replace('res = query_obj.order_by(ModelClass.id.desc()).limit(limit_count).all()\n                if res and cutoff:', 'res = query_obj.order_by(ModelClass.id.desc()).limit(limit_count).all()\n                if res:')


with open(r'agent.py', 'w', encoding='utf-8') as f:
    f.write(code)
