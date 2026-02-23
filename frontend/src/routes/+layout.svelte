<script>
  import '../app.css';
  import { page } from '$app/state';

  let { children } = $props();

  const nav = [
    { href: '/', label: 'Overview', icon: 'grid' },
    { href: '/projects', label: 'Projects', icon: 'folder' },
    { href: '/logs', label: 'Logs', icon: 'terminal' },
    { href: '/settings', label: 'Settings', icon: 'settings' },
  ];

  function isActive(href) {
    if (href === '/') return page.url.pathname === '/';
    return page.url.pathname.startsWith(href);
  }
</script>

<div class="flex h-screen overflow-hidden">
  <!-- Sidebar -->
  <aside class="w-56 flex-shrink-0 border-r border-border bg-surface-1 flex flex-col">
    <!-- Brand -->
    <div class="px-4 h-14 flex items-center border-b border-border">
      <span class="text-sm font-bold text-white tracking-tight">Gantry</span>
      <span class="ml-2 text-xs text-zinc-500 font-medium">Mission Control</span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-3 py-4 space-y-1">
      {#each nav as item}
        <a href={item.href} class="nav-item" class:active={isActive(item.href)}>
          {#if item.icon === 'grid'}
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path d="M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z" />
            </svg>
          {:else if item.icon === 'folder'}
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
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
  <main class="flex-1 overflow-y-auto">
    {@render children()}
  </main>
</div>
