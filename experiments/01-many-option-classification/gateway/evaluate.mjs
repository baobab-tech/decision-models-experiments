// Bridge from Jev wire-format requests to Vercel AI Gateway via AI SDK experimental_evaluate.
// stdin: JSONL {id, state, questions}; questions use Jev types (choice, score, noul).
// stdout: JSONL {id, answers, usage, latency_ms, model_id, provider_metadata} or {id, error}.
// Answers come back in Jev shape: noul -> {type: "noul", noul: p}.
//
// Usage: node evaluate.mjs --model typesafe-ai/jev [--only typesafe-ai] [--concurrency 8] < requests.jsonl > responses.jsonl
// --only pins the gateway provider (comma-separated); the provider used is recorded per call.
// Auth: AI_GATEWAY_API_KEY from the repo's .env.

import { experimental_evaluate as evaluate } from 'ai';
import { config } from 'dotenv';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';

config({ path: fileURLToPath(new URL('../../../.env', import.meta.url)), quiet: true });

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, a, i, all) => (a.startsWith('--') ? [...acc, [a.slice(2), all[i + 1]]] : acc), []),
);
const model = args.model;
const concurrency = Number(args.concurrency ?? 8);
const providerOptions = args.only ? { gateway: { only: args.only.split(',') } } : undefined;
if (!model) throw new Error('--model is required, e.g. typesafe-ai/jev or liquid/d1');

const toGateway = (questions) =>
  Object.fromEntries(
    Object.entries(questions).map(([key, q]) => [key, q.type === 'noul' ? { ...q, type: 'boolean' } : q]),
  );

const fromGateway = (answers) =>
  Object.fromEntries(
    Object.entries(answers).map(([key, a]) =>
      [key, a.type === 'boolean' ? { type: 'noul', noul: a.probability } : a]),
  );

async function run(req) {
  const t0 = performance.now();
  try {
    const r = await evaluate({ model, state: req.state, questions: toGateway(req.questions), maxRetries: 4, providerOptions });
    return {
      id: req.id,
      answers: fromGateway(r.answers),
      usage: r.usage,
      latency_ms: Math.round(performance.now() - t0),
      model_id: r.response?.modelId,
      provider: r.providerMetadata?.gateway?.routing?.finalProvider,
      provider_metadata: r.providerMetadata,
    };
  } catch (e) {
    return { id: req.id, error: String(e?.message ?? e).slice(0, 500), latency_ms: Math.round(performance.now() - t0) };
  }
}

const queue = [];
for await (const line of createInterface({ input: process.stdin })) if (line.trim()) queue.push(JSON.parse(line));

let next = 0;
await Promise.all(
  Array.from({ length: Math.min(concurrency, queue.length) }, async () => {
    while (next < queue.length) {
      const res = await run(queue[next++]);
      process.stdout.write(JSON.stringify(res) + '\n');
    }
  }),
);
