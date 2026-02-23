<script>
  import { onMount, onDestroy } from 'svelte';

  let status = $state(null);
  let containers = $state([]);
  let coreLogic = $state(null);
  let scheduledOps = $state(null);
  let memory = $state(null);
  let gatewayStatus = $state(null);
  let pollTimer = $state(null);

  const API = '/api';

  async function fetchAll() {
    const endpoints = [
      ['status', `${API}/status`],
      ['containers', `${API}/containers`],
      ['coreLogic', `${API}/core-logic`],
      ['scheduledOps', `${API}/scheduled-ops`],
      ['memory', `${API}/memory`],
    ];
    const results = await Promise.allSettled(
      endpoints.map(([, url]) => fetch(url).then(r => r.json()))
    );
    if (results[0].status === 'fulfilled') status = results[0].value;
    if (results[1].status === 'fulfilled') containers = Array.isArray(results[1].value) ? results[1].value : [];
    if (results[2].status === 'fulfilled') coreLogic = results[2].value;
    if (results[3].status === 'fulfilled') scheduledOps = results[3].value;
    if (results[4].status === 'fulfilled') memory = results[4].value;
  }

  function fmtUptime(seconds) {
    if (!seconds) return '0s';
    const d = Math.floor(seconds / 86400);
    const h = Math.floor((seconds % 86400) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    if (d > 0) return `${d}d ${h}h ${m}m`;
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
  }

  onMount(async () => {
    await fetchAll();
    pollTimer = setInterval(fetchAll, 5000);
  });

  onDestroy(() => {
    if (pollTimer) clearInterval(pollTimer);
  });
</script>

<div class="p-6 space-y-6">
  <!-- Page header -->
  <div>
    <h1 class="text-lg font-semibold text-white">Overview</h1>
    <p class="text-sm text-zinc-500 mt-0.5">System status and active workloads</p>
  </div>

  <!-- Top row: Active Sessions + Docker Fleet -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">

    <!-- Active Sessions -->
    <div class="card">
      <div class="card-header">
        <h2>Active Sessions</h2>
        <span class="badge {coreLogic?.thinking === 'ACTIVE' ? 'badge-active' : 'badge-idle'}">
          {coreLogic?.thinking ?? 'Loading'}
        </span>
      </div>
      <div class="card-body">
        {#if coreLogic?.sessions?.length}
          {#each coreLogic.sessions as session}
            <div class="list-row">
              <span class="status-dot {session.pid ? 'running' : 'stopped'}"></span>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-zinc-200 truncate">{session.label}</div>
                <div class="text-xs text-zinc-500 mt-0.5 flex gap-3">
                  {#if session.uptime_s}
                    <span>Uptime: {fmtUptime(session.uptime_s)}</span>
                  {/if}
                  {#if session.windows}
                    <span>{session.windows} windows</span>
                  {/if}
                  {#if session.pid}
                    <span>PID {session.pid}</span>
                  {/if}
                </div>
              </div>
            </div>
          {/each}
        {:else}
          <p class="text-sm text-zinc-500 py-4">No active sessions detected.</p>
        {/if}
      </div>
    </div>

    <!-- Docker Fleet -->
    <div class="card">
      <div class="card-header">
        <h2>Docker Fleet</h2>
        <span class="badge badge-count">{containers.length} containers</span>
      </div>
      <div class="card-body">
        {#if containers.length}
          {#each containers as ctr}
            <div class="list-row">
              <span class="status-dot {ctr.status === 'running' ? 'running' : 'stopped'}"></span>
              <span class="flex-1 text-sm text-zinc-200 truncate">{ctr.name}</span>
              <span class="text-xs text-zinc-500 truncate max-w-[10rem]">{ctr.image}</span>
            </div>
          {/each}
        {:else}
          <p class="text-sm text-zinc-500 py-4">Waiting for Docker daemon...</p>
        {/if}
      </div>
    </div>
  </div>

  <!-- Second row: Scheduled Operations -->
  <div class="card">
    <div class="card-header">
      <h2>Scheduled Operations</h2>
      <span class="badge badge-count">{scheduledOps?.count ?? 0} jobs</span>
    </div>
    <div class="card-body">
      {#if scheduledOps?.jobs?.length}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6">
          {#each scheduledOps.jobs as job}
            <div class="list-row {job.disabled ? 'opacity-40' : ''}">
              <span class="text-xs font-medium px-1.5 py-0.5 rounded {job.source === 'systemd' ? 'bg-indigo-500/10 text-indigo-400' : 'bg-zinc-500/10 text-zinc-400'}">
                {job.source}
              </span>
              <span class="flex-1 text-sm text-zinc-300 truncate {job.disabled ? 'line-through' : ''}">{job.entry}</span>
            </div>
          {/each}
        </div>
      {:else}
        <p class="text-sm text-zinc-500 py-4">No scheduled jobs detected.</p>
      {/if}
    </div>
  </div>

  <!-- Third row: Architectural Memory -->
  <div class="card">
    <div class="card-header">
      <h2>Architectural Memory</h2>
      <span class="badge {memory?.exists ? 'badge-active' : 'badge-idle'}">
        {memory?.exists ? `${memory.total_lines} lines` : 'No file'}
      </span>
    </div>
    <div class="card-body max-h-80 overflow-y-auto">
      {#if memory?.lines?.length}
        {#each memory.lines as line}
          {#if line.startsWith('#')}
            <div class="memory-line heading">{line.replace(/^#+\s*/, '')}</div>
          {:else if line.startsWith('-') || line.startsWith('*')}
            <div class="memory-line bullet">{line}</div>
          {:else}
            <div class="memory-line">{line}</div>
          {/if}
        {/each}
      {:else}
        <p class="text-sm text-zinc-500 py-4">No architectural memories found. Memory banks will populate as sessions accumulate.</p>
      {/if}
    </div>
  </div>
</div>
