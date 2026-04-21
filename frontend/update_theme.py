import re
with open(r'C:\Users\r6304076576\Downloads\brahmos\frontend\src\App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Make the theme default to 'light'
code = code.replace('useState("dark")', 'useState("light")')
code = code.replace("theme === 'light'", "true")

# The user explicitly states:
# Card Background: #FFFFFF (bg-white)
# Main Background: #F8FAFC (bg-slate-50)
# Border Color: #E2E8F0 (border-slate-200)

code = code.replace('bg-slate-900', 'bg-white')
code = code.replace('bg-slate-950', 'bg-slate-50')
code = code.replace('border-slate-800', 'border-slate-200')
code = code.replace('border-slate-700', 'border-slate-300')
code = code.replace('text-slate-300', 'text-slate-700')
code = code.replace('text-slate-400', 'text-slate-500')
code = code.replace('bg-slate-800', 'bg-slate-100')
code = code.replace('text-white', 'text-slate-900')

# Restore actual text-white inside indigo buttons or active states
code = code.replace('bg-indigo-600 text-slate-900', 'bg-indigo-600 text-white')
code = code.replace('bg-indigo-500 text-slate-900', 'bg-indigo-500 text-white')

# Critical Badges
code = code.replace('bg-red-900/50 border border-red-500', 'bg-red-100 border border-red-200')
code = code.replace('text-red-400', 'text-red-600')

# Allowed Badges
code = code.replace('bg-green-500/10 text-green-400', 'bg-green-100 text-green-700 font-bold')
code = code.replace('bg-orange-500/10 text-orange-400', 'bg-red-100 text-red-700 font-bold')
code = code.replace('bg-red-500/10 text-red-400', 'bg-red-100 text-red-700 font-bold')
code = code.replace('text-red-500 font-bold', 'text-red-600 font-bold')

# Typography and specific color overrides
code = code.replace('bg-slate-800/50 text-slate-700', 'bg-slate-50 text-slate-700 border-slate-200 border')
code = code.replace('text-indigo-300', 'text-indigo-700')

# Charts
code = code.replace('#334155', '#E2E8F0') # Grid lines
code = code.replace('#94a3b8', '#475569') # Axis labels
code = code.replace("backgroundColor: '#0f172a'", "backgroundColor: '#FFFFFF'")
code = code.replace("borderColor: '#1e293b'", "borderColor: '#E2E8F0'")
code = code.replace("itemStyle={{ color: '#e2e8f0' }}", "itemStyle={{ color: '#0F172A' }}")

# Add maximize feature to Log Viewer Widget
if 'const [isLogsMaximized, setIsLogsMaximized] = useState(false);' not in code:
    code = code.replace('const [isChatMaximized, setIsChatMaximized] = useState(false);', 'const [isChatMaximized, setIsChatMaximized] = useState(false);\n  const [isLogsMaximized, setIsLogsMaximized] = useState(false);')

# Inject Maximize button into Logs Viewer header
replacement_header = """<h2 className="text-lg font-semibold flex items-center gap-2"><Activity className="w-5 h-5" /> {logSource === 'live' ? 'Live Network Logs' : 'Offline Uploaded Logs'}</h2>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500">Updates every 2s</span>
              <button onClick={() => setIsLogsMaximized(!isLogsMaximized)} className="p-1 hover:bg-slate-200 rounded-md text-slate-600 transition-colors">
                {isLogsMaximized ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
              </button>
            </div>"""
code = code.replace('<h2 className="text-lg font-semibold flex items-center gap-2"><Activity className="w-5 h-5" /> {logSource === \'live\' ? \'Live Network Logs\' : \'Offline Uploaded Logs\'}</h2>\n            <span className="text-xs text-slate-500">Updates every 2s</span>', replacement_header)

# Make Logs Viewer container dynamic based on isLogsMaximized
code = code.replace('<div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-xl overflow-hidden flex flex-col h-[55vh]">', '<div className={`bg-white rounded-xl border border-slate-200 shadow-[0px_1px_2px_rgba(0,0,0,0.05)] overflow-hidden flex flex-col ${isLogsMaximized ? \'fixed inset-4 z-50 lg:inset-x-20 lg:inset-y-10\' : \'lg:col-span-2 h-[55vh]\'}`}>')

# Ensure Zero Trust active items look right, and other minor tweaks
code = code.replace('shadow-xl', 'shadow-[0px_1px_2px_rgba(0,0,0,0.05)] hover:shadow-[0px_4px_8px_rgba(0,0,0,0.08)]')

# Also fix the chart legend to use specific donut colors requested:
# Critical -> #EF4444
# High -> #F59E0B
# Low -> #CBD5F5
code = code.replace("{ name: 'Low/Other', value: severityCount.Low, color: '#94a3b8' }", "{ name: 'Low/Other', value: severityCount.Low, color: '#CBD5F5' }")

# Add a backdrop when isLogsMaximized is true
if 'isLogsMaximized &&' not in code:
    code = code.replace('{isChatMaximized && (', '{isLogsMaximized && (\n        <div className="fixed inset-0 bg-black/60 z-40 backdrop-blur-sm" onClick={() => setIsLogsMaximized(false)}></div>\n      )}\n      {isChatMaximized && (')

with open(r'C:\Users\r6304076576\Downloads\brahmos\frontend\src\App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Processed successfully")
