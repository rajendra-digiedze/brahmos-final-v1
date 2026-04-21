import re

with open(r'C:\Users\r6304076576\Downloads\brahmos\backend\agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix first instance of query_obj
first_block_old = '''            now = datetime.datetime.now()
            ModelClass = OfflineLogEntry if source == "offline" else LogEntry
            query_obj = db.query(ModelClass)
            
            if source == "live":
                if min_match:
                    cutoff = now - datetime.timedelta(minutes=int(min_match.group(1)))
                    query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime('%Y-%m-%dT%H:%M:%SZ'))
                elif hour_match:
                    cutoff = now - datetime.timedelta(hours=int(hour_match.group(1)))
                    query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime('%Y-%m-%dT%H:%M:%SZ'))'''

first_block_new = '''            from sqlalchemy import func
            now = datetime.datetime.now()
            ModelClass = OfflineLogEntry if source == "offline" else LogEntry
            
            if source == "offline":
                max_time_str = db.query(func.max(ModelClass.timeline)).scalar()
                if max_time_str:
                    try:
                        now = datetime.datetime.strptime(max_time_str, "%Y-%m-%dT%H:%M:%SZ")
                    except:
                        pass
                        
            query_obj = db.query(ModelClass)
            
            if min_match:
                cutoff = now - datetime.timedelta(minutes=int(min_match.group(1)))
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime('%Y-%m-%dT%H:%M:%SZ'))
            elif hour_match:
                cutoff = now - datetime.timedelta(hours=int(hour_match.group(1)))
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime('%Y-%m-%dT%H:%M:%SZ'))'''
code = code.replace(first_block_old, first_block_new)

# Fix second instance of query_obj (heuristic block)
second_block_old = '''            now = datetime.datetime.now()
            cutoff = None
            
            if min_match:
                minutes = int(min_match.group(1))
                cutoff = now - datetime.timedelta(minutes=minutes)
            elif hour_match:
                hours = int(hour_match.group(1))
                cutoff = now - datetime.timedelta(hours=hours)

            ModelClass = OfflineLogEntry if source == "offline" else LogEntry
            query_obj = db.query(ModelClass)
            cutoff_str = ""
            limit_count = 20
            if cutoff and source == "live":
                cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff_str)
                limit_count = 500
            elif source == "offline":
                limit_count = 500'''

second_block_new = '''            from sqlalchemy import func
            now = datetime.datetime.now()
            ModelClass = OfflineLogEntry if source == "offline" else LogEntry
            
            if source == "offline":
                max_time_str = db.query(func.max(ModelClass.timeline)).scalar()
                if max_time_str:
                    try:
                        now = datetime.datetime.strptime(max_time_str, "%Y-%m-%dT%H:%M:%SZ")
                    except:
                        pass

            cutoff = None
            if min_match:
                minutes = int(min_match.group(1))
                cutoff = now - datetime.timedelta(minutes=minutes)
            elif hour_match:
                hours = int(hour_match.group(1))
                cutoff = now - datetime.timedelta(hours=hours)

            query_obj = db.query(ModelClass)
            cutoff_str = ""
            limit_count = 20
            if cutoff:
                cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff_str)
                limit_count = 500
            if source == "offline":
                limit_count = 500'''
code = code.replace(second_block_old, second_block_new)

# Fix third instance of query_obj (llm context block)
third_block_old = '''        now = datetime.datetime.now()
        
        ModelClass = OfflineLogEntry if source == "offline" else LogEntry
        query_obj = db.query(ModelClass)
        if source == "live":
            if min_match:
                cutoff = now - datetime.timedelta(minutes=int(min_match.group(1)))
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"))
            elif hour_match:
                cutoff = now - datetime.timedelta(hours=int(hour_match.group(1)))
                query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"))'''

third_block_new = '''        from sqlalchemy import func
        now = datetime.datetime.now()
        ModelClass = OfflineLogEntry if source == "offline" else LogEntry
        
        if source == "offline":
            max_time_str = db.query(func.max(ModelClass.timeline)).scalar()
            if max_time_str:
                try:
                    now = datetime.datetime.strptime(max_time_str, "%Y-%m-%dT%H:%M:%SZ")
                except:
                    pass
                    
        query_obj = db.query(ModelClass)
        if min_match:
            cutoff = now - datetime.timedelta(minutes=int(min_match.group(1)))
            query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"))
        elif hour_match:
            cutoff = now - datetime.timedelta(hours=int(hour_match.group(1)))
            query_obj = query_obj.filter(ModelClass.timeline >= cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"))'''
code = code.replace(third_block_old, third_block_new)

with open(r'C:\Users\r6304076576\Downloads\brahmos\backend\agent.py', 'w', encoding='utf-8') as f:
    f.write(code)
