<script>
  import { onMount, onDestroy } from 'svelte';

  let logs = $state([]);
  let pollTimer = $state(null);
  let autoScroll = $state(true);
  let logContainer;

  async function fetchLogs() {
    try {
      const res = await fetch('/api/logs');
      if (res.ok) {
        logs = await res.json();
        if (autoScroll && logContainer) {
          requestAnimationFrame(() => {
            logContainer.scrollTop = logContainer.scrollHeight;
          });
        }
      }
    } catch {
      // API not available yet
    }
  }

  onMount(async () => {
    await fetchLogs();
    pollTimer = setInterval(fetchLogs, 5000);
  });

  onDestroy(() => {
    if (pollTimer) clearInterval(pollTimer);
  });

  function levelColor(level) {
    if (level === 'error' || level === 'ERROR') return 'text-red-400';
    if (level === 'warn' || level === 'WARN') return 'text-amber-400';
    if (level === 'info' || level === 'INFO') return 'text-zinc-300';
    return 'text-zinc-500';
  }
</script>

<div class="flex flex-col h-screen">
  <header class="px-4 py-3 border-b border-border flex justify-between items-center">
    <h1 class="text-sm font-semibold text-zinc-100">Logs</h1>
    <label class="flex items-center gap-2 text-xs text-zinc-500 cursor-pointer">
      <input type="checkbox" bind:checked={autoScroll} class="accent-indigo-500" />
      Auto-scroll
    </label>
  </header>

  <div
    bind:this={logContainer}
    class="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-0.5"
  >
    {#if logs.length}
      {#each logs as entry}
        <div class="flex gap-3 py-0.5 border-b border-zinc-900">
          {#if entry.timestamp}
            <span class="text-zinc-600 shrink-0">{new Date(entry.timestamp * 1000).toLocaleTimeString()}</span>
          {/if}
          {#if entry.level}
            <span class="{levelColor(entry.level)} w-12 shrink-0 uppercase">{entry.level}</span>
          {/if}
          <span class="text-zinc-300">{entry.message ?? entry}</span>
        </div>
      {/each}
    {:else}
      <div class="text-zinc-600 mt-8 text-center">
        <p>No log entries available.</p>
        <p class="mt-1 text-zinc-700">Logs will appear here once the Gantry backend emits them.</p>
      </div>
    {/if}
  </div>
</div>
