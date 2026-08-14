// @ts-check
import { defineConfig } from 'astro/config';

/*
  Static output. Every route is a real HTML file on disk at build time.

  This is the whole reason for the rebuild: the current site is a
  client-rendered SPA that serves the same empty 19,882-byte shell for
  every URL, so search engines get nothing, every page shares one title
  and one canonical, and 404s return HTTP 200. Pre-rendering fixes all
  four by construction rather than by discipline.
*/
export default defineConfig({
  site: 'https://www.scandicmarketing.se',
  output: 'static',
  trailingSlash: 'always',
  compressHTML: true,
  build: {
    inlineStylesheets: 'auto',
  },
  vite: {
    build: {
      // The hero poster and logos are already optimised; don't inline them
      // as base64 and bloat the HTML.
      assetsInlineLimit: 0,
    },
  },
});
