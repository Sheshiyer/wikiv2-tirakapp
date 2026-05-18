export type WikiDocument = {
  slug: string;
  title: string;
  description: string;
  category: string;
  sourcePath: string;
  content: string;
};

export type CorpusFile = {
  generatedAt: string;
  docs: WikiDocument[];
};

export type ChunkRecord = {
  id: string;
  appId: string;
  slug: string;
  title: string;
  category: string;
  sourcePath: string;
  chunkIndex: number;
  text: string;
  embedding: number[];
};
