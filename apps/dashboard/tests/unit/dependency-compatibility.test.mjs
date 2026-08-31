import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import test from "node:test";
import Papa from "papaparse";
import yaml, { load } from "../../vendor/js-yaml-compat/index.mjs";

const loadCommonJs = createRequire(import.meta.url);
const manifest = JSON.parse(
  readFileSync(new URL("../../package.json", import.meta.url), "utf8"),
);
const lock = JSON.parse(
  readFileSync(new URL("../../package-lock.json", import.meta.url), "utf8"),
);

test("compatible pins and the YAML alias remain synchronized in the lockfile", () => {
  for (const [name, version] of Object.entries({
    astro: "7.2.9",
    "@cosmograph/react": "2.5.1",
    papaparse: "5.7.0",
    typescript: "6.0.3",
  })) {
    assert.equal(manifest.dependencies[name], version);
    assert.equal(lock.packages[""].dependencies[name], version);
    assert.equal(lock.packages[`node_modules/${name}`].version, version);
  }
  const wrapper = loadCommonJs("../../vendor/js-yaml-compat/package.json");
  assert.equal(manifest.dependencies["js-yaml-orig"], "npm:js-yaml@5.4.1");
  assert.equal(
    wrapper.dependencies["js-yaml-orig"],
    manifest.dependencies["js-yaml-orig"],
  );
  assert.equal(lock.packages["node_modules/js-yaml-orig"].version, "5.4.1");
  assert.equal(wrapper.version, "5.4.1-compat.0");
  assert.equal(lock.packages["node_modules/js-yaml"].link, true);
  assert.equal(manifest.overrides["js-yaml"], "file:vendor/js-yaml-compat");
});

test("YAML wrapper supports ESM named/default and CommonJS load/dump", () => {
  const common = loadCommonJs("../../vendor/js-yaml-compat/index.cjs");
  // Verify the override through its real consumer, not just a direct vendor import.
  const astroRequire = createRequire(
    loadCommonJs.resolve("astro/package.json"),
  );
  assert.equal(astroRequire("js-yaml").load, common.load);
  const source = "title: Dashboard\nenabled: true\nitems:\n  - code: '001'\n";
  const expected = {
    title: "Dashboard",
    enabled: true,
    items: [{ code: "001" }],
  };
  for (const api of [yaml, common, common.default]) {
    assert.deepEqual(api.load(source), expected);
    assert.deepEqual(api.load(api.dump(expected)), expected);
    assert.throws(() => api.load("value: [unterminated"));
  }
  assert.deepEqual(load(source), expected);
});

test("PapaParse preserves dashboard CSV headers, quoted content and string identifiers", () => {
  const result = Papa.parse(
    'id,label\r\n001,"A, B"\r\n002,"Line 1\nLine 2"\r\n',
    {
      delimiter: ",",
      header: true,
      skipEmptyLines: true,
    },
  );
  assert.deepEqual(result.errors, []);
  assert.deepEqual(result.meta.fields, ["id", "label"]);
  assert.deepEqual(result.data, [
    { id: "001", label: "A, B" },
    { id: "002", label: "Line 1\nLine 2" },
  ]);
  const malformed = Papa.parse("id,label\n001,a,extra", {
    header: true,
    skipEmptyLines: true,
  });
  assert.ok(malformed.errors.some((error) => error.code === "TooManyFields"));
  for (const file of ["graph_nodes.csv", "graph_edges.csv"]) {
    const text = readFileSync(
      new URL(`../../public/data/${file}`, import.meta.url),
      "utf8",
    );
    const parsed = Papa.parse(text, { header: true, skipEmptyLines: true });
    assert.deepEqual(parsed.errors, []);
    assert.ok(parsed.data.length > 0);
  }
});
