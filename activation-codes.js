/* JaFaFa activation-code layer — prototype/local data only. */
(()=>{
  'use strict';
  const ACTIVATION_KEY='jafafa_activation_codes_v1';
  const DONGLE_KEY='jafafa_dongle_registry_v1';
  const DB_KEY='jafafa_fleet_suite_v3';
  const uid=p=>`${p}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,9)}`;
  const read=(k,f)=>{try{const v=JSON.parse(localStorage.getItem(k)||'null');return v??f}catch{return f}};
  const write=(k,v)=>localStorage.setItem(k,JSON.stringify(v));
  const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const normMac=v=>String(v??'').trim().toUpperCase().replace(/[-.\s]/g,':').replace(/:{2,}/g,':');
  const validMac=v=>/^([0-9A-F]{2}:){5}[0-9A-F]{2}$/.test(normMac(v));
  const normCode=v=>String(v??'').trim().toUpperCase().replace(/[\s_]+/g,'-');
  const now=()=>new Date().toISOString();

  function codes(){const x=read(ACTIVATION_KEY,[]);return Array.isArray(x)?x:[]}
  function saveCodes(x){write(ACTIVATION_KEY,x)}
  function dongles(){const x=read(DONGLE_KEY,[]);return Array.isArray(x)?x:[]}
  function saveDongles(x){write(DONGLE_KEY,x)}
  function db(){const x=read(DB_KEY,[]);return Array.isArray(x)?x:[]}
  function assigned(mac){const m=normMac(mac);return db().some(c=>(c.cars||[]).some(v=>normMac(v.dongleMac||v.deviceId||v.obdId||v.mac||'')===m))}
  function randomCode(){
    const alphabet='ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    const bytes=new Uint8Array(12); if(window.crypto?.getRandomValues) crypto.getRandomValues(bytes); else for(let i=0;i<bytes.length;i++)bytes[i]=Math.floor(Math.random()*256);
    let s=''; for(const b of bytes)s+=alphabet[b%alphabet.length];
    return `JF-ACT-${s.slice(0,4)}-${s.slice(4,8)}-${s.slice(8,12)}`;
  }
  function seed(){
    const list=codes(); if(list.length)return;
    saveCodes([{id:uid('ACT'),code:'JF-ACT-DEMO-2026-TEST',mac:'00:10:CC:4F:36:03',status:'AVAILABLE',createdAt:now(),source:'demo'}]);
  }
  function getActivation(code){const n=normCode(code);return codes().find(x=>normCode(x.code)===n)||null}
  function activate(code,customer,vehicle){
    const n=normCode(code), list=codes(), item=list.find(x=>normCode(x.code)===n);
    if(!item)return{ok:false,reason:'Activation code not found.'};
    if(item.status==='DISABLED')return{ok:false,reason:'This activation code has been disabled.'};
    if(item.status!=='AVAILABLE')return{ok:false,reason:'This activation code has already been used.'};
    const mac=normMac(item.mac); if(!validMac(mac))return{ok:false,reason:'This activation code is not linked to a valid JaFaFa device.'};
    if(assigned(mac))return{ok:false,reason:'The dongle linked to this activation code is already assigned.'};
    item.status='ACTIVATED'; item.activatedAt=now(); item.activatedByCustomerId=String(customer?.id||''); item.vehicleId=String(vehicle?.id||'');
    saveCodes(list);
    return{ok:true,mac,item};
  }
  function ensureAdminUI(){
    const tabs=document.querySelector('.jf-suite-tabs'); if(!tabs||tabs.querySelector('[data-suite="activation-codes"]'))return false;
    const b=document.createElement('button'); b.type='button'; b.dataset.suite='activation-codes'; b.textContent='Activation Codes';
    b.onclick=()=>renderAdmin(); tabs.appendChild(b); return true;
  }
  function style(){
    if(document.getElementById('jf-activation-style'))return;
    const s=document.createElement('style');s.id='jf-activation-style';s.textContent=`
      .jf-activation-grid{display:grid;grid-template-columns:minmax(280px,.8fr) minmax(420px,1.2fr);gap:14px}
      .jf-activation-card{border:1px solid var(--line,#26344a);border-radius:16px;background:rgba(7,14,26,.72);padding:18px}
      .jf-activation-card h3{margin:0 0 6px}.jf-activation-muted{color:var(--muted,#94a3b8);font-size:.72rem;line-height:1.55}
      .jf-activation-form{display:grid;gap:9px;margin-top:14px}.jf-activation-form label{font-size:.65rem;color:var(--muted,#94a3b8);text-transform:uppercase;letter-spacing:.08em}
      .jf-activation-form input{width:100%;border:1px solid var(--line,#26344a);border-radius:10px;background:#050c18;color:var(--text,#fff);padding:10px 11px}
      .jf-activation-form button,.jf-activation-action{border:1px solid var(--line-bright,#38bdf8);border-radius:10px;background:rgba(56,189,248,.1);color:var(--text,#fff);padding:10px 12px;font-weight:800;cursor:pointer}
      .jf-activation-list{display:grid;gap:8px;margin-top:12px}.jf-activation-row{display:grid;grid-template-columns:1.4fr .8fr 1fr auto;gap:10px;align-items:center;border:1px solid var(--line,#26344a);border-radius:11px;padding:11px}
      .jf-activation-row code{font-size:.72rem;color:#dff8ff}.jf-activation-status{font-size:.62rem;font-weight:900;text-transform:uppercase}.jf-activation-status.available{color:#4ade80}.jf-activation-status.activated{color:#38bdf8}.jf-activation-status.disabled{color:#fb7185}
      @media(max-width:900px){.jf-activation-grid{grid-template-columns:1fr}.jf-activation-row{grid-template-columns:1fr 1fr}.jf-activation-row button{grid-column:1/-1}}
    `;document.head.appendChild(s);
  }
  function renderAdmin(){
    ensureAdminUI(); style(); const host=document.getElementById('jfFleetHost'); if(!host)return;
    const list=codes().slice().reverse();
    host.innerHTML=`<div class="jf-activation-grid">
      <div class="jf-activation-card"><div class="eyebrow">Device provisioning</div><h3>Issue activation code</h3><div class="jf-activation-muted">Enter the dongle MAC from the physical device inventory. The customer will receive only the one-time activation code.</div>
      <form id="jfActivationForm" class="jf-activation-form"><label for="jfActivationMac">Dongle MAC</label><input id="jfActivationMac" placeholder="00:10:CC:4F:36:03" autocomplete="off" required><button>Generate one-time code</button></form><div id="jfActivationResult" class="jf-activation-muted" style="margin-top:12px"></div></div>
      <div class="jf-activation-card"><div class="eyebrow">Activation inventory</div><h3>Codes</h3><div class="jf-activation-muted">AVAILABLE codes can be used once. ACTIVATED codes are permanently consumed. DISABLED codes cannot be used.</div><div class="jf-activation-list">${list.length?list.map(renderRow).join(''):'<div class="jf-activation-muted">No activation codes yet.</div>'}</div></div>
    </div>`;
    document.querySelectorAll('[data-suite]').forEach(x=>x.classList.toggle('active',x.dataset.suite==='activation-codes'));
    document.getElementById('jfActivationForm').onsubmit=e=>{e.preventDefault();const mac=normMac(document.getElementById('jfActivationMac').value);const out=document.getElementById('jfActivationResult');if(!validMac(mac)){out.textContent='Enter a valid MAC address.';return}if(assigned(mac)){out.textContent='This dongle is already assigned to a vehicle.';return}const list=codes();if(list.some(x=>normMac(x.mac)===mac&&x.status==='AVAILABLE')){out.textContent='An unused activation code already exists for this dongle.';return}const ds=dongles();if(!ds.some(x=>normMac(x.mac||x.deviceId||x.obdId||'')===mac)){ds.push({id:uid('DNG'),mac,disabled:false,status:'ACTIVE',createdAt:now(),source:'activation-provisioning'});saveDongles(ds)}const item={id:uid('ACT'),code:randomCode(),mac,status:'AVAILABLE',createdAt:now(),source:'admin'};list.push(item);saveCodes(list);out.innerHTML=`<strong>Code created:</strong> <code>${esc(item.code)}</code><br>Store this code with the physical dongle. It can be used once.`;renderAdmin()};
    document.querySelectorAll('[data-activation-disable]').forEach(btn=>btn.onclick=()=>{const id=btn.dataset.activationDisable;const list=codes();const item=list.find(x=>x.id===id);if(!item||item.status!=='AVAILABLE')return;item.status='DISABLED';item.disabledAt=now();saveCodes(list);renderAdmin()});
  }
  function renderRow(x){return `<div class="jf-activation-row"><div><code>${esc(x.code)}</code><div class="jf-activation-muted">${esc(x.mac)} · ${new Date(x.createdAt).toLocaleDateString()}</div></div><span class="jf-activation-status ${String(x.status||'').toLowerCase()}">${esc(x.status)}</span><span class="jf-activation-muted">${x.activatedAt?'Used '+new Date(x.activatedAt).toLocaleString():'One time only'}</span>${x.status==='AVAILABLE'?`<button class="jf-activation-action" data-activation-disable="${esc(x.id)}">Disable</button>`:'<span></span>'}</div>`}

  function patchCustomer(){
    const form=document.getElementById('registerForm'); if(!form||form.dataset.activationPatched)return;
    form.dataset.activationPatched='1';
    const clone=form.cloneNode(true); form.replaceWith(clone);
    const f=clone, mac=f.querySelector('#vMac'), macField=mac?.closest('.field'), result=f.querySelector('#macResult');
    if(!mac||!macField||!result)return;
    macField.hidden=true; mac.required=false; mac.disabled=true;
    const field=document.createElement('div');field.className='field';field.innerHTML='<label for="vActivation">Activation code</label><input id="vActivation" required placeholder="JF-ACT-XXXX-XXXX-XXXX" autocomplete="one-time-code" spellcheck="false"><div class="jf-activation-help">Enter the one-time code supplied with your JaFaFa dongle. The code is consumed after successful registration.</div>';macField.parentElement.insertBefore(field,macField);
    result.id='activationResult'; result.textContent='';
    const heading=document.querySelector('#register .hero p'); if(heading)heading.textContent='Enter the vehicle information and the one-time activation code supplied with your JaFaFa dongle.';
    const notice=document.querySelector('#register .card .notice'); if(notice)notice.textContent='The activation code proves that this physical JaFaFa dongle was provisioned for activation. It can be used once. The dongle MAC remains hidden and locked after registration.';
    const button=f.querySelector('#registerSubmit');
    f.addEventListener('submit',e=>{
      e.preventDefault(); if(button)button.disabled=true; if(button)button.textContent='Verifying activation…'; result.className='notice'; result.textContent='Checking the one-time activation code.'; result.classList.remove('hidden');
      const code=normCode(f.querySelector('#vActivation').value), item=getActivation(code);
      if(!item){return fail('Activation code not found. Check the code and try again.')}
      if(item.status!=='AVAILABLE'){return fail(item.status==='DISABLED'?'This activation code has been disabled.':'This activation code has already been used.')}
      const macValue=normMac(item.mac); if(!validMac(macValue))return fail('This activation code is not linked to a valid device. Contact JaFaFa support.');
      if(assigned(macValue))return fail('The dongle linked to this activation code is already assigned.');
      const d=read(DB_KEY,[]);const session=read('jafafa_customer_session_v3',null);const c=d.find(x=>String(x.id)===String(session?.id)||String(x.email||'').toLowerCase()===String(session?.email||'').toLowerCase());
      if(!c)return fail('Customer account not found. Please sign in with Google again.');
      const id=uid('JFV'),plate=f.querySelector('#vPlate').value.trim();const v={id,recordId:id,customerId:String(c.id),make:f.querySelector('#vMake').value.trim(),model:f.querySelector('#vModel').value.trim(),year:Number(f.querySelector('#vYear').value),vin:f.querySelector('#vVin').value.trim().toUpperCase(),plate,registration:plate,nickname:f.querySelector('#vNickname').value.trim(),image:f.querySelector('#vImage').value.trim(),dongleMac:macValue,deviceId:macValue,obdId:macValue,status:'Active',activationCodeId:item.id,createdAt:now(),updatedAt:now()};
      c.cars=Array.isArray(c.cars)?c.cars:[];c.vehicleIds=Array.isArray(c.vehicleIds)?c.vehicleIds.map(String):[];c.cars.push(v);c.vehicleIds.push(id);c.updatedAt=now();d[d.findIndex(x=>String(x.id)===String(c.id))]=c;write(DB_KEY,d);
      item.status='ACTIVATED';item.activatedAt=now();item.activatedByCustomerId=String(c.id);item.vehicleId=id;saveCodes(codes());
      result.className='notice ok';result.textContent='Activation verified. Your dongle is now permanently locked to this vehicle.';f.reset();if(button){button.disabled=false;button.textContent='Verify & register vehicle'};window.dispatchEvent(new StorageEvent('storage',{key:DB_KEY}));if(typeof window.toast==='function')window.toast('Vehicle registered successfully.');else{const t=document.getElementById('toast');if(t){t.textContent='Vehicle registered successfully.';t.classList.add('show')}}setTimeout(()=>{document.querySelector('[data-view="vehicles"]')?.click()},600);
      function fail(msg){result.className='notice error';result.textContent=msg;result.classList.remove('hidden');if(button){button.disabled=false;button.textContent='Verify & register vehicle'}}
    });
    const codeInput=f.querySelector('#vActivation'); codeInput.addEventListener('input',()=>{const x=getActivation(codeInput.value);result.className=x?.status==='AVAILABLE'?'notice ok':'notice warn';result.textContent=x? (x.status==='AVAILABLE'?'✓ Activation code is valid and unused.':'This activation code is no longer available.') :'Activation code will be checked when entered completely.';result.classList.remove('hidden')});
    const help=document.createElement('style');help.textContent='.jf-activation-help{color:var(--muted,#8ea0b8);font-size:.62rem;line-height:1.45;margin-top:5px}';document.head.appendChild(help);
  }
  function boot(){seed(); if(location.pathname.toLowerCase().includes('customer'))patchCustomer(); else ensureAdminUI(); style();}
  window.JaFaFaActivation={codes,getActivation,activate,normalizeCode:normCode,renderAdmin};
  const obs=new MutationObserver(()=>{if(location.pathname.toLowerCase().includes('customer'))patchCustomer();else if(document.querySelector('.jf-suite-tabs'))ensureAdminUI()});
  function start(){boot();obs.observe(document.body,{childList:true,subtree:true});setInterval(()=>{if(location.pathname.toLowerCase().includes('customer'))patchCustomer();else{if(ensureAdminUI()&&document.querySelector('[data-suite="activation-codes"].active'))renderAdmin()}},700)}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
