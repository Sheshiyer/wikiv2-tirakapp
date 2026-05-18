declare namespace Cloudflare {
  interface Env {
    APP_CONFIG: KVNamespace;
    APP_INDEX: KVNamespace;
    NVIDIA_API_KEY: string;
    ENVIRONMENT?: string;
  }
}

interface Env extends Cloudflare.Env {}
