import{M as H,j as s,u as F,P as L,a as P,b as I,L as $,m as D}from"./proxy.DbPUtWmP.js";import{r as t}from"./index.DK-fsZOb.js";class O extends t.Component{getSnapshotBeforeUpdate(r){const e=this.props.childRef.current;if(e&&r.isPresent&&!this.props.isPresent){const o=this.props.sizeRef.current;o.height=e.offsetHeight||0,o.width=e.offsetWidth||0,o.top=e.offsetTop,o.left=e.offsetLeft}return null}componentDidUpdate(){}render(){return this.props.children}}function S({children:n,isPresent:r}){const e=t.useId(),o=t.useRef(null),h=t.useRef({width:0,height:0,top:0,left:0}),{nonce:f}=t.useContext(H);return t.useInsertionEffect(()=>{const{width:d,height:a,top:u,left:i}=h.current;if(r||!o.current||!d||!a)return;o.current.dataset.motionPopId=e;const c=document.createElement("style");return f&&(c.nonce=f),document.head.appendChild(c),c.sheet&&c.sheet.insertRule(`
          [data-motion-pop-id="${e}"] {
            position: absolute !important;
            width: ${d}px !important;
            height: ${a}px !important;
            top: ${u}px !important;
            left: ${i}px !important;
          }
        `),()=>{document.head.removeChild(c)}},[r]),s.jsx(O,{isPresent:r,childRef:o,sizeRef:h,children:t.cloneElement(n,{ref:o})})}const T=({children:n,initial:r,isPresent:e,onExitComplete:o,custom:h,presenceAffectsLayout:f,mode:d})=>{const a=F(U),u=t.useId(),i=t.useCallback(p=>{a.set(p,!0);for(const x of a.values())if(!x)return;o&&o()},[a,o]),c=t.useMemo(()=>({id:u,initial:r,isPresent:e,custom:h,onExitComplete:i,register:p=>(a.set(p,!1),()=>a.delete(p))}),f?[Math.random(),i]:[e,i]);return t.useMemo(()=>{a.forEach((p,x)=>a.set(x,!1))},[e]),t.useEffect(()=>{!e&&!a.size&&o&&o()},[e]),d==="popLayout"&&(n=s.jsx(S,{isPresent:e,children:n})),s.jsx(L.Provider,{value:c,children:n})};function U(){return new Map}const C=n=>n.key||"";function R(n){const r=[];return t.Children.forEach(n,e=>{t.isValidElement(e)&&r.push(e)}),r}const K=({children:n,custom:r,initial:e=!0,onExitComplete:o,presenceAffectsLayout:h=!0,mode:f="sync",propagate:d=!1})=>{const[a,u]=P(d),i=t.useMemo(()=>R(n),[n]),c=d&&!a?[]:i.map(C),p=t.useRef(!0),x=t.useRef(i),k=F(()=>new Map),[z,A]=t.useState(i),[g,M]=t.useState(i);I(()=>{p.current=!1,x.current=i;for(let m=0;m<g.length;m++){const l=C(g[m]);c.includes(l)?k.delete(l):k.get(l)!==!0&&k.set(l,!1)}},[g,c.length,c.join("-")]);const b=[];if(i!==z){let m=[...i];for(let l=0;l<g.length;l++){const y=g[l],w=C(y);c.includes(w)||(m.splice(l,0,y),b.push(y))}f==="wait"&&b.length&&(m=b),M(R(m)),A(i);return}const{forceRender:j}=t.useContext($);return s.jsx(s.Fragment,{children:g.map(m=>{const l=C(m),y=d&&!a?!1:i===g||c.includes(l),w=()=>{if(k.has(l))k.set(l,!0);else return;let N=!0;k.forEach(B=>{B||(N=!1)}),N&&(j?.(),M(x.current),d&&u?.(),o&&o())};return s.jsx(T,{isPresent:y,initial:!p.current||e?void 0:!1,custom:y?void 0:r,presenceAffectsLayout:h,mode:f,onExitComplete:y?void 0:w,children:m},l)})})};/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var q={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const V=n=>n.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase().trim(),v=(n,r)=>{const e=t.forwardRef(({color:o="currentColor",size:h=24,strokeWidth:f=2,absoluteStrokeWidth:d,className:a="",children:u,...i},c)=>t.createElement("svg",{ref:c,...q,width:h,height:h,stroke:o,strokeWidth:d?Number(f)*24/Number(h):f,className:["lucide",`lucide-${V(n)}`,a].join(" "),...i},[...r.map(([p,x])=>t.createElement(p,x)),...Array.isArray(u)?u:[u]]));return e.displayName=`${n}`,e};/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const W=v("Book",[["path",{d:"M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20",key:"t4utmx"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const X=v("FolderOpen",[["path",{d:"m6 14 1.5-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.54 6a2 2 0 0 1-1.95 1.5H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H18a2 2 0 0 1 2 2v2",key:"usdka0"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const G=v("Home",[["path",{d:"m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",key:"y5dka4"}],["polyline",{points:"9 22 9 12 15 12 15 22",key:"e2us08"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Z=v("Megaphone",[["path",{d:"m3 11 18-5v12L3 14v-3z",key:"n962bs"}],["path",{d:"M11.6 16.8a3 3 0 1 1-5.8-1.6",key:"1yl0tm"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const _=v("Menu",[["line",{x1:"4",x2:"20",y1:"12",y2:"12",key:"1e0a9i"}],["line",{x1:"4",x2:"20",y1:"6",y2:"6",key:"1owob3"}],["line",{x1:"4",x2:"20",y1:"18",y2:"18",key:"yk5zj1"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const J=v("Users",[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["path",{d:"M16 3.13a4 4 0 0 1 0 7.75",key:"1da9ce"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Q=v("X",[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]]),E=[{name:"Introduction",href:"/docs/01-introduction/welcome",icon:G},{name:"Foundation",href:"/docs/02-foundation/positioning",icon:W},{name:"Audiences",href:"/docs/03-audience/companion-persona",icon:J},{name:"Campaigns",href:"/docs/04-campaign/pre-launch-ads",icon:Z},{name:"Resources",href:"/docs/05-resources/faq",icon:X}],te=()=>{const[n,r]=t.useState(!1);return s.jsxs("nav",{className:"fixed top-0 left-0 right-0 z-50 px-4 py-3 border-b border-white/10 bg-[#0f0f13]/80 backdrop-blur-lg",children:[s.jsxs("div",{className:"max-w-7xl mx-auto flex items-center justify-between",children:[s.jsxs("a",{href:"/",className:"flex items-center gap-2 group",children:[s.jsx("div",{className:"w-8 h-8 rounded-full bg-gradient-to-br from-[#F5A6BF] to-[#9B8FD9] group-hover:scale-110 transition-transform duration-300"}),s.jsx("span",{className:"text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#F5A6BF] to-[#9B8FD9]",children:"Tirak"})]}),s.jsx("div",{className:"hidden md:flex items-center gap-6",children:E.map(e=>s.jsxs("a",{href:e.href,className:"text-gray-300 hover:text-white transition-colors text-sm font-medium flex items-center gap-2 group",children:[s.jsx(e.icon,{size:16,className:"group-hover:text-[#F5A6BF] transition-colors"}),e.name]},e.name))}),s.jsx("button",{onClick:()=>r(!n),className:"md:hidden p-2 text-gray-300 hover:text-white","aria-label":"Toggle menu",children:n?s.jsx(Q,{size:24}):s.jsx(_,{size:24})})]}),s.jsx(K,{children:n&&s.jsx(D.div,{initial:{opacity:0,height:0},animate:{opacity:1,height:"auto"},exit:{opacity:0,height:0},className:"md:hidden overflow-hidden bg-[#0f0f13] border-b border-white/10",children:s.jsx("div",{className:"px-4 py-6 space-y-4",children:E.map(e=>s.jsxs("a",{href:e.href,className:"block text-gray-300 hover:text-[#F5A6BF] text-lg font-medium flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors",onClick:()=>r(!1),children:[s.jsx(e.icon,{size:20,className:"text-[#9B8FD9]"}),e.name]},e.name))})})})]})};export{te as Navigation};
