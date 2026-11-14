import {resources} from '../src/lib/resources';
import {readAuditStore,renderAuditReport} from '../src/lib/link-audit';
import {writeFile} from 'node:fs/promises';
import path from 'node:path';
async function main(){const file=path.join(process.cwd(),'src/data/link-status.json');const store=await readAuditStore(file);const report=renderAuditReport(resources,store);await writeFile(path.join(process.cwd(),'LINK_AUDIT.md'),report);const counts=resources.reduce((acc,r)=>{acc[store.resources[r.id]?.status??'not-checked']++;return acc},{verified:0,redirected:0,blocked:0,broken:0,'not-checked':0} as Record<string,number>);console.log(`Wrote LINK_AUDIT.md: ${counts.verified} verified, ${counts.redirected} redirected, ${counts.blocked} blocked, ${counts.broken} broken, ${counts['not-checked']} not checked.`)}
void main().catch(error=>{console.error(error);process.exitCode=1});
