import re

with open(r'C:\Users\r6304076576\Downloads\brahmos\backend\agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update PDF Report generation to calculate real counts without limits, but limit PDF print
report_query_old = '''            res_db = query_obj.order_by(ModelClass.id.desc()).limit(200).all()
            res = [(r.raw_log, r.severity) for r in res_db]'''

report_query_new = '''            res_db = query_obj.order_by(ModelClass.id.desc()).all()
            res = [(r.raw_log, r.severity) for r in res_db]'''

code = code.replace(report_query_old, report_query_new)


pdf_payload_old = '''            # Log payloads
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(190, 6, f"Complete Event Payloads ({len(res)} matches):", ln=1)
            pdf.set_font("Helvetica", "", 8)
            
            if not res:
                pdf.multi_cell(190, 5, " - No specific log events matched the exact timeframe and status query.")
            for r in res: 
                pdf.multi_cell(190, 4, f" - {r[0]}")
                pdf.ln(1)'''

pdf_payload_new = '''            # Log payloads
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(190, 6, f"Event Payloads (Displaying latest 200 of {len(res)} matches):", ln=1)
            pdf.set_font("Helvetica", "", 8)
            
            if not res:
                pdf.multi_cell(190, 5, " - No specific log events matched the exact timeframe and status query.")
            for r in res[:200]: 
                pdf.multi_cell(190, 4, f" - {r[0]}")
                pdf.ln(1)'''
code = code.replace(pdf_payload_old, pdf_payload_new)


# 2. Update AI Agent to extract global frequencies if queried over 'top', 'repeat', 'hits'
ai_context_old = '''        sql_res = query_obj.order_by(ModelClass.id.desc()).limit(100).all()
        if sql_res:
            sql_context = "\\n".join([f"- {r.raw_log}" for r in sql_res])
    except Exception as e:
        print("SQL Context Error:", e)'''

ai_context_new = '''        sql_res = query_obj.order_by(ModelClass.id.desc()).limit(100).all()
        if sql_res:
            sql_context = "\\n".join([f"- {r.raw_log}" for r in sql_res])
        
        # Explicit Exact Counting mapping for Top Hit arrays
        top_stats_context = ""
        if "top" in query_lower or "repeat" in query_lower or "hit" in query_lower or "count" in query_lower:
            full_res = query_obj.all()
            src_counts = {}
            for r in full_res:
                parts = [p.strip() for p in r.raw_log.split('|')]
                if len(parts) > 2:
                    src = parts[1]
                    src_counts[src] = src_counts.get(src, 0) + 1
            if src_counts:
                top_d = sorted(src_counts.items(), key=lambda x: x[1], reverse=True)[:15]
                top_str = "\\n".join([f"IP: {ip} -> Hits: {cnt}" for ip, cnt in top_d])
                top_stats_context = f"\\n\\n=== EXPLICIT TOP IP FREQUENCIES (TRUE NATIVE AGGREGATION) ===\\nThese are the exact mathematical IP hit counts from the current parameters:\\n{top_str}\\n"
            
    except Exception as e:
        print("SQL Context Error:", e)'''
code = code.replace(ai_context_old, ai_context_new)

# Inject top_stats_context into combined context
combined_context_old = '''    combined_context = f"=== EXACT SYSTEM LOGS MATCHING QUERY ===\\n{sql_context if sql_context else 'No exact logs matched in the relational DB.'}\\n\\n=== RECENT HIGH/CRITICAL EVENT SUMMARIES ===\\n{rag_context}\\n\\n=== DATABASE STATS ===\\n{stats_str}"'''
combined_context_new = '''    combined_context = f"=== EXACT SYSTEM LOGS MATCHING QUERY ===\\n{sql_context if sql_context else 'No exact logs matched in the relational DB.'}\\n\\n=== RECENT HIGH/CRITICAL EVENT SUMMARIES ===\\n{rag_context}\\n\\n=== DATABASE STATS ===\\n{stats_str}{top_stats_context if 'top_stats_context' in locals() else ''}"'''
code = code.replace(combined_context_old, combined_context_new)

with open(r'agent.py', 'w', encoding='utf-8') as f:
    f.write(code)
