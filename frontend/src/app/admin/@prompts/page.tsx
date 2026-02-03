import { Card } from '@/components/ui';
import { fetchPromptLogs } from '@/lib/api';
import { DUMMY_PROMPT_LOGS } from '@/lib/dummyData';

export default async function PromptsSlot() {
  let promptLogs: Array<Record<string, any>> = [];
  let isDummy = false;

  try {
    const data = await fetchPromptLogs(20);
    promptLogs = data?.logs || [];
    if (promptLogs.length === 0) {
      promptLogs = DUMMY_PROMPT_LOGS;
      isDummy = true;
    }
  } catch {
    promptLogs = DUMMY_PROMPT_LOGS;
    isDummy = true;
  }

  return (
    <Card.Root className="p-6">
      <Card.Title className="mb-4">프롬프트 로그</Card.Title>
      {promptLogs.length === 0 ? (
        <p className="text-sm text-[var(--color-muted)]">프롬프트 로그가 없습니다.</p>
      ) : (
        <>
          {promptLogs === DUMMY_PROMPT_LOGS && <p className="text-xs text-[var(--color-muted)] mb-2">(더미 데이터)</p>}
          <div className="space-y-3">
            {promptLogs.map((log, index) => (
              <details key={`${log.history_id}-${index}`} className="border border-[var(--color-border)] rounded-[var(--radius-md)] p-3">
                <summary className="cursor-pointer font-medium text-[var(--color-foreground)]">
                  {log.product_name || 'N/A'} · {log.executed_at || 'N/A'}
                </summary>
                <pre className="text-xs mt-3 bg-[var(--color-secondary)] p-3 rounded-[var(--radius-sm)] overflow-auto">
                  {JSON.stringify(log.prompt_log, null, 2)}
                </pre>
              </details>
            ))}
          </div>
        </>
      )}
    </Card.Root>
  );
}
