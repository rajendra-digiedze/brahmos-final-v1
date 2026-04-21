with open(r'C:\Users\r6304076576\Downloads\brahmos\frontend\src\App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add Allowed and Denied extracting to processChartData
code = code.replace('''        return {
          time: timeKey,
          count: c.count,
          Critical: c.Critical,
          High: c.High,
          Low: lows
        };''', '''        return {
          time: timeKey,
          count: c.count,
          Critical: c.Critical || 0,
          High: c.High || 0,
          Low: lows,
          Allowed: c.Allowed || 0,
          Denied: c.Denied || 0
        };''')

# Update AreaChart to show all requested metrics
area_chart_old = '''              <Area type="monotone" dataKey="count" name={activeTab === "All" ? "Total Events" : `${activeTab} Events`} stroke="#6366f1" fillOpacity={1} fill="url(#colorCount)" />
              {activeTab === "All" && (
                <Area type="monotone" dataKey="Critical" name="Critical Events" stroke="#ef4444" fillOpacity={1} fill="url(#colorCrit)" />
              )}'''

area_chart_new = '''              <defs>
                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorCrit" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorAllow" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorDeny" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.6} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
              <XAxis dataKey="time" stroke="#475569" fontSize={12} tickMargin={10} minTickGap={20} />
              <YAxis stroke="#475569" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '8px' }}
                itemStyle={{ color: '#0F172A' }}
              />
              <Area type="monotone" dataKey="count" name={activeTab === "All" ? "Total Events" : `${activeTab} Events`} stroke="#6366f1" fillOpacity={1} fill="url(#colorCount)" />
              {activeTab === "All" && (
                <>
                  <Area type="monotone" dataKey="Critical" name="Critical Events" stroke="#ef4444" fillOpacity={1} fill="url(#colorCrit)" />
                  <Area type="monotone" dataKey="Allowed" name="Healthy/Allowed" stroke="#22c55e" fillOpacity={1} fill="url(#colorAllow)" />
                  <Area type="monotone" dataKey="Denied" name="Denied Events" stroke="#f59e0b" fillOpacity={1} fill="url(#colorDeny)" />
                </>
              )}'''

import re
code = re.sub(r'<defs>.*?</AreaChart>', area_chart_new + '\n            </AreaChart>', code, flags=re.DOTALL)

# Update Stats bar
stats_old = '''          <div className={`px-4 py-2 rounded-lg border flex items-center gap-2 bg-white border-slate-200`}>
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse shadow-sm"></div>
            <span className={`text-sm font-medium text-slate-900`}>Critical (L2 NiFi): {maliciousCount}</span>
          </div>
          <div className={`px-4 py-2 rounded-lg border flex items-center gap-2 bg-white border-slate-200`}>
            <div className="w-2 h-2 rounded-full bg-amber-500"></div>
            <span className={`text-sm font-medium text-slate-900`}>Denied (L1 K8s): {deniedCount}</span>
          </div>'''

stats_new = '''          <div className={`px-4 py-1.5 rounded-lg border flex items-center gap-2 bg-white border-slate-200 shadow-[0px_1px_2px_rgba(0,0,0,0.05)]`}>
            <div className="w-2 h-2 rounded-full bg-indigo-500"></div>
            <span className={`text-xs font-medium text-slate-900`}>Total Events: {stats?.total || 0}</span>
          </div>
          <div className={`px-4 py-1.5 rounded-lg border flex items-center gap-2 bg-white border-slate-200 shadow-[0px_1px_2px_rgba(0,0,0,0.05)]`}>
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <span className={`text-xs font-medium text-slate-900`}>Healthy (Allowed): {stats?.allowed || 0}</span>
          </div>
          <div className={`px-4 py-1.5 rounded-lg border flex items-center gap-2 bg-white border-slate-200 shadow-[0px_1px_2px_rgba(0,0,0,0.05)]`}>
            <div className="w-2 h-2 rounded-full bg-amber-500"></div>
            <span className={`text-xs font-medium text-slate-900`}>Denied (L1 K8s): {deniedCount}</span>
          </div>
          <div className={`px-4 py-1.5 rounded-lg border flex items-center gap-2 bg-white border-slate-200 shadow-[0px_1px_2px_rgba(0,0,0,0.05)]`}>
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse shadow-sm"></div>
            <span className={`text-xs font-medium text-slate-900`}>Critical/Malicious: {maliciousCount}</span>
          </div>'''

code = code.replace(stats_old, stats_new)

with open(r'C:\Users\r6304076576\Downloads\brahmos\frontend\src\App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
