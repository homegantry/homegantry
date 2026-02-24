<script>
  import { onMount } from 'svelte';

  let columns = $state([]);
  let loading = $state(true);
  let newCardTitle = $state('');
  let newCardType = $state('feature');

  async function fetchKanban() {
    try {
      const res = await fetch('/api/kanban');
      if (res.ok) {
        const data = await res.json();
        columns = data.columns || [];
      }
    } catch (e) {
      console.error('Failed to fetch kanban', e);
    } finally {
      loading = false;
    }
  }

  function getTypeColor(type) {
    return type === 'feature' ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' 
         : type === 'bug' ? 'bg-red-500/20 text-red-400 border-red-500/30'
         : type === 'g' ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
         : 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30';
  }

  function getSourceLabel(source) {
    return source === 'g' ? 'Gerald' : source === 'ai' ? 'G (AI)' : source;
  }

  function formatDate(ts) {
    return new Date(ts * 1000).toLocaleDateString('nl-NL', { 
      day: 'numeric', month: 'short' 
    });
  }

  onMount(() => {
    fetchKanban();
  });
</script>

<div class="p-4 md:p-6 h-full overflow-x-auto">
  <div class="mb-6">
    <h1 class="text-xl md:text-2xl font-bold text-white">Kanban Board</h1>
    <p class="text-sm text-zinc-500 mt-1">Track features, bugs, and actions</p>
  </div>

  {#if loading}
    <div class="text-center py-12">
      <div class="text-zinc-500">Loading board...</div>
    </div>
  {:else}
    <div class="flex gap-4 min-w-max">
      {#each columns as column}
        <div class="w-72 flex-shrink-0">
          <!-- Column header -->
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-semibold text-zinc-300">{column.name}</h2>
            <span class="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">{column.cards?.length || 0}</span>
          </div>

          <!-- Cards -->
          <div class="space-y-2">
            {#if column.cards?.length}
              {#each column.cards as card}
                <div class="card p-3 hover:border-zinc-600 transition-colors">
                  <div class="flex items-start justify-between gap-2">
                    <div class="flex-1 min-w-0">
                      <div class="text-sm text-zinc-200">{card.title}</div>
                      <div class="flex items-center gap-2 mt-2">
                        <span class="text-xs px-1.5 py-0.5 rounded border {getTypeColor(card.type)}">
                          {card.type}
                        </span>
                        <span class="text-xs text-zinc-600">by {getSourceLabel(card.source)}</span>
                      </div>
                    </div>
                  </div>
                  {#if card.created}
                    <div class="text-xs text-zinc-600 mt-2">{formatDate(card.created)}</div>
                  {/if}
                </div>
              {/each}
            {:else}
              <div class="text-xs text-zinc-600 text-center py-4">No items</div>
            {/if}
          </div>
        </div>
      {/each}
    </div>

    <!-- Legend -->
    <div class="mt-6 pt-4 border-t border-zinc-800">
      <div class="flex flex-wrap gap-4 text-xs">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded bg-indigo-500"></span>
          <span class="text-zinc-500">Feature</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded bg-red-500"></span>
          <span class="text-zinc-500">Bug</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded bg-amber-500"></span>
          <span class="text-zinc-500">Requested by Gerald</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded bg-zinc-500"></span>
          <span class="text-zinc-500">Suggested by AI</span>
        </div>
      </div>
    </div>
  {/if}
</div>