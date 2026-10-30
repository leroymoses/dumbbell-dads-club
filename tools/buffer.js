// Dumbbell Dads Club: Buffer composer helpers.
// Loaded into publish.buffer.com in the Claude desktop app's built-in browser.
// Flow per post: open composer (real mouse click on the green "+"/New Post), then
//   await ddcFill(weekFile, postId)   -> uploads slides + caption
//   await ddcFinish()                 -> TikTok title, date/time, Schedule Posts
// Each call stays under ~20s so it fits the browser tool's time limit.

window.DDC_RAW = 'https://raw.githubusercontent.com/leroymoses/dumbbell-dads-club/main/posts/';
window.ddcSleep = ms => new Promise(r => setTimeout(r, ms));
window.ddcDlg = () => document.querySelector('input[name=file-upload-input]')?.closest('[role=dialog]');
window.ddcSetInput = (el, v) => {
  const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  el.focus(); s.call(el, v);
  el.dispatchEvent(new Event('input', { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
};
window.ddcBtn = (root, re) => [...root.querySelectorAll('button')].find(b => re.test(b.innerText.trim()));

window.ddcFill = async function (weekFile, id) {
  const sleep = ddcSleep;
  const disc = ddcBtn(document, /^Discard$/); if (disc) { disc.click(); await sleep(800); }
  const spec = await (await fetch(DDC_RAW + weekFile + '?' + Date.now())).json();
  const p = spec.posts.find(x => x.id === id); if (!p) throw new Error('no post ' + id);
  window.ddcP = p;
  const d = ddcDlg(); if (!d) throw new Error('composer not open');
  const inp = d.querySelector('input[name=file-upload-input]');
  const files = await Promise.all(p.images.map(async n => {
    const r = await fetch(DDC_RAW + n); if (!r.ok) throw new Error(n + ' ' + r.status);
    return new File([await r.blob()], n, { type: 'image/jpeg' });
  }));
  const dt = new DataTransfer(); files.forEach(f => dt.items.add(f));
  inp.files = dt.files; inp.dispatchEvent(new Event('change', { bubbles: true }));
  await sleep(5000);
  const ed = d.querySelector('[contenteditable=true]'); ed.focus(); await sleep(200);
  const lines = p.caption.split('\n');
  for (let i = 0; i < lines.length; i++) {
    if (lines[i]) document.execCommand('insertText', false, lines[i]);
    if (i < lines.length - 1) document.execCommand('insertParagraph');
  }
  await sleep(800);
  const imgs = [...d.querySelectorAll('button')].filter(b => (b.innerText.trim() || b.getAttribute('aria-label')) === 'Select to edit image').length;
  return { id, imgs, want: p.images.length, caption: ed.innerText.replace(/﻿/g, '').slice(0, 60) };
};

window.ddcFinish = async function () {
  const sleep = ddcSleep; const p = window.ddcP; const d = ddcDlg();
  const cz = ddcBtn(d, /^Customize/); if (cz) { cz.click(); await sleep(1500); }
  const t = d.querySelector('input[placeholder="Your post title"]'); if (t) { ddcSetInput(t, p.title); await sleep(300); }
  const trig = [...d.querySelectorAll('button')].find(b => /Next Available|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d/.test(b.innerText.trim()) && b.innerText.trim().length < 30);
  trig.click(); await sleep(800);
  const mi = [...document.querySelectorAll('[role=menuitem]')].find(e => e.innerText.trim().startsWith('Set Date and Time'));
  if (mi) { mi.click(); await sleep(1000); }
  let pk = document.querySelector('[class*=dateTimePicker]');
  if (!pk) { trig.click(); await sleep(1000); pk = document.querySelector('[class*=dateTimePicker]'); }
  if (!pk) throw new Error('no date picker');
  for (let k = 0; k < 3; k++) {
    const b = pk.querySelector(`button[aria-label^="${p.date_label}"]`);
    if (b) { b.click(); break; }
    pk.querySelector('button[aria-label^="Go to the Next Month"]').click(); await sleep(500);
  }
  await sleep(500); ddcSetInput(pk.querySelector('input[type=text]'), p.time); await sleep(600);
  const o = [...document.querySelectorAll('[role=option]')].find(e => e.innerText.trim() === p.time);
  if (o) { o.click(); await sleep(600); }
  const done = ddcBtn(document, /^Done$/); done && done.click(); await sleep(400);
  const footer = [...d.querySelectorAll('button')].map(b => b.innerText.trim()).find(x => /(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d/.test(x));
  const expect = p.date_label.replace(/^\w+, (\w{3})\w* (\d+)\w+, \d+$/, '$1 $2') + ', ' + p.time;
  if (footer !== expect || !t || t.value !== p.title) return { ABORT: true, footer, expect, title: t && t.value };
  if (window.DDC_MODE === 'draft') ddcBtn(d, /^Save Drafts?$/).click();
  else ddcBtn(d, /^Schedule Posts$/).click();
  await sleep(5000);
  return { ok: true, id: p.id, footer, mode: window.DDC_MODE || 'schedule', queue: document.querySelector('main')?.innerText.match(/Queue\s*\d+/)?.[0] };
};
'ddc helpers loaded';
