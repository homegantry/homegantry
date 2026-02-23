<script>
  import { onMount, onDestroy } from 'svelte';

  let pollTimer = $state(null);
  let gatewayStatus = $state(null);

  const projects = [
    {
      name: 'decisum.ai',
      description: 'AI-powered decision intelligence platform',
      status: 'active',
    },
  ];

  async function fetchGateway() {
    try {
      const res = await fetch('/api/gateway-status');
      if (res.ok) gatewayStatus = await res.json();
    } catch {
      // API not available
    }
  }

  onMount(async () => {
    await fetchGateway();
    pollTimer = setInterval(fetchGateway, 15000);
  });

  onDestroy(() => {
    if (pollTimer) clearInterval(pollTimer);
  });
</script>

<div class="p-6 space-y-6">
  <div>
    <h1 class="text-lg font-semibold text-white">Projects</h1>
    <p class="text-sm text-zinc-500 mt-0.5">Track deployments and milestones across your projects</p>
  </div>

  {#each projects as project}
    <div class="space-y-4">
      <!-- Project Header -->
      <div class="card">
        <div class="card-header">
          <div class="flex items-center gap-3">
            <h2>{project.name}</h2>
            <span class="badge badge-active">Active</span>
          </div>
        </div>
        <div class="card-body">
          <p class="text-sm text-zinc-400">{project.description}</p>
        </div>
      </div>

      <!-- Project Detail Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

        <!-- Build Status -->
        <div class="card">
          <div class="card-header">
            <h2>Build Status</h2>
          </div>
          <div class="card-body space-y-3">
            <div class="flex items-center gap-2">
              <span class="status-dot running"></span>
              <span class="text-sm text-zinc-200">Passing</span>
            </div>
            <div class="text-xs text-zinc-500 space-y-1">
              <div class="flex justify-between">
                <span>Branch</span>
                <span class="text-zinc-400">main</span>
              </div>
              <div class="flex justify-between">
                <span>Last Build</span>
                <span class="text-zinc-400">Awaiting CI integration</span>
              </div>
              <div class="flex justify-between">
                <span>Duration</span>
                <span class="text-zinc-400">--</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Last Deployment -->
        <div class="card">
          <div class="card-header">
            <h2>Last Deployment</h2>
          </div>
          <div class="card-body space-y-3">
            <div class="flex items-center gap-2">
              <span class="status-dot running"></span>
              <span class="text-sm text-zinc-200">Live</span>
            </div>
            <div class="text-xs text-zinc-500 space-y-1">
              <div class="flex justify-between">
                <span>Environment</span>
                <span class="text-zinc-400">Production</span>
              </div>
              <div class="flex justify-between">
                <span>Deployed</span>
                <span class="text-zinc-400">Awaiting CD integration</span>
              </div>
              <div class="flex justify-between">
                <span>Commit</span>
                <span class="text-zinc-400 font-mono">------</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Milestones -->
        <div class="card">
          <div class="card-header">
            <h2>Upcoming Milestones</h2>
          </div>
          <div class="card-body">
            <div class="space-y-2">
              <div class="list-row">
                <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0"></span>
                <div class="flex-1 min-w-0">
                  <div class="text-sm text-zinc-200">MVP Launch</div>
                  <div class="text-xs text-zinc-500">Target: Q1 2026</div>
                </div>
              </div>
              <div class="list-row">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0"></span>
                <div class="flex-1 min-w-0">
                  <div class="text-sm text-zinc-200">Beta Testing</div>
                  <div class="text-xs text-zinc-500">Target: Q2 2026</div>
                </div>
              </div>
              <div class="list-row">
                <span class="w-1.5 h-1.5 rounded-full bg-zinc-600 shrink-0"></span>
                <div class="flex-1 min-w-0">
                  <div class="text-sm text-zinc-200">Public Release</div>
                  <div class="text-xs text-zinc-500">Target: Q3 2026</div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  {/each}
</div>
