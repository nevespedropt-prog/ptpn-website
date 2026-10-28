// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// The marketing site is static on purpose: complete HTML for search and answer
// engines, zero JavaScript by default. The member app is served separately
// under /app (built from its own repo and copied in at deploy time).
export default defineConfig({
  site: 'https://www.ptpn.co.uk',
  trailingSlash: 'ignore',
  build: {
    inlineStylesheets: 'auto',
    format: 'directory',
  },
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/app/'),
    }),
  ],
  vite: {
    build: {
      // the marketing site ships no framework runtime
      assetsInlineLimit: 2048,
    },
  },
});
