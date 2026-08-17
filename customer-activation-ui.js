/* Customer activation UI hardening: keep device identity private. */
(()=>{
  'use strict';
  if(!location.pathname.toLowerCase().includes('customer')) return;
  function patch(){
    document.querySelectorAll('#dashboardVehicles .metric,#vehiclesList .metric').forEach(m=>{
      const label=m.querySelector('small');
      if(label&&/dongle\s*mac/i.test(label.textContent||'')){
        label.textContent='Activation';
        const value=m.querySelector('b');
        if(value)value.textContent='Verified · Locked';
      }
    });
    const editLabel=[...document.querySelectorAll('#vehicleModal label')].find(x=>/dongle\s*mac/i.test(x.textContent||''));
    if(editLabel){editLabel.textContent='Activation status';const input=document.getElementById('editMac');if(input){input.value='Verified · Locked';input.disabled=true;input.type='text'}}
    document.querySelectorAll('#vehiclesList .empty,#dashboardVehicles .empty').forEach(x=>{x.innerHTML=x.innerHTML.replace(/using its JaFaFa dongle MAC/gi,'using your JaFaFa activation code').replace(/verify its JaFaFa dongle/gi,'verify your JaFaFa activation code')});
    const note=document.querySelector('#register .notice');if(note&&!note.dataset.activationPrivacy){note.dataset.activationPrivacy='1';note.textContent='Use the one-time activation code supplied with your physical JaFaFa dongle. The device identity is verified internally and remains locked after registration.'}
  }
  const observer=new MutationObserver(patch);
  function start(){patch();observer.observe(document.body,{childList:true,subtree:true});setInterval(patch,1200)}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
