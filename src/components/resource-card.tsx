'use client';
import { useState, useSyncExternalStore } from 'react';
import { ArrowUpRight, Bookmark, Check, Copy, ExternalLink, Globe2, ShieldCheck, CircleAlert, CircleX } from 'lucide-react';
import Link from 'next/link';
import { type Resource, getCategory } from '@/lib/resources';
import { recordVisit } from './app-shell';
const KEY='atlas-saved-v1';
const subscribe=(callback:()=>void)=>{window.addEventListener('storage',callback);window.addEventListener('atlas-saved',callback);return()=>{window.removeEventListener('storage',callback);window.removeEventListener('atlas-saved',callback)}};
export function ResourceCard({resource,compact=false}:{resource:Resource;compact?:boolean}){
 const saved=useSyncExternalStore(subscribe,()=>JSON.parse(localStorage.getItem(KEY)||'[]').includes(resource.id),()=>false);const [copied,setCopied]=useState(false);
 function toggle(){const all:string[]=JSON.parse(localStorage.getItem(KEY)||'[]');const next=all.includes(resource.id)?all.filter(x=>x!==resource.id):[...all,resource.id];localStorage.setItem(KEY,JSON.stringify(next));window.dispatchEvent(new Event('atlas-saved'))}
 async function copy(){try{await navigator.clipboard.writeText(resource.url);setCopied(true);setTimeout(()=>setCopied(false),1400)}catch{}}
 return <article className={'resource-card '+(compact?'resource-compact':'')} style={{'--category-accent':getCategory(resource.category)?.accent||'#b7e6b0'} as React.CSSProperties}>
  <div className="card-topline"><span className="site-monogram" aria-hidden="true">{resource.name.replace(/[^A-Za-z0-9]/g,'').slice(0,1).toUpperCase()}</span><div className="card-top-meta">{resource.featured&&<span className="pick-badge"><span/> EDITOR’S PICK</span>}<span className={'link-state status-'+resource.linkStatus} title={resource.lastCheckedAt?`Link status: ${resource.linkStatus}; checked ${new Date(resource.lastCheckedAt).toLocaleDateString()}`:'Not independently checked by the current audit'}>{resource.linkStatus==='verified'?<><Check size={11}/> Verified</>:resource.linkStatus==='redirected'?<><ArrowUpRight size={11}/> Redirected</>:resource.linkStatus==='blocked'?<><CircleAlert size={11}/> Review</>:resource.linkStatus==='broken'?<><CircleX size={11}/> Broken</>:<><Globe2 size={11}/> Not checked</>}</span></div><button className={'bookmark-button '+(saved?'is-saved':'')} onClick={toggle} aria-label={saved?'Remove '+resource.name+' from saved resources':'Save '+resource.name}>{saved?<Bookmark size={17} fill="currentColor"/>:<Bookmark size={17}/>}</button></div>
  <h3 className="resource-title">{resource.name}</h3><p className="resource-description">{resource.description}</p>
  <div className="tag-row"><span className="tag tag-type">{resource.resourceType}</span><span className="tag">{resource.pricingModel}</span>{resource.openSource&&<span className="tag tag-open"><ShieldCheck size={12}/> Open source</span>}</div>
  <div className="card-bottom"><Link className="category-link" href={'/'+resource.category}>{getCategory(resource.category)?.shortTitle}</Link><div className="card-actions"><button className="micro-action" onClick={copy} aria-label={`Copy ${resource.name} link`} title="Copy link">{copied?<Check size={15}/>:<Copy size={15}/>}</button><a href={resource.url} target="_blank" rel="noopener noreferrer" className="visit-link" onClick={()=>recordVisit(resource)} aria-label={`Visit ${resource.name} in a new tab`}>Visit <ArrowUpRight size={15}/></a></div></div>
  <details className="resource-details"><summary>Why it’s here <span>+</span></summary><p>{resource.selectionReason||resource.description}</p><div className="detail-data"><span>{resource.platform.join(' · ')}</span><span>Link status: {resource.linkStatus==='not-checked'?'not yet checked':resource.linkStatus}</span></div><a href={resource.sourceCategoryUrl} target="_blank" rel="noopener noreferrer">Research starting point: FMHY category <ExternalLink size={12}/></a></details>
 </article>
}
