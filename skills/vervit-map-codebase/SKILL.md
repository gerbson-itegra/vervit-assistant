---
name: vervit-map-codebase
description: Use esta skill quando o usuario pedir para mapear, analisar, documentar ou atualizar o codebase no padrao Vervit/Superpowers, especialmente criando ou revisando .specs/codebase. Quando o usuario pedir TLC, combine com tlc-spec-driven para mapeamento brownfield estruturado.
metadata:
  short-description: Mapear codebase no padrao Vervit
---

# Vervit Map Codebase

Mapeie um projeto existente e mantenha a memoria tecnica em `.specs/codebase/`.

## Arquivos Esperados

- `.specs/codebase/STACK.md`
- `.specs/codebase/ARCHITECTURE.md`
- `.specs/codebase/CONVENTIONS.md`
- `.specs/codebase/STRUCTURE.md`
- `.specs/codebase/TESTING.md`
- `.specs/codebase/INTEGRATIONS.md`
- `.specs/codebase/CONCERNS.md`

## Fluxo

1. Leia instrucoes locais (`AGENTS.md`, `.agents/main-agent.md`) antes de analisar.
2. Identifique stack, package manager, scripts, estrutura, rotas, testes, CI, banco, auth e integracoes.
3. Separe fatos observados de inferencias.
4. Registre riscos ou areas frageis em `CONCERNS.md`.
5. Nao implemente codigo durante o mapeamento, a menos que o usuario peca explicitamente.

## TLC Sob Demanda

Superpowers continua sendo o padrao do fluxo Vervit. Quando o usuario pedir `TLC`, `tlc-spec-driven`, `map codebase TLC` ou equivalente:

1. Use `tlc-spec-driven` para orientar a profundidade do mapeamento brownfield.
2. Preserve a estrutura `.specs/codebase/` ja adotada pelo Vervit.
3. Registre fatos, inferencias e lacunas com rastreabilidade.
4. Nao duplique arquivos quando o conteudo existente puder ser atualizado com seguranca.

## Nivel De Profundidade

- Projeto pequeno: resumo objetivo em cada arquivo.
- Projeto medio: arquivos completos, mas sem perseguir cada detalhe.
- Projeto grande: mapear por areas e registrar lacunas explicitamente.

## Saida Esperada

Entregue uma lista dos arquivos atualizados, evidencias usadas e lacunas que precisam de revisao humana.
