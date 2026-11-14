export function getSiteOrigin(env:NodeJS.ProcessEnv=process.env):string{
 const configured=env.NEXT_PUBLIC_SITE_URL?.trim();
 const vercel=env.VERCEL_URL?.trim();
 const candidate=configured||(vercel?`https://${vercel}`:'http://localhost:3000');
 let url:URL;try{url=new URL(candidate)}catch{throw new Error('NEXT_PUBLIC_SITE_URL must be a valid absolute URL (for example https://atlas.example).')}
 if(!['https:','http:'].includes(url.protocol)||url.username||url.password||url.search||url.hash||url.pathname!=='/')throw new Error('NEXT_PUBLIC_SITE_URL must be an origin only, without credentials, path, query or fragment.');
 if(env.NODE_ENV==='production'&&(configured||vercel)&&url.protocol!=='https:')throw new Error('Production NEXT_PUBLIC_SITE_URL must use HTTPS.');
 if(env.NODE_ENV==='production'&&env.VERCEL==='1'&&!configured&&!vercel)throw new Error('Vercel production builds require NEXT_PUBLIC_SITE_URL or VERCEL_URL.');
 return url.origin;
}
