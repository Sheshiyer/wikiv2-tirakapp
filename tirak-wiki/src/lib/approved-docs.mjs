export const APPROVED_DOC_IDS = Object.freeze([
  '01-introduction/welcome',
  '02-foundation/product-overview',
  '02-foundation/positioning',
  '02-foundation/messaging-framework',
]);

const approvedDocIds = new Set(APPROVED_DOC_IDS);

export function isApprovedDocId(id) {
  return approvedDocIds.has(id.replace(/\.(md|mdx)$/i, ''));
}

export function isApprovedSourcePath(sourcePath) {
  const normalized = sourcePath.replaceAll('\\', '/');
  const marker = 'src/content/docs/';
  const markerIndex = normalized.indexOf(marker);

  if (markerIndex === -1) {
    return false;
  }

  return isApprovedDocId(normalized.slice(markerIndex + marker.length));
}
