<script>
  import { onMount, onDestroy } from 'svelte';

  let weather = $state(null);
  let status = $state(null);
  let memory = $state(null);
  let gatewayStatus = $state(null);
  let openclawStatus = $state(null);
  let pollTimer = $state(null);
  let time = $state(new Date());

  const API = '/api';

  async function fetchAll() {
    const [w, s, m, g, o] = await Promise.allSettled([
      fetch(`${API}/weather`).then(r => r.json()),
      fetch(`${API}/status`).then(r => r.json()),
      fetch(`${API}/memory`).then(r => r.json()),
      fetch(`${API}/gateway-status`).then(r => r.json()),
      fetch(`${API}/openclaw`).then(r => r.json()),
    ]);
    if (w.status === 'fulfilled') weather = w.value;
    if (s.status === 'fulfilled') status = s.value;
    if (m.status === 'fulfilled') memory = m.value;
    if (g.status === 'fulfilled') gatewayStatus = g.value;
    if (o.status === 'fulfilled') openclawStatus = o.value;
  }

  function fmtUptime(seconds) {
    if (!seconds) return '0s';
    const d = Math.floor(seconds / 86400);
    const h = Math.floor((seconds % 86400) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    if (d > 0) return `${d}d ${h}h`;
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
  }

  function fmtTime() {
    return time.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
  }

  function fmtDate() {
    return time.toLocaleDateString('nl-NL', { weekday: 'long', day: 'numeric', month: 'short' });
  }

  onMount(async () => {
    await fetchAll();
    pollTimer = setInterval(() => {
      time = new Date();
      fetchAll();
    }, 30000);
  });

  onDestroy(() => {
    if (pollTimer) clearInterval(pollTimer);
  });
</script>

<div class="p-6 space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-white">Good {time.getHours() < 12 ? 'morning' : time.getHours() < 18 ? 'afternoon' : 'evening'}, Gerald</h1>
      <p class="text-zinc-500 mt-1">{fmtDate()} · {fmtTime()}</p>
    </div>
    <div class="flex items-center gap-2">
      <span class="status-dot {gatewayStatus?.reachable ? 'running' : 'stopped'}"></span>
      <span class="text-sm text-zinc-400">{gatewayStatus?.reachable ? 'Gateway Online' : 'Gateway Offline'}</span>
    </div>
  </div>

  <!-- Top row: Weather + System -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Weather -->
    <div class="card bg-gradient-to-br from-indigo-500/10 to-zinc-800/50">
      <div class="card-header">
        <h2>Amsterdam</h2>
        <span class="text-2xl">🌧️</span>
      </div>
      <div class="card-body">
        {#if weather}
          <div class="text-4xl font-bold text-white">{weather.temp_C}°</div>
          <div class="text-sm text-zinc-400 mt-1">{weather.condition}</div>
          <div class="text-xs text-zinc-500 mt-2">Feels {weather.feels_C}° · {weather.wind_kmh}km/h wind</div>
        {:else}
          <div class="text-zinc-500">Loading...</div>
        {/if}
      </div>
    </div>

    <!-- CPU -->
    <div class="card">
      <div class="card-header">
        <h2>CPU</h2>
        <span class="text-xs text-zinc-500">Host</span>
      </div>
      <div class="card-body">
        {#if status}
          <div class="text-4xl font-bold text-white">{status.system.cpu}%</div>
          <div class="text-xs text-zinc-500 mt-2">Load: {status.system.load_avg?.[0]?.toFixed(2)}</div>
        {:else}
          <div class="text-zinc-500">Loading...</div>
        {/if}
      </div>
    </div>

    <!-- RAM -->
    <div class="card">
      <div class="card-header">
        <h2>RAM</h2>
        <span class="text-xs text-zinc-500">Host</span>
      </div>
      <div class="card-body">
        {#if status}
          <div class="text-4xl font-bold text-white">{status.system.ram}%</div>
          <div class="w-full bg-zinc-700 h-1.5 mt-3 rounded-full overflow-hidden">
            <div class="bg-indigo-500 h-full rounded-full" style="width: {status.system.ram}%"></div>
          </div>
        {:else}
          <div class="text-zinc-500">Loading...</div>
        {/if}
      </div>
    </div>

    <!-- Uptime -->
    <div class="card">
      <div class="card-header">
        <h2>Uptime</h2>
        <span class="text-xs text-zinc-500">Host</span>
      </div>
      <div class="card-body">
        {#if status}
          <div class="text-4xl font-bold text-white">{fmtUptime(status.system.uptime)}</div>
          <div class="text-xs text-zinc-500 mt-2">Since {new Date(Date.now() - status.system.uptime * 1000).toLocaleDateString('nl-NL')}</div>
        {:else}
          <div class="text-zinc-500">Loading...</div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Second row: Memory + Quick Actions -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
    <!-- G's Memory -->
    <div class="card lg:col-span-2">
      <div class="card-header">
        <h2>What's on my mind</h2>
        <span class="text-xs text-zinc-500">From memory</span>
      </div>
      <div class="card-body max-h-64 overflow-y-auto">
        {#if memory?.lines?.length}
          <div class="space-y-2">
            {#each memory.lines.slice(0, 15) as line}
              {#if line.startsWith('#')}
                <div class="text-lg font-semibold text-indigo-400 mt-4 first:mt-0">{line.replace(/^#+\s*/, '')}</div>
              {:else if line.startsWith('-')}
                <div class="text-zinc-300 text-sm">• {line.replace(/^-\s*/, '')}</div>
              {:else if line.includes(':')}
                <div class="text-zinc-400 text-sm"><span class="text-zinc-500">{line.split(':')[0]}:</span> {line.split(':').slice(1).join(':')}</div>
              {:else}
                <div class="text-zinc-300 text-sm">{line}</div>
              {/if}
            {/each}
          </div>
        {:else}
          <p class="text-zinc-500 text-sm">No memories yet. Building them as we go.</p>
        {/if}
      </div>
    </div>

    <!-- Quick Links -->
    <div class="card">
      <div class="card-header">
        <h2>Quick Actions</h2>
      </div>
      <div class="card-body space-y-2">
        <a href="/projects" class="flex items-center gap-3 p-2 rounded-lg hover:bg-zinc-800 transition-colors">
          <span class="text-lg">📁</span>
          <span class="text-sm text-zinc-300">Projects</span>
        </a>
        <a href="/logs" class="flex items-center gap-3 p-2 rounded-lg hover:bg-zinc-800 transition-colors">
          <span class="text-lg">📋</span>
          <span class="text-sm text-zinc-300">System Logs</span>
        </a>
        <a href="/settings" class="flex items-center gap-3 p-2 rounded-lg hover:bg-zinc-800 transition-colors">
          <span class="text-lg">⚙️</span>
          <span class="text-sm text-zinc-300">Settings</span>
        </a>
      </div>
    </div>
  </div>

  <!-- System Info -->
  <div class="card">
    <div class="card-header">
      <h2>System</h2>
    </div>
    <div class="card-body">
      {#if status}
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span class="text-zinc-500">Disk</span>
            <div class="text-zinc-200 font-medium">{status.system.disk}% used</div>
          </div>
          <div>
            <span class="text-zinc-500">Network Sent</span>
            <div class="text-zinc-200 font-medium">{(status.system.net_sent / 1024 / 1024).toFixed(1)} MB</div>
          </div>
          <div>
            <span class="text-zinc-500">Network Recv</span>
            <div class="text-zinc-200 font-medium">{(status.system.net_recv / 1024 / 1024).toFixed(1)} MB</div>
          </div>
          <div>
            <span class="text-zinc-500">Gantry Version</span>
            <div class="text-zinc-200 font-medium">{status.gantry.version}</div>
          </div>
          {#if openclawStatus}
            <div>
              <span class="text-zinc-500">OpenClaw</span>
              <div class="text-zinc-200 font-medium">{openclawStatus.gateway_reachable ? '🟢 Online' : '🔴 Offline'}</div>
            </div>
          {/if}
        </div>
      {:else}
        <div class="text-zinc-500">Loading system info...</div>
      {/if}
    </div>
  </div>
</div>