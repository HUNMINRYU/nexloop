import { Card } from '@/components/ui';

export default function Loading() {
  return (
    <Card.Root className="p-6 animate-pulse">
      <div className="h-6 bg-slate-100 rounded w-1/4 mb-4" />
      <div className="space-y-3">
        <div className="h-4 bg-slate-100 rounded w-full" />
        <div className="h-4 bg-slate-100 rounded w-5/6" />
      </div>
    </Card.Root>
  );
}
