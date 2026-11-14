import {mkdir,readFile,rename,writeFile} from 'node:fs/promises';
import path from 'node:path';

export type AuditStatus='verified'|'redirected'|'blocked'|'broken'|'not-checked';
export type AuditMethod='http-head'|'http-get-range'|'web-content-fetch'|'legacy';
export type AuditCheck={resourceId:string;status:AuditStatus;checkedAt:string|null;method:AuditMethod|string;httpStatus:number|null;finalUrl:string|null;note:string;redirected:boolean;crossHostRedirect:boolean};
export type AuditEntry=AuditCheck&{history:AuditCheck[]};
export type AuditStore={version:1;resources:Record<string,AuditEntry>};
export type AuditableResource={id:string;name:string;url:string};
export function isAuditStatus(value:unknown):value is AuditStatus{return value==='verified'||value==='redirected'||value==='blocked'||value==='broken'||value==='not-checked'}
export function classifyHttpResponse(status:number,redirected=false,note?:string|null):AuditStatus{
 if(status===404||status===410)return 'broken';
 if([401,403,406,418,429].includes(status)||status<200||status>=300||note)return 'blocked';
 return redirected?'redirected':'verified';
}
export function emptyAuditStore():AuditStore{return{version:1,resources:{}}}
function normalizeCheck(id:string,value:Partial<AuditCheck>&{status?:unknown}):AuditCheck{
 const status=isAuditStatus(value.status)?value.status:'not-checked';
 return{resourceId:id,status,checkedAt:typeof value.checkedAt==='string'?value.checkedAt:null,method:typeof value.method==='string'?value.method:'legacy',httpStatus:typeof value.httpStatus==='number'?value.httpStatus:null,finalUrl:typeof value.finalUrl==='string'?value.finalUrl:null,note:typeof value.note==='string'?value.note:'No verification note was recorded.',redirected:value.redirected===true||status==='redirected',crossHostRedirect:value.crossHostRedirect===true};
}
export function parseAuditStore(value:unknown):AuditStore{
 if(!value||typeof value!=='object')return emptyAuditStore();
 const root=value as Record<string,unknown>;
 const source=root.resources&&typeof root.resources==='object'?root.resources as Record<string,unknown>:root;
 const resources:Record<string,AuditEntry>={};
 for(const [id,raw] of Object.entries(source)){
  if(!raw||typeof raw!=='object'||id==='version')continue;
  const entry=raw as Record<string,unknown>;const current=normalizeCheck(id,entry as Partial<AuditCheck>&{status?:unknown});
  const history=Array.isArray(entry.history)?entry.history.filter((x):x is Record<string,unknown>=>!!x&&typeof x==='object').map(x=>normalizeCheck(id,x as Partial<AuditCheck>&{status?:unknown})):[];
  resources[id]={...current,history};
 }
 return{version:1,resources};
}
export async function readAuditStore(file:string):Promise<AuditStore>{try{return parseAuditStore(JSON.parse(await readFile(file,'utf8')))}catch(error){if((error as NodeJS.ErrnoException).code==='ENOENT')return emptyAuditStore();throw error}}
export function mergeAuditRun(previous:AuditStore,run:Record<string,AuditCheck>,expectedIds:string[]):AuditStore{
 const expected=new Set(expectedIds);const supplied=Object.keys(run);const missing=expectedIds.filter(id=>!run[id]);const unexpected=supplied.filter(id=>!expected.has(id));
 if(missing.length||unexpected.length)throw new Error(`Refusing incomplete audit run: missing ${missing.join(', ')||'none'}; unexpected ${unexpected.join(', ')||'none'}`);
 const resources={...previous.resources};
 for(const id of expectedIds){const current=normalizeCheck(id,run[id]);const old=previous.resources[id];const history=[...(old?.history??[]),...(old?[normalizeCheck(id,old)]:[])].filter(x=>x.checkedAt).slice(-20);resources[id]={...current,history};}
 return{version:1,resources};
}
export async function saveAuditRun(file:string,previous:AuditStore,run:Record<string,AuditCheck>,expectedIds:string[]):Promise<AuditStore>{const next=mergeAuditRun(previous,run,expectedIds);await mkdir(path.dirname(file),{recursive:true});const temporary=`${file}.${process.pid}.${Date.now()}.tmp`;await writeFile(temporary,JSON.stringify(next,null,2)+'\n',{flag:'wx'});await rename(temporary,file);return next;}
export function renderAuditReport(items:AuditableResource[],store:AuditStore,runAt?:string):string{
 const counts:Record<AuditStatus,number>={verified:0,redirected:0,blocked:0,broken:0,'not-checked':0};
 for(const resource of items){const status=store.resources[resource.id]?.status??'not-checked';counts[status]++;}
 const dates=items.flatMap(r=>store.resources[r.id]?.checkedAt?[store.resources[r.id].checkedAt!]:[]).sort();const latest=runAt??dates.at(-1)??'none recorded';
 const lines=['# Atlas link audit','',`Latest recorded check: ${latest}`,`Resources in directory: ${items.length}`,`Results: ${counts.verified} verified · ${counts.redirected} redirected · ${counts.blocked} blocked / inconclusive · ${counts.broken} broken · ${counts['not-checked']} not checked`,'','## How to read this report','','The HTTP checker records each response and redirect hop, uses a bounded HEAD request followed by a small ranged GET when needed, refuses local/private-network targets, and follows only HTTPS redirects. HTTP 401/403/406/418/429, 5xx responses, timeouts, bot challenges, suspicious parking pages and other ambiguous results are **blocked / inconclusive**, not broken. Only clear 404/410 responses are classified broken. Cross-host redirects are explicitly flagged for relevance review. A successful HTTP response is not a safety, legal, licensing or quality guarantee. A failed or incomplete audit run is not written; when an individual request is inconclusive, the latest status is shown while previous checks remain in the entry history. Run `npm run check:links:update` to refresh the stored audit.','','## Destinations'];
 for(const resource of items){const entry=store.resources[resource.id];if(!entry){lines.push(`- **${resource.name}** — **not-checked**. No recorded result. Source URL: <${resource.url}>`);continue}const final=entry.finalUrl?` Final URL: <${entry.finalUrl}>.`:'';const code=entry.httpStatus===null?'no HTTP response':`HTTP ${entry.httpStatus}`;const redirect=entry.redirected?` Redirected${entry.crossHostRedirect?' across hosts; review destination relevance':''}.`:'';lines.push(`- **${resource.name}** — **${entry.status}**; ${entry.checkedAt?`checked ${entry.checkedAt}`:'no timestamp'} by ${entry.method}; ${code}.${redirect}${final} ${entry.note} Source URL: <${resource.url}>`);if(entry.history.length){for(const old of entry.history)lines.push(`  - Previous: ${old.status} at ${old.checkedAt??'unknown time'} by ${old.method}; ${old.httpStatus===null?'no HTTP response':`HTTP ${old.httpStatus}`}; final ${old.finalUrl??'not reached'}; ${old.note}`)}}
 const urls=new Map<string,string[]>();for(const item of items){try{const key=new URL(item.url).href;urls.set(key,[...(urls.get(key)??[]),item.name])}catch{}}
 const duplicates=[...urls].filter(([,names])=>names.length>1);lines.push('','## Duplicate exact URLs',...(duplicates.length?duplicates.map(([url,names])=>`- ${names.join(', ')} — ${url}`):['None detected.']),'');return lines.join('\n');
}
