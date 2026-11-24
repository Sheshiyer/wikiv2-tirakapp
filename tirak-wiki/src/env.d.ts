/// <reference path="../.astro/types.d.ts" />

interface ImportMetaEnv {
  readonly PUBLIC_RAG_API_URL?: string;
  readonly PUBLIC_RAG_APP_ID?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
