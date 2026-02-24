<script>
  import { onMount } from 'svelte';

  let services = $state([
    { name: 'Homegantry UI', key: 'homegantry-ui', status: 'unknown', url: 'http://localhost:3000' },
    { name: 'Homegantry API', key: 'homegantry-api', url: 'http://localhost:8000', status: 'unknown' },
    { name: 'Nginx', key: 'homegantry-nginx', url: 'http://localhost:80', status: 'unknown' },
  ]);

  let runningAction = $state(null);

  async function checkServices() {
    for (let s of services) {
      try {
        const res = await fetch(s.url, { method: 'HEAD', mode: 'no-cors' });
        s.status = 'online';
      } catch {
        s.status = 'offline';
      }
    }
    services = [...services];
  }

  async function restartService(serviceKey) {
    runningAction = serviceKey;
    // In production, this would call an API
    await new Promise(r => setTimeout(r, 1000));
    runningAction = null;
    await checkServices();
  }

  onMount(() => {
    checkServices();
  });
</script>

<div class="p-4 md:p-6 space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl md:text-2xl font-bold text-white">Quick Actions</h1>
      <p class="text-sm text-zinc-500 mt-1">One-click controls for your services</p>
    </div>
    <button 
      onclick={checkServices}
      class="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg text-sm"
    >
      Refresh
    </button>
  </div>

  <!-- Service Status -->
  <div class="card">
    <div class="card-header">
      <h2>Service Health</h2>
    </div>
    <div class="card-body space-y-3">
      {#each services as service}
        <div class="flex items-center justify-between py-2 border-b border-zinc-800 last:border-0">
          <div class="flex items-center gap-3">
            <span class="w-2 h-2 rounded-full {service.status === 'online' ? 'bg-green-500' : service.status === 'offline' ? 'bg-red-500' : 'bg-zinc-500'}"></span>
            <span class="text-sm text-zinc-300">{service.name}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-zinc-500 capitalize">{service.status}</span>
            <button
              onclick={() => restartService(service.key)}
              disabled={runningAction === service.key}
              class="px-2 py-1 text-xs bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded transition-colors disabled:opacity-50"
            >
              {runningAction === service.key ? 'Restarting...' : 'Restart'}
            </button>
          </div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Quick Actions Grid -->
  <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
    <button class="card p-4 hover:border-indigo-500/50 transition-colors text-left">
      <div class="text-lg mb-1">🔄</div>
      <div class="text-sm font-medium text-zinc-200">Rebuild UI</div>
      <div class="text-xs text-zinc-500 mt-1">Rebuild and deploy frontend</div>
    </button>
    
    <button class="card p-4 hover:border-indigo-500/50 transition-colors text-left">
      <div class="text-lg mb-1">📦</div>
      <div class="text-sm font-medium text-zinc-200">Backup Data</div>
      <div class="text-xs text-zinc-500 mt-1">Save workspace to GitHub</div>
    </button>
    
    <button class="card p-4 hover:border-indigo-500/50 transition-colors text-left">
      <div class="text-lg mb-1">📊</div>
      <div class="text-sm font-medium text-zinc-200">View Logs</div>
      <div class="text-xs text-zinc-500 mt-1">System log viewer</div>
    </button>
    
    <button class="card p-4 hover:border-indigo-500/50 transition-colors text-left">
      <div class="text-lg mb-1">🔧</div>
      <div class="text-sm font-medium text-zinc-200">Update News</div>
      <div class="text-xs text-zinc-500 mt-1">Fetch latest headlines</div>
    </button>
    
    <button class="card p-4 hover:border-indigo-500/50 transition-colors text-left">
      <div class="text-lg mb-1">🧹</div>
      <div class="text-sm font-medium text-zinc-200">Clear Cache</div>
      <div class="text-xs text-zinc-500 mt-1">Purge cached data</div>
    </button>
    
    <button class="card p-4 hover:border-indigo-500/50 transition-colors text-left">
      <div class="text-lg mb-1">ℹ️</div>
      <div class="text-sm font-medium text-zinc-200">System Info</div>
      <div class="text-xs text-zinc-500 mt-1">View system details</div>
    </button>
  </div>
</div>