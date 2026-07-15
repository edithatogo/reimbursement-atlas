import { fileURLToPath } from "node:url";
import react from "@astrojs/react";
import { defineConfig } from "astro/config";

const glBenchModule = fileURLToPath(
  new URL("./node_modules/gl-bench/dist/gl-bench.module.js", import.meta.url),
);
const isGitHubPages = process.env.PUBLIC_DEPLOY_TARGET === "github-pages";

export default defineConfig({
  integrations: [react()],
  output: "static",
  site: isGitHubPages ? "https://edithatogo.github.io" : undefined,
  base: isGitHubPages ? "/reimbursement-atlas" : undefined,
  vite: {
    build: {
      chunkSizeWarningLimit: 3000,
    },
    resolve: {
      alias: {
        "gl-bench": glBenchModule,
      },
    },
  },
});
