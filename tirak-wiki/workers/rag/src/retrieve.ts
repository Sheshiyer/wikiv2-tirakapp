import { createEmbedding, createEmbeddings } from './nvidia';
import type { AppConfig, Env } from './config';
import type { ChunkRecord, CorpusFile, WikiDocument } from './types';

export type SearchResult = {
  id: string;
  score: number;
  text: string;
  metadata: Record<string, unknown>;
};

type SearchPayload = {
  query: string;
  topK?: number;
};

const CHUNK_SIZE = 1200;
const CHUNK_OVERLAP = 200;
const EMBEDDING_BATCH_SIZE = 32;

export function chunkWikiDocument(doc: WikiDocument): Array<Omit<ChunkRecord, 'appId' | 'embedding'>> {
  const text = normalizeText(doc.content);
  const chunks = splitIntoChunks(text);

  return chunks.map((chunk, chunkIndex) => ({
    id: `${doc.slug}#${chunkIndex}`,
    slug: doc.slug,
    title: doc.title,
    category: doc.category,
    sourcePath: doc.sourcePath,
    chunkIndex,
    text: chunk,
  }));
}

export async function ingestCorpusForApp(
  env: Env,
  appConfig: AppConfig,
  corpus: CorpusFile,
): Promise<{ count: number }> {
  const chunksForEmbedding: Array<Omit<ChunkRecord, 'appId' | 'embedding'>> = [];

  for (const doc of corpus.docs) {
    const chunks = chunkWikiDocument(doc);
    chunksForEmbedding.push(...chunks);
  }

  const chunkRecords: ChunkRecord[] = [];

  for (let start = 0; start < chunksForEmbedding.length; start += EMBEDDING_BATCH_SIZE) {
    const batch = chunksForEmbedding.slice(start, start + EMBEDDING_BATCH_SIZE);
    const embeddings = await createEmbeddings(
      env,
      batch.map((chunk) => chunk.text),
      appConfig.embeddingModel,
      'passage',
    );

    for (let index = 0; index < batch.length; index += 1) {
      chunkRecords.push({
        ...batch[index],
        appId: appConfig.appId,
        embedding: embeddings[index],
      });
    }
  }

  await env.APP_INDEX.put(indexKey(appConfig.appId), JSON.stringify(chunkRecords));
  return { count: chunkRecords.length };
}

export async function searchAppCorpus(
  env: Env,
  appConfig: AppConfig,
  payload: SearchPayload,
): Promise<SearchResult[]> {
  const stored = await env.APP_INDEX.get<ChunkRecord[]>(indexKey(appConfig.appId), 'json');
  if (!stored?.length) {
    return [];
  }

  const queryEmbedding = await createEmbedding(
    env,
    payload.query,
    appConfig.embeddingModel,
    'query',
  );

  const topK = payload.topK ?? appConfig.searchTopK;

  return stored
    .map((chunk) => ({
      id: chunk.id,
      score: cosineSimilarity(queryEmbedding, chunk.embedding),
      text: chunk.text,
      metadata: {
        appId: chunk.appId,
        slug: chunk.slug,
        title: chunk.title,
        category: chunk.category,
        sourcePath: chunk.sourcePath,
        chunkIndex: chunk.chunkIndex,
      },
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);
}

export function formatContext(results: SearchResult[]): string {
  return results
    .map((result, index) => {
      const title = String(result.metadata.title ?? 'Untitled');
      const slug = String(result.metadata.slug ?? 'unknown');
      return `[${index + 1}] ${title} (${slug})\n${result.text}`;
    })
    .join('\n\n');
}

function indexKey(appId: string): string {
  return `index:${appId}`;
}

function splitIntoChunks(text: string): string[] {
  const chunks: string[] = [];
  let start = 0;

  while (start < text.length) {
    const end = Math.min(start + CHUNK_SIZE, text.length);
    const chunk = text.slice(start, end).trim();
    if (chunk) {
      chunks.push(chunk);
    }

    if (end === text.length) {
      break;
    }

    start = Math.max(end - CHUNK_OVERLAP, start + 1);
  }

  return chunks;
}

function normalizeText(text: string): string {
  return text.replace(/\r\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
}

function cosineSimilarity(a: number[], b: number[]): number {
  let dot = 0;
  let normA = 0;
  let normB = 0;

  const length = Math.min(a.length, b.length);
  for (let index = 0; index < length; index += 1) {
    dot += a[index] * b[index];
    normA += a[index] * a[index];
    normB += b[index] * b[index];
  }

  if (!normA || !normB) {
    return 0;
  }

  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}
