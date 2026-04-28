function buildNav(role) {
  const nav = document.getElementById('sidebar-nav');
  const currentPath = window.location.pathname;

  const COMMON = [
    { href: '/dashboard/',     icon: 'grid',    label: 'Dashboard' },
    { href: '/reports/',       icon: 'reports', label: 'Reports' },
    { href: '/hierarchy/',     icon: 'sitemap', label: 'Hierarchy' },
    { href: '/notifications/', icon: 'bell',    label: 'Notifications' },
    { href: '/profile/',       icon: 'profile', label: 'My Profile' },
  ];

  const EXEC_EXTRA = [
    { href: '/manager/tasks/',  icon: 'check',  label: 'My Tasks' },
    { href: '/manager/assign/', icon: 'plus',   label: 'Assign Task' },
    { href: '/manager/team/',   icon: 'users',  label: 'Team View' },
    { href: '/team/add/',       icon: 'useradd',label: 'Add to Team' },
  ];

  const navItems = {
    employee: [
      { href: '/dashboard/',     icon: 'grid',    label: 'Dashboard' },
      { href: '/tasks/',         icon: 'check',   label: 'My Tasks' },
      { href: '/reports/',       icon: 'reports', label: 'Reports' },
      { href: '/hierarchy/',     icon: 'sitemap', label: 'Hierarchy' },
      { href: '/notifications/', icon: 'bell',    label: 'Notifications' },
      { href: '/profile/',       icon: 'profile', label: 'My Profile' },
    ],
    manager: [
      { href: '/dashboard/',     icon: 'grid',    label: 'Dashboard' },
      { href: '/manager/tasks/', icon: 'check',   label: 'My Tasks' },
      { href: '/reports/',       icon: 'reports', label: 'Reports' },
      { href: '/manager/assign/',icon: 'plus',    label: 'Assign Task' },
      { href: '/manager/team/',  icon: 'users',   label: 'Team View' },
      { href: '/team/add/',      icon: 'useradd', label: 'Add to Team' },
      { href: '/hierarchy/',     icon: 'sitemap', label: 'Hierarchy' },
      { href: '/notifications/', icon: 'bell',    label: 'Notifications' },
      { href: '/profile/',       icon: 'profile', label: 'My Profile' },
    ],
    // CEO sees everything — all departments report up to them
    ceo: [
      { href: '/dashboard/',     icon: 'grid',    label: 'Dashboard' },
      { href: '/manager/tasks/', icon: 'check',   label: 'My Tasks' },
      { href: '/reports/',       icon: 'reports', label: 'Reports' },
      { href: '/manager/assign/',icon: 'plus',    label: 'Assign Task' },
      { href: '/manager/team/',  icon: 'users',   label: 'Team View' },
      { href: '/team/add/',      icon: 'useradd', label: 'Add to Team' },
      { href: '/hierarchy/',     icon: 'sitemap', label: 'Hierarchy' },
      { href: '/notifications/', icon: 'bell',    label: 'Notifications' },
      { href: '/profile/',       icon: 'profile', label: 'My Profile' },
    ],
    // CFO — Finance & related
    cfo: [
      { href: '/dashboard/',     icon: 'grid',    label: 'Dashboard' },
      { href: '/manager/tasks/', icon: 'check',   label: 'My Tasks' },
      { href: '/reports/',       icon: 'reports', label: 'Reports' },
      { href: '/manager/assign/',icon: 'plus',    label: 'Assign Task' },
      { href: '/manager/team/',  icon: 'users',   label: 'Team View' },
      { href: '/team/add/',      icon: 'useradd', label: 'Add to Team' },
      { href: '/hierarchy/',     icon: 'sitemap', label: 'Hierarchy' },
      { href: '/notifications/', icon: 'bell',    label: 'Notifications' },
      { href: '/profile/',       icon: 'profile', label: 'My Profile' },
    ],
    // CTO — Tech & related
    cto: [
      { href: '/dashboard/',     icon: 'grid',    label: 'Dashboard' },
      { href: '/manager/tasks/', icon: 'check',   label: 'My Tasks' },
      { href: '/reports/',       icon: 'reports', label: 'Reports' },
      { href: '/manager/assign/',icon: 'plus',    label: 'Assign Task' },
      { href: '/manager/team/',  icon: 'users',   label: 'Team View' },
      { href: '/team/add/',      icon: 'useradd', label: 'Add to Team' },
      { href: '/hierarchy/',     icon: 'sitemap', label: 'Hierarchy' },
      { href: '/notifications/', icon: 'bell',    label: 'Notifications' },
      { href: '/profile/',       icon: 'profile', label: 'My Profile' },
    ],
  };

  const icons = {
    grid:    '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>',
    check:   '<path stroke-linecap="round" d="M9 11l3 3L22 4"/><path stroke-linecap="round" d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>',
    clock:   '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    chart:   '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    bell:    '<path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/>',
    plus:    '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
    users:   '<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>',
    useradd: '<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/>',
    sitemap: '<rect x="8" y="1" width="8" height="5" rx="1"/><rect x="1" y="17" width="8" height="5" rx="1"/><rect x="15" y="17" width="8" height="5" rx="1"/><path d="M12 6v4M4.5 17v-4h15v4" stroke-linecap="round"/>',
    reports: '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    profile: '<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  };

  const items = navItems[role] || navItems.employee;
  const currentFull = currentPath + window.location.hash;
  nav.innerHTML = items.map(item => {
    const active = currentFull === item.href ? 'active' : '';
    return `
      <a href="${item.href}" class="nav-item ${active}">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="flex-shrink:0;">
          ${icons[item.icon] || ''}
        </svg>
        <span class="sidebar-label">${item.label}</span>
      </a>
    `;
  }).join('');
}

function enforceRoleRoute(role) {
  const path = window.location.pathname;
  const ELEVATED = ['manager', 'ceo', 'cfo', 'cto'];

  const elevatedOnly = ['/manager/tasks/', '/manager/assign/', '/manager/team/', '/team/add/'];
  const employeeOnly = ['/tasks/'];

  if (!ELEVATED.includes(role) && elevatedOnly.some(p => path.startsWith(p))) {
    window.location.href = '/dashboard/';
  }
  if (role === 'employee' && employeeOnly.includes(path)) {
    // employee is allowed on /tasks/
  }
  if (ELEVATED.includes(role) && path === '/tasks/') {
    window.location.href = '/manager/tasks/';
  }
}

function toggleSidebar() {
  const sidebar  = document.getElementById('sidebar');
  const mainArea = document.getElementById('main-area');
  const isCollapsed = sidebar.style.width === 'var(--sidebar-collapsed-w)';

  if (isCollapsed) {
    sidebar.style.width = 'var(--sidebar-w)';
    mainArea.style.marginLeft = 'var(--sidebar-w)';
    document.getElementById('app-shell').classList.remove('sidebar-collapsed');
  } else {
    sidebar.style.width = 'var(--sidebar-collapsed-w)';
    mainArea.style.marginLeft = 'var(--sidebar-collapsed-w)';
    document.getElementById('app-shell').classList.add('sidebar-collapsed');
  }
}

function closeSidebar() {
  document.getElementById('sidebar-overlay').style.display = 'none';
}

function toggleUserMenu() {
  const menu = document.getElementById('user-menu');
  menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
}

function clearStoredAuthArtifacts() {
  const keys = ['access_token', 'refresh_token', 'token', 'auth_token', 'authToken', 'jwt', 'jwt_access', 'jwt_refresh'];
  keys.forEach(key => {
    localStorage.removeItem(key);
    sessionStorage.removeItem(key);
  });
}

function logout() {
  clearStoredAuthArtifacts();
  fetch('/api/v1/auth/logout/', {
    method: 'POST',
    credentials: 'include',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    cache: 'no-store',
  }).finally(() => {
    window.location.href = '/';
  });
}

async function loadUnreadCount() {
  try {
    const res = await fetch('/api/v1/notifications/unread-count/', { credentials: 'include' });
    if (!res.ok) return;
    const data = await res.json();
    const badge = document.getElementById('notif-badge');
    if (!badge) return;
    if (data.count > 0) {
      badge.textContent = data.count > 99 ? '99+' : data.count;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  } catch(e) { /* silent */ }
}

async function loadUser() {
  try {
    let res = await fetch('/api/v1/auth/me/', { credentials: 'include' });

    if (res.status === 401) {
      const refresh = await fetch('/api/v1/auth/token/refresh/', {
        method: 'POST', credentials: 'include',
      });
      if (!refresh.ok) { window.location.href = '/'; return; }
      res = await fetch('/api/v1/auth/me/', { credentials: 'include' });
    }

    if (!res.ok) { window.location.href = '/'; return; }
    const user = await res.json();

    const parts    = user.full_name.trim().split(' ');
    const initials = parts.map(p => p[0]).join('').slice(0, 2).toUpperCase();

    document.getElementById('topbar-avatar').textContent = initials;
    document.getElementById('topbar-name').textContent   = user.first_name || user.full_name;
    document.getElementById('user-avatar').textContent   = initials;
    document.getElementById('sidebar-name').textContent  = user.full_name;

    // Show role label — uppercase for executives, capitalized for others
    const EXEC_ROLES = ['ceo', 'cfo', 'cto'];
    const roleLabel  = EXEC_ROLES.includes(user.role)
      ? user.role.toUpperCase()
      : user.role.charAt(0).toUpperCase() + user.role.slice(1);
    document.getElementById('sidebar-role').textContent = roleLabel;

    currentRole = user.role;
    buildNav(user.role);
    enforceRoleRoute(user.role);
    loadUnreadCount();

  } catch(e) {
    console.error('User load error:', e);
    const sidebar = document.getElementById('sidebar-name');
    if (sidebar) {
      sidebar.textContent = 'Connection Error';
      sidebar.style.color = '#ef4444';
    }
    setTimeout(() => { window.location.href = '/'; }, 2000);
  }
}

window.addEventListener('hashchange', () => {
  if (typeof switchTab === 'function') {
    switchTab(window.location.hash === '#performance' ? 'performance' : 'tasks');
  }
  if (currentRole) buildNav(currentRole);
});

// Init
loadUser();