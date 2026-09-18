const fs = require('fs');
const html = fs.readFileSync('/tmp/claude-0/-home-user-AMAIA/464edf24-c932-58ed-8871-d89913aab2e6/scratchpad/floor-planner-demo.html','utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>\s*$/)[1];
function mkEl(id){
  return { id, style:{}, dataset:{}, classList:{add(){},remove(){},toggle(){},contains(){return false}},
    innerHTML:'', value:'', textContent:'', disabled:false,
    addEventListener(){}, focus(){}, blur(){},
    getBoundingClientRect(){ return {width:390, height:520, left:0, top:0}; },
    setAttribute(){}, removeAttribute(){}, getAttribute(){return null},
    querySelectorAll(){return []}, querySelector(){return null}, closest(){return null}, parentElement:null };
}
const els = {};
global.document = { documentElement: mkEl('root'),
  getElementById(id){ return els[id] || (els[id] = mkEl(id)); },
  querySelector(){ return {dataset:{val:'r5'}}; }, querySelectorAll(){ return []; },
  createElement(){ return mkEl('t'); }, body:{appendChild(){}} };
global.window = { addEventListener(){}, visualViewport:null, scrollTo(){} };
global.getComputedStyle = () => ({ getPropertyValue: () => '#000' });
global.navigator = {};

const probe = `;module.exports = { parsePrompt, applySpec, quoteLines, CAT, CHAIRS, SPACING,
  chairSpots, tentSeats, getItems:()=>items, getVenue:()=>venue,
  setItems:v=>{items=v;}, setVenue:v=>{venue=v;}, lastToast:()=>document.getElementById("toastMsg").innerHTML };`;
const mod = {exports:{}};
new Function('module','exports', script + probe)(mod, mod.exports);
const A = mod.exports;

const CHAIR = 1.4;            // chair is 1.4ft square
// world-space AABB of every chair + every table top
function occupants(){
  const out = [];
  for (const it of A.getItems()){
    const c = A.CAT[it.k];
    if (c.cat !== 'table') continue;
    const rad = it.rot * Math.PI/180, cs = Math.cos(rad), sn = Math.sin(rad);
    for (const sp of A.chairSpots(c, it.props.chairs)){
      const x = it.x + sp.x*cs - sp.y*sn, y = it.y + sp.x*sn + sp.y*cs;
      out.push({ kind:'chair', tid:it.id, x, y, r: CHAIR/2 });
    }
    out.push({ kind:'table', tid:it.id, x:it.x, y:it.y,
               r: (c.shape==='round' ? c.d/2 : Math.max(c.w,c.h)/2) });
  }
  return out;
}
function overlaps(){
  const o = occupants(), bad = [];
  for (let i=0;i<o.length;i++) for (let j=i+1;j<o.length;j++){
    if (o[i].tid === o[j].tid) continue;           // same table's own chairs are fine
    const d = Math.hypot(o[i].x-o[j].x, o[i].y-o[j].y);
    const need = o[i].r + o[j].r;
    if (d < need - 0.02) bad.push(`${o[i].kind}#${o[i].tid} ↔ ${o[j].kind}#${o[j].tid} (gap ${(d-need).toFixed(2)}ft)`);
  }
  return bad;
}

const CASES = [
  "20x20 tent with 5 round tables, white tablecloths and 40 padded chairs",
  "20x20 tent with 4 round tables and 32 padded chairs",
  "60 guests, 8 ft tables, basic chairs, two 10x20 tents with string lights",
  "10 cocktail tables under a 20x20 tent with bistro lights",
  "40 guests",
  "100 guests with 8ft tables",
  "a tent for 24 people with 6ft tables and padded chairs",
  "10x10 tent, 2 six foot tables, 12 basic chairs",
  "backyard party in a 30x50 yard, 8 round tables, 64 padded chairs",
  "three 20x20 tents with 12 round tables and 96 chairs",
  "two 10x10 tents and one 20x20 tent with 6 round tables and 48 chairs",
  "150 guests, 5ft rounds, padded chairs, tents",
  "12 round tables in a 20x20 tent",
  "seating for 200",
  "6 cocktail tables and 4 round tables with 32 chairs under a 20x20 tent",
];
let fails = 0;
for (const c of CASES){
  A.setItems([]); A.setVenue({w:40,h:60});
  const spec = A.parsePrompt(c);
  A.applySpec(spec);
  const bad = overlaps();
  const v = A.getVenue();
  const tents = A.getItems().filter(i => A.CAT[i.k].cat==='tent').length;
  const tables = A.getItems().filter(i => A.CAT[i.k].cat==='table').length;
  const seats = A.getItems().reduce((n,i)=>n+(A.CAT[i.k].cat==='table'?i.props.chairs:0),0);
  if (bad.length) fails++;
  console.log(`${bad.length ? '❌' : '✅'} "${c}"`);
  console.log(`    canvas ${v.w}x${v.h} · ${tents} tents · ${tables} tables · ${seats} seats`);
  if (bad.length) console.log('    ' + bad.slice(0,3).join('\n    ') + (bad.length>3 ? `\n    ...and ${bad.length-3} more` : ''));
  const note = A.lastToast().replace(/<[^>]+>/g,' ').replace(/\s+/g,' ');
  if (/outside the tent|Seated|Aisles|grown/.test(note)) console.log('    note:', note.split('—').slice(1).join('—').trim().slice(0,150));
}
console.log(`\n${CASES.length - fails}/${CASES.length} layouts clean`);
console.log('tent seating at proper spacing: 10x10=' + A.tentSeats('tt1010','r5') +
            ' 10x20=' + A.tentSeats('tt1020','r5') + ' 20x20=' + A.tentSeats('tt2020','r5'));
