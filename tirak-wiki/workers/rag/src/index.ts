import { getAppConfig, getDefaults, isAuthorizedRequest, type Env } from './config';
import { createChatCompletion } from './nvidia';
import { formatContext, ingestCorpusForApp, searchAppCorpus } from './retrieve';
import type { CorpusFile } from './types';

type Json = Record<string, unknown>;

type ChatMode = 'best' | 'fast';

const CHAT_TIMEOUT_MS: Record<ChatMode, number> = {
  fast: 12000,
  best: 20000,
};

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders() });
    }

    try {
      if (url.pathname === '/health') {
        return json({ ok: true, environment: env.ENVIRONMENT ?? 'development' });
      }

      if (url.pathname === '/v1/models') {
        const defaults = await getDefaults(env);
        return json({
          defaults,
          note: 'Model aliases and overrides belong in KV. Nvidia credentials belong in Worker secrets.',
        });
      }

      if (url.pathname === '/v1/search' && request.method === 'POST') {
        return withCors(await handleSearch(request, env));
      }

      if (url.pathname === '/v1/ingest' && request.method === 'POST') {
        return withCors(await handleIngest(request, env));
      }

      if (url.pathname === '/v1/chat' && request.method === 'POST') {
        return withCors(await handleChat(request, env));
      }

      return withCors(json({ error: 'Not found' }, 404));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      return withCors(json({ error: message }, 500));
    }
  },
};

async function handleSearch(request: Request, env: Env): Promise<Response> {
  const body = await request.json() as { appId?: string; query?: string; topK?: number };
  const appId = body.appId?.trim();

  if (!appId || !body.query) {
    return json({ error: 'appId and query are required' }, 400);
  }

  if (!(await isAuthorizedRequest(env, request, appId))) {
    return json({ error: 'Unauthorized' }, 401);
  }

  const appConfig = await getAppConfig(env, appId);
  if (!appConfig || !appConfig.enabled) {
    return json({ error: 'Unknown or disabled app' }, 404);
  }

  const results = await searchAppCorpus(env, appConfig, {
    query: body.query,
    topK: body.topK,
  });

  return json({
    appId,
    corpusId: appConfig.corpusId,
    vectorIndexBinding: appConfig.vectorIndexBinding,
    results,
  });
}

async function handleIngest(request: Request, env: Env): Promise<Response> {
  const body = await request.json() as { appId?: string; corpus?: CorpusFile };
  const appId = body.appId?.trim();

  if (!appId || !body.corpus?.docs?.length) {
    return json({ error: 'appId and corpus.docs are required' }, 400);
  }

  if (!(await isAuthorizedRequest(env, request, appId))) {
    return json({ error: 'Unauthorized' }, 401);
  }

  const appConfig = await getAppConfig(env, appId);
  if (!appConfig || !appConfig.enabled) {
    return json({ error: 'Unknown or disabled app' }, 404);
  }

  const ingested = await ingestCorpusForApp(env, appConfig, body.corpus);

  return json({
    appId,
    corpusId: appConfig.corpusId,
    embeddingModel: appConfig.embeddingModel,
    chunkCount: ingested.count,
  });
}

async function handleChat(request: Request, env: Env): Promise<Response> {
  const body = await request.json() as {
    appId?: string;
    query?: string;
    responseMode?: ChatMode;
    currentPage?: { slug?: string; title?: string };
  };
  const appId = body.appId?.trim();

  if (!appId || !body.query) {
    return json({ error: 'appId and query are required' }, 400);
  }

  if (!(await isAuthorizedRequest(env, request, appId))) {
    return json({ error: 'Unauthorized' }, 401);
  }

  const appConfig = await getAppConfig(env, appId);
  if (!appConfig || !appConfig.enabled) {
    return json({ error: 'Unknown or disabled app' }, 404);
  }

  const responseMode = body.responseMode ?? 'best';

  const context = await searchAppCorpus(env, appConfig, {
    query: [
      body.query,
      body.currentPage?.title ? `Current page title: ${body.currentPage.title}` : '',
      body.currentPage?.slug ? `Current page slug: ${body.currentPage.slug}` : '',
    ].filter(Boolean).join('\n'),
    topK: responseMode === 'fast' ? Math.min(3, appConfig.searchTopK) : appConfig.searchTopK,
  });

  const contextText = formatContext(context);
  const gate = evaluateChatGate({
    query: body.query,
    responseMode,
    currentPage: body.currentPage,
    contextCount: context.length,
    contextText,
  });

  if (gate.shouldBypassGeneration) {
    return json({
      appId,
      model: appConfig.chatModel,
      embeddingModel: appConfig.embeddingModel,
      promptId: appConfig.promptId,
      mode: responseMode,
      gated: true,
      gateReason: gate.reason,
      retryable: true,
      retryHint: responseMode === 'best'
        ? 'Try Faster answer for a shorter source-led response.'
        : 'Try asking from a more specific page or narrowing the question.',
      retrievedContext: context,
      answer: buildFallbackAnswer(context, body.query),
    });
  }

  try {
    const answer = await withTimeout(createChatCompletion(env, appConfig.chatModel, [
    {
      role: 'system',
      content: [
        'You answer questions only using the provided wiki context.',
        'If the answer is not in the context, say you do not see it in the wiki.',
        'Cite relevant source titles and slugs briefly.',
      ].join(' '),
    },
    {
      role: 'user',
      content: [
        `Question:\n${body.query}`,
        body.currentPage?.title ? `Current page:\n${body.currentPage.title} (${body.currentPage.slug ?? 'unknown'})` : '',
        `Response mode:\n${responseMode}`,
        `Wiki context:\n${contextText}`,
      ].filter(Boolean).join('\n\n'),
    },
  ], responseMode === 'fast'
    ? { maxTokens: 90, temperature: 0.1 }
    : { maxTokens: 180, temperature: 0.2 }), CHAT_TIMEOUT_MS[responseMode], `Chat generation exceeded ${CHAT_TIMEOUT_MS[responseMode]}ms`);

    return json({
      appId,
      model: appConfig.chatModel,
      embeddingModel: appConfig.embeddingModel,
      secretSource: 'NVIDIA_API_KEY worker secret',
      promptId: appConfig.promptId,
      mode: responseMode,
      gated: false,
      retrievedContext: context,
      answer,
    });
  } catch (error) {
    return json({
      appId,
      model: appConfig.chatModel,
      embeddingModel: appConfig.embeddingModel,
      promptId: appConfig.promptId,
      mode: responseMode,
      gated: true,
      gateReason: 'generation_failed',
      retryable: true,
      retryHint: responseMode === 'best'
        ? 'Try Faster answer for a shorter source-led response.'
        : 'Try a narrower question or ask about one specific page section.',
      retrievedContext: context,
      answer: buildFallbackAnswer(context, body.query),
    });
  }
}

function evaluateChatGate(input: {
  query: string;
  responseMode: ChatMode;
  currentPage?: { slug?: string; title?: string };
  contextCount: number;
  contextText: string;
}): { shouldBypassGeneration: boolean; reason: string } {
  const queryLength = input.query.trim().length;
  const contextLength = input.contextText.length;
  const pageContextLength = `${input.currentPage?.title ?? ''}${input.currentPage?.slug ?? ''}`.length;
  const totalBudget = queryLength + contextLength + pageContextLength;

  if (input.contextCount === 0) {
    return { shouldBypassGeneration: true, reason: 'no_retrieval_context' };
  }

  if (input.responseMode === 'fast' && totalBudget > 7000) {
    return { shouldBypassGeneration: true, reason: 'fast_mode_budget_exceeded' };
  }

  if (input.responseMode === 'best' && totalBudget > 7000) {
    return { shouldBypassGeneration: true, reason: 'best_mode_budget_exceeded' };
  }

  return { shouldBypassGeneration: false, reason: 'within_budget' };
}

function buildFallbackAnswer(
  context: Array<{ metadata: Record<string, unknown>; text: string }>,
  query: string,
): string {
  if (!context.length) {
    return `I couldn't find enough wiki context to answer "${query}" yet. Try asking about a more specific page, partner step, or campaign topic.`;
  }

  const lead = context[0];
  const title = String(lead.metadata.title ?? 'Relevant page');
  const slug = String(lead.metadata.slug ?? 'unknown');
  const excerpt = lead.text.slice(0, 320).trim();

  return [
    `Here is the most relevant wiki context I found for "${query}".`,
    `Start with ${title} (${slug}).`,
    excerpt,
  ].join('\n\n');
}

function json(body: Json, status = 200): Response {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
    },
  });
}

function withCors(response: Response): Response {
  const headers = new Headers(response.headers);
  for (const [key, value] of Object.entries(corsHeaders())) {
    headers.set(key, value);
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

function corsHeaders(): Record<string, string> {
  return {
    'access-control-allow-origin': '*',
    'access-control-allow-methods': 'GET,POST,OPTIONS',
    'access-control-allow-headers': 'authorization,content-type,x-client-key',
  };
}

async function withTimeout<T>(promise: Promise<T>, timeoutMs: number, message: string): Promise<T> {
  return await Promise.race([
    promise,
    new Promise<T>((_, reject) => {
      setTimeout(() => reject(new Error(message)), timeoutMs);
    }),
  ]);
}
