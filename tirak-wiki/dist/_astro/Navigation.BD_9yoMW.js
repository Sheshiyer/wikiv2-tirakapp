import{M as A,j as t,u as F,P as B,a as I,b as L,L as O,m as D}from"./proxy.DbPUtWmP.js";import{r as n}from"./index.DK-fsZOb.js";import{c as y}from"./createLucideIcon.By8KUoG6.js";import{U as $}from"./users.of0paSPY.js";class S extends n.Component{getSnapshotBeforeUpdate(r){const e=this.props.childRef.current;if(e&&r.isPresent&&!this.props.isPresent){const o=this.props.sizeRef.current;o.height=e.offsetHeight||0,o.width=e.offsetWidth||0,o.top=e.offsetTop,o.left=e.offsetLeft}return null}componentDidUpdate(){}render(){return this.props.children}}function T({children:s,isPresent:r}){const e=n.useId(),o=n.useRef(null),g=n.useRef({width:0,height:0,top:0,left:0}),{nonce:f}=n.useContext(A);return n.useInsertionEffect(()=>{const{width:h,height:a,top:p,left:i}=g.current;if(r||!o.current||!h||!a)return;o.current.dataset.motionPopId=e;const l=document.createElement("style");return f&&(l.nonce=f),document.head.appendChild(l),l.sheet&&l.sheet.insertRule(`
          [data-motion-pop-id="${e}"] {
            position: absolute !important;
            width: ${h}px !important;
            height: ${a}px !important;
            top: ${p}px !important;
            left: ${i}px !important;
          }
        `),()=>{document.head.removeChild(l)}},[r]),t.jsx(S,{isPresent:r,childRef:o,sizeRef:g,children:n.cloneElement(s,{ref:o})})}const U=({children:s,initial:r,isPresent:e,onExitComplete:o,custom:g,presenceAffectsLayout:f,mode:h})=>{const a=F(K),p=n.useId(),i=n.useCallback(u=>{a.set(u,!0);for(const v of a.values())if(!v)return;o&&o()},[a,o]),l=n.useMemo(()=>({id:p,initial:r,isPresent:e,custom:g,onExitComplete:i,register:u=>(a.set(u,!1),()=>a.delete(u))}),f?[Math.random(),i]:[e,i]);return n.useMemo(()=>{a.forEach((u,v)=>a.set(v,!1))},[e]),n.useEffect(()=>{!e&&!a.size&&o&&o()},[e]),h==="popLayout"&&(s=t.jsx(T,{isPresent:e,children:s})),t.jsx(B.Provider,{value:l,children:s})};function K(){return new Map}const b=s=>s.key||"";function R(s){const r=[];return n.Children.forEach(s,e=>{n.isValidElement(e)&&r.push(e)}),r}const V=({children:s,custom:r,initial:e=!0,onExitComplete:o,presenceAffectsLayout:g=!0,mode:f="sync",propagate:h=!1})=>{const[a,p]=I(h),i=n.useMemo(()=>R(s),[s]),l=h&&!a?[]:i.map(b),u=n.useRef(!0),v=n.useRef(i),k=F(()=>new Map),[N,E]=n.useState(i),[m,w]=n.useState(i);L(()=>{u.current=!1,v.current=i;for(let d=0;d<m.length;d++){const c=b(m[d]);l.includes(c)?k.delete(c):k.get(c)!==!0&&k.set(c,!1)}},[m,l.length,l.join("-")]);const C=[];if(i!==N){let d=[...i];for(let c=0;c<m.length;c++){const x=m[c],M=b(x);l.includes(M)||(d.splice(c,0,x),C.push(x))}f==="wait"&&C.length&&(d=C),w(R(d)),E(i);return}const{forceRender:j}=n.useContext(O);return t.jsx(t.Fragment,{children:m.map(d=>{const c=b(d),x=h&&!a?!1:i===m||l.includes(c),M=()=>{if(k.has(c))k.set(c,!0);else return;let H=!0;k.forEach(P=>{P||(H=!1)}),H&&(j?.(),w(v.current),h&&p?.(),o&&o())};return t.jsx(U,{isPresent:x,initial:!u.current||e?void 0:!1,custom:x?void 0:r,presenceAffectsLayout:g,mode:f,onExitComplete:x?void 0:M,children:d},c)})})};/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const W=y("Book",[["path",{d:"M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20",key:"t4utmx"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const X=y("FolderOpen",[["path",{d:"m6 14 1.5-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.54 6a2 2 0 0 1-1.95 1.5H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H18a2 2 0 0 1 2 2v2",key:"usdka0"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const q=y("HeartHandshake",[["path",{d:"M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z",key:"c3ymky"}],["path",{d:"M12 5 9.04 7.96a2.17 2.17 0 0 0 0 3.08v0c.82.82 2.13.85 3 .07l2.07-1.9a2.82 2.82 0 0 1 3.79 0l2.96 2.66",key:"12sd6o"}],["path",{d:"m18 15-2-2",key:"60u0ii"}],["path",{d:"m15 18-2-2",key:"6p76be"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const G=y("Home",[["path",{d:"m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",key:"y5dka4"}],["polyline",{points:"9 22 9 12 15 12 15 22",key:"e2us08"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Y=y("Megaphone",[["path",{d:"m3 11 18-5v12L3 14v-3z",key:"n962bs"}],["path",{d:"M11.6 16.8a3 3 0 1 1-5.8-1.6",key:"1yl0tm"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Z=y("Menu",[["line",{x1:"4",x2:"20",y1:"12",y2:"12",key:"1e0a9i"}],["line",{x1:"4",x2:"20",y1:"6",y2:"6",key:"1owob3"}],["line",{x1:"4",x2:"20",y1:"18",y2:"18",key:"yk5zj1"}]]);/**
 * @license lucide-react v0.300.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const _=y("X",[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]]),z=[{name:"Welcome",href:"/docs/01-introduction/welcome",icon:G},{name:"About Tirak",href:"/docs/02-foundation/positioning",icon:W},{name:"Your Customers",href:"/docs/03-audience/companion-persona",icon:$},{name:"Marketing Hub",href:"/docs/04-campaign/pre-launch-ads",icon:Y},{name:"Resources",href:"/docs/05-resources/faq",icon:X},{name:"Partner Portal",href:"/docs/06-vendor-pipeline",icon:q}],ne=()=>{const[s,r]=n.useState(!1);return t.jsxs("nav",{className:"fixed top-0 left-0 right-0 z-50 px-4 py-3 border-b border-white/10 bg-[#0f0f13]/80 backdrop-blur-lg",children:[t.jsxs("div",{className:"max-w-7xl mx-auto flex items-center justify-between",children:[t.jsxs("a",{href:"/",className:"flex items-center gap-2 group",children:[t.jsx("div",{className:"w-8 h-8 rounded-full bg-gradient-to-br from-[#F5A6BF] to-[#9B8FD9] group-hover:scale-110 transition-transform duration-300"}),t.jsx("span",{className:"text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#F5A6BF] to-[#9B8FD9]",children:"Tirak"})]}),t.jsx("div",{className:"hidden md:flex items-center gap-6",children:z.map(e=>t.jsxs("a",{href:e.href,className:"text-gray-300 hover:text-white transition-colors text-sm font-medium flex items-center gap-2 group",children:[t.jsx(e.icon,{size:16,className:"group-hover:text-[#F5A6BF] transition-colors"}),e.name]},e.name))}),t.jsx("button",{onClick:()=>r(!s),className:"md:hidden p-2 text-gray-300 hover:text-white","aria-label":s?"Close navigation menu":"Open navigation menu","aria-expanded":s,"aria-controls":"mobile-nav-menu",children:s?t.jsx(_,{size:24}):t.jsx(Z,{size:24})})]}),t.jsx(V,{children:s&&t.jsx(D.div,{id:"mobile-nav-menu",initial:{opacity:0,height:0},animate:{opacity:1,height:"auto"},exit:{opacity:0,height:0},className:"md:hidden overflow-hidden bg-[#0f0f13] border-b border-white/10",children:t.jsx("div",{className:"px-4 py-6 space-y-4",children:z.map(e=>t.jsxs("a",{href:e.href,className:"block text-gray-300 hover:text-[#F5A6BF] text-lg font-medium flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors",onClick:()=>r(!1),children:[t.jsx(e.icon,{size:20,className:"text-[#9B8FD9]"}),e.name]},e.name))})})})]})};export{ne as Navigation};
