export type AppConfig = {
  appId: string;
  displayName: string;
  corpusId: string;
  vectorIndexBinding: string;
  chatModel: string;
  embeddingModel: string;
  searchTopK: number;
  promptId: string;
  authMode: 'bearer' | 'client-key';
  enabled: boolean;
};

export type RagDefaults = {
  defaultChatModel: string;
  defaultEmbeddingModel: string;
  defaultSearchTopK: number;
};

type RagDefaultsRecord = Partial<RagDefaults>;

type AppConfigRecord = Partial<Omit<AppConfig, 'appId'>>;

type AuthRecord = {
  token?: string;
  clientKey?: string;
};

export type Env = {
  APP_CONFIG: KVNamespace;
  APP_INDEX: KVNamespace;
  NVIDIA_API_KEY: string;
  ENVIRONMENT?: string;
};

const DEFAULTS_KEY = 'rag:defaults';

export async function getDefaults(env: Env): Promise<RagDefaults> {
  const raw = await env.APP_CONFIG.get<RagDefaultsRecord>(DEFAULTS_KEY, 'json');

  return {
    defaultChatModel: raw?.defaultChatModel ?? 'meta/llama-3.1-8b-instruct',
    defaultEmbeddingModel: raw?.defaultEmbeddingModel ?? 'nvidia/nv-embedqa-e5-v5',
    defaultSearchTopK: raw?.defaultSearchTopK ?? 6,
  };
}

export async function getAppConfig(env: Env, appId: string): Promise<AppConfig | null> {
  const defaults = await getDefaults(env);
  const raw = await env.APP_CONFIG.get<AppConfigRecord>(`apps:${appId}`, 'json');

  if (!raw) {
    return null;
  }

  return {
    appId,
    displayName: raw.displayName ?? appId,
    corpusId: raw.corpusId ?? appId,
    vectorIndexBinding: raw.vectorIndexBinding ?? 'VECTOR_INDEX',
    chatModel: raw.chatModel ?? defaults.defaultChatModel,
    embeddingModel: raw.embeddingModel ?? defaults.defaultEmbeddingModel,
    searchTopK: raw.searchTopK ?? defaults.defaultSearchTopK,
    promptId: raw.promptId ?? 'default',
    authMode: raw.authMode ?? 'bearer',
    enabled: raw.enabled ?? true,
  };
}

export async function isAuthorizedRequest(env: Env, request: Request, appId: string): Promise<boolean> {
  const config = await getAppConfig(env, appId);
  if (!config || !config.enabled) {
    return false;
  }

  const authHeader = request.headers.get('authorization');
  const clientKey = request.headers.get('x-client-key');
  const stored = await env.APP_CONFIG.get<AuthRecord>(`auth:${appId}`, 'json');

  if (!stored) {
    return false;
  }

  if (config.authMode === 'bearer') {
    return authHeader === `Bearer ${stored.token}`;
  }

  return clientKey === stored.clientKey;
}
