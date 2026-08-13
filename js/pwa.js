// pwa.js – PWA registration, install prompt, and online/offline indicators

(function() {
    'use strict';

    // ---------- STATE ----------
    let deferredPrompt = null;
    let isAppInstalled = false;

    // ---------- SERVICE WORKER REGISTRATION ----------
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(function(reg) {
                    console.log('[PWA] Service Worker registered:', reg.scope);

                    reg.addEventListener('updatefound', function() {
                        const newWorker = reg.installing;
                        if (newWorker) {
                            console.log('[PWA] New service worker installing...');
                            newWorker.addEventListener('statechange', function() {
                                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                    console.log('[PWA] Update available - refreshing');
                                    window.location.reload();
                                }
                            });
                        }
                    });
                })
                .catch(function(err) {
                    console.warn('[PWA] Service Worker registration failed:', err);
                });
        });
    }

    // ---------- INSTALL PROMPT ----------
    window.addEventListener('beforeinstallprompt', function(e) {
        e.preventDefault();
        deferredPrompt = e;
        console.log('[PWA] beforeinstallprompt fired! Showing install UI.');
        showInstallBar();
    });

    window.addEventListener('appinstalled', function() {
        console.log('[PWA] App installed successfully');
        isAppInstalled = true;
        hideInstallButton();
        hideInstallBar();
        deferredPrompt = null;
    });

    // ---------- INSTALL BUTTON (always visible in bottom-right) ----------
    function ensureInstallButton() {
        if (isAppInstalled) return;
        if (sessionStorage.getItem('pwa_install_dismissed') === 'true') return;
        if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
            isAppInstalled = true;
            return;
        }

        let floatingBtn = document.getElementById('pwa-floating-install-btn');
        if (floatingBtn) return;

        floatingBtn = document.createElement('button');
        floatingBtn.id = 'pwa-floating-install-btn';
        floatingBtn.innerHTML = '⬇️ Install App';
        floatingBtn.style.cssText =
            'position: fixed; bottom: 20px; right: 20px; z-index: 9998;' +
            'background: #28a745; color: white; border: none; padding: 12px 20px;' +
            'border-radius: 50px; font-size: 15px; font-weight: bold; cursor: pointer;' +
            'box-shadow: 0 4px 12px rgba(0,0,0,0.3); font-family: "Segoe UI", sans-serif;';

        floatingBtn.addEventListener('click', function() {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then(function(choiceResult) {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('[PWA] User accepted the install prompt');
                    } else {
                        console.log('[PWA] User dismissed the install prompt');
                    }
                    deferredPrompt = null;
                });
            } else {
                showInstallInstructions();
            }
        });

        document.body.appendChild(floatingBtn);
        console.log('[PWA] Floating install button added');
    }

    function hideInstallButton() {
        const btn = document.getElementById('pwa-floating-install-btn');
        if (btn) btn.remove();
    }

    // ---------- INSTALL BAR (bottom banner) ----------
    function showInstallBar() {
        if (sessionStorage.getItem('pwa_install_dismissed') === 'true') return;
        if (isAppInstalled) return;
        if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
            isAppInstalled = true;
            return;
        }

        let container = document.getElementById('pwa-install-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'pwa-install-container';
            container.style.cssText =
                'position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);' +
                'background: #343a40; color: white; padding: 15px 20px; border-radius: 8px;' +
                'box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 9999; display: flex;' +
                'align-items: center; gap: 15px; max-width: 90%; font-family: "Segoe UI", sans-serif;';

            const text = document.createElement('div');
            text.textContent = '📱 Install Smart Inventory on your device for faster access';
            text.style.fontSize = '14px';

            const btn = document.createElement('button');
            btn.id = 'pwa-install-btn';
            btn.textContent = 'Install';
            btn.style.cssText =
                'background: #28a745; border: none; color: white; padding: 8px 16px;' +
                'border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 14px;';

            const closeBtn = document.createElement('button');
            closeBtn.textContent = '✕';
            closeBtn.style.cssText =
                'background: transparent; border: none; color: #aaa; cursor: pointer;' +
                'font-size: 16px; padding: 5px;';

            btn.addEventListener('click', function() {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then(function(choiceResult) {
                        if (choiceResult.outcome === 'accepted') {
                            console.log('[PWA] User accepted the install prompt');
                        } else {
                            console.log('[PWA] User dismissed the install prompt');
                        }
                        deferredPrompt = null;
                        hideInstallBar();
                    });
                } else {
                    hideInstallBar();
                    showInstallInstructions();
                }
            });

            closeBtn.addEventListener('click', function() {
                hideInstallBar();
                sessionStorage.setItem('pwa_install_dismissed', 'true');
            });

            container.appendChild(text);
            container.appendChild(btn);
            container.appendChild(closeBtn);
            document.body.appendChild(container);
            console.log('[PWA] Install bar displayed');
        }
    }

    function hideInstallBar() {
        const container = document.getElementById('pwa-install-container');
        if (container) container.remove();
    }

    // ---------- INSTALL INSTRUCTIONS MODAL ----------
    function showInstallInstructions() {
        const modal = document.createElement('div');
        modal.id = 'pwa-install-modal';
        modal.style.cssText =
            'position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 10001;' +
            'background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center;';

        const box = document.createElement('div');
        box.style.cssText =
            'background: white; border-radius: 12px; padding: 30px; max-width: 400px;' +
            'width: 90%; text-align: center; font-family: "Segoe UI", sans-serif;' +
            'box-shadow: 0 10px 40px rgba(0,0,0,0.3);';

        const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

        let instructionsHtml = '';
        if (isMobile) {
            instructionsHtml = `
                <p style="font-size: 16px; margin-bottom: 15px;">To install Smart Inventory on this device:</p>
                <ol style="text-align: left; margin-bottom: 15px; line-height: 2;">
                    <li>Tap the browser menu <strong>(⋮)</strong></li>
                    <li>Select <strong>"Add to Home screen"</strong> or <strong>"Install app"</strong></li>
                    <li>Confirm the installation</li>
                </ol>
            `;
        } else {
            instructionsHtml = `
                <p style="font-size: 16px; margin-bottom: 15px;">To install Smart Inventory on this computer:</p>
                <ol style="text-align: left; margin-bottom: 15px; line-height: 2;">
                    <li>Click the browser menu <strong>(⋮ / ⋯)</strong></li>
                    <li>Select <strong>"Install Smart Inventory"</strong> or <strong>"Add to desktop"</strong></li>
                    <li>Confirm the installation</li>
                </ol>
            `;
        }

        box.innerHTML = `
            <h3 style="margin-bottom: 15px;">📱 Install Smart Inventory</h3>
            ${instructionsHtml}
            <button id="pwa-modal-close" class="btn btn-success" style="width:100%;">Got it</button>
        `;

        modal.appendChild(box);
        document.body.appendChild(modal);

        document.getElementById('pwa-modal-close').addEventListener('click', function() {
            modal.remove();
        });

        modal.addEventListener('click', function(e) {
            if (e.target === modal) modal.remove();
        });
    }

    // ---------- SHOW FLOATING BUTTON ON PAGE LOAD ----------
    window.addEventListener('load', function() {
        setTimeout(ensureInstallButton, 1500);
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(ensureInstallButton, 2000);
        });
    } else {
        setTimeout(ensureInstallButton, 2000);
    }

    // ---------- ONLINE / OFFLINE INDICATORS ----------
    function updateOnlineStatus() {
        const isOnline = navigator.onLine;
        let indicator = document.getElementById('pwa-connection-status');

        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'pwa-connection-status';
            indicator.style.cssText =
                'position: fixed; top: 0; left: 0; right: 0; text-align: center;' +
                'padding: 5px; font-size: 13px; font-weight: bold; z-index: 10000;' +
                'font-family: "Segoe UI", sans-serif; display: none;';
            document.body.appendChild(indicator);
        }

        if (!isOnline) {
            indicator.textContent = '⚠️ Offline Mode – Data will sync when you reconnect';
            indicator.style.background = '#dc3545';
            indicator.style.color = 'white';
            indicator.style.display = 'block';
        } else {
            indicator.style.display = 'none';
        }
    }

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();

    console.log('[PWA] PWA module loaded');
})();