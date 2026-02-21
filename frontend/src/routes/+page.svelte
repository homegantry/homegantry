<script>
  import { onMount, onDestroy } from 'svelte';

  let status = $state(null);
  let containers = $state([]);
  let coreLogic = $state(null);
  let scheduledOps = $state(null);
  let memory = $state(null);
  let pollTimer = $state(null);
  let tick = $state(0);
  let bootLines = $state([]);
  let booted = $state(false);

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

  function fmtBytes(b) {
    if (b > 1e9) return (b / 1e9).toFixed(1) + ' GB';
    if (b > 1e6) return (b / 1e6).toFixed(1) + ' MB';
    return (b / 1e3).toFixed(0) + ' KB';
  }

  function barClass(pct) {
    if (pct > 90) return 'crit';
    if (pct > 70) return 'warn';
    return '';
  }

  const BOOT_SEQUENCE = [
    '> GANTRY_MISSION_CONTROL v2026.2.21',
    '> Initializing subsystem monitors...',
    '> Connecting to Docker daemon...',
    '> Scanning active OpenClaw sessions...',
    '> Loading architectural memory banks...',
    '> Enumerating scheduled operations...',
    '> All systems nominal. Dashboard ONLINE.',
  ];

  onMount(async () => {
    // Boot sequence animation
    for (let i = 0; i < BOOT_SEQUENCE.length; i++) {
      await new Promise(r => setTimeout(r, 120));
      bootLines = [...bootLines, BOOT_SEQUENCE[i]];
    }
    await new Promise(r => setTimeout(r, 300));
    booted = true;

    await fetchAll();
    pollTimer = setInterval(() => {
      fetchAll();
      tick++;
    }, 5000);
  });

  onDestroy(() => {
    if (pollTimer) clearInterval(pollTimer);
  });
</script>

{#if !booted}
  <!-- BOOT SEQUENCE -->
  <div class="h-screen flex items-center justify-center">
    <div class="text-xs font-mono space-y-1 max-w-lg">
      {#each bootLines as line}
        <div class="text-green-500/80">{line}</div>
      {/each}
      <div class="cursor-blink text-green-400 mt-2"></div>
    </div>
  </div>
{:else}
  <!-- HEADER -->
  <header class="px-3 py-2 border-b border-green-500/50 flex justify-between items-center text-xs">
    <div class="flex items-center gap-3">
      <span class="text-sm font-bold flicker tracking-widest">GANTRY_MISSION_CONTROL</span>
      <span class="text-green-500/30 text-[0.6rem]">v{status?.gantry?.version ?? '...'}</span>
    </div>
    <div class="flex items-center gap-4">
      <span class="text-green-500/40">UPTIME: <span class="text-green-400">{fmtUptime(status?.system?.uptime)}</span></span>
      <span class="text-green-500/40">POLL: <span class="text-green-400">{tick * 5}s</span></span>
      <span class="pulse-dot active"></span>
      <span class="text-green-400 text-[0.6rem]">ONLINE</span>
    </div>
  </header>

  <!-- MAIN GRID -->
  <main class="p-2 grid grid-cols-12 grid-rows-[auto_1fr_1fr] gap-2 h-[calc(100vh-2.5rem)]">

    <!-- ============ ROW 1: SYSTEM VITALS (full width) ============ -->
    <div class="col-span-12 panel p-2">
      <div class="panel-header">
        <span>[ SYSTEM_VITALS ]</span>
        <span class="tag tag-active">LIVE</span>
      </div>
      <div class="grid grid-cols-6 gap-3 p-2 text-xs">
        <!-- CPU -->
        <div>
          <div class="data-label text-[0.6rem]">CPU</div>
          <div class="data-value text-lg">{status?.system?.cpu?.toFixed(1) ?? '--'}%</div>
          <div class="bar-track mt-1">
            <div class="bar-fill {barClass(status?.system?.cpu ?? 0)}" style="width: {status?.system?.cpu ?? 0}%"></div>
          </div>
        </div>
        <!-- RAM -->
        <div>
          <div class="data-label text-[0.6rem]">RAM</div>
          <div class="data-value text-lg">{status?.system?.ram?.toFixed(1) ?? '--'}%</div>
          <div class="bar-track mt-1">
            <div class="bar-fill {barClass(status?.system?.ram ?? 0)}" style="width: {status?.system?.ram ?? 0}%"></div>
          </div>
        </div>
        <!-- DISK -->
        <div>
          <div class="data-label text-[0.6rem]">DISK</div>
          <div class="data-value text-lg">{status?.system?.disk?.toFixed(1) ?? '--'}%</div>
          <div class="bar-track mt-1">
            <div class="bar-fill {barClass(status?.system?.disk ?? 0)}" style="width: {status?.system?.disk ?? 0}%"></div>
          </div>
        </div>
        <!-- LOAD -->
        <div>
          <div class="data-label text-[0.6rem]">LOAD (1/5/15)</div>
          <div class="data-value">{status?.system?.load_avg?.map(l => l.toFixed(2)).join(' / ') ?? '--'}</div>
        </div>
        <!-- NET -->
        <div>
          <div class="data-label text-[0.6rem]">NET TX</div>
          <div class="data-value cyan">{fmtBytes(status?.system?.net_sent ?? 0)}</div>
        </div>
        <div>
          <div class="data-label text-[0.6rem]">NET RX</div>
          <div class="data-value cyan">{fmtBytes(status?.system?.net_recv ?? 0)}</div>
        </div>
      </div>
    </div>

    <!-- ============ ROW 2: LEFT - ACTIVE CORE LOGIC ============ -->
    <div class="col-span-4 panel flex flex-col">
      <div class="panel-header">
        <span>[ ACTIVE_CORE_LOGIC ]</span>
        <span class="tag {coreLogic?.thinking === 'ACTIVE' ? 'tag-active' : 'tag-idle'}">
          {coreLogic?.thinking ?? '...'}
        </span>
      </div>
      <div class="p-2 text-xs flex-1 overflow-y-auto scroll-fade">
        {#if coreLogic?.sessions?.length}
          {#each coreLogic.sessions as session}
            <div class="mb-2 border-b border-green-500/10 pb-2">
              <div class="flex justify-between">
                <span class="data-value text-[0.65rem]">{session.label}</span>
                {#if session.pid}
                  <span class="text-green-500/30 text-[0.55rem]">PID {session.pid}</span>
                {/if}
              </div>
              {#if session.uptime_s}
                <div class="data-label text-[0.55rem]">UPTIME: {fmtUptime(session.uptime_s)}</div>
              {/if}
              {#if session.windows}
                <div class="data-label text-[0.55rem]">WINDOWS: {session.windows}</div>
              {/if}
              {#if session.cmd_hint}
                <div class="text-green-500/30 text-[0.5rem] truncate mt-0.5">{session.cmd_hint}</div>
              {/if}
            </div>
          {/each}
        {:else}
          <div class="text-green-500/30 text-[0.6rem] mt-2">
            > No active OpenClaw sessions detected.<br>
            > Core logic is in standby mode.<br>
            > <span class="cursor-blink"></span>
          </div>
        {/if}
        <div class="mt-2 text-green-500/20 text-[0.5rem]">
          Sessions polled: {coreLogic?.session_count ?? 0} | Last scan: {new Date((coreLogic?.ts ?? 0) * 1000).toLocaleTimeString()}
        </div>
      </div>
    </div>

    <!-- ============ ROW 2: CENTER - CONTAINERS ============ -->
    <div class="col-span-4 panel flex flex-col">
      <div class="panel-header">
        <span>[ DOCKER_FLEET ]</span>
        <span class="tag tag-active">{containers.length} CTR</span>
      </div>
      <div class="p-2 text-xs flex-1 overflow-y-auto scroll-fade">
        {#if containers.length}
          {#each containers as ctr}
            <div class="data-row">
              <span class="truncate flex-1">
                <span class="{ctr.status === 'running' ? 'text-green-400' : 'text-amber-400'} mr-1">
                  {ctr.status === 'running' ? '●' : '○'}
                </span>
                {ctr.name}
              </span>
              <span class="text-green-500/40 text-[0.55rem] ml-2 truncate max-w-[8rem]">{ctr.image}</span>
            </div>
          {/each}
        {:else}
          <div class="text-green-500/30 text-[0.6rem] mt-2">
            > Awaiting Docker daemon connection...<br>
            > <span class="cursor-blink"></span>
          </div>
        {/if}
      </div>
    </div>

    <!-- ============ ROW 2: RIGHT - SCHEDULED OPS ============ -->
    <div class="col-span-4 panel flex flex-col">
      <div class="panel-header">
        <span>[ SCHEDULED_OPERATIONS ]</span>
        <span class="tag tag-active">{scheduledOps?.count ?? 0} JOBS</span>
      </div>
      <div class="p-2 text-xs flex-1 overflow-y-auto scroll-fade">
        {#if scheduledOps?.jobs?.length}
          {#each scheduledOps.jobs as job}
            <div class="data-row">
              <span class="text-[0.55rem] {job.disabled ? 'text-green-500/20 line-through' : ''}">
                <span class="tag text-[0.5rem] mr-1 {job.source === 'systemd' ? 'text-cyan-400' : 'text-green-400'}">{job.source}</span>
                {job.entry}
              </span>
            </div>
          {/each}
        {:else}
          <div class="text-green-500/30 text-[0.6rem] mt-2">
            > No cron jobs or systemd timers detected.<br>
            > Schedule operations via crontab -e<br>
            > or systemd .timer units.<br>
            > <span class="cursor-blink"></span>
          </div>
        {/if}
      </div>
    </div>

    <!-- ============ ROW 3: LEFT - AVAILABLE SERVICES ============ -->
    <div class="col-span-3 panel flex flex-col">
      <div class="panel-header">
        <span>[ SERVICES ]</span>
      </div>
      <div class="p-2 text-xs flex-1">
        <div class="data-row"><span class="data-label">> HOSEGantry.com</span><span class="data-value text-[0.6rem]">UP</span></div>
        <div class="data-row"><span class="data-label">> DECISUM.ai</span><span class="data-value text-[0.6rem]">UP</span></div>
        <div class="data-row"><span class="data-label">> Gantry API</span><span class="data-value text-[0.6rem]">UP</span></div>
      </div>
    </div>

    <!-- ============ ROW 3: RIGHT - ARCHITECTURAL MEMORY ============ -->
    <div class="col-span-9 panel flex flex-col">
      <div class="panel-header">
        <span>[ ARCHITECTURAL_MEMORY ]</span>
        <span class="tag {memory?.exists ? 'tag-active' : 'tag-idle'}">
          {memory?.exists ? `${memory.total_lines} LINES` : 'NO FILE'}
        </span>
      </div>
      <div class="p-2 flex-1 overflow-y-auto scroll-fade">
        {#if memory?.lines?.length}
          {#each memory.lines as line}
            {#if line.startsWith('#')}
              <div class="memory-line heading">{line}</div>
            {:else if line.startsWith('-') || line.startsWith('*')}
              <div class="memory-line text-green-400/70">&nbsp;&nbsp;{line}</div>
            {:else}
              <div class="memory-line">{line}</div>
            {/if}
          {/each}
        {:else}
          <div class="text-green-500/30 text-[0.6rem] mt-2 font-mono">
            > No architectural memories found.<br>
            > Memory banks will populate as sessions accumulate.<br>
            > Path: ~/.claude/projects/.../memory/MEMORY.md<br>
            > <span class="cursor-blink"></span>
          </div>
        {/if}
      </div>
    </div>

  </main>
{/if}
