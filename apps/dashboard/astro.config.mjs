import { fileURLToPath } from "node:url";
import react from "@astrojs/react";
import { defineConfig } from "astro/config";

const glBenchModule = fileURLToPath(
  new URL("./node_modules/gl-bench/dist/gl-bench.module.js", import.meta.url),
);

export default defineConfig({
  integrations: [react()],
  output: "static",
  vite: {
    resolve: {
      alias: {
        "gl-bench": glBenchModule,
      },
    },
  },
});
