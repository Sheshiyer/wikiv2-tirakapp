import type { Env } from './config';

const NVIDIA_BASE_URL = 'https://integrate.api.nvidia.com/v1';

type EmbeddingInputType = 'passage' | 'query';

type ChatMessage = {
  role: 'system' | 'user' | 'assistant';
  content: string;
};

export async function createEmbedding(
  env: Env,
  text: string,
  model: string,
  inputType: EmbeddingInputType,
): Promise<number[]> {
  const [embedding] = await createEmbeddings(env, [text], model, inputType);
  if (!embedding) {
    throw new Error('Nvidia embeddings response did not include an embedding vector');
  }

  return embedding;
}

export async function createEmbeddings(
  env: Env,
  texts: string[],
  model: string,
  inputType: EmbeddingInputType,
): Promise<number[][]> {
  ensureNvidiaKey(env);

  const response = await fetch(`${NVIDIA_BASE_URL}/embeddings`, {
    method: 'POST',
    headers: nvidiaHeaders(env),
    body: JSON.stringify({
      model,
      input: texts,
      input_type: inputType,
      encoding_format: 'float',
      truncate: 'END',
    }),
  });

  if (!response.ok) {
    throw new Error(`Nvidia embeddings request failed with ${response.status}`);
  }

  const data = await response.json() as {
    data?: Array<{ embedding?: number[] }>;
  };

  const embeddings = data.data?.map((item) => item.embedding).filter((item): item is number[] => Boolean(item)) ?? [];
  if (embeddings.length !== texts.length) {
    throw new Error('Nvidia embeddings response did not include the expected embedding vectors');
  }

  return embeddings;
}

export async function createChatCompletion(
  env: Env,
  model: string,
  messages: ChatMessage[],
  options?: { maxTokens?: number; temperature?: number },
): Promise<string> {
  ensureNvidiaKey(env);

  const response = await fetch(`${NVIDIA_BASE_URL}/chat/completions`, {
    method: 'POST',
    headers: nvidiaHeaders(env),
    body: JSON.stringify({
      model,
      messages,
      temperature: options?.temperature ?? 0.2,
      max_tokens: options?.maxTokens ?? 220,
    }),
  });

  if (!response.ok) {
    throw new Error(`Nvidia chat request failed with ${response.status}`);
  }

  const data = await response.json() as {
    choices?: Array<{
      message?: {
        content?: string;
      };
    }>;
  };

  const text = data.choices?.[0]?.message?.content?.trim();
  if (!text) {
    throw new Error('Nvidia chat response did not include assistant content');
  }

  return text;
}

function nvidiaHeaders(env: Env): HeadersInit {
  return {
    authorization: `Bearer ${env.NVIDIA_API_KEY}`,
    'content-type': 'application/json',
  };
}

function ensureNvidiaKey(env: Env): void {
  if (!env.NVIDIA_API_KEY) {
    throw new Error('Missing NVIDIA_API_KEY. Set a Worker secret or local .dev.vars entry before using embeddings or chat.');
  }
}
