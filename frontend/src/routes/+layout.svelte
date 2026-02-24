<script>
  import '../app.css';
  import { page } from '$app/state';

  let { children } = $props();
  let sidebarOpen = $state(false);

  const nav = [
    { href: '/', label: 'Overview', icon: 'grid' },
    { href: '/news', label: 'News', icon: 'news' },
    { href: '/kanban', label: 'Kanban', icon: 'kanban' },
    { href: '/actions', label: 'Actions', icon: 'actions' },
    { href: '/projects', label: 'Projects', icon: 'folder' },
    { href: '/settings', label: 'Settings', icon: 'settings' },
  ];

  function isActive(href) {
    if (href === '/') return page.url.pathname === '/';
    return page.url.pathname.startsWith(href);
  }

  function closeSidebar() {
    sidebarOpen = false;
  }
</script>

<div class="flex h-screen overflow-hidden">
  <!-- Mobile menu button -->
  <button 
    onclick={() => sidebarOpen = !sidebarOpen}
    class="md:hidden fixed top-3 left-3 z-50 p-2 bg-zinc-800 rounded-lg text-zinc-400 hover:text-white border border-zinc-700"
  >
    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  </button>

  <!-- Mobile overlay -->
  {#if sidebarOpen}
    <div 
      class="md:hidden fixed inset-0 bg-black/50 z-30"
      onclick={closeSidebar}
      role="button"
      tabindex="0"
      onkeydown={(e) => e.key === 'Escape' && closeSidebar()}
    ></div>
  {/if}

  <!-- Sidebar -->
  <aside 
    class="w-56 flex-shrink-0 border-r border-border bg-surface-1 flex flex-col transition-transform duration-200
           {sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 fixed md:relative h-full z-40"
  >
    <!-- Brand -->
    <div class="px-4 h-14 flex items-center border-b border-border">
      <span class="text-sm font-bold text-white tracking-tight">Gantry</span>
      <span class="ml-2 text-xs text-zinc-500 font-medium">Mission Control</span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-3 py-4 space-y-1">
      {#each nav as item}
        <a 
          href={item.href} 
          class="nav-item" 
          class:active={isActive(item.href)}
          onclick={closeSidebar}
        >
          {#if item.icon === 'grid'}
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path d="M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z" />
            </svg>
          {:else if item.icon === 'folder'}
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
          {:else if item.icon === 'news'}
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
          {:else if item.icon === 'kanban'}
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          {:else if item.icon === 'terminal'}
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path d="M4 17l6-5-6-5M12 19h8" />
            </svg>
          {:else if item.icon === 'settings'}
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path d="M12.22 2h-.44a2 2 0 00-2 2v.18a2 2 0 01-1 1.73l-.43.25a2 2 0 01-2 0l-.15-.08a2 2 0 00-2.73.73l-.22.38a2 2 0 00.73 2.73l.15.1a2 2 0 011 1.72v.51a2 2 0 01-1 1.74l-.15.09a2 2 0 00-.73 2.73l.22.38a2 2 0 002.73.73l.15-.08a2 2 0 012 0l.43.25a2 2 0 011 1.73V20a2 2 0 002 2h.44a2 2 0 002-2v-.18a2 2 0 011-1.73l.43-.25a2 2 0 012 0l.15.08a2 2 0 002.73-.73l.22-.39a2 2 0 00-.73-2.73l-.15-.08a2 2 0 01-1-1.74v-.5a2 2 0 011-1.74l.15-.09a2 2 0 00.73-2.73l-.22-.38a2 2 0 00-2.73-.73l-.15.08a2 2 0 01-2 0l-.43-.25a2 2 0 01-1-1.73V4a2 2 0 00-2-2z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          {/if}
          {item.label}
        </a>
      {/each}
    </nav>

    <!-- Footer -->
    <div class="px-4 py-3 border-t border-border">
      <div class="flex items-center gap-2">
        <span class="status-dot running animate-pulse-subtle"></span>
        <span class="text-xs text-zinc-500">System Online</span>
      </div>
    </div>
  </aside>

  <!-- Main content -->
  <main class="flex-1 overflow-y-auto p-4 md:p-6 pt-16 md:pt-6">
    {@render children()}
  </main>
</div>