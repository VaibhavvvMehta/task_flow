const loginForm     = document.getElementById('login-form');
const loginBtn      = document.getElementById('login-btn');
const errorBox      = document.getElementById('error-box');
const errorText     = document.getElementById('error-text');
const emailInput    = document.getElementById('email');
const passwordInput = document.getElementById('password');
const toggleBtn     = document.getElementById('toggle-password');

function clearStoredAuthArtifacts() {
  const keys = ['access_token', 'refresh_token', 'token', 'auth_token', 'authToken', 'jwt', 'jwt_access', 'jwt_refresh'];
  keys.forEach((key) => {
    localStorage.removeItem(key);
    sessionStorage.removeItem(key);
  });
}

clearStoredAuthArtifacts();

// Server status check
async function checkServerStatus(evt) {
  const btn = evt && evt.target ? evt.target : null;
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Checking...';
  }

  try {
    const res = await fetch('/api/v1/auth/me/', { credentials: 'include' });
    if (res.ok) {
      errorText.innerHTML = 'Server is responding! Redirecting...';
      setTimeout(() => {
        window.location.href = '/dashboard/';
      }, 1000);
    } else if (res.status === 401) {
      errorText.innerHTML = 'Server is running. Please sign in again.';
    } else {
      errorText.innerHTML = 'Server responded with an error. Please try again.';
    }
  } catch (err) {
    errorText.innerHTML = 'Server is not responding. Please:<br/>1. Check if Docker container is running<br/>2. Check if port 8002 is accessible<br/>3. Wait a moment and try again';
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Check Server Status';
    }
  }
}

// Show/hide password
if (toggleBtn && passwordInput) {
  toggleBtn.addEventListener('click', () => {
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
  });
}

function showFieldError(fieldId, message) {
  const el = document.getElementById(fieldId);
  el.textContent = message;
  el.style.display = 'block';
}

function clearFieldErrors() {
  ['email-error', 'password-error'].forEach(id => {
    const el = document.getElementById(id);
    el.textContent = '';
    el.style.display = 'none';
  });
}

function showError(message) {
  errorText.innerHTML = message;
  errorBox.style.display = 'flex';
}

function hideError() {
  errorBox.style.display = 'none';
}

function setLoading(loading) {
  loginBtn.disabled = loading;
  loginBtn.textContent = loading ? 'Signing in...' : 'Sign in to TaskFlow';
}

function redirectByRole(role) {
  window.location.href = '/dashboard/';
}

function getApiUrl(path) {
  return `${window.location.origin}${path}`;
}


async function handleLoginSubmit(e) {
  e.preventDefault();

  if (!emailInput || !passwordInput || !loginBtn || !errorBox || !errorText) return;

  clearFieldErrors();
  hideError();

  const email    = emailInput.value.trim();
  const password = passwordInput.value.trim();

  let hasError = false;

  if (email === '') {
    showFieldError('email-error', 'Email is required');
    hasError = true;
  }

  if (password === '') {
    showFieldError('password-error', 'Password is required');
    hasError = true;
  }

  if (hasError) return;

  setLoading(true);

  try {
    const response = await fetch(getApiUrl('/api/v1/auth/login/'), {
      method:      'POST',
      credentials: 'include',
      headers:     { 'Content-Type': 'application/json' },
      body:        JSON.stringify({ email, password }),
    });

    if (response.ok) {
      window.location.replace('/dashboard/');
      return;
    }

    const contentType = response.headers.get('content-type') || '';
    const data = contentType.includes('application/json')
      ? await response.json()
      : { error: await response.text() };

    showError(data.error || 'Something went wrong. Please try again.');

  } catch (err) {
    console.error('Login error:', err);

    // If fetch errored but cookie may have been set, probe /me/ to confirm
    try {
      const meRes = await fetch(getApiUrl('/api/v1/auth/me/'), { credentials: 'include' });
      if (meRes.ok) {
        window.location.replace('/dashboard/');
        return;
      }
    } catch (probeErr) {
      console.error('Session probe failed:', probeErr);
    }

    showError('Unable to reach the server. Please check:<br/>1. Server is running<br/>2. Check network connection<br/>3. Try again in a few moments');
  } finally {
    setLoading(false);
  }
}

if (loginForm) {
  loginForm.addEventListener('submit', handleLoginSubmit);
}

// On page load: if already authenticated, skip the login page entirely.
// Using replace() so the login page is never added to the browser history —
// pressing Back from the dashboard won't loop back here.
async function redirectIfAuthenticated() {
  try {
    const res = await fetch('/api/v1/auth/me/', { credentials: 'include' });
    if (res.ok) {
      window.location.replace('/dashboard/');
    }
  } catch (_) {
    // Not logged in or server unreachable — stay on login page
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', redirectIfAuthenticated);
} else {
  redirectIfAuthenticated();
}