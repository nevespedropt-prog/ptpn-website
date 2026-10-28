// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import path from 'node:path';

const norm = (s) => s.replace(/^\/+/, '').replace(/\/+$/, '');

export default defineConfig({
  site: 'https://www.ptpn.co.uk',
  trailingSlash: 'ignore',
  build: {
    inlineStylesheets: 'auto',
    format: 'directory',
  },
  integrations: [
    sitemap({ filter: (page) => !page.includes('/app/') }),
  ],
  vite: { build: { assetsInlineLimit: 2048 } },
});
