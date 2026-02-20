<script lang="ts">
	import { onMount } from 'svelte';

	let systemStatus = { cpu: 0, ram: 0 };
	let containers = [];
	let logs = [
		'[BOOT] Gantry Kernel Initialized...',
		'[SYS] Scanning local environment...',
		'[NET] Traefik discovered via reverse proxy.',
		'[AUTH] SSO Handlers active.'
	];

	async function refresh() {
		try {
			// In production these would hit the backend service
			// const res = await fetch('/api/status');
			// systemStatus = await res.json();
		} catch (e) {}
	}

	onMount(() => {
		const interval = setInterval(refresh, 5000);
		return () => clearInterval(interval);
	});
</script>

<div class="grid grid-cols-12 gap-4 h-screen max-h-screen">
	<!-- Top Bar -->
	<header class="col-span-12 terminal-border p-2 mb-2 flex justify-between items-center">
		<div class="font-bold flicker">GANTRY_MISSION_CONTROL v1.0.0</div>
		<div class="text-xs">HOST: homegantry.com | STATUS: <span class="text-green-400">SECURE</span></div>
	</header>

	<!-- Sidebar: Stats -->
	<aside class="col-span-3 terminal-border p-4 flex flex-col gap-4">
		<section>
			<h2 class="border-b border-green-500 mb-2">/usr/bin/top</h2>
			<div class="text-sm">
				<p>CPU: [####------] {systemStatus.cpu}%</p>
				<p>RAM: [######----] {systemStatus.ram}%</p>
			</div>
		</section>

		<section>
			<h2 class="border-b border-green-500 mb-2">/etc/active_nodes</h2>
			<ul class="text-xs list-none p-0">
				<li>• 192.168.6.6 (Primary)</li>
				<li>• 192.168.6.7 (Media)</li>
			</ul>
		</section>
	</aside>

	<!-- Main: Logs/Console -->
	<main class="col-span-9 terminal-border p-4 overflow-hidden relative">
		<h2 class="border-b border-green-500 mb-2">/var/log/gantry.log</h2>
		<div class="text-sm font-mono overflow-y-auto max-h-[70vh]">
			{#each logs as log}
				<p class="mb-1 leading-tight">> {log}</p>
			{/each}
			<p class="animate-pulse">_</p>
		</div>

		<!-- Command Prompt -->
		<div class="absolute bottom-4 left-4 right-4 flex gap-2">
			<span>gantry@home:~$</span>
			<input 
				type="text" 
				class="bg-transparent border-none outline-none text-green-500 w-full" 
				placeholder="awaiting input..."
			/>
		</div>
	</main>
</div>
