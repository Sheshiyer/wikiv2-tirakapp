import { defineCollection, z } from 'astro:content';

const docs = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    category: z.enum(['introduction', 'foundation', 'audience', 'campaign', 'resources']).optional(),
    order: z.number().optional(),
    icon: z.string().optional(), // Lucide icon name
    tags: z.array(z.string()).optional(),
    lastUpdated: z.date().optional(),
  }),
});

export const collections = { docs };
