<script>
  import { onMount } from 'svelte';

  let topics = $state([]);
  let selectedTopic = $state(null);
  let articles = $state([]);
  let loading = $state(false);

  async function fetchTopics() {
    try {
      const res = await fetch('/api/news');
      if (res.ok) {
        const data = await res.json();
        topics = data.topics || [];
        if (topics.length && !selectedTopic) {
          selectTopic(topics[0].id);
        }
      }
    } catch (e) {
      console.error('Failed to fetch topics', e);
    }
  }

  async function selectTopic(topicId) {
    selectedTopic = topicId;
    loading = true;
    try {
      const res = await fetch(`/api/news/${topicId}`);
      if (res.ok) {
        const data = await res.json();
        articles = data.articles || [];
      }
    } catch (e) {
      console.error('Failed to fetch articles', e);
    } finally {
      loading = false;
    }
  }

  function formatDate(ts) {
    if (!ts) return '';
    return new Date(ts * 1000).toLocaleDateString('nl-NL', { 
      day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' 
    });
  }

  onMount(() => {
    fetchTopics();
  });
</script>

<div class="p-4 md:p-6 space-y-4 md:space-y-6">
  <div>
    <h1 class="text-xl md:text-2xl font-bold text-white">News</h1>
    <p class="text-sm text-zinc-500 mt-1">Stay updated on your topics of interest</p>
  </div>

  <!-- Topic Selector -->
  <div class="flex flex-wrap gap-2">
    {#each topics as topic}
      <button
        onclick={() => selectTopic(topic.id)}
        class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors {selectedTopic === topic.id 
          ? 'bg-indigo-600 text-white' 
          : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200'}"
      >
        {topic.name}
        <span class="ml-1.5 text-xs opacity-70">({topic.count})</span>
      </button>
    {/each}
  </div>

  <!-- Articles -->
  {#if loading}
    <div class="text-center py-12">
      <div class="text-zinc-500">Loading articles...</div>
    </div>
  {:else if articles.length === 0}
    <div class="text-center py-12">
      <div class="text-zinc-500">No articles yet. News fetching is coming soon.</div>
    </div>
  {:else}
    <div class="space-y-3">
      {#each articles as article}
        <a 
          href={article.url} 
          target="_blank" 
          rel="noopener noreferrer"
          class="block card hover:border-indigo-500/50 transition-colors"
        >
          <div class="p-4">
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <h3 class="text-sm font-medium text-zinc-200 line-clamp-2">{article.title}</h3>
                {#if article.summary}
                  <p class="text-xs text-zinc-500 mt-1 line-clamp-2">{article.summary}</p>
                {/if}
                <div class="flex items-center gap-2 mt-2 text-xs text-zinc-600">
                  {#if article.source}
                    <span>{article.source}</span>
                  {/if}
                  {#if article.published}
                    <span>• {article.published}</span>
                  {/if}
                </div>
              </div>
              <span class="text-zinc-600 shrink-0">↗</span>
            </div>
          </div>
        </a>
      {/each}
    </div>
  {/if}
</div>