/* ==========================================
   THEME TOGGLE - DARK MODE
   ========================================== */

const THEME_KEY = 'vinnuu_theme_preference';
const DARK_MODE_CLASS = 'dark-mode';

/**
 * Initialize theme on page load
 */
function initializeTheme() {
    // Check for saved preference or system preference
    const savedTheme = localStorage.getItem(THEME_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDarkMode = savedTheme === 'dark' || (savedTheme === null && prefersDark);
    
    if (isDarkMode) {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
}

/**
 * Enable dark mode
 */
function enableDarkMode() {
    document.body.classList.add(DARK_MODE_CLASS);
    localStorage.setItem(THEME_KEY, 'dark');
    updateThemeToggleIcon();
}

/**
 * Disable dark mode
 */
function disableDarkMode() {
    document.body.classList.remove(DARK_MODE_CLASS);
    localStorage.setItem(THEME_KEY, 'light');
    updateThemeToggleIcon();
}

/**
 * Toggle between dark and light mode
 */
function toggleTheme() {
    const isDarkMode = document.body.classList.contains(DARK_MODE_CLASS);
    
    if (isDarkMode) {
        disableDarkMode();
    } else {
        enableDarkMode();
    }
}

/**
 * Update theme toggle button icon
 */
function updateThemeToggleIcon() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    const isDarkMode = document.body.classList.contains(DARK_MODE_CLASS);
    const icon = themeToggle.querySelector('.theme-icon');
    
    if (isDarkMode) {
        icon.textContent = '☀️';
        themeToggle.title = 'Switch to Light Mode';
    } else {
        icon.textContent = '🌙';
        themeToggle.title = 'Switch to Dark Mode';
    }
}

/**
 * Listen to system theme changes
 */
if (window.matchMedia) {
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    darkModeQuery.addEventListener('change', (e) => {
        if (!localStorage.getItem(THEME_KEY)) {
            if (e.matches) {
                enableDarkMode();
            } else {
                disableDarkMode();
            }
        }
    });
}

// ==========================================
// Event Listeners
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme
    initializeTheme();
    
    // Add theme toggle listener
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});

// Make toggle function globally available
window.toggleTheme = toggleTheme;
window.isDarkMode = () => document.body.classList.contains(DARK_MODE_CLASS);
