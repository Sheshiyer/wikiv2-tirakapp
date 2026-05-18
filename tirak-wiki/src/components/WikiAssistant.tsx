import React, { useMemo, useState } from 'react';
import { Loader2, MessageSquareText, Search, Sparkles, AlertCircle, ArrowUpRight, Stars } from 'lucide-react';
import { cn } from '../lib/utils';

type SourceItem = {
  id: string;
  metadata?: {
    slug?: string;
    title?: string;
  };
};

type ChatResponse = {
  answer?: string;
  retrievedContext?: SourceItem[];
  error?: string;
  gated?: boolean;
  gateReason?: string;
  retryable?: boolean;
  retryHint?: string;
};

type WikiAssistantProps = {
  docSlug: string;
  docTitle: string;
};

const responseModes = [
  { id: 'best', label: 'Best answer', hint: 'More grounded, richer synthesis' },
  { id: 'fast', label: 'Faster answer', hint: 'Quicker, concise response' },
];

const promptSuggestions = [
  'Tell me about Tirak.',
  'Summarize this page for a new partner.',
  'What should a vendor care about most here?',
];

export const WikiAssistant = ({ docSlug, docTitle }: WikiAssistantProps) => {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState('fast');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [submittedQuery, setSubmittedQuery] = useState<string | null>(null);

  const config = useMemo(() => ({
    endpoint: import.meta.env.PUBLIC_RAG_API_URL ?? '',
    appId: import.meta.env.PUBLIC_RAG_APP_ID ?? 'tirak-wiki',
    token: import.meta.env.PUBLIC_RAG_TOKEN ?? '',
  }), []);

  const disabled = !config.endpoint || !config.token || isLoading;

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmed = query.trim();
    if (!trimmed || disabled) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setAnswer(null);
    setSources([]);
    setSubmittedQuery(trimmed);

    try {
      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), 25000);

      const response = await fetch(`${config.endpoint}/v1/chat`, {
        method: 'POST',
        signal: controller.signal,
        headers: {
          'content-type': 'application/json',
          authorization: `Bearer ${config.token}`,
        },
        body: JSON.stringify({
          appId: config.appId,
          query: trimmed,
          responseMode: mode,
          currentPage: {
            slug: docSlug,
            title: docTitle,
          },
        }),
      });

      window.clearTimeout(timeoutId);

      const data = await response.json() as ChatResponse;
      if (!response.ok) {
        throw new Error(data.error ?? 'The assistant could not answer right now.');
      }

      setAnswer(data.answer ?? 'No answer returned.');
      setSources(data.retrievedContext ?? []);
      setError(null);
    } catch (requestError) {
      const message = requestError instanceof DOMException && requestError.name === 'AbortError'
        ? 'I could not get a useful answer in time. Try Faster answer or ask a more focused question.'
        : requestError instanceof Error
          ? requestError.message
          : 'Unknown request error';
      setError(message);
      setAnswer(null);
      setSources([]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex h-full flex-col bg-[radial-gradient(circle_at_top,rgba(155,143,217,0.16),transparent_35%),linear-gradient(180deg,rgba(255,255,255,0.03),rgba(255,255,255,0))] p-4 text-sm text-gray-200 sm:p-6 lg:p-8">
      <div className="grid h-full gap-4 lg:grid-cols-[1.05fr_1.45fr]">
        <div className="flex min-h-[18rem] flex-col rounded-[1.5rem] border border-white/10 bg-white/[0.03] p-5 sm:p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-[#F5A6BF]">
                <Sparkles size={14} />
                Ask Tirak Wiki
              </p>
              <h3 className="mt-3 max-w-sm text-3xl font-semibold leading-tight text-white sm:text-4xl">
                Grounded answers with a more natural chat flow
              </h3>
              <p className="mt-3 max-w-md text-sm leading-6 text-gray-400">
                Ask questions about the current page, get a grounded response, and follow the source trail without leaving the overlay.
              </p>
            </div>
            <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-medium leading-5 text-gray-300">
              {docTitle}
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {promptSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => setQuery(suggestion)}
                className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-left text-xs text-gray-200 transition hover:border-[#F5A6BF]/40 hover:bg-[#F5A6BF]/10 hover:text-white"
              >
                {suggestion}
              </button>
            ))}
          </div>

          <div className="mt-6 grid gap-2 sm:grid-cols-2">
            {responseModes.map((option) => {
              const active = option.id === mode;
              return (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => setMode(option.id)}
                  className={cn(
                    'rounded-2xl border px-4 py-4 text-left transition',
                    active
                      ? 'border-[#F5A6BF]/40 bg-[#F5A6BF]/10 text-white shadow-[0_0_0_1px_rgba(245,166,191,0.12)]'
                      : 'border-white/10 bg-white/[0.03] text-gray-300 hover:border-white/20 hover:bg-white/[0.06]'
                  )}
                >
                  <span className="flex items-center gap-2 text-sm font-semibold">
                    {option.id === 'best' ? <MessageSquareText size={16} /> : <Search size={16} />}
                    {option.label}
                  </span>
                  <span className="mt-2 block text-xs leading-5 text-gray-400">{option.hint}</span>
                </button>
              );
            })}
          </div>

          <div className="mt-auto pt-6">
            <div className="rounded-2xl border border-white/10 bg-[#14141a]/90 p-4 text-xs leading-6 text-gray-400">
              <div className="flex items-center gap-2 text-[#9B8FD9]">
                <Stars size={14} />
                <span className="font-semibold uppercase tracking-[0.18em]">Live context</span>
              </div>
              <p className="mt-2">
                {config.endpoint && config.token
                  ? 'Connected to the configured RAG worker and scoped to the current page context.'
                  : 'Set PUBLIC_RAG_API_URL and PUBLIC_RAG_TOKEN to enable answers.'}
              </p>
            </div>
          </div>
        </div>

        <div className="flex min-h-0 flex-col rounded-[1.5rem] border border-white/10 bg-[#111018]/85">
          <div className="border-b border-white/10 px-5 py-4 sm:px-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gray-400">Conversation</p>
                <p className="mt-1 text-sm text-gray-500">Ask anything about the current doc, product context, or partner guidance.</p>
              </div>
              <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-2 text-xs text-gray-300">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                Ready
              </div>
            </div>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto px-5 py-5 sm:px-6">
            {!submittedQuery && !answer && !error && !isLoading && (
              <div className="rounded-3xl border border-dashed border-white/10 bg-white/[0.02] px-5 py-6 text-sm leading-7 text-gray-400">
                Start with a quick question, use one of the prompt chips, or ask for a summary of what matters on this page.
              </div>
            )}

            {submittedQuery && (
              <div className="ml-auto max-w-2xl rounded-[1.75rem] rounded-br-md bg-[linear-gradient(135deg,#F5A6BF,#9B8FD9)] px-5 py-4 text-sm font-medium leading-7 text-[#140f18] shadow-lg">
                {submittedQuery}
              </div>
            )}

            {isLoading && (
              <div className="max-w-xl rounded-[1.75rem] rounded-bl-md border border-white/10 bg-white/[0.04] px-5 py-4 text-gray-200 shadow-[0_10px_30px_rgba(0,0,0,0.18)]">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-full bg-[#F5A6BF]/10 text-[#F5A6BF]">
                    <Sparkles size={16} />
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-white">Tirak Wiki is thinking</p>
                    <div className="mt-2 flex items-center gap-2">
                      <span className="h-2.5 w-2.5 animate-bounce rounded-full bg-[#F5A6BF] [animation-delay:-0.2s]" />
                      <span className="h-2.5 w-2.5 animate-bounce rounded-full bg-[#9B8FD9] [animation-delay:-0.1s]" />
                      <span className="h-2.5 w-2.5 animate-bounce rounded-full bg-white/80" />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="max-w-xl rounded-[1.75rem] rounded-bl-md border border-rose-400/20 bg-rose-400/10 px-5 py-4 text-sm text-rose-100">
                <p className="flex items-center gap-2 font-semibold">
                  <AlertCircle size={16} />
                  Assistant guidance
                </p>
                <p className="mt-2 leading-7 text-rose-100/90">{error}</p>
                <p className="mt-2 text-xs text-rose-100/70">Try a shorter question, one page section, or the Faster answer mode.</p>
              </div>
            )}

            {answer && (
              <div className="space-y-4">
                <div className="max-w-3xl rounded-[1.75rem] rounded-bl-md border border-white/10 bg-white/[0.04] px-5 py-5 text-gray-100 shadow-[0_10px_30px_rgba(0,0,0,0.18)]">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9B8FD9]">Answer</p>
                  <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-gray-100">{answer}</p>
                </div>

                {sources.length > 0 && (
                  <div className="max-w-3xl rounded-[1.75rem] border border-white/10 bg-[#14141a] px-5 py-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gray-400">Retrieved sources</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {sources.slice(0, 6).map((source) => (
                        <a
                          key={source.id}
                          href={source.metadata?.slug ? `/docs/${source.metadata.slug}` : '#'}
                          className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-xs text-gray-200 transition hover:border-[#F5A6BF]/30 hover:text-white"
                        >
                          <span>{source.metadata?.title ?? source.id}</span>
                          <ArrowUpRight size={12} />
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <form className="border-t border-white/10 px-5 py-5 sm:px-6" onSubmit={handleSubmit}>
            <label className="block">
              <span className="mb-2 block text-xs font-medium uppercase tracking-wide text-gray-400">Question</span>
              <textarea
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                rows={3}
                placeholder="Ask about partner onboarding, messaging, positioning, or any page-specific detail."
                className="w-full rounded-2xl border border-white/10 bg-[#17171d] px-4 py-4 text-sm text-white outline-none transition focus:border-[#9B8FD9]"
              />
            </label>

            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-xs text-gray-500">
                Press ask to send the current question with page-aware context.
              </p>
              <button
                type="submit"
                disabled={disabled || !query.trim()}
                className="inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-[#F5A6BF] to-[#9B8FD9] px-5 py-3 text-sm font-semibold text-[#0f0f13] transition disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                {isLoading ? 'Thinking...' : 'Ask the wiki'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
