(()=>{"use strict";(()=>{let t;var e=Object.defineProperty,i=Object.getOwnPropertyDescriptor,r=(t,r,o,s)=>{for(var a,n=s>1?void 0:s?i(r,o):r,l=t.length-1;l>=0;l--)(a=t[l])&&(n=(s?a(r,o,n):a(n))||n);return s&&n&&e(r,o,n),n},o=globalThis,s=o.ShadowRoot&&(void 0===o.ShadyCSS||o.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,a=Symbol(),n=new WeakMap,l=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==a)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(s&&void 0===t){let i=void 0!==e&&1===e.length;i&&(t=n.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&n.set(e,t))}return t}toString(){return this.cssText}},h=(t,...e)=>new l(1===t.length?t[0]:e.reduce((e,i,r)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[r+1],t[0]),t,a),p=s?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e,i="";for(let e of t.cssRules)i+=e.cssText;return new l("string"==typeof(e=i)?e:e+"",void 0,a)})(t):t,{is:d,defineProperty:c,getOwnPropertyDescriptor:g,getOwnPropertyNames:u,getOwnPropertySymbols:b,getPrototypeOf:f}=Object,v=globalThis,m=v.trustedTypes,$=m?m.emptyScript:"",x=v.reactiveElementPolyfillSupport,w={toAttribute(t,e){switch(e){case Boolean:t=t?$:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},y=(t,e)=>!d(t,e),_={attribute:!0,type:String,converter:w,reflect:!1,hasChanged:y};Symbol.metadata??=Symbol("metadata"),v.litPropertyMetadata??=new WeakMap;var k=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=_){if(e.state&&(e.attribute=!1),this._$Ei(),this.elementProperties.set(t,e),!e.noAccessor){let i=Symbol(),r=this.getPropertyDescriptor(t,i,e);void 0!==r&&c(this.prototype,t,r)}}static getPropertyDescriptor(t,e,i){let{get:r,set:o}=g(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get(){return r?.call(this)},set(e){let s=r?.call(this);o.call(this,e),this.requestUpdate(t,s,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??_}static _$Ei(){if(this.hasOwnProperty("elementProperties"))return;let t=f(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty("finalized"))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty("properties")){let t=this.properties;for(let e of[...u(t),...b(t)])this.createProperty(e,t[e])}let t=this[Symbol.metadata];if(null!==t){let e=litPropertyMetadata.get(t);if(void 0!==e)for(let[t,i]of e)this.elementProperties.set(t,i)}for(let[t,e]of(this._$Eh=new Map,this.elementProperties)){let i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t))for(let i of new Set(t.flat(1/0).reverse()))e.unshift(p(i));else void 0!==t&&e.push(p(t));return e}static _$Eu(t,e){let i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map;for(let e of this.constructor.elementProperties.keys())this.hasOwnProperty(e)&&(t.set(e,this[e]),delete this[e]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{if(s)t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let i of e){let e=document.createElement("style"),r=o.litNonce;void 0!==r&&e.setAttribute("nonce",r),e.textContent=i.cssText,t.appendChild(e)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EC(t,e){let i=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,i);if(void 0!==r&&!0===i.reflect){let o=(void 0!==i.converter?.toAttribute?i.converter:w).toAttribute(e,i.type);this._$Em=t,null==o?this.removeAttribute(r):this.setAttribute(r,o),this._$Em=null}}_$AK(t,e){let i=this.constructor,r=i._$Eh.get(t);if(void 0!==r&&this._$Em!==r){let t=i.getPropertyOptions(r),o="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:w;this._$Em=r,this[r]=o.fromAttribute(e,t.type),this._$Em=null}}requestUpdate(t,e,i){if(void 0!==t){if(!((i??=this.constructor.getPropertyOptions(t)).hasChanged??y)(this[t],e))return;this.P(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$ET())}P(t,e,i){this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$Em!==t&&(this._$Ej??=new Set).add(t)}async _$ET(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}let t=this.constructor.elementProperties;if(t.size>0)for(let[e,i]of t)!0!==i.wrapped||this._$AL.has(e)||void 0===this[e]||this.P(e,this[e],i)}let t=!1,e=this._$AL;try{(t=this.shouldUpdate(e))?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EU()}catch(e){throw t=!1,this._$EU(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Ej&&=this._$Ej.forEach(t=>this._$EC(t,this[t])),this._$EU()}updated(t){}firstUpdated(t){}};k.elementStyles=[],k.shadowRootOptions={mode:"open"},k.elementProperties=new Map,k.finalized=new Map,x?.({ReactiveElement:k}),(v.reactiveElementVersions??=[]).push("2.0.4");var A=globalThis,E=A.trustedTypes,S=E?E.createPolicy("lit-html",{createHTML:t=>t}):void 0,U="$lit$",P=`lit$${Math.random().toFixed(9).slice(2)}$`,C="?"+P,O=`<${C}>`,N=document,L=()=>N.createComment(""),T=t=>null===t||"object"!=typeof t&&"function"!=typeof t,R=Array.isArray,M="[ 	\n\f\r]",H=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,D=/-->/g,I=/>/g,z=RegExp(`>|${M}(?:([^\\s"'>=/]+)(${M}*=${M}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),j=/'/g,B=/"/g,W=/^(?:script|style|textarea|title)$/i,F=t=>(e,...i)=>({_$litType$:t,strings:e,values:i}),V=F(1);F(2),F(3);var K=Symbol.for("lit-noChange"),q=Symbol.for("lit-nothing"),Z=new WeakMap,G=N.createTreeWalker(N,129);function J(t,e){if(!R(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==S?S.createHTML(e):e}var Y=class t{constructor({strings:e,_$litType$:i},r){let o;this.parts=[];let s=0,a=0;const n=e.length-1,l=this.parts,[h,p]=((t,e)=>{let i=t.length-1,r=[],o,s=2===e?"<svg>":3===e?"<math>":"",a=H;for(let e=0;e<i;e++){let i=t[e],n,l,h=-1,p=0;for(;p<i.length&&(a.lastIndex=p,null!==(l=a.exec(i)));)p=a.lastIndex,a===H?"!--"===l[1]?a=D:void 0!==l[1]?a=I:void 0!==l[2]?(W.test(l[2])&&(o=RegExp("</"+l[2],"g")),a=z):void 0!==l[3]&&(a=z):a===z?">"===l[0]?(a=o??H,h=-1):void 0===l[1]?h=-2:(h=a.lastIndex-l[2].length,n=l[1],a=void 0===l[3]?z:'"'===l[3]?B:j):a===B||a===j?a=z:a===D||a===I?a=H:(a=z,o=void 0);let d=a===z&&t[e+1].startsWith("/>")?" ":"";s+=a===H?i+O:h>=0?(r.push(n),i.slice(0,h)+U+i.slice(h)+P+d):i+P+(-2===h?e:d)}return[J(t,s+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),r]})(e,i);if(this.el=t.createElement(h,r),G.currentNode=this.el.content,2===i||3===i){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(o=G.nextNode())&&l.length<n;){if(1===o.nodeType){if(o.hasAttributes())for(const t of o.getAttributeNames())if(t.endsWith(U)){const e=p[a++],i=o.getAttribute(t).split(P),r=/([.?@])?(.*)/.exec(e);l.push({type:1,index:s,name:r[2],strings:i,ctor:"."===r[1]?ti:"?"===r[1]?tr:"@"===r[1]?to:te}),o.removeAttribute(t)}else t.startsWith(P)&&(l.push({type:6,index:s}),o.removeAttribute(t));if(W.test(o.tagName)){const t=o.textContent.split(P),e=t.length-1;if(e>0){o.textContent=E?E.emptyScript:"";for(let i=0;i<e;i++)o.append(t[i],L()),G.nextNode(),l.push({type:2,index:++s});o.append(t[e],L())}}}else if(8===o.nodeType)if(o.data===C)l.push({type:2,index:s});else{let t=-1;for(;-1!==(t=o.data.indexOf(P,t+1));)l.push({type:7,index:s}),t+=P.length-1}s++}}static createElement(t,e){let i=N.createElement("template");return i.innerHTML=t,i}};function Q(t,e,i=t,r){if(e===K)return e;let o=void 0!==r?i.o?.[r]:i.l,s=T(e)?void 0:e._$litDirective$;return o?.constructor!==s&&(o?._$AO?.(!1),void 0===s?o=void 0:(o=new s(t))._$AT(t,i,r),void 0!==r?(i.o??=[])[r]=o:i.l=o),void 0!==o&&(e=Q(t,o._$AS(t,e.values),o,r)),e}var X=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:i}=this._$AD,r=(t?.creationScope??N).importNode(e,!0);G.currentNode=r;let o=G.nextNode(),s=0,a=0,n=i[0];for(;void 0!==n;){if(s===n.index){let e;2===n.type?e=new tt(o,o.nextSibling,this,t):1===n.type?e=new n.ctor(o,n.name,n.strings,this,t):6===n.type&&(e=new ts(o,this,t)),this._$AV.push(e),n=i[++a]}s!==n?.index&&(o=G.nextNode(),s++)}return G.currentNode=N,r}p(t){let e=0;for(let i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},tt=class t{get _$AU(){return this._$AM?._$AU??this.v}constructor(t,e,i,r){this.type=2,this._$AH=q,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=r,this.v=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){let i;T(t=Q(this,t,e))?t===q||null==t||""===t?(this._$AH!==q&&this._$AR(),this._$AH=q):t!==this._$AH&&t!==K&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):R(i=t)||"function"==typeof i?.[Symbol.iterator]?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==q&&T(this._$AH)?this._$AA.nextSibling.data=t:this.T(N.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:i}=t,r="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=Y.createElement(J(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===r)this._$AH.p(e);else{let t=new X(r,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=Z.get(t.strings);return void 0===e&&Z.set(t.strings,e=new Y(t)),e}k(e){R(this._$AH)||(this._$AH=[],this._$AR());let i=this._$AH,r,o=0;for(let s of e)o===i.length?i.push(r=new t(this.O(L()),this.O(L()),this,this.options)):r=i[o],r._$AI(s),o++;o<i.length&&(this._$AR(r&&r._$AB.nextSibling,o),i.length=o)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t&&t!==this._$AB;){let e=t.nextSibling;t.remove(),t=e}}setConnected(t){void 0===this._$AM&&(this.v=t,this._$AP?.(t))}},te=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,r,o){this.type=1,this._$AH=q,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=o,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=q}_$AI(t,e=this,i,r){let o=this.strings,s=!1;if(void 0===o)(s=!T(t=Q(this,t,e,0))||t!==this._$AH&&t!==K)&&(this._$AH=t);else{let r,a,n=t;for(t=o[0],r=0;r<o.length-1;r++)(a=Q(this,n[i+r],e,r))===K&&(a=this._$AH[r]),s||=!T(a)||a!==this._$AH[r],a===q?t=q:t!==q&&(t+=(a??"")+o[r+1]),this._$AH[r]=a}s&&!r&&this.j(t)}j(t){t===q?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},ti=class extends te{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===q?void 0:t}},tr=class extends te{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==q)}},to=class extends te{constructor(t,e,i,r,o){super(t,e,i,r,o),this.type=5}_$AI(t,e=this){if((t=Q(this,t,e,0)??q)===K)return;let i=this._$AH,r=t===q&&i!==q||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,o=t!==q&&(i===q||r);r&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},ts=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){Q(this,t)}},ta=A.litHtmlPolyfillSupport;ta?.(Y,tt),(A.litHtmlVersions??=[]).push("3.2.0");var tn=class extends k{constructor(){super(...arguments),this.renderOptions={host:this},this.o=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this.o=((t,e,i)=>{let r=i?.renderBefore??e,o=r._$litPart$;if(void 0===o){let t=i?.renderBefore??null;r._$litPart$=o=new tt(e.insertBefore(L(),t),t,void 0,i??{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this.o?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this.o?.setConnected(!1)}render(){return K}};tn._$litElement$=!0,tn.finalized=!0,globalThis.litElementHydrateSupport?.({LitElement:tn});var tl=globalThis.litElementPolyfillSupport;tl?.({LitElement:tn}),(globalThis.litElementVersions??=[]).push("4.1.0");var th={attribute:!0,type:String,converter:w,reflect:!1,hasChanged:y};function tp(t){return(e,i)=>{let r;return"object"==typeof i?((t=th,e,i)=>{let{kind:r,metadata:o}=i,s=globalThis.litPropertyMetadata.get(o);if(void 0===s&&globalThis.litPropertyMetadata.set(o,s=new Map),s.set(i.name,t),"accessor"===r){let{name:r}=i;return{set(i){let o=e.get.call(this);e.set.call(this,i),this.requestUpdate(r,o,t)},init(e){return void 0!==e&&this.P(r,void 0,t),e}}}if("setter"===r){let{name:r}=i;return function(i){let o=this[r];e.call(this,i),this.requestUpdate(r,o,t)}}throw Error("Unsupported decorator location: "+r)})(t,e,i):(r=e.hasOwnProperty(i),e.constructor.createProperty(i,r?{...t,wrapped:!0}:t),r?Object.getOwnPropertyDescriptor(e,i):void 0)}}function td(t){return tp({...t,state:!0,attribute:!1})}var tc={"--pb-background-color":{light:h`#ffffff`,dark:h`#121212`},"--pb-background-color-hover":{light:h`#f9fafb`,dark:h`#1e293b`},"--pb-text-color":{light:h`#000000`,dark:h`#e0e0e0`},"--pb-border-color":{light:h`rgba(124, 139, 154, 0.25)`,dark:h`#80808034`},"--pb-text-color-light":{light:h`rgba(0, 0, 0, 0.7)`,dark:h`rgba(255, 255, 255, 0.8)`},"--pb-fallback-img-color":{light:h`hsl(220, 13%, 80%)`,dark:h`hsl(220, 13%, 40%)`},"--pb-fallback-img-background":{light:h`rgb(229, 231, 235)`,dark:h`rgb(55, 65, 81)`},"--pb-skeleton-color":{light:h`rgb(229, 231, 235)`,dark:h`rgb(55, 65, 81)`}};function tg(t,e){Object.keys(tc).forEach(i=>{t.style.setProperty(i,tc[i][e].toString())})}var tu=h`
  ${h`
    :host {
      --pb-background-color: ${tc["--pb-background-color"].light};
      --pb-dark-background-color: ${tc["--pb-background-color"].dark};
      --pb-background-color-hover: ${tc["--pb-background-color-hover"].light};
      --pb-dark-background-color-hover: ${tc["--pb-background-color-hover"].dark};
      --pb-text-color: ${tc["--pb-text-color"].light};
      --pb-dark-text-color: ${tc["--pb-text-color"].dark};
      --pb-border-color: ${tc["--pb-border-color"].light};
      --pb-dark-border-color: ${tc["--pb-border-color"].dark};
      --pb-text-color-light: ${tc["--pb-text-color-light"].light};
      --pb-dark-metadata-color: ${tc["--pb-text-color-light"].dark};
      --pb-skeleton-color: ${tc["--pb-skeleton-color"].light};
      --pb-dark-skeleton-color: ${tc["--pb-skeleton-color"].dark};
      --pb-fallback-img-color: ${tc["--pb-fallback-img-color"].light};
      --pb-dark-fallback-img-color: ${tc["--pb-fallback-img-color"].dark};
      --pb-fallback-img-background: ${tc["--pb-fallback-img-background"].light};
      --pb-dark-fallback-img-background: ${tc["--pb-fallback-img-background"].dark};
      --pb-favicon-size: 20px;
    }

    @media (prefers-color-scheme: dark) {
      :host {
        --pb-background-color: var(--pb-dark-background-color);
        --pb-background-color-hover: var(--pb-dark-background-color-hover);
        --pb-text-color: var(--pb-dark-text-color);
        --pb-border-color: var(--pb-dark-border-color);
        --pb-text-color-light: var(--pb-dark-metadata-color);
        --pb-fallback-img-color: var(--pb-dark-fallback-img-color);
        --pb-fallback-img-background: var(--pb-dark-fallback-img-background);
        --pb-skeleton-color: var(--pb-dark-skeleton-color);
      }
    }
  `}
  :host {
    display: block;
    box-sizing: border-box;
    width: 100%;
    font-family: inherit;
  }


  .container {
    margin: 0;
    padding: 0;
    background-color: var(--pb-background-color);
  }

  .previewbox-title,
  .previewbox-link {
    color: var(--pb-text-color);
  }

  .previewbox-description {
    color: var(--pb-text-color-light);
  }

  .previewbox-link {
    text-decoration: none;
    display: flex;
    text-decoration: none;
    color: inherit;
  }
`,tb=h`
  ${tu}
  :host {
    display: block;
    box-sizing: border-box;
    width: 100%;
    font-family: inherit;
  }

  .container {
    background-color: var(--pb-background-color);
    margin: 0;
    padding: 0;
    overflow: hidden;
    border-radius: 3px;
    border: 1px solid var(--pb-border-color);
    position: relative;
  }

  .previewbox-link {
    text-decoration: none;
    color: var(--pb-text-color);
    display: flex;
    text-decoration: none;
    color: inherit;
  }

  .previewbox-content {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    flex-basis: 100%;
    align-items: flex-start;
    justify-content: flex-start;
    padding: 20px;
    overflow: hidden;
    position: relative;
  }

  .previewbox-title {
    display: -webkit-box;
    font-size: 1rem;
    font-weight: 500;
    line-height: 1.2;
    height: 40px;
    overflow: hidden;
    @media (min-width: 768px) {
      line-height: 1.4;
      height: 24px;
    }
    color: var(--pb-text-color);
  }

  .previewbox-description {
    display: -webkit-box;
    font-size: 0.875rem;
    line-height: 1.5em;
    margin-top: 3px;
    font-weight: 400;
    width: 100%;
    height: 44px;
    overflow-y: hidden;
    opacity: 0.7;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    color: var(--pb-text-color-light);
  }

  .previewbox-metadata {
    display: flex;
    align-items: center;
    margin-top: 22px;
    width: 100%;
    height: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    white-space: nowrap;
    color: var(--pb-text-color-light);
    .previewbox-metadata-skeleton {
      display: flex;
      column-gap: 4px;
      align-items: center;

      .rounded::part(skeleton-shape) {
        border-radius: 50%;
      }
    }
    svg {
      width: var(--pb-favicon-size);
      height: var(--pb-favicon-size);
      margin-right: 6px;
    }
  }

  .previewbox-metadata > span:nth-of-type(2)::before {
    content: '•';
    margin: 0px 6px;
  }

  .previewbox-metadata > span:last-of-type {
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .previewbox-metadata > :not(previewbox-favicon) {
    opacity: 0.7;
  }

  previewbox-favicon {
    margin-right: 6px;
  }

  .previewbox-thumbnail {
    position: relative;
    flex-grow: 1;
    min-width: 33%;
  }


`,tf=class extends tn{constructor(){super(...arguments),this.href="",this.target="_blank",this.rel=""}};function tv(t){try{var e;return e=t,t=e?.replace(/https:\/\/|http:\/\/|www.|/gi,"")??"",(t=t?.split("/")[0])??""}catch(e){return t??""}}r([tp()],tf.prototype,"href",2),r([tp()],tf.prototype,"target",2),r([tp()],tf.prototype,"rel",2);var tm=new class{async fetchLinkPreviewData(t,e){try{let i=new URLSearchParams;i.set("url",t);let r=await fetch(`${e.apiUrl}?${i.toString()}`,{headers:{origin:window.location.origin}});if(!r.ok){if(429===r.status)return{error:"API_LIMIT_REACHED"};return{error:"UNKNOWN_ERROR"}}return{data:await r.json()}}catch(t){return{error:"UNKNOWN_ERROR"}}}},t$=class extends tf{constructor(){super(...arguments),this.url=null,this.title="",this.description=null,this.author=null,this.imageUrl=null,this.imageAlt=null,this.faviconUrl=null,this.date=null,this.hidePoweredBy=void 0,this.apiUrl=window.location.href.startsWith("http://localhost:8000/demo")?"http://localhost:4444/api/v1/meta":"https://previewbox.link/api/v1/meta",this.dark=void 0,this.light=void 0,this.fetchedLinkPreviewData=null,this._isLoading=!1,this._isError=!1,this._apiError=null}get linkData(){return this.fetchedLinkPreviewData?this.fetchedLinkPreviewData:{url:this.url,description:this.description,title:this.title,author:this.author,imageUrl:this.imageUrl,imageAlt:this.imageAlt,favicon:this.faviconUrl,date:this.date,origin:tv(this.url)}}firstUpdated(t){if(void 0!==this.dark&&tg(this,"dark"),void 0!==this.light&&tg(this,"light"),!this.href&&!this.url)throw Error(`No href or url provided for ${this.localName}`);this.href?this._fetchLinkPreviewData():this._setManualData()}_fetchLinkPreviewData(){this._isLoading=!0,tm.fetchLinkPreviewData(this.href,{apiUrl:this.apiUrl}).then(t=>{"data"in t?this.fetchedLinkPreviewData=t.data:(this._isError=!0,this._apiError=t.error)}).catch(t=>{console.error(`Error fetching link preview data for ${this.href}: ${t}`),this._isError=!0,this._apiError="UNKNOWN_ERROR"}).finally(()=>{this._isLoading=!1})}_setManualData(){if(!this.url)throw Error(`As no href was provided, url is required for ${this.localName}`);this.fetchedLinkPreviewData={url:this.url,description:this.description,title:this.title,author:this.author,imageUrl:this.imageUrl,imageAlt:this.imageAlt,favicon:this.faviconUrl,date:this.date,origin:tv(this.url)}}};r([tp()],t$.prototype,"url",2),r([tp()],t$.prototype,"title",2),r([tp()],t$.prototype,"description",2),r([tp()],t$.prototype,"author",2),r([tp()],t$.prototype,"imageUrl",2),r([tp()],t$.prototype,"imageAlt",2),r([tp()],t$.prototype,"faviconUrl",2),r([tp()],t$.prototype,"date",2),r([tp()],t$.prototype,"hidePoweredBy",2),r([tp()],t$.prototype,"apiUrl",2),r([tp()],t$.prototype,"dark",2),r([tp()],t$.prototype,"light",2),r([td()],t$.prototype,"fetchedLinkPreviewData",2),r([td()],t$.prototype,"_isLoading",2),r([td()],t$.prototype,"_isError",2),r([td()],t$.prototype,"_apiError",2);var tx=h`
  :host {
    display: block;
    box-sizing: border-box;
    font-family: inherit;
  }

  .skeleton-shape {
    background-color: var(--pb-skeleton-color);
    animation: pulse 1.5s infinite ease-in-out;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.7;
    }
  }
`,tw=(t,e)=>{customElements.get(t)||document.createElement(t).constructor!==HTMLElement||customElements.define(t,e)},ty=class extends tn{constructor(){super(...arguments),this.width="100%",this.height="16px"}static{this.styles=tx}render(){return V`<div
      class="skeleton-shape"
      part="skeleton-shape"
      role="progressbar"
      style="width: ${this.width}; height: ${this.height};"
    >
      <slot></slot>
    </div>`}};r([tp()],ty.prototype,"width",2),r([tp()],ty.prototype,"height",2),tw("previewbox-skeleton-shape",ty);var t_=h`
  :host {
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    background: #000000b5;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
    text-align: center;
  }

  .limit-info-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    row-gap: 8px;
  }

  .limit-info-text {
    color: white;
  }

  .limit-info-cta {
    color: white;
    text-decoration: none;
    background-color: #5046e5;
    padding: 8px 16px;
    border-radius: 4px;
  }
`;tw("previewbox-limit-info",class extends tn{static{this.styles=t_}render(){let t=window.location.origin;return V`<div class="limit-info-container">
      <span class="limit-info-text"
        >You've reached the API limit for ${t}</span
      >
      <a
        class="limit-info-cta"
        target="_blank"
        href="https://previewbox.link/usage/${encodeURIComponent(t)}"
        >Check Usage</a
      >
    </div>`}});var tk=h`
  .powered-by {
    position: absolute;
    bottom: 2px;
    right: 2px;
    font-size: 9.5px;
    color: #000000;
    background-color: #ffffff7d;
    padding: 1px 2px;
    z-index: 2;
    border-radius: 2px;
    line-height: 1.2;

    a {
      color: #000000;
      font-weight: bold;
      text-decoration: none;
    }
  }
`;tw("powered-by-previewbox",class extends tn{static{this.styles=tk}render(){return V`<span class="powered-by">
      Powered by
      <a href="https://previewbox.link">Previewbox</a>
    </span> `}});var tA=h`
  .previewbox-favicon {
    width: var(--pb-favicon-size);
    height: var(--pb-favicon-size);
  }
`,tE=V`<svg
  aria-hidden="true"
  xmlns="http://www.w3.org/2000/svg"
  fill="currentColor"
  viewBox="0 0 20 18"
>
  <path
    d="M18 0H2a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2Zm-5.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3Zm4.376 10.481A1 1 0 0 1 16 15H4a1 1 0 0 1-.895-1.447l3.5-7A1 1 0 0 1 7.468 6a.965.965 0 0 1 .9.5l2.775 4.757 1.546-1.887a1 1 0 0 1 1.618.1l2.541 4a1 1 0 0 1 .028 1.011Z"
  />
</svg>`,tS=V`<svg
  aria-hidden="true"
  xmlns="http://www.w3.org/2000/svg"
  width="24"
  height="24"
  data-testid="${"FAVICON_FALLBACK"}"
  stroke-width="1.5"
  fill="none"
  viewBox="0 0 24 24"
>
  <path
    stroke="currentColor"
    stroke-linecap="round"
    stroke-width="2"
    d="M4.37 7.657c2.063.528 2.396 2.806 3.202 3.87 1.07 1.413 2.075 1.228 3.192 2.644 1.805 2.289 1.312 5.705 1.312 6.705M20 15h-1a4 4 0 0 0-4 4v1M8.587 3.992c0 .822.112 1.886 1.515 2.58 1.402.693 2.918.351 2.918 2.334 0 .276 0 2.008 1.972 2.008 2.026.031 2.026-1.678 2.026-2.008 0-.65.527-.9 1.177-.9H20M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
  />
</svg> `,tU=class extends tn{constructor(){super(...arguments),this.faviconUrl=null,this.isFaviconError=!1}static{this.styles=tA}render(){return V`
      ${this.faviconUrl&&!this.isFaviconError?V`
            <img
              data-testid="${"FAVICON"}"
              class="previewbox-favicon"
              part="favicon"
              src=${this.faviconUrl??""}
              alt="Favicon"
              @error=${()=>this.isFaviconError=!0}
            />
          `:tS}
    `}};r([tp()],tU.prototype,"faviconUrl",2),r([td()],tU.prototype,"isFaviconError",2),tw("previewbox-favicon",tU);var tP=h`
  img,
  previewbox-skeleton-shape,
  .fallback-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    top: 0;
    left: 0;
    border-radius: 0 2px 2px 0;
    margin: 0;
    background-color: var(--pb-fallback-img-background);


    svg {
      width: 40px;
      height: 40px;
      color: var(--pb-fallback-img-color);
    }
  }
`,tC=class extends tn{constructor(){super(...arguments),this.imageUrl=null,this.imageAlt=null,this.isLoading=!0,this.isImageError=!1}static{this.styles=tP}render(){return this.isLoading?V`<previewbox-skeleton-shape
        height="100%"
        data-testid="${"IMAGE_SKELETON"}"
      >
        ${tE}
      </previewbox-skeleton-shape>`:V`
      ${this.imageUrl&&!this.isImageError?V`
            <img
              data-testid="${"IMAGE"}"
              part="image"
              src=${this.imageUrl??""}
              alt=${this.imageAlt??"Thumbnail image"}
              @error=${()=>this.isImageError=!0}
            />
          `:V`
            <figure
              class="fallback-img"
              part="image"
              data-testid="${"IMAGE_FALLBACK"}"
            >
              ${tE}
            </figure>
          `}
    `}};r([tp()],tC.prototype,"imageUrl",2),r([tp()],tC.prototype,"imageAlt",2),r([tp({type:Boolean})],tC.prototype,"isLoading",2),r([td()],tC.prototype,"isImageError",2),tw("previewbox-image",tC);var tO=class extends t${render(){return V`
      <figure part="container" class="container">
        ${"API_LIMIT_REACHED"===this._apiError?V`<previewbox-limit-info></previewbox-limit-info>`:""}
        <a
          href=${this.linkData.url||this.href}
          target=${this.target}
          part="link"
          rel=${this.rel}
          class="previewbox-link"
          data-testid="${"ANCHOR_ELEMENT"}"
        >
          <div class="previewbox-content">
            <div class="previewbox-title" data-testid="${"TITLE"}">
              ${this._isLoading?V`<previewbox-skeleton-shape
                    width="200px"
                    height="20px"
                    data-testid="${"TITLE_SKELETON"}"
                  />`:this.linkData.title}
            </div>
            <div
              class="previewbox-description"
              data-testid="${"DESCRIPTION"}"
            >
              ${this._isLoading?V`
                    <previewbox-skeleton-shape
                      width="100%"
                      height="16px"
                    ></previewbox-skeleton-shape>
                    <previewbox-skeleton-shape
                      width="70%"
                      height="16px"
                      style="margin-top: 4px;"
                    ></previewbox-skeleton-shape>
                  `:this.linkData.description}
            </div>
            <div class="previewbox-metadata">
              ${this._isLoading?V`
                    <div class="previewbox-metadata-skeleton">
                      <previewbox-skeleton-shape
                        width="14px"
                        data-testid="${"FAVICON_SKELETON"}"
                        height="14px"
                        class="rounded"
                      ></previewbox-skeleton-shape>
                      <previewbox-skeleton-shape
                        width="60px"
                        height="14px"
                      ></previewbox-skeleton-shape>
                      <previewbox-skeleton-shape
                        width="4px"
                        height="4px"
                        class="rounded"
                      ></previewbox-skeleton-shape>
                      <previewbox-skeleton-shape
                        width="44px"
                        height="14px"
                      ></previewbox-skeleton-shape>
                    </div>
                  `:V`
                    <previewbox-favicon
                      .faviconUrl=${this.linkData.favicon}
                    ></previewbox-favicon>
                    <span data-testid="${"PUBLISHER"}"
                      >${this.linkData.origin}</span
                    >${this.linkData.author?V`<span data-testid="${"AUTHOR"}"
                          >${this.linkData.author}</span
                        >`:""}
                  `}
            </div>
          </div>
          <div class="previewbox-thumbnail">
            <previewbox-image
              .isLoading=${this._isLoading}
              .imageUrl=${this.linkData?.imageUrl}
              .imageAlt=${this.linkData?.imageAlt}
            ></previewbox-image>
          </div>
        </a>
        ${void 0!==this.hidePoweredBy?"":V`<powered-by-previewbox
              data-testid="${"POWERED_BY"}"
            ></powered-by-previewbox>`}
      </figure>
    `}};tO.styles=tb,tO=r([(t="previewbox-link",(e,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)})],tO)})()})();
//# sourceMappingURL=main.js.map
