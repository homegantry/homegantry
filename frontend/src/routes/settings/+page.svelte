<script>
  import { onMount } from 'svelte';

  let saving = $state(false);
  let saved = $state(false);

  let settings = $state({
    theme: 'dark',
    newsTopics: ['dutch-politics', 'ai-news'],
    refreshInterval: 30,
    telegramEnabled: true,
  });

  const themes = [
    { value: 'dark', label: 'Dark' },
    { value: 'light', label: 'Light' },
    { value: 'auto', label: 'Auto' },
  ];

  const topics = [
    { value: 'dutch-politics', label: 'Dutch Politics' },
    { value: 'ai-news', label: 'AI News' },
  ];

  async function saveSettings() {
    saving = true;
    // In production, this would POST to an API
    await new Promise(r => setTimeout(r, 500));
    saving = false;
    saved = true;
    setTimeout(() => saved = false, 2000);
  }

  onMount(() => {
    // Load settings from API if available
  });
</script>

<div class="p-4 md:p-6 space-y-6 max-w-2xl">
  <div>
    <h1 class="text-xl md:text-2xl font-bold text-white">Settings</h1>
    <p class="text-sm text-zinc-500 mt-1">Configure your dashboard</p>
  </div>

  <!-- Theme -->
  <div class="card">
    <div class="card-header">
      <h2>Appearance</h2>
    </div>
    <div class="card-body space-y-4">
      <div>
        <label class="text-sm text-zinc-400 block mb-2">Theme</label>
        <select bind:value={settings.theme} class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-zinc-200">
          {#each themes as t}
            <option value={t.value}>{t.label}</option>
          {/each}
        </select>
      </div>
    </div>
  </div>

  <!-- News -->
  <div class="card">
    <div class="card-header">
      <h2>News</h2>
    </div>
    <div class="card-body space-y-4">
      <div>
        <label class="text-sm text-zinc-400 block mb-2">Topics</label>
        <div class="space-y-2">
          {#each topics as t}
            <label class="flex items-center gap-3 cursor-pointer">
              <input 
                type="checkbox" 
                checked={settings.newsTopics.includes(t.value)}
                onchange={(e) => {
                  if (e.target.checked) {
                    settings.newsTopics = [...settings.newsTopics, t.value];
                  } else {
                    settings.newsTopics = settings.newsTopics.filter(x => x !== t.value);
                  }
                }}
                class="w-4 h-4 rounded bg-zinc-800 border-zinc-700 text-indigo-500"
              />
              <span class="text-sm text-zinc-300">{t.label}</span>
            </label>
          {/each}
        </div>
      </div>
    </div>
  </div>

  <!-- Refresh -->
  <div class="card">
    <div class="card-header">
      <h2>Data</h2>
    </div>
    <div class="card-body space-y-4">
      <div>
        <label class="text-sm text-zinc-400 block mb-2">Auto-refresh interval (seconds)</label>
        <input 
          type="number" 
          bind:value={settings.refreshInterval}
          min="10"
          max="300"
          class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-zinc-200"
        />
      </div>
    </div>
  </div>

  <!-- Notifications -->
  <div class="card">
    <div class="card-header">
      <h2>Notifications</h2>
    </div>
    <div class="card-body space-y-4">
      <label class="flex items-center justify-between cursor-pointer">
        <span class="text-sm text-zinc-300">Telegram alerts</span>
        <input 
          type="checkbox" 
          bind:checked={settings.telegramEnabled}
          class="w-4 h-4 rounded bg-zinc-800 border-zinc-700 text-indigo-500"
        />
      </label>
    </div>
  </div>

  <!-- Save -->
  <div class="flex items-center gap-4">
    <button 
      onclick={saveSettings}
      disabled={saving}
      class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-800 text-white rounded-lg text-sm font-medium transition-colors"
    >
      {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Settings'}
    </button>
    {#if saved}
      <span class="text-sm text-green-400">Settings saved successfully</span>
    {/if}
  </div>
</div>