#!/usr/bin/env node
// open-intake-pr.mjs: the ONLY sanctioned PR path for the skill-forge intake lane.
//
// STANDS ALONE: ~/bin/gh-app-token.mjs (the existing counterpart considered) only mints
// tokens; nothing else stages-validates, branches, pushes, and opens forge intake PRs.
// It lives in the repo (not ~/.claude/crons), so no G4 glue-budget impact.
//
// owner: Matthew (HIL merge gate until graduation)
// sink:  a DRAFT PR on github.com/m2ai-st-metro/skill-forge + data/forge-cycle-ledger.json
// kill:  exits non-zero on any allowlist violation (2) or duplicate branch/PR (3);
//        no retries, no loops; the nightly routine escalates on failure.
//
// Usage:
//   node scripts/open-intake-pr.mjs --skill <name> [--title "..."] [--body-file path] [--validate-only]
//   node scripts/open-intake-pr.mjs --tool-issue --name <kebab> --source-url <url> --summary-file <path>
//                                   [--title "..."] [--hooks "a; b; c"] [--project <lane>] [--dry-run]
//   node scripts/open-intake-pr.mjs --graduation-check
//
// Allowed staged paths: skills/<name>/** (new files only), registry.yaml,
// data/intake/*.processed.md, data/last_check.txt. Anything else = exit 2.
// Existing forge/<name> branch or open PR = exit 3 (kills the MAI-7 duplicate race).
//
// CLASSIFICATION GATE (MAI-206). Every intake candidate is classified technique | tool | other
// BEFORE anything is drafted (rule: ~/.claude/rules/tool-skill-subagent-triage.md). Only a
// `technique` becomes a skill. The staged skills/<name>/skill-registry.yaml MUST carry
// `classification: technique`; a missing value or tool/other = exit 2, no branch, no PR.
// A `tool` (PR #112, subscription-sdk-bridge, was a tool force-fit into a SKILL.md) exits the
// intake through `--tool-issue`: a Paperclip evaluation issue (Pattern-4 discovery exit)
// carrying the source URL, a one-paragraph summary, and relevance hooks. The intake file
// records `**Classification:** tool` + `**Routing:** CARD — MAI-nnn` per idea, enforced by
// scripts/mark_intake_processed.py, so every classification is grep-able after the fact.
//
// The sidecar is parsed as real YAML with duplicate-key rejection (scripts/strict_yaml.py), so
// the gate judges the value the parser resolves, not the first line a regex happens to match.
//
// `--tool-issue` does NOT post to Paperclip itself. It renders a goal-maker-shaped card and hands
// it to the workspace's ONE sanctioned intake funnel, ~/.claude/crons/goal-to-issue.mjs (owner/
// sink/kill guards, evidence gate, dedup, idempotency, read-back all live there, once). Override
// the funnel path with FORGE_GOAL_TO_ISSUE for fixture tests.
//
// HIL graduation: PRs open as DRAFT until data/forge-cycle-ledger.json cleanCycles >= 7.
// POST-GRADUATION FLIP: change `draft: !graduated` below to `draft: false` semantics is
// already automatic once cleanCycles >= 7; the remaining one-line decision is enabling
// auto-merge in the review routine. KNOWN CONSTRAINT: the GitHub App cannot approve its
// own PRs, so post-graduation auto-merge still needs a second reviewer identity or
// Matthew's review to satisfy branch protection (require 1 approving review).
//
// The App token is minted per run via ~/bin/gh-app-token.mjs --owner m2ai-st-metro
// --repo skill-forge, held in memory, used in an ephemeral push URL, and never logged
// or written to disk/git config.

import { spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync, unlinkSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir, tmpdir } from 'node:os';

const args = process.argv.slice(2);
const opt = (f) => (args.includes(f) ? args[args.indexOf(f) + 1] : null);
const die = (code, msg) => { console.error(msg); process.exit(code); };

// --repo exists so the gate can be exercised against a fixture repo (tests/test_open_intake_pr.py);
// production runs never pass it and resolve to the checkout this script lives in.
const REPO = opt('--repo') ? resolve(opt('--repo')) : resolve(dirname(fileURLToPath(import.meta.url)), '..');
const OWNER = 'm2ai-st-metro';
const NAME = 'skill-forge';
const LEDGER = resolve(REPO, 'data/forge-cycle-ledger.json');
const GRADUATION_BAR = 7;

const CLASSIFICATIONS = ['technique', 'tool', 'other'];

const git = (...a) => {
  const r = spawnSync('git', ['-C', REPO, ...a], { encoding: 'utf8' });
  if (r.status !== 0) die(1, `git ${a[0]} failed: ${r.stderr.trim()}`);
  return r.stdout.trim();
};

const loadLedger = () => {
  if (!existsSync(LEDGER)) return { cleanCycles: 0, lastCycle: null, history: [] };
  return JSON.parse(readFileSync(LEDGER, 'utf8'));
};

if (args.includes('--graduation-check')) {
  const l = loadLedger();
  console.log(`cleanCycles: ${l.cleanCycles}`);
  process.exit(l.cleanCycles >= GRADUATION_BAR ? 0 : 1);
}

// ---------------------------------------------------------------------------------------------
// --tool-issue: the tool-classified exit. No SKILL.md, no forge/<name> branch, no PR. Renders ONE
// goal-maker card and routes it through goal-to-issue.mjs (the sanctioned funnel), then prints
// the identifier it created (`created MAI-nnn`) or referenced (`existing MAI-nnn`, from the
// funnel's dedup refusal) so the intake file can record `**Routing:** CARD — MAI-nnn`.
// ---------------------------------------------------------------------------------------------
if (args.includes('--tool-issue')) {
  const name = opt('--name');
  if (!name || !/^[a-z0-9][a-z0-9-]*$/.test(name)) die(2, 'usage: --tool-issue --name <kebab-name> required');
  const sourceUrl = opt('--source-url');
  if (!sourceUrl || !/^https?:\/\//.test(sourceUrl)) die(2, 'usage: --source-url <http(s) url> required');
  const summaryFile = opt('--summary-file');
  if (!summaryFile || !existsSync(summaryFile)) die(2, 'usage: --summary-file <path> required (one-paragraph summary of the tool)');
  const summary = readFileSync(summaryFile, 'utf8').trim();
  if (summary.length < 40) die(2, 'summary must be a real paragraph (>= 40 chars)');
  const hooks = (opt('--hooks') || '').split(';').map((h) => h.trim()).filter(Boolean);
  // Default lane: `build`, where evaluation work is routed by the daily routing pass.
  const project = opt('--project') || process.env.FORGE_TOOL_ISSUE_PROJECT || 'build';
  const title = (opt('--title') || `Evaluate tool: ${name}`).slice(0, 200);

  // goal-maker card shape: front-matter with REAL owner/sink/kill (goal-to-issue refuses
  // placeholders) plus a testable done-when (its evidence gate refuses boilerplate).
  const card = [
    '---',
    `title: ${title}`,
    `owner: Matthew (evaluation decision)`,
    `sink: comment on the issue with adopt / trial / no-go and the reason`,
    `kill: one evaluation pass; close with the decision recorded`,
    `lane: ${project}`,
    `shape: one-shot`,
    `classification: tool`,
    `source: forge intake (tool-vs-technique gate, scripts/open-intake-pr.mjs --tool-issue)`,
    `source_url: ${sourceUrl}`,
    `candidate: ${name}`,
    '---',
    '',
    '## Summary',
    summary,
    '',
    '## Relevance hooks',
    ...(hooks.length ? hooks.map((h) => `- ${h}`) : ['- (none recorded by the scan; add before evaluating)']),
    '',
    '## Why this is an issue and not a skill',
    'The forge intake classified this candidate as a TOOL (a thing to install or call), not a TECHNIQUE',
    '(a procedure to distill into a SKILL.md). Tools do not become skills (tool-skill-subagent triage).',
    'This is the Pattern-4 discovery exit: the intake file records `**Routing:** CARD — <this issue>`.',
    '',
    '## Done when',
    `A comment on this issue records adopt, trial, or no-go for ${name} with a one-line reason, and the issue is closed.`,
    '',
  ].join('\n');

  // Dry-run renders the card locally: no token, no funnel call, no network.
  if (args.includes('--dry-run')) {
    console.log(`DRY-RUN --tool-issue (nothing created; this card would go to goal-to-issue.mjs)\n${card}`);
    process.exit(0);
  }

  const funnel = process.env.FORGE_GOAL_TO_ISSUE || resolve(homedir(), '.claude/crons/goal-to-issue.mjs');
  if (!existsSync(funnel)) die(1, `sanctioned intake funnel not found at ${funnel} (set FORGE_GOAL_TO_ISSUE to override)`);
  const scratch = process.env.PAPERCLIP_RUN_SCRATCH_DIR || process.env.PAPERCLIP_SCRATCH_DIR || tmpdir();
  const cardPath = resolve(scratch, `forge-tool-issue-${name}-${process.pid}.md`);
  writeFileSync(cardPath, card);
  let run;
  try {
    // No --force: the funnel's dedup (Jaccard >= 0.75 on open titles) is the dedup. An exact
    // title match is reported as `existing`; a near-match is surfaced for a human to decide.
    run = spawnSync('node', [funnel, '--file', cardPath, '--project', project], { encoding: 'utf8', env: process.env });
  } finally {
    try { unlinkSync(cardPath); } catch { /* scratch dir may already be gone */ }
  }
  if (run.status === 3) {
    // Exact-title open duplicate (goal-to-issue: "dedup refusal: near-duplicate of MAI-nnn ...").
    const m = (run.stderr || '').match(/near-duplicate of ([A-Z]+-\d+) "([^"]*)"/);
    if (m && m[2].trim().toLowerCase() === title.trim().toLowerCase()) {
      console.log(`existing ${m[1]}`);
      process.exit(0);
    }
    die(3, `goal-to-issue refused as a near-duplicate (re-run with a more specific --title):\n${(run.stderr || '').trim()}`);
  }
  if (run.status !== 0) die(run.status || 1, `goal-to-issue.mjs failed (exit ${run.status}):\n${(run.stderr || '').trim()}`);
  const created = (run.stdout || '').match(/^created ([A-Z]+-\d+)/m);
  if (!created) die(1, `goal-to-issue.mjs exited 0 but printed no "created <id>" line (treat this capture as LOST):\n${run.stdout}`);
  const link = ((run.stdout || '').match(/https?:\/\/\S+/) || [''])[0];
  console.log(`created ${created[1]} ${link}`.trim());
  process.exit(0);
}

const skill = opt('--skill');
if (!skill || !/^[a-z0-9][a-z0-9-]*$/.test(skill)) die(2, 'usage: --skill <kebab-name> required');
const branch = `forge/${skill}`;

// 1. Validate the staged change set against the allowlist.
const staged = git('diff', '--cached', '--name-status', '-z').split('\0').filter(Boolean);
const entries = [];
for (let i = 0; i < staged.length; i += 2) entries.push({ status: staged[i][0], path: staged[i + 1] });
if (entries.length === 0) die(2, 'nothing staged');

const bad = [];
const skillDirs = new Set();
for (const { status, path } of entries) {
  if (path === 'registry.yaml' || path === 'data/last_check.txt') continue;
  if (/^data\/intake\/[^/]+\.processed\.md$/.test(path)) continue;
  const m = path.match(/^skills\/([^/]+)\//);
  if (m) {
    skillDirs.add(m[1]);
    if (status !== 'A') bad.push(`${path} (skill files must be new, got status ${status})`);
    continue;
  }
  bad.push(path);
}
if (skillDirs.size > 1) die(2, `more than one skills/<dir> staged: ${[...skillDirs].join(', ')}`);
if (skillDirs.size === 0) die(2, `nothing staged under skills/${skill}/; --skill is the skill-creation path and requires the new skill dir (with skill-registry.yaml) to be staged`);
if (!skillDirs.has(skill)) die(2, `staged skill dir "${[...skillDirs][0]}" does not match --skill ${skill}`);
if (bad.length) die(2, `staged paths outside the intake allowlist:\n  ${bad.join('\n  ')}`);

// 1b. Classification gate: the staged sidecar, parsed as YAML with duplicate keys REJECTED, must
// resolve top-level `classification` to `technique`. (A regex on the text was bypassable: a first
// `classification: technique` line masked a later `classification: tool` that the YAML parser,
// and therefore the registry, would actually use.)
const sidecarPath = `skills/${skill}/skill-registry.yaml`;
if (!entries.some((e) => e.path === sidecarPath)) die(2, `${sidecarPath} must be staged (carries the classification field)`);
const sidecarText = git('show', `:${sidecarPath}`);
const parsed = spawnSync('python3', [resolve(dirname(fileURLToPath(import.meta.url)), 'strict_yaml.py')], { input: sidecarText, encoding: 'utf8' });
if (parsed.status !== 0) die(2, `${sidecarPath} is not valid strict YAML: ${(parsed.stderr || '').trim()}`);
const sidecar = JSON.parse(parsed.stdout || 'null');
if (!sidecar || typeof sidecar !== 'object' || Array.isArray(sidecar)) die(2, `${sidecarPath} must be a YAML mapping`);
const cls = sidecar.classification;
if (cls === undefined || cls === null || cls === '') die(2, `${sidecarPath} has no classification field; add \`classification: technique\` (only techniques become skills; tools exit via --tool-issue)`);
if (typeof cls !== 'string' || !CLASSIFICATIONS.includes(cls)) die(2, `${sidecarPath}: classification "${cls}" is not one of ${CLASSIFICATIONS.join(' | ')}`);
if (cls !== 'technique') die(2, `${sidecarPath}: classification "${cls}" does not become a skill. Unstage skills/${skill}/ and run:\n  node scripts/open-intake-pr.mjs --tool-issue --name ${skill} --source-url <url> --summary-file <path> [--hooks "a; b"]`);
if (args.includes('--validate-only')) { console.log(`validate-only: staged set for ${skill} passes the allowlist and classification gate`); process.exit(0); }

// 2. Mint a repo-scoped App token (stdout only, never logged).
const mint = spawnSync('node', [resolve(homedir(), 'bin/gh-app-token.mjs'), '--owner', OWNER, '--repo', NAME], { encoding: 'utf8' });
if (mint.status !== 0) die(1, `token mint failed: ${mint.stderr.trim()}`);
const token = mint.stdout.trim();
if (!token) die(1, 'token mint returned empty stdout');

const api = async (path, opts = {}) => {
  const r = await fetch(`https://api.github.com${path}`, {
    ...opts,
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', ...opts.headers },
  });
  const body = await r.json().catch(() => ({}));
  return { ok: r.ok, status: r.status, body };
};

// 3. Duplicate guards: existing remote branch or open PR = refuse.
const br = await api(`/repos/${OWNER}/${NAME}/branches/${encodeURIComponent(branch)}`);
if (br.ok) die(3, `branch ${branch} already exists on origin; refusing (duplicate race guard)`);
const prs = await api(`/repos/${OWNER}/${NAME}/pulls?state=open&head=${OWNER}:${encodeURIComponent(branch)}`);
if (prs.ok && prs.body.length > 0) die(3, `open PR already exists for ${branch}: ${prs.body[0].html_url}`);

// 4. Branch from origin/main, commit staged paths, push with the ephemeral token URL.
git('fetch', 'origin', 'main');
const startBranch = git('rev-parse', '--abbrev-ref', 'HEAD');
git('checkout', '-b', branch, 'origin/main');
try {
  git('commit', '-m', `forge(intake): add skill ${skill}\n\nOpened by scripts/open-intake-pr.mjs (sanctioned forge intake lane).`);
  const pushUrl = `https://x-access-token:${token}@github.com/${OWNER}/${NAME}.git`;
  const push = spawnSync('git', ['-C', REPO, 'push', pushUrl, `${branch}:${branch}`], { encoding: 'utf8' });
  if (push.status !== 0) die(1, `push failed: ${push.stderr.replace(token, '***')}`);
} finally {
  spawnSync('git', ['-C', REPO, 'checkout', startBranch], { encoding: 'utf8' });
}

// 5. Open the PR (DRAFT until graduation).
const ledger = loadLedger();
const graduated = ledger.cleanCycles >= GRADUATION_BAR;
const bodyFile = opt('--body-file');
const pr = await api(`/repos/${OWNER}/${NAME}/pulls`, {
  method: 'POST',
  body: JSON.stringify({
    title: opt('--title') || `forge(intake): ${skill}`,
    head: branch,
    base: 'main',
    draft: !graduated,
    body: bodyFile ? readFileSync(bodyFile, 'utf8') : `Automated forge intake PR for \`${skill}\`.\n\nOpened via \`scripts/open-intake-pr.mjs\` (allowlist-validated). ${graduated ? 'Lane is GRADUATED.' : `HIL gate active: draft until ${GRADUATION_BAR} clean cycles (currently ${ledger.cleanCycles}).`}`,
  }),
});
if (!pr.ok) die(1, `PR creation failed ${pr.status}: ${JSON.stringify(pr.body).slice(0, 500)}`);

// 6. Ledger: append this cycle record (cleanCycles is advanced by the review routine, not here).
const record = { ts: new Date().toISOString(), skill, pr: pr.body.html_url, draft: !graduated };
ledger.lastCycle = record;
ledger.history.push(record);
writeFileSync(LEDGER, JSON.stringify(ledger, null, 2) + '\n');

console.log(pr.body.html_url);
