const fs = require('fs');
const html = fs.readFileSync(__dirname + '/prototype.html','utf8');
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

const probe = `;module.exports = { parsePrompt, applySpec, shuffleLayout, PATTERNS, CAT, chairSpots,
  arrangementsFor, areaOfTent, areaOfCanvas, tentHolding, latticeFor, validArrangement,
  getItems:()=>items, setItems:v=>{items=v;}, setVenue:v=>{venue=v;}, getVenue:()=>venue,
  lastToast:()=>document.getElementById("toastMsg").innerHTML };`;
const mod = {exports:{}};
new Function('module','exports', script + probe)(mod, mod.exports);
const A = mod.exports;

const { overlaps } = require('./geom-check')(A);

function insideTents(){
  const tents = A.getItems().filter(i => A.CAT[i.k].cat === 'tent');
  if (!tents.length) return 'no tent';
  const tables = A.getItems().filter(i => A.CAT[i.k].cat === 'table');
  return `${tables.filter(t => A.tentHolding(t, tents)).length}/${tables.length} inside tents`;
}

const CASES = [
  '20x20 tent with 4 round tables and 32 padded chairs',
  'three 20x20 tents with 12 round tables and 96 chairs',
  '10x20 tent with 2 8ft tables and 16 basic chairs',
  '20x20 tent with 8 cocktail tables',
  '40 guests',
  '20x20 tent with 6 6ft tables and 36 chairs',
  '20x20 tent with 4 6ft tables and 24 basic chairs',
  '30x40 yard with 6 8ft tables and 48 chairs',
  '20x20 tent with 3 6ft tables and 18 chairs',
];
let fails = 0;
for (const c of CASES){
  A.setItems([]); A.setVenue({w:40,h:60});
  A.applySpec(A.parsePrompt(c));
  console.log(`\n"${c}"`);
  const seen = new Set();
  for (let k = 0; k < 8; k++){
    A.shuffleLayout();
    const toast = A.lastToast().replace(/<[^>]+>/g, ' ').replace(/\s+/g,' ').trim();
    const name = toast.split('—')[0].trim();
    const bad = overlaps();
    if (bad.length){ fails++; console.log(`   ❌ ${name}: ${bad.slice(0,2).join(', ')}`); }
    else if (!seen.has(name)){
      seen.add(name);
      console.log(`   ✅ ${name.padEnd(16)} ${insideTents()}`);
    }
  }
  if (seen.size <= 1 && !seen.has('Nothing to rearrange yet')) console.log('   (only one arrangement available)');
}
console.log(fails ? `\n❌ ${fails} shuffles produced overlaps` : '\n✅ no shuffle produced an overlap');
