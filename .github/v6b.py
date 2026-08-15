from pathlib import Path
import re

# Admin
p=Path('index.html');s=p.read_text(encoding='utf-8')
s=re.sub(r'(-webkit-backdrop-filter:[^;]+;)\s*\1',r'\1',s)
s=re.sub(r'(-webkit-user-select:[^;]+;)\s*\1',r'\1',s)
s=s.replace('if(Number(l.ctemp||0)>=TELEMETRY_CONFIG.ctemp.critical&&!existing.has(`${v.id}|High engine temperature`))', 'if(Number.isFinite(Number(l.ctemp))&&Number(l.ctemp)>=TELEMETRY_CONFIG.ctemp.critical&&!existing.has(`${v.id}|High engine temperature`))')
s=s.replace('function conn(v){const l=lastTelemetry(v);if(!l)return "offline";const t=parseTime(l.time);if(!t)return "offline";const age=Math.max(0,Date.now()-t.getTime());return age<10000?"online":age<900000?"recent":"offline"}', 'function conn(v){const a=window.analyzeVehicleTelemetry?.(v?.telemetry||[]);return a?.connection||"offline"}')
s=re.sub(r'function connLabel\(v\)\{.*?\}', 'function connLabel(v){const s=conn(v);return s==="live"?"LIVE":s==="recent"?"RECENT":s==="stale"?"STALE":"OFFLINE"}', s, count=1)
s=re.sub(r'function connClass\(v\)\{.*?\}', 'function connClass(v){const s=conn(v);return s==="live"?"live":s==="recent"?"recent":s==="stale"?"stale":"off"}', s, count=1)
s=re.sub(r'\s*if\(\(e\.ctrlKey\|\|e\.metaKey\)&&e\.key\.toLowerCase\(\)==="k"\)\{\s*e\.preventDefault\(\);\s*showScreen\("screen-customers"\);\s*customerSearchInput\?\.focus\(\);\s*\}', '', s, count=1)
s=re.sub(r'\s*function createLocalDemoCredential\(\)\{.*?\}\s*','\n',s,count=1,flags=re.S)
s=re.sub(r'\s*if\(r\?\.credential===["\']local-demo["\']\)\{.*?\}\s*','\n',s,count=1,flags=re.S)
# Preserve explicit ownership values in fleet data adapters.
s=s.replace('customerId:String(c.id)', 'customerId:String(v.customerId||c.id)')
# Conflict detector: no silent owner repair.
if 'function detectOwnershipConflicts(db)' not in s:
    fn='''function detectOwnershipConflicts(db){const seen=new Map(),conflicts=[];(Array.isArray(db)?db:[]).forEach(c=>(Array.isArray(c.cars)?c.cars:[]).forEach(v=>{const id=String(v?.id??v?.recordId??"");if(!id)return;const owner=String(c.id),prior=seen.get(id);if(prior&&prior.owner!==owner){const key=[id,prior.owner,owner].sort().join("|");if(!conflicts.some(x=>x.key===key))conflicts.push({key,vehicleId:id,customerIds:[prior.owner,owner]});v.ownershipConflict=true;v.ownershipConflictOwners=[prior.owner,owner];prior.vehicle.ownershipConflict=true;prior.vehicle.ownershipConflictOwners=[prior.owner,owner]}else if(!prior)seen.set(id,{owner,vehicle:v})}));window.JaFaFaOwnershipConflicts=conflicts;return conflicts}\n'''
    s=s.replace('function load(){',fn+'function load(){',1)
if 'detectOwnershipConflicts(MOCK_DATABASE)' not in s:
    s=s.replace('MOCK_DATABASE = JSON.parse', 'MOCK_DATABASE = JSON.parse',1)
    # Call after the first load() function body by inserting before the next major marker.
    m=re.search(r'(function load\(\)\{.*?\n\})',s,re.S)
    if m:s=s[:m.end()]+'\ndetectOwnershipConflicts(MOCK_DATABASE);'+s[m.end():]
p.write_text(s,encoding='utf-8')

# Customer
p=Path('customer.html');s=p.read_text(encoding='utf-8')
s=re.sub(r'(-webkit-backdrop-filter:[^;]+;)\s*\1',r'\1',s)
s=s.replace('v.customerId=String(c.id);v.recordId=', 'if(!v.customerId)v.customerId=String(c.id);v.recordId=')
s=re.sub(r'function analyze\(v\)\{.*?\}\nfunction health\(v\)\{.*?\}\n','function analyze(v){return window.analyzeVehicleTelemetry?window.analyzeVehicleTelemetry(v?.telemetry||[]):{latest:latest(v),connection:"offline",overall:"warning",score:null,categories:[]}}\nfunction health(v){return window.vehicleHealthScore?.(v?.telemetry||[])??null}\n',s,count=1,flags=re.S)
s=re.sub(r'function latest\(v\)\{[^}]*\}','function latest(v){return window.latestTelemetry?.(v?.telemetry||[])||((v?.telemetry||[]).slice().sort((a,b)=>new Date(b.time||b.timestamp)-new Date(a.time||a.timestamp))[0]||null)}',s,count=1)
s=re.sub(r'function telemetryState\(ts\)\{.*?\}','function telemetryState(ts){const age=Date.now()-new Date(ts||0).getTime();if(!Number.isFinite(age)||age<0)return"offline";if(age<10000)return"live";if(age<30000)return"recent";if(age<120000)return"stale";return"offline"}',s,count=1)
# Customer overlay health adapter delegates to shared score.
s=re.sub(r'function health4\(v\)\{.*?\}\n\s*window\.JaFaFaCore=', '''function health4(v){const a=window.analyzeVehicleTelemetry?.(v?.telemetry||[]);if(!a)return{score:null,reasons:["Telemetry analysis unavailable"],severity:"offline"};const reasons=[];if(a.cooling==="overheating")reasons.push("Coolant temperature critical");else if(a.cooling==="warm")reasons.push("Coolant temperature elevated");if(a.electrical==="low-voltage")reasons.push("Battery voltage below normal");if(a.latest?.rpm!=null&&Number(a.latest.rpm)>=TELEMETRY_CONFIG.rpm.warning)reasons.push("High engine RPM");if(a.latest?.speed!=null&&Number(a.latest.speed)>=TELEMETRY_CONFIG.speed.warning)reasons.push("High vehicle speed");if(a.connection==="offline")reasons.push("Telemetry connection offline");else if(a.connection==="stale")reasons.push("Telemetry connection is stale");return{score:a.score,reasons,severity:a.overall}}\nwindow.JaFaFaCore=''',s,count=1,flags=re.S)
# Ownership conflict detection in customer normalize.
s=re.sub(r'function normalizeDb\(db\)\{.*?\}\n\s*function writeDb','''function normalizeDb(db){const list=Array.isArray(db)?db:[],seen=new Map(),conflicts=[];list.forEach(c=>{c.cars=Array.isArray(c.cars)?c.cars:[];c.cars.forEach(v=>{const id=String(v.id??v.recordId??"");if(!id)return;const owner=String(c.id),prior=seen.get(id);if(prior&&prior.owner!==owner){const key=[id,prior.owner,owner].sort().join("|");if(!conflicts.some(x=>x.key===key))conflicts.push({key,vehicleId:id,customerIds:[prior.owner,owner]});v.ownershipConflict=true;v.ownershipConflictOwners=[prior.owner,owner];prior.vehicle.ownershipConflict=true;prior.vehicle.ownershipConflictOwners=[prior.owner,owner]}else if(!prior)seen.set(id,{owner,vehicle:v});if(!v.customerId&&!v.ownershipConflict)v.customerId=owner;v.recordId=v.recordId||uid("veh");v.telemetry=Array.isArray(v.telemetry)?v.telemetry:[]})});window.JaFaFaOwnershipConflicts=conflicts;return list}\nfunction writeDb''',s,count=1,flags=re.S)
s=s.replace('owner.cars.push(x.v);','x.v.customerId=String(owner.id);owner.cars.push(x.v);')
# Sortable customer log: if log header exists, replace renderer; otherwise leave DOM intact.
if 'customerLogSort' not in s:
    s=s.replace('function renderLog(data){const rows=data.slice().sort((a,b)=>new Date(b.time)-new Date(a.time));', 'let customerLogSort={key:"time",dir:"desc"};\nfunction renderLog(data){const rows=data.slice().sort((a,b)=>{const av=a[customerLogSort.key]??a.time??a.timestamp,bv=b[customerLogSort.key]??b.time??b.timestamp;const an=Number(av),bn=Number(bv);let c=customerLogSort.key==="time"?(new Date(av)-new Date(bv)):(Number.isFinite(an)&&Number.isFinite(bn)?an-bn:String(av).localeCompare(String(bv)));return customerLogSort.dir==="asc"?c:-c});',1)
p.write_text(s,encoding='utf-8')

# Remove temporary automation files; this commit leaves only the application changes.
for f in ('.github/v6_cleanup.py','.github/v6b.py','.github/workflows/jafafa-v6-cleanup.yml','.github/workflows/jafafa-v6-run.yml'):
    q=Path(f)
    if q.exists():q.unlink()

for f in ('index.html','customer.html'):
    t=Path(f).read_text(encoding='utf-8')
    if '<html' not in t.lower() or '</html>' not in t.lower():raise SystemExit(f'{f}: invalid html')
print('v6b patch complete')
