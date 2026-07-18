import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';

import {
  APPROVED_DOC_IDS,
  isApprovedDocId,
  isApprovedSourcePath,
} from '../src/lib/approved-docs.mjs';

test('only the current Tirak product contract documents are approved', () => {
  assert.deepEqual(APPROVED_DOC_IDS, [
    '01-introduction/welcome',
    '02-foundation/product-overview',
    '02-foundation/positioning',
    '02-foundation/messaging-framework',
  ]);
});

test('legacy person-first audience and campaign content is not publishable', () => {
  assert.equal(isApprovedDocId('01-introduction/welcome'), true);
  assert.equal(isApprovedDocId('03-audience/companion-persona'), false);
  assert.equal(isApprovedDocId('04-campaign/short-form-hook-generator'), false);
  assert.equal(isApprovedSourcePath('src/content/docs/02-foundation/product-overview.md'), true);
  assert.equal(isApprovedSourcePath('src/content/docs/04-campaign/press-release-copy.md'), false);
});

test('the wiki landing page presents experiences rather than people as the product', async () => {
  const surfaces = await Promise.all([
    '../src/pages/index.astro',
    '../src/layouts/BaseLayout.astro',
    '../src/components/Navigation.tsx',
    '../src/components/WikiAssistant.tsx',
  ].map((file) => readFile(new URL(file, import.meta.url), 'utf8')));
  const home = surfaces.join('\n');

  assert.match(home, /guided experiences in Thailand/i);
  assert.doesNotMatch(home, /companion-first|not a tour\.\s*a vibe|start as a companion|your rates|companion guidance|companion onboarding/i);
});
