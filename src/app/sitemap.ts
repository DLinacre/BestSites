import type {MetadataRoute} from 'next';
import {categories} from '@/lib/resources';
import {getSiteOrigin} from '@/lib/site-url';
export default function sitemap():MetadataRoute.Sitemap{const origin=getSiteOrigin();return[{url:origin,lastModified:new Date('2026-11-14'),changeFrequency:'weekly',priority:1},{url:`${origin}/about`,lastModified:new Date('2026-11-14'),changeFrequency:'monthly',priority:.5},...categories.map(category=>({url:`${origin}/${category.id}`,lastModified:new Date('2026-11-14'),changeFrequency:'monthly' as const,priority:.8}))]}
