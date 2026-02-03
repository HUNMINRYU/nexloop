import StorageSlugClient from '@/components/StorageSlugClient';
import { storageSlugs } from '@/lib/slugs';

export function generateStaticParams() {
  return storageSlugs.map((slug) => ({ slug }));
}

export default async function StorageSlugPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <StorageSlugClient slug={slug} />;
}
