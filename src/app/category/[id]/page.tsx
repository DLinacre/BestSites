import {notFound,permanentRedirect} from 'next/navigation';
import {categories,getCategory} from '@/lib/resources';
export function generateStaticParams(){return categories.map(category=>({id:category.id}))}
export default async function DuplicateCategoryRoute({params}:{params:Promise<{id:string}>}){const {id}=await params;if(!getCategory(id))notFound();permanentRedirect(`/${id}`)}
