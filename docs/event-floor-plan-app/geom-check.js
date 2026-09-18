/* Exact overlap geometry, shared by the layout tests.
   Usage: require('./geom-check')(A).overlaps()  where A is the app module. */
module.exports = function(A){
/* Exact geometry check, independent of the app's own maths.
   Chairs and rectangular tables are oriented boxes (SAT); round tables are
   circles (distance, or clamp-to-box against a rotated table). */
const EPS = 0.02;
function obbVsObb(a, b){
  const axes = [];
  for (const o of [a, b]){
    const c = Math.cos(o.a), s = Math.sin(o.a);
    axes.push({x:c, y:s}, {x:-s, y:c});
  }
  const span = (o, ax) => {
    const c = Math.cos(o.a), s = Math.sin(o.a);
    const r = Math.abs(c*ax.x + s*ax.y)*o.hw + Math.abs(-s*ax.x + c*ax.y)*o.hh;
    const ctr = o.x*ax.x + o.y*ax.y;
    return [ctr - r, ctr + r];
  };
  for (const ax of axes){
    const [a0,a1] = span(a, ax), [b0,b1] = span(b, ax);
    if (a1 <= b0 + EPS || b1 <= a0 + EPS) return false;    // separating axis
  }
  return true;
}
function circleVsObb(c, o){
  const ca = Math.cos(-o.a), sa = Math.sin(-o.a);
  const dx = c.x - o.x, dy = c.y - o.y;
  const lx = dx*ca - dy*sa, ly = dx*sa + dy*ca;            // circle in box frame
  const qx = Math.max(-o.hw, Math.min(o.hw, lx));
  const qy = Math.max(-o.hh, Math.min(o.hh, ly));
  return Math.hypot(lx-qx, ly-qy) < c.r - EPS;
}
function hits(a, b){
  if (a.r && b.r) return Math.hypot(a.x-b.x, a.y-b.y) < a.r + b.r - EPS;
  if (a.r) return circleVsObb(a, b);
  if (b.r) return circleVsObb(b, a);
  return obbVsObb(a, b);
}
function shapes(){
  const out = [];
  for (const it of A.getItems()){
    const c = A.CAT[it.k];
    if (c.cat !== 'table') continue;
    const rad = it.rot*Math.PI/180, cs = Math.cos(rad), sn = Math.sin(rad);
    for (const sp of A.chairSpots(c, it.props.chairs))
      out.push({kind:'chair', tid:it.id,
                x: it.x + sp.x*cs - sp.y*sn, y: it.y + sp.x*sn + sp.y*cs,
                hw:0.7, hh:0.7, a: rad + sp.rot*Math.PI/180});
    if (c.shape === 'round') out.push({kind:'table', tid:it.id, x:it.x, y:it.y, r:c.d/2});
    else out.push({kind:'table', tid:it.id, x:it.x, y:it.y, hw:c.w/2, hh:c.h/2, a:rad});
  }
  return out;
}
function overlaps(){
  const s = shapes(), bad = [];
  for (let i=0;i<s.length;i++) for (let j=i+1;j<s.length;j++){
    if (s[i].tid === s[j].tid) continue;
    if (hits(s[i], s[j])) bad.push(`${s[i].kind}#${s[i].tid}/${s[j].kind}#${s[j].tid}`);
  }
  return bad;
}
function insideTents(){
  const tents = A.getItems().filter(i => A.CAT[i.k].cat==='tent');
  if (!tents.length) return 'n/a';
  const tables = A.getItems().filter(i => A.CAT[i.k].cat==='table');
  const inside = tables.filter(t => A.tentHolding(t, tents)).length;
  return `${inside}/${tables.length} inside tents`;
}
  return { overlaps, shapes };
};
