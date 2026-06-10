import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { marketplaceIsConfigured, parseArgs } from "../bin/install.mjs";

const installerPath = fileURLToPath(new URL("../bin/install.mjs", import.meta.url));

test("usa o repositorio privado e a branch main por padrao", () => {
  assert.deepEqual(parseArgs([]), {
    source: "gerbson-itegra/vervit-assistant",
    ref: "main",
  });
});

test("aceita fonte local para validacao sem acessar GitHub", () => {
  assert.deepEqual(parseArgs(["--source", "C:\\repo", "--ref", "feature/test"]), {
    source: "C:\\repo",
    ref: "feature/test",
  });
});

test("detecta marketplace configurado na saida do Codex", () => {
  const output = `MARKETPLACE  ROOT
personal     C:\\Users\\dev
vervit       C:\\repo`;

  assert.equal(marketplaceIsConfigured(output), true);
  assert.equal(marketplaceIsConfigured(output, "missing"), false);
});

test("rejeita argumentos desconhecidos", () => {
  assert.throws(() => parseArgs(["--public"]), /Argumento desconhecido/);
});

test("executa diretamente e exibe ajuda", () => {
  const result = spawnSync(process.execPath, [installerPath, "--help"], {
    encoding: "utf8",
  });

  assert.equal(result.status, 0);
  assert.match(result.stdout, /npx github:gerbson-itegra\/vervit-assistant/);
});
