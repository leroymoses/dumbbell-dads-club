await new Promise(r=>setTimeout(r,5000));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const IDX=__I__;
const els=[...document.querySelectorAll('*')].filter(e=>e.childElementCount===0&&e.textContent.trim()==='Edit post');
const b=els[IDX].closest('button'); b.scrollIntoView({block:'center'}); await sleep(300); b.click();
for(let k=0;k<12;k++){await sleep(700); const d=document.querySelector('[role=dialog]'); if(d&&d.querySelector('[contenteditable=true]')&&/Nov \d/.test(d.innerText)) break;}
const d=document.querySelector('[role=dialog]');
if(!d||!d.querySelector('[contenteditable=true]')) ({IDX,err:'no editor'}); else {
const net=d.innerText.includes('Reel')?'instagram':'tiktok';
const date=[...d.querySelectorAll('button')].map(b=>b.innerText.trim()).find(t=>/Nov \d/.test(t));
let mode=[...d.querySelectorAll('button')].map(b=>b.innerText.trim()).find(t=>/^(Automatic|Notify Me)$/.test(t));
let res={IDX,net,date,mode};
if(net==='tiktok'&&mode==='Automatic'){
 const a=[...d.querySelectorAll('button')].find(b=>b.innerText.trim()==='Automatic');
 for(const t of ['pointerdown','mousedown','pointerup','mouseup']) a.dispatchEvent(new PointerEvent(t,{bubbles:true,button:0,pointerType:'mouse'})); await sleep(700);
 let item=[...document.querySelectorAll('[role=menuitem],[role=menuitemradio],[role=option]')].find(e=>e.innerText.trim().startsWith('Notify Me'));
 if(!item){a.click(); await sleep(700); item=[...document.querySelectorAll('[role=menuitem],[role=menuitemradio],[role=option]')].find(e=>e.innerText.trim().startsWith('Notify Me'));}
 if(item){ item.click(); await sleep(800);
  mode=[...d.querySelectorAll('button')].map(b=>b.innerText.trim()).find(t=>/^(Automatic|Notify Me)$/.test(t));
  if(mode==='Notify Me'){ [...d.querySelectorAll('button')].find(b=>b.innerText.trim()==='Save').click(); await sleep(4000); res.saved=!document.querySelector('[role=dialog] [contenteditable=true]'); } else res.err='mode '+mode;
 } else res.err='menu';
}
res }
