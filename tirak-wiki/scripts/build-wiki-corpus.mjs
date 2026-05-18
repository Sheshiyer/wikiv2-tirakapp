import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

const docsRoot = path.resolve('src/content/docs');
const outDir = path.resolve('workers/rag/data');
const outFile = path.join(outDir, 'wiki-corpus.json');

async function main() {
  const files = await collectMarkdownFiles(docsRoot);
  const docs = [];

  for (const file of files) {
    const raw = await readFile(file, 'utf8');
    const parsed = parseFrontmatter(raw);
    const relativePath = path.relative(docsRoot, file).replaceAll(path.sep, '/');
    const slug = relativePath.replace(/\.(md|mdx)$/i, '');

    docs.push({
      slug,
      title: parsed.frontmatter.title ?? slug,
      description: parsed.frontmatter.description ?? '',
      category: parsed.frontmatter.category ?? 'unknown',
      sourcePath: `src/content/docs/${relativePath}`,
      content: parsed.content.trim(),
    });
  }

  await mkdir(outDir, { recursive: true });
  await writeFile(outFile, JSON.stringify({ generatedAt: new Date().toISOString(), docs }, null, 2));
  process.stdout.write(`Wrote ${docs.length} docs to ${path.relative(process.cwd(), outFile)}\n`);
}

async function collectMarkdownFiles(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...await collectMarkdownFiles(fullPath));
      continue;
    }

    if (/\.(md|mdx)$/i.test(entry.name)) {
      files.push(fullPath);
    }
  }

  return files;
}

function parseFrontmatter(raw) {
  if (!raw.startsWith('---\n')) {
    return { frontmatter: {}, content: raw };
  }

  const end = raw.indexOf('\n---\n', 4);
  if (end === -1) {
    return { frontmatter: {}, content: raw };
  }

  const frontmatterBlock = raw.slice(4, end);
  const content = raw.slice(end + 5);
  const frontmatter = {};

  for (const line of frontmatterBlock.split('\n')) {
    const separator = line.indexOf(':');
    if (separator === -1) {
      continue;
    }

    const key = line.slice(0, separator).trim();
    const value = line.slice(separator + 1).trim().replace(/^"|"$/g, '').replace(/^'|'$/g, '');
    frontmatter[key] = value;
  }

  return { frontmatter, content };
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
