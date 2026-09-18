const fs = require('fs');
const html = fs.readFileSync(__dirname + '/prototype.html','utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>\s*$/)[1];
function mkEl(id){ return { id, style:{}, dataset:{}, classList:{add(){},remove(){},toggle(){},contains(){return false}},
  innerHTML:'', value:'', textContent:'', disabled:false, addEventListener(){}, focus(){}, blur(){}, setSelectionRange(){},
  getBoundingClientRect(){ return {width:390,height:520,left:0,top:0}; }, setAttribute(){}, removeAttribute(){},
  getAttribute(){return null}, querySelectorAll(){return []}, querySelector(){return null}, closest(){return null}, parentElement:null }; }
const els={};
global.document={documentElement:mkEl('r'),getElementById(i){return els[i]||(els[i]=mkEl(i))},
  querySelector(){return{dataset:{val:'r5'}}},querySelectorAll(){return[]},createElement(){return mkEl('t')},body:{appendChild(){}}};
global.window={addEventListener(){},visualViewport:null,scrollTo(){}};
global.getComputedStyle=()=>({getPropertyValue:()=>'#000'});
global.navigator={};
const mod={exports:{}};
new Function('module','exports', script + `;module.exports={parsePrompt,applySpec,quoteLines,CAT,chairSpots,
  DANCE,FLOOR_KEYS,recommendFloor,danceAreaFor,floorDancers,floorArea,shuffleLayout,
  getItems:()=>items,setItems:v=>{items=v},setVenue:v=>{venue=v},getVenue:()=>venue,
  lastToast:()=>document.getElementById("toastMsg").innerHTML};`)(mod, mod.exports);
const A = mod.exports;
const { overlaps } = require('./geom-check')(A);

console.log('--- sizing rule: 50% dancing x 3 sq ft ---');
for (const g of [30, 40, 60, 80, 100, 120, 150, 200, 300]){
  const need = A.danceAreaFor(g), k = A.recommendFloor(g);
  console.log(`  ${String(g).padStart(3)} guests -> ${String(Math.round(g*A.DANCE.share)).padStart(3)} dancing`
    + ` x3 = ${String(need).padStart(4)} sq ft -> ${A.CAT[k].size.padEnd(6)} (${String(A.floorArea(k)).padStart(3)} sq ft, ${A.floorDancers(k)} dancers)`);
}
console.log('\n--- stocked sizes ---');
console.log('  ' + A.FLOOR_KEYS.map(k=>`${A.CAT[k].size} (${A.floorArea(k)}sf/${A.floorDancers(k)})`).join('  '));

console.log('\n--- prompts ---');
const CASES = [
  '20x20 tent with 4 round tables, 32 padded chairs and a dance floor',
  '100 guests, 5ft rounds, padded chairs, tents and a dance floor',
  '20x20 tent with an 18x18 dance floor',
  '20x20 tent with a 30x30 dance floor',
  '60 guests with a dance floor',
  '20x20 tent with 4 round tables and 32 chairs, no dance floor',
];
let fails = 0;
for (const c of CASES){
  A.setItems([]); A.setVenue({w:40,h:60});
  A.applySpec(A.parsePrompt(c));
  const floors = A.getItems().filter(i => A.CAT[i.k].cat==='floor');
  const bad = overlaps();
  if (bad.length) fails++;
  const q = A.quoteLines();
  console.log(`${bad.length?'❌':'✅'} "${c}"`);
  const tents = A.getItems().filter(i=>A.CAT[i.k].cat==='tent');
  const tbl = A.getItems().filter(i=>A.CAT[i.k].cat==='table');
  const inside = tbl.filter(t => tents.some(n => {const c=A.CAT[n.k];
    return Math.abs(t.x-n.x)<=c.w/2 && Math.abs(t.y-n.y)<=c.h/2;})).length;
  console.log(`    floors: ${floors.map(f=>A.CAT[f.k].size).join(',') || 'none'}`
    + ` · tables: ${inside}/${tbl.length} inside tents`
    + ` · $${q.total.toFixed(2)}${q.onReq?' + on request':''}`);
  const nt = A.lastToast().replace(/<[^>]+>/g,' ').replace(/\s+/g,' ');
  const after = nt.split('—').slice(1).join('—').trim();
  if (after) console.log(`    note: ${after.slice(0,170)}`);
  if (bad.length) console.log('    ' + bad.slice(0,3).join(', '));
  const line = q.cats['Dance floor'].map(l=>`${l.qty}x ${l.label}`).join('; ');
  if (line) console.log(`    quote: ${line}`);
}

console.log('\n--- shuffle keeps clear of the floor ---');
A.setItems([]); A.setVenue({w:40,h:60});
A.applySpec(A.parsePrompt('20x20 tent with 4 round tables, 32 chairs and a dance floor'));
for (let i=0;i<6;i++){
  A.shuffleLayout();
  const bad = overlaps();
  const floors = A.getItems().filter(i=>A.CAT[i.k].cat==='floor');
  const tables = A.getItems().filter(i=>A.CAT[i.k].cat==='table');
  // tables must not sit on the floor
  let onFloor = 0;
  for (const f of floors){ const c=A.CAT[f.k];
    for (const t of tables) if (Math.abs(t.x-f.x) < c.w/2 && Math.abs(t.y-f.y) < c.h/2) onFloor++; }
  if (bad.length || onFloor) fails++;
  console.log(`  ${bad.length||onFloor?'❌':'✅'} shuffle ${i+1}: ${A.lastToast().replace(/<[^>]+>/g,' ').split('—')[0].trim()}`
    + (onFloor?` — ${onFloor} table(s) ON the dance floor`:''));
}
console.log(fails ? `\n❌ ${fails} failures` : '\n✅ all dance-floor layouts clean');
