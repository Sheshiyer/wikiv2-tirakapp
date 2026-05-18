/// <reference path="../.astro/types.d.ts" />

interface ImportMetaEnv {
  readonly PUBLIC_RAG_API_URL?: string;
  readonly PUBLIC_RAG_APP_ID?: string;
  readonly PUBLIC_RAG_TOKEN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
