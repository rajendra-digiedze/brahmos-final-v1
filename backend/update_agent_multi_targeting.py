import re

with open(r'agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Update AI extraction logic for top IPs
ai_old = '''        # Explicit Exact Counting mapping for Top Hit arrays
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
                top_stats_context = f"\\n\\n=== EXPLICIT TOP IP FREQUENCIES (TRUE NATIVE AGGREGATION) ===\\nThese are the exact mathematical IP hit counts from the current parameters:\\n{top_str}\\n"'''

ai_new = '''        # Explicit Exact Counting mapping for Top Hit arrays
        top_stats_context = ""
        if "top" in query_lower or "repeat" in query_lower or "hit" in query_lower or "count" in query_lower:
            limit_n = 10
            num_match = re.search(r'top\s+(\d+)', query_lower)
            if num_match:
                limit_n = int(num_match.group(1))

            full_res = query_obj.all()
            src_counts = {}
            dst_counts = {}
            for r in full_res:
                parts = [p.strip() for p in r.raw_log.split('|')]
                if len(parts) > 3:
                    src = parts[1]
                    dst = parts[2]
                    src_counts[src] = src_counts.get(src, 0) + 1
                    dst_counts[dst] = dst_counts.get(dst, 0) + 1
            
            top_str = ""
            if "source" in query_lower and "dest" not in query_lower:
                if src_counts:
                    top_s = sorted(src_counts.items(), key=lambda x: x[1], reverse=True)[:limit_n]
                    top_str += "Top Source IPs:\\n" + "\\n".join([f"IP: {ip} -> Hits: {cnt}" for ip, cnt in top_s]) + "\\n"
            elif "dest" in query_lower and "source" not in query_lower:
                if dst_counts:
                    top_d = sorted(dst_counts.items(), key=lambda x: x[1], reverse=True)[:limit_n]
                    top_str += "Top Destination IPs:\\n" + "\\n".join([f"IP: {ip} -> Hits: {cnt}" for ip, cnt in top_d]) + "\\n"
            else:
                if src_counts:
                    top_s = sorted(src_counts.items(), key=lambda x: x[1], reverse=True)[:limit_n]
                    top_str += "Top Source IPs:\\n" + "\\n".join([f"IP: {ip} -> Hits: {cnt}" for ip, cnt in top_s]) + "\\n\\n"
                if dst_counts:
                    top_d = sorted(dst_counts.items(), key=lambda x: x[1], reverse=True)[:limit_n]
                    top_str += "Top Destination IPs:\\n" + "\\n".join([f"IP: {ip} -> Hits: {cnt}" for ip, cnt in top_d]) + "\\n"

            if top_str:
                top_stats_context = f"\\n\\n=== EXPLICIT TOP IP FREQUENCIES (TRUE NATIVE AGGREGATION) ===\\nThese are the exact numerical IP hit counts (up to {limit_n}) from the filtered parameters:\\n{top_str}\\n"'''

if ai_old in code:
    code = code.replace(ai_old, ai_new)
else:
    print("Warning: ai_old block not found precisely. Trying regex fallback.")
    code = re.sub(r'# Explicit Exact Counting mapping.*?top_stats_context =.*?\\n"(?=\s*except Exception as e:)', ai_new, code, flags=re.DOTALL)


# Update PDF Report dynamic bar chart to support Destination
chart_old = '''                # Dynamic bar chart
                s_ips = sorted(src_ips.items(), key=lambda x: x[1], reverse=True)[:6]
                if s_ips:
                    b_labels = [x[0][-12:] for x in s_ips]
                    b_counts = [x[1] for x in s_ips]
                else:
                    b_labels = ['No Data']
                    b_counts = [0]
                
                ax2.bar(b_labels, b_counts, color=['#3b82f6']*len(b_labels))
                ax2.set_title("Top Source IPs by Hit Count", fontsize=10)'''

chart_new = '''                # Dynamic bar chart
                if "dest" in query_lower and "source" not in query_lower:
                    dest_counts_map = {}
                    for r in res:
                        parts = [p.strip() for p in r[0].split('|')]
                        if len(parts) >= 3:
                            dest_counts_map[parts[2]] = dest_counts_map.get(parts[2], 0) + 1
                    s_ips = sorted(dest_counts_map.items(), key=lambda x: x[1], reverse=True)[:6]
                    c_title = "Top Dest IPs by Hit"
                else: 
                    s_ips = sorted(src_ips.items(), key=lambda x: x[1], reverse=True)[:6]
                    c_title = "Top Source IPs by Hit"
                    
                if s_ips:
                    b_labels = [x[0][-12:] for x in s_ips]
                    b_counts = [x[1] for x in s_ips]
                else:
                    b_labels = ['No Data']
                    b_counts = [0]
                
                ax2.bar(b_labels, b_counts, color=['#3b82f6']*len(b_labels))
                ax2.set_title(c_title, fontsize=10)'''
if chart_old in code:
    code = code.replace(chart_old, chart_new)
else:
    print("Warning: chart_old block not found precisely.")

# Fix PDF Table length so it outputs limit_n rows if asked for "top N report"
tbl_old = '''            for (sip, dip, dport, stat), count in sorted(conn_map.items(), key=lambda x: x[1], reverse=True)[:7]:'''

tbl_new = '''            limit_n = 7
            num_match = re.search(r'top\s+(\d+)', query_lower)
            if num_match:
                limit_n = int(num_match.group(1))
            for (sip, dip, dport, stat), count in sorted(conn_map.items(), key=lambda x: x[1], reverse=True)[:limit_n]:'''
code = code.replace(tbl_old, tbl_new)

with open(r'agent.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("agent.py successfully modified for dynamic IP aggregations.")
