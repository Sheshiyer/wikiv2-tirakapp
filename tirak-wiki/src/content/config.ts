import { defineCollection, z } from 'astro:content';

const docs = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    category: z.enum([
      'introduction',
      'foundation',
      'audience',
      'campaign',
      'resources',
      'vendor-pipeline',
      'vendor-onboarding',
      'vendor-directory',
      'partner-resources',
    ]).optional(),
    order: z.number().optional(),
    icon: z.string().optional(),
    tags: z.array(z.string()).optional(),
    lastUpdated: z.date().optional(),
    cta_text: z.string().optional(),
    cta_url: z.string().optional(),
    downloadable: z.boolean().optional(),
  }),
});

export const collections = { docs };
