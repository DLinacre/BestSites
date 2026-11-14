import {test} from 'node:test';
import assert from 'node:assert/strict';
import sitemap from '../src/app/sitemap';
import robots from '../src/app/robots';
import {categories} from '../src/lib/resources';
test('sitemap lists one canonical URL for every category and no duplicate category paths',()=>{const entries=sitemap();const urls=entries.map(entry=>new URL(entry.url).pathname);for(const category of categories){assert.equal(urls.filter(path=>path===`/${category.id}`).length,1);assert.ok(!urls.includes(`/category/${category.id}`))}assert.ok(!urls.includes('/saved'));assert.equal(new Set(urls).size,urls.length)});
test('robots sitemap origin is aligned with canonical site origin',()=>{const config=robots();assert.equal(config.sitemap,`${sitemap()[0].url}/sitemap.xml`);const rules=Array.isArray(config.rules)?config.rules[0]:config.rules;assert.deepEqual(rules?.disallow,['/saved'])});
