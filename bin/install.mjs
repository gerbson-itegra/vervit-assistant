#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { pathToFileURL } from "node:url";

const MARKETPLACE = "vervit";
const PLUGIN = "vervit-assistant";
const DEFAULT_SOURCE = "gerbson-itegra/vervit-assistant";
const DEFAULT_REF = "main";

export function parseArgs(args) {
  const options = { source: DEFAULT_SOURCE, ref: DEFAULT_REF };

  for (let index = 0; index < args.length; index += 1) {
    const argument = args[index];
    if (argument === "--source" || argument === "--ref") {
      const value = args[index + 1];
      if (!value) {
        throw new Error(`Valor ausente para ${argument}.`);
      }
      options[argument.slice(2)] = value;
      index += 1;
      continue;
    }
    if (argument === "--help" || argument === "-h") {
      options.help = true;
      continue;
    }
    throw new Error(`Argumento desconhecido: ${argument}`);
  }

  return options;
}

export function marketplaceIsConfigured(output, marketplace = MARKETPLACE) {
  return output
    .split(/\r?\n/)
    .some((line) => line.trimStart().startsWith(`${marketplace} `));
}

function runCodex(args, { capture = false } = {}) {
  const result = spawnSync("codex", args, {
    encoding: "utf8",
    stdio: capture ? ["ignore", "pipe", "pipe"] : "inherit",
  });

  if (result.error?.code === "ENOENT") {
    throw new Error("O CLI 'codex' nao foi encontrado no PATH.");
  }
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    const details = [result.stdout, result.stderr].filter(Boolean).join("\n").trim();
    throw new Error(
      `Falha ao executar 'codex ${args.join(" ")}'.${details ? `\n${details}` : ""}`,
    );
  }

  return result.stdout ?? "";
}

export function install({ source = DEFAULT_SOURCE, ref = DEFAULT_REF } = {}) {
  const marketplaces = runCodex(["plugin", "marketplace", "list"], { capture: true });

  if (marketplaceIsConfigured(marketplaces)) {
    if (existsSync(source)) {
      console.log(`Marketplace local '${MARKETPLACE}' ja configurado.`);
    } else {
      console.log(`Atualizando marketplace privado '${MARKETPLACE}'...`);
      runCodex(["plugin", "marketplace", "upgrade", MARKETPLACE]);
    }
  } else {
    console.log(`Adicionando marketplace privado '${MARKETPLACE}'...`);
    const addArguments = ["plugin", "marketplace", "add", source];
    if (!existsSync(source)) {
      addArguments.push("--ref", ref);
    }
    runCodex(addArguments);
  }

  console.log(`Instalando '${PLUGIN}@${MARKETPLACE}'...`);
  runCodex(["plugin", "add", `${PLUGIN}@${MARKETPLACE}`]);
  console.log("Vervit Assistant instalado. Abra uma nova thread no Codex para usa-lo.");
}

function printHelp() {
  console.log(`Instala o Vervit Assistant a partir do marketplace GitHub privado.

Uso:
  npx github:gerbson-itegra/vervit-assistant
  vervit-assistant-install [--source <repo-ou-caminho>] [--ref <git-ref>]

Requisitos:
  - Node.js 18+
  - Codex CLI no PATH
  - acesso Git autenticado ao repositorio privado`);
}

const isDirectExecution =
  process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;

if (isDirectExecution) {
  try {
    const options = parseArgs(process.argv.slice(2));
    if (options.help) {
      printHelp();
    } else {
      install(options);
    }
  } catch (error) {
    console.error(`Erro: ${error.message}`);
    process.exitCode = 1;
  }
}
