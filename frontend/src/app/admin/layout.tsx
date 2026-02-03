import { Navbar } from '@/features/landing';

export default function AdminLayout({
  children,
  cache,
  gcs,
  prompts,
  notion,
}: {
  children: React.ReactNode;
  cache: React.ReactNode;
  gcs: React.ReactNode;
  prompts: React.ReactNode;
  notion: React.ReactNode;
}) {
  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--color-background)] p-8 pt-24">
        <div className="max-w-6xl mx-auto space-y-8">
          {children}
          <div className="grid gap-8">
            {cache}
            {gcs}
            {prompts}
            {notion}
          </div>
        </div>
      </main>
    </>
  );
}
