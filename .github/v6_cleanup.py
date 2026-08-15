from pathlib import Path
import re

ROOT = Path('.')

def replace_once(s, pattern, repl, name, flags=0):
    out, n = re.subn(pattern, repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'{name}: expected 1 match, got {n}')
    return out

# ============================= ADMIN =============================
p = ROOT / 'index.html'
s = p.read_text(encoding='utf-8')

# Duplicate vendor declarations from stacked UI patches.
s = re.sub(r'(-webkit-backdrop-filter:[^;]+;)\s*\1', r'\1', s)
s = re.sub(r'(-webkit-user-select:[^;]+;)\s*\1', r'\1', s)

# Fleet/UX layers use the canonical telemetry engine for freshness.
s = replace_once(
    s,
    r'function conn\(v\)\{.*?\}',
    'function conn(v){const a=window.analyzeVehicleTelemetry?.(v?.telemetry||[]);return a?.connection||"offline"}',
    'admin conn', re.S)

s = re.sub(r'function connLabel\(v\)\{.*?\}',
           'function connLabel(v){const s=conn(v);return s==="live"?"LIVE":s==="recent"?"RECENT":s==="stale"?"STALE":"OFFLINE"}', s, count=1)
s = re.sub(r'function connClass\(v\)\{.*?\}',
           'function connClass(v){const s=conn(v);return s==="live"?"live":s==="recent"?"recent":s==="stale"?"stale":"off"}', s, count=1)

# Alert rules must distinguish missing values from numeric zero.
for key in ('ctemp','rpm','speed'):
    s = re.sub(
        rf'if\(Number\(l\.{key}\|\|0\)>=TELEMETRY_CONFIG\.{key}\.(?:critical|warning)\)',
        lambda m: m.group(0).replace(f'Number(l.{key}||0)>=', f'Number.isFinite(Number(l.{key}))&&Number(l.{key})>='),
        s)
s = re.sub(r'if\(Number\(l\.voltage\|\|0\)<TELEMETRY_CONFIG\.voltage\.warningBelow\)',
             'if(Number.isFinite(Number(l.voltage))&&Number(l.voltage)>0&&Number(l.voltage)<TELEMETRY_CONFIG.voltage.warningBelow)', s)

# Remove the old Ctrl+K customer-search shortcut, leaving the actual command palette.
s = re.sub(r'\s*if\(\(e\.ctrlKey\|\|e\.metaKey\)&&e\.key\.toLowerCase\(\)==="k"\)\{\s*e\.preventDefault\(\);\s*showScreen\("screen-customers"\);\s*customerSearchInput\?\.focus\(\);\s*\}', '', s, count=1)

# Remove local-demo credential acceptance and generator.
s = re.sub(r'\s*function createLocalDemoCredential\(\)\{.*?\}\s*', '\n', s, count=1, flags=re.S)
s = re.sub(r'\s*if\(r\?\.credential===["\']local-demo["\']\)\{.*?\}\s*', '\n', s, count=1, flags=re.S)

# Detect nested ownership conflicts rather than silently changing customerId.
ownership_fn = '''function detectOwnershipConflicts(db){
  const seen=new Map(),conflicts=[];
  (Array.isArray(db)?db:[]).forEach(c=>(Array.isArray(c.cars)?c.cars:[]).forEach(v=>{
    const id=String(v?.id??v?.recordId??""); if(!id)return;
    const owner=String(c.id),prior=seen.get(id);
    if(prior&&prior.owner!==owner){
      const key=[id,prior.owner,owner].sort().join("|");
      if(!conflicts.some(x=>x.key===key))conflicts.push({key,vehicleId:id,customerIds:[prior.owner,owner]});
      v.ownershipConflict=true;v.ownershipConflictOwners=[prior.owner,owner];
      prior.vehicle.ownershipConflict=true;prior.vehicle.ownershipConflictOwners=[prior.owner,owner];
    }else if(!prior)seen.set(id,{owner,vehicle:v});
  }));
  window.JaFaFaOwnershipConflicts=conflicts;return conflicts;
}
'''
if 'function detectOwnershipConflicts(db)' not in s:
    s = s.replace('function load(){', ownership_fn + '\nfunction load(){', 1)
# Add conflict scan after the database has been loaded.
if 'detectOwnershipConflicts(MOCK_DATABASE)' not in s:
    s = re.sub(r'(function load\(\)\{.*?)(return MOCK_DATABASE;)', r'\1detectOwnershipConflicts(MOCK_DATABASE);\n\2', s, count=1, flags=re.S)

# Do not turn a nested vehicle into a different owner just because normalize ran.
s = s.replace('customerId:String(c.id)', 'customerId:String(v.customerId||c.id)')

p.write_text(s, encoding='utf-8')

# ============================ CUSTOMER ============================
p = ROOT / 'customer.html'
s = p.read_text(encoding='utf-8')

s = re.sub(r'(-webkit-backdrop-filter:[^;]+;)\s*\1', r'\1', s)

# Shared health/status engine is the only scoring authority.
s = re.sub(
    r'function analyze\(v\)\{.*?\}\nfunction health\(v\)\{.*?\}\n',
    'function analyze(v){return window.analyzeVehicleTelemetry?window.analyzeVehicleTelemetry(v?.telemetry||[]):{latest:latest(v),connection:"offline",overall:"warning",score:null,categories:[]}}\nfunction health(v){return window.vehicleHealthScore?.(v?.telemetry||[])??null}\n',
    s, count=1, flags=re.S)

# Login/sync should not silently overwrite an existing explicit owner.
s = s.replace('v.customerId=String(c.id);v.recordId=', 'if(!v.customerId)v.customerId=String(c.id);v.recordId=')

# Canonical latest reducer when the shared admin/core helper exists.
s = re.sub(
    r'function latest\(v\)\{[^}]*\}',
    'function latest(v){return window.latestTelemetry?.(v?.telemetry||[])||((v?.telemetry||[]).slice().sort((a,b)=>new Date(b.time||b.timestamp)-new Date(a.time||a.timestamp))[0]||null)}',
    s, count=1)

# v4/customer UI health adapter now derives from the same score/state engine.
s = re.sub(
    r'function health4\(v\)\{.*?\}\n\s*window\.JaFaFaCore=',
    '''function health4(v){
  const a=window.analyzeVehicleTelemetry?.(v?.telemetry||[]);
  if(!a)return {score:null,reasons:["Telemetry analysis unavailable"],severity:"offline"};
  const reasons=[];
  if(a.cooling==="overheating")reasons.push("Coolant temperature critical");else if(a.cooling==="warm")reasons.push("Coolant temperature elevated");
  if(a.electrical==="low-voltage")reasons.push("Battery voltage below normal");
  if(a.latest?.rpm!=null&&Number(a.latest.rpm)>=TELEMETRY_CONFIG.rpm.warning)reasons.push("High engine RPM");
  if(a.latest?.speed!=null&&Number(a.latest.speed)>=TELEMETRY_CONFIG.speed.warning)reasons.push("High vehicle speed");
  if(a.connection==="offline")reasons.push("Telemetry connection offline");else if(a.connection==="stale")reasons.push("Telemetry connection is stale");
  return {score:a.score,reasons,severity:a.overall};
}
window.JaFaFaCore=''',
    s, count=1, flags=re.S)

# Shared freshness policy: LIVE/RECENT/STALE/OFFLINE at 10/30/120 seconds.
s = re.sub(r'function telemetryState\(ts\)\{.*?\}',
           'function telemetryState(ts){const age=Date.now()-new Date(ts||0).getTime();if(!Number.isFinite(age)||age<0)return"offline";if(age<10000)return"live";if(age<30000)return"recent";if(age<120000)return"stale";return"offline"}', s, count=1)

# Explicit dashboard connectivity buckets, without calling RECENT a warning.
s = s.replace(
    "set('statOnline',as.filter(a=>a.connection==='online').length);set('statWarnings',as.filter(a=>a.overall==='warning').length+as.filter(a=>a.connection==='offline').length);",
    "set('statOnline',as.filter(a=>a.connection==='live').length);set('statWarnings',as.filter(a=>a.connection==='recent').length);set('statOffline',as.filter(a=>a.connection==='offline').length);"
)

# Preserve missing chart samples as gaps by drawing separate polyline segments.
s = re.sub(
    r'const pts=points\.map\(\(v,i\)=>v===null\?null:`\$\{35\+\(i/\(points\.length-1\|\|1\)\)\*830\},\$\{h-25-\(\(v-min\)/range\)\*170\}`\)\.filter\(Boolean\)\.join\(" "\);svg=',
    'const segments=[];let current=[];points.forEach((v,i)=>{if(v===null){if(current.length)segments.push(current.join(" "));current=[];return}current.push(`${35+(i/(points.length-1||1))*830},${h-25-((v-min)/range)*170}`)});if(current.length)segments.push(current.join(" "));svg=',
    s)
s = s.replace('<polyline class="line" points="${pts}"/>', '${segments.map(points=>`<polyline class="line" points="${points}"/>`).join("")}')

# Sortable customer log headers.
old = r'function renderLog\(data\)\{const rows=data\.slice\(\)\.sort\(\(a,b\)=>new Date\(b\.time\)-new Date\(a\.time\)\);\$\("logCount"\)\.textContent=`Showing \$\{rows\.length\.toLocaleString\(\)\} of \$\{rows\.length\.toLocaleString\(\)\} logs`;\$\("logBody"\)\.innerHTML=rows\.map\(x=>`<tr><td>\$\{new Date\(x\.time\|\|x\.timestamp\)\.toLocaleString\(\)</td><td>\$\{x\.speed\?\?"—"\}</td><td>\$\{x\.rpm\?\?"—"\}</td><td>\$\{x\.ctemp\?\?x\.coolant\?\?"—"\} °C</td><td>\$\{x\.voltage\?\?"—"\} V</td><td>\$\{x\.load\?\?"—"\}%</td></tr>`\)\.join\(""\);\}'
new = '''let customerLogSort={key:"time",dir:"desc"};
function renderLog(data){const rows=data.slice().sort((a,b)=>{const av=a[customerLogSort.key]??a.time??a.timestamp,bv=b[customerLogSort.key]??b.time??b.timestamp;const an=Number(av),bn=Number(bv);let cmp=customerLogSort.key==="time"?(new Date(av).getTime()-new Date(bv).getTime()):(Number.isFinite(an)&&Number.isFinite(bn)?an-bn:String(av??"").localeCompare(String(bv??"")));return customerLogSort.dir==="asc"?cmp:-cmp});
$("logCount").textContent=`Showing ${rows.length.toLocaleString()} of ${rows.length.toLocaleString()} logs`;
const headers=[['time','Time'],['speed','Speed'],['rpm','RPM'],['ctemp','Coolant'],['voltage','Voltage'],['load','Load']];
const head=document.querySelector("#logHead");if(head)head.innerHTML=headers.map(([k,label])=>`<th scope="col"><button type="button" class="log-sort ${customerLogSort.key===k?'active':''}" data-sort="${k}">${label} ${customerLogSort.key===k?(customerLogSort.dir==='asc'?'↑':'↓'):'↕'}</button></th>`).join("");
$("logBody").innerHTML=rows.map(x=>`<tr><td>${new Date(x.time||x.timestamp).toLocaleString()}</td><td>${x.speed??"—"}</td><td>${x.rpm??"—"}</td><td>${x.ctemp??x.coolant??"—"} °C</td><td>${x.voltage??"—"} V</td><td>${x.load??"—"}%</td></tr>`).join("");
head?.querySelectorAll("[data-sort]").forEach(b=>b.onclick=()=>{const k=b.dataset.sort;if(customerLogSort.key===k)customerLogSort.dir=customerLogSort.dir==='asc'?'desc':'asc';else{customerLogSort.key=k;customerLogSort.dir='asc'}renderLog(data)})}
'''
s = re.sub(old, new, s, count=1)

# Customer DB normalization detects conflicting ownership instead of repairing it by force.
s = re.sub(
    r'function normalizeDb\(db\)\{.*?\}\n\s*function writeDb',
    '''function normalizeDb(db){
  const list=Array.isArray(db)?db:[],seen=new Map(),conflicts=[];
  list.forEach(c=>{
    c.cars=Array.isArray(c.cars)?c.cars:[];
    c.cars.forEach(v=>{
      const id=String(v.id??v.recordId??"");if(!id)return;
      const owner=String(c.id),prior=seen.get(id);
      if(prior&&prior.owner!==owner){
        const key=[id,prior.owner,owner].sort().join("|");
        if(!conflicts.some(x=>x.key===key))conflicts.push({key,vehicleId:id,customerIds:[prior.owner,owner]});
        v.ownershipConflict=true;v.ownershipConflictOwners=[prior.owner,owner];
        prior.vehicle.ownershipConflict=true;prior.vehicle.ownershipConflictOwners=[prior.owner,owner];
      }else if(!prior)seen.set(id,{owner,vehicle:v});
      if(!v.customerId&&!v.ownershipConflict)v.customerId=owner;
      v.recordId=v.recordId||uid("veh");v.telemetry=Array.isArray(v.telemetry)?v.telemetry:[];
    });
  });
  window.JaFaFaOwnershipConflicts=conflicts;return list;
}
function writeDb''', s, count=1, flags=re.S)

# Reassignment explicitly writes the canonical owner.
s = s.replace('owner.cars.push(x.v);', 'x.v.customerId=String(owner.id);owner.cars.push(x.v);')

p.write_text(s, encoding='utf-8')

# ============================ SANITY ============================
for name in ('index.html','customer.html'):
    text=(ROOT/name).read_text(encoding='utf-8')
    if '<html' not in text.lower() or '</html>' not in text.lower():
        raise SystemExit(f'{name}: invalid HTML wrapper')

idx=(ROOT/'index.html').read_text(encoding='utf-8')
cx=(ROOT/'customer.html').read_text(encoding='utf-8')
for label,needle,text in [
    ('admin shared connection','window.analyzeVehicleTelemetry?.(v?.telemetry||[])',idx),
    ('admin finite alert','Number.isFinite(Number(l.ctemp))',idx),
    ('admin ownership conflict','detectOwnershipConflicts',idx),
    ('customer shared health','window.vehicleHealthScore?.(v?.telemetry||[])',cx),
    ('customer sortable log','customerLogSort',cx),
    ('customer ownership conflict','ownershipConflictOwners',cx),
]:
    if needle not in text: raise SystemExit(f'validation failed: {label}')

# Remove the temporary v6 automation itself in the same commit. The next push
# therefore cannot trigger these one-shot workflows again.
for rel in ('.github/v6_cleanup.py','.github/workflows/jafafa-v6-run.yml','.github/workflows/jafafa-v6-cleanup.yml'):
    q=ROOT/rel
    if q.exists(): q.unlink()

print('JaFaFa v6 cleanup complete')
