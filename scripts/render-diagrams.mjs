#!/usr/bin/env node
// Render every ```mermaid block in the learning docs to a committed, GitHub-safe
// SVG, and rewrite the doc to embed the SVG with the Mermaid source kept beside it
// in a collapsed <details> block.
//
// Source of truth stays the Mermaid text (diffable, AI-editable); the committed SVG
// is what renders in GitHub, plain markdown viewers, PDF/HTML exports, etc.
//
//   node scripts/render-diagrams.mjs            # render everything
//   node scripts/render-diagrams.mjs <files...> # render only the given .md files
//   node scripts/render-diagrams.mjs --check    # verify, don't write (for pre-commit/CI)
//
// The rewrite is idempotent: re-running re-renders from the (unwrapped) Mermaid
// source, so it is safe to run after editing either the diagram or the prose.

import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync, readdirSync, statSync } from 'node:fs';
import { dirname, join, basename, relative, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const MMDC = join(ROOT, 'node_modules', '.bin', 'mmdc');
const CONFIG = join(ROOT, 'scripts', 'mermaid.config.json');
const PUPPETEER = join(ROOT, 'scripts', 'puppeteer.config.json');
const DOC_ROOTS = ['courses', 'upskill-readings', 'hobby'];

const argv = process.argv.slice(2);
const CHECK = argv.includes('--check');
const fileArgs = argv.filter((a) => !a.startsWith('--'));

const WRAP_RE = /<!-- DIAGRAM:START -->[\s\S]*?<!-- DIAGRAM:END -->/g;
const FENCE_RE = /```mermaid\r?\n([\s\S]*?)\r?\n```/g;
const INNER_RE = /```mermaid\r?\n([\s\S]*?)\r?\n```/;

function findChrome() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) return process.env.PUPPETEER_EXECUTABLE_PATH;
  for (const c of [
    '/usr/bin/google-chrome-stable',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/snap/bin/chromium',
  ]) if (existsSync(c)) return c;
  return null;
}

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    if (name === 'node_modules' || name === 'diagrams' || name.startsWith('.')) continue;
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) walk(p, out);
    else if (name.endsWith('.md')) out.push(p);
  }
  return out;
}

function targets() {
  if (fileArgs.length) return fileArgs.map((f) => resolve(f));
  const out = [];
  for (const r of DOC_ROOTS) {
    const d = join(ROOT, r);
    if (existsSync(d)) walk(d, out);
  }
  return out;
}

const CHROME = findChrome();
const childEnv = CHROME ? { ...process.env, PUPPETEER_EXECUTABLE_PATH: CHROME } : process.env;

function renderSvg(src, outPath) {
  mkdirSync(dirname(outPath), { recursive: true });
  const tmp = outPath.replace(/\.svg$/, '.tmp.mmd');
  writeFileSync(tmp, src + '\n');
  try {
    execFileSync(MMDC, ['-i', tmp, '-o', outPath, '-c', CONFIG, '-p', PUPPETEER, '-b', 'transparent', '--quiet'], {
      stdio: 'pipe',
      env: childEnv,
    });
  } catch (e) {
    const msg = (e.stderr || e.stdout || e.message || '').toString();
    throw new Error(`mmdc failed for ${outPath}:\n${msg}`);
  } finally {
    rmSync(tmp, { force: true });
  }
  // GitHub strips <foreignObject>; htmlLabels:false should prevent it, but verify.
  if (readFileSync(outPath, 'utf8').includes('<foreignObject')) {
    throw new Error(`${outPath} contains <foreignObject> — it will not render on GitHub. Check mermaid.config.json (htmlLabels:false).`);
  }
}

// Normalize a doc back to bare ```mermaid fences (undo any prior wrapping).
function unwrap(text) {
  return text.replace(WRAP_RE, (block) => {
    const m = block.match(INNER_RE);
    return m ? '```mermaid\n' + m[1].trim() + '\n```' : block;
  });
}

function wrapBlock(n, src, svgRel) {
  return (
    '<!-- DIAGRAM:START -->\n' +
    `![Diagram ${n}](${svgRel})\n\n` +
    '<details>\n<summary>Diagram source (Mermaid)</summary>\n\n' +
    '```mermaid\n' + src + '\n```\n\n' +
    '</details>\n' +
    '<!-- DIAGRAM:END -->'
  );
}

function processFile(file) {
  const original = readFileSync(file, 'utf8');
  const text = unwrap(original);
  const docDir = dirname(file);
  const base = basename(file, '.md');
  const matches = [...text.matchAll(FENCE_RE)];

  if (CHECK) {
    // Verify: doc already wrapped (no bare fences outside a wrapper) and every SVG exists.
    const problems = [];
    const wrappedSrc = (original.match(WRAP_RE) || []).join('\n');
    const bareCount = [...original.matchAll(FENCE_RE)].length;
    const inWrapCount = [...wrappedSrc.matchAll(FENCE_RE)].length;
    if (bareCount !== inWrapCount) problems.push(`${bareCount - inWrapCount} un-wrapped mermaid block(s)`);
    matches.forEach((_, i) => {
      const svg = join(docDir, 'diagrams', `${base}-${i + 1}.svg`);
      if (!existsSync(svg)) problems.push(`missing ${relative(ROOT, svg)}`);
    });
    return { file, count: matches.length, problems };
  }

  if (matches.length === 0) {
    if (text !== original) writeFileSync(file, text);
    return { file, count: 0, problems: [] };
  }

  let result = '';
  let last = 0;
  matches.forEach((mt, i) => {
    const n = i + 1;
    const src = mt[1].trim();
    const svgRel = `diagrams/${base}-${n}.svg`;
    renderSvg(src, join(docDir, 'diagrams', `${base}-${n}.svg`));
    result += text.slice(last, mt.index) + wrapBlock(n, src, svgRel);
    last = mt.index + mt[0].length;
  });
  result += text.slice(last);
  if (result !== original) writeFileSync(file, result);
  return { file, count: matches.length, problems: [] };
}

// ---- main ----
if (!existsSync(MMDC)) {
  console.error('mmdc not found. Run: npm install');
  process.exit(1);
}
if (!CHECK && !CHROME) {
  console.error('No Chrome/Chromium found. Set PUPPETEER_EXECUTABLE_PATH or install Chrome.');
  process.exit(1);
}

const files = targets().filter((f) => readFileSync(f, 'utf8').includes('```mermaid') || readFileSync(f, 'utf8').includes('DIAGRAM:START'));
let totalDiagrams = 0;
let totalProblems = 0;

for (const file of files) {
  try {
    const { count, problems } = processFile(file);
    totalDiagrams += count;
    const rel = relative(ROOT, file);
    if (problems.length) {
      totalProblems += problems.length;
      console.log(`✗ ${rel}: ${problems.join('; ')}`);
    } else if (count) {
      console.log(`${CHECK ? '✓' : '→'} ${rel} (${count} diagram${count === 1 ? '' : 's'})`);
    }
  } catch (e) {
    totalProblems++;
    console.error(`✗ ${relative(ROOT, file)}: ${e.message}`);
  }
}

console.log(`\n${CHECK ? 'Checked' : 'Rendered'} ${totalDiagrams} diagram(s) across ${files.length} file(s).`);
if (CHROME && !CHECK) console.log(`(Chrome: ${CHROME})`);
if (totalProblems) {
  console.error(`${totalProblems} problem(s).`);
  process.exit(1);
}
