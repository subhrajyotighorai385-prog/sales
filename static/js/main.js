/**
 * HIGH VALUE SALES — CORE UI / UX & INTERACTION SCRIPTS
 * Includes: GSAP page animations, password toggle, form auto-calculators, modals, toasts.
 */

document.addEventListener('DOMContentLoaded', () => {

    // -------------------------------------------------------------
    // 1. GSAP ENTRANCE ANIMATIONS (Smooth & Lightweight)
    // -------------------------------------------------------------
    if (window.gsap && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        // Hero Section Animation
        if (document.querySelector('.hero-animate-in')) {
            gsap.from('.hero-animate-in > *', {
                y: 30,
                opacity: 0,
                duration: 0.9,
                stagger: 0.15,
                ease: 'power3.out'
            });
        }

        // Dashboard KPI Cards Stagger Reveal & Number Count-Up
        if (document.querySelectorAll('.kpi-card').length > 0) {
            gsap.from('.kpi-card', {
                y: 20,
                opacity: 0,
                duration: 0.6,
                stagger: 0.08,
                ease: 'back.out(1.2)'
            });

            document.querySelectorAll('.kpi-value').forEach(el => {
                const rawText = el.innerText.trim();
                const match = rawText.match(/^([^\d]*)([\d,\.]+)(.*)$/);
                if (match) {
                    const prefix = match[1] || '';
                    const num = parseFloat(match[2].replace(/,/g, ''));
                    const suffix = match[3] || '';
                    if (!isNaN(num) && num > 0) {
                        const counter = { val: 0 };
                        gsap.to(counter, {
                            val: num,
                            duration: 1.1,
                            ease: 'power2.out',
                            onUpdate: () => {
                                el.innerText = `${prefix}${Math.floor(counter.val).toLocaleString()}${suffix}`;
                            },
                            onComplete: () => {
                                el.innerText = rawText;
                            }
                        });
                    }
                }
            });
        }

        // Table Rows Entrance
        if (document.querySelectorAll('.cyber-table tbody tr').length > 0) {
            gsap.from('.cyber-table tbody tr', {
                opacity: 0,
                y: 10,
                duration: 0.4,
                stagger: 0.03,
                ease: 'power2.out'
            });
        }
    }

    // -------------------------------------------------------------
    // 2. PASSWORD VISIBILITY TOGGLE
    // -------------------------------------------------------------
    const togglePasswordBtns = document.querySelectorAll('.btn-toggle-password');
    togglePasswordBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (!input) return;

            if (input.type === 'password') {
                input.type = 'text';
                btn.innerHTML = `
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                    </svg>
                `;
            } else {
                input.type = 'password';
                btn.innerHTML = `
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                `;
            }
        });
    });

    // -------------------------------------------------------------
    // 3. REAL-TIME TOTAL AMOUNT AUTO-CALCULATOR & PREMIUM BADGE
    // -------------------------------------------------------------
    const qtyInput = document.getElementById('transaction-quantity');
    const priceInput = document.getElementById('transaction-price');
    const totalDisplay = document.getElementById('preview-total-amount');
    const badgeDisplay = document.getElementById('preview-threshold-badge');

    function calculateTotal() {
        if (!qtyInput || !priceInput || !totalDisplay) return;

        const qty = parseFloat(qtyInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        const total = (qty * price).toFixed(2);
        const threshold = parseFloat(totalDisplay.getAttribute('data-threshold')) || 50000.0;
        const currency = totalDisplay.getAttribute('data-currency') || '₹';

        totalDisplay.textContent = `${currency}${Number(total).toLocaleString(undefined, {minimumFractionDigits: 2})}`;

        if (badgeDisplay) {
            if (parseFloat(total) >= threshold) {
                badgeDisplay.innerHTML = `<span class="badge-vip">★ HIGH-VALUE DEAL (≥ ${currency}${threshold})</span>`;
            } else {
                badgeDisplay.innerHTML = `<span class="badge-regular">Regular Sale (&lt; ${currency}${threshold})</span>`;
            }
        }
    }

    if (qtyInput && priceInput) {
        qtyInput.addEventListener('input', calculateTotal);
        priceInput.addEventListener('input', calculateTotal);
        calculateTotal();
    }

    // -------------------------------------------------------------
    // 4. TOAST NOTIFICATIONS AUTO-DISMISS
    // -------------------------------------------------------------
    const toasts = document.querySelectorAll('.toast-cyber');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(80px)';
            setTimeout(() => toast.remove(), 400);
        }, 5000);
    });

    // -------------------------------------------------------------
    // 5. MODAL SYSTEM (CSV Import, Details, Confirmations)
    // -------------------------------------------------------------
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    // Close modal on backdrop click
    document.querySelectorAll('.modal-cyber-backdrop').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });

    // -------------------------------------------------------------
    // 6. TRANSACTION DETAIL AJAX MODAL
    // -------------------------------------------------------------
    window.showTransactionDetails = function(saleId) {
        const detailModal = document.getElementById('modal-transaction-detail');
        const contentBox = document.getElementById('transaction-detail-content');
        if (!detailModal || !contentBox) return;

        contentBox.innerHTML = `
            <div style="text-align:center;padding:2rem;">
                <div style="color:var(--accent-cyan);font-size:1.5rem;margin-bottom:0.5rem;">✦ Loading Deal Telemetry...</div>
            </div>
        `;
        openModal('modal-transaction-detail');

        fetch(`/transactions/${saleId}/json`)
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    const s = data.sale;
                    const badge = s.is_premium 
                        ? `<span class="badge-vip">★ HIGH-VALUE (PREMIUM)</span>`
                        : `<span class="badge-regular">REGULAR TRANSACTION</span>`;

                    const curr = s.currency || '₹';
                    contentBox.innerHTML = `
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1.2rem;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:1rem;">
                            <div>
                                <h3 style="font-size:1.35rem;margin-bottom:0.2rem;">${s.product_name}</h3>
                                <div style="color:#94a3b8;font-size:0.85rem;">Deal ID: #${s.id} &bull; Date: ${s.transaction_date}</div>
                            </div>
                            <div>${badge}</div>
                        </div>

                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;margin-bottom:1.5rem;">
                            <div class="glass-panel" style="padding:1rem;">
                                <div class="cyber-label">Total Amount</div>
                                <div style="font-size:1.6rem;font-weight:800;color:#22d3ee;">${curr}${Number(s.total_amount).toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                            </div>
                            <div class="glass-panel" style="padding:1rem;">
                                <div class="cyber-label">Pricing Matrix</div>
                                <div style="font-size:1rem;color:#ffffff;">${s.quantity} units &times; ${curr}${Number(s.unit_price).toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                            </div>
                            <div class="glass-panel" style="padding:1rem;">
                                <div class="cyber-label">Client / Customer</div>
                                <div style="font-size:1rem;color:#ffffff;font-weight:600;">${s.customer_name || 'Enterprise Client'}</div>
                            </div>
                            <div class="glass-panel" style="padding:1rem;">
                                <div class="cyber-label">Category & Status</div>
                                <div style="font-size:0.95rem;color:#cbd5e1;">${s.category} &bull; <span class="status-dot status-dot-${s.status.toLowerCase()}"></span> ${s.status}</div>
                            </div>
                        </div>

                        <div style="margin-bottom:1.5rem;">
                            <div class="cyber-label">Description / Internal Notes</div>
                            <p style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);padding:0.9rem;border-radius:10px;font-size:0.9rem;color:#cbd5e1;">
                                ${s.description || 'No description provided for this transaction.'}
                            </p>
                        </div>

                        <div style="display:flex;justify-content:flex-end;gap:0.8rem;">
                            <a href="/transactions/${s.id}/edit" class="btn-cyber-outline">Edit Deal</a>
                            <button onclick="closeModal('modal-transaction-detail')" class="btn-cyber-primary">Close</button>
                        </div>
                    `;
                }
            })
            .catch(err => {
                contentBox.innerHTML = `<div style="color:var(--accent-rose);text-align:center;padding:1.5rem;">Failed to retrieve transaction data.</div>`;
            });
    };

    // -------------------------------------------------------------
    // 7. MOBILE NAVIGATION TOGGLE
    // -------------------------------------------------------------
    const navToggle = document.getElementById('cyber-mobile-toggle');
    const navMenu = document.getElementById('cyber-nav-menu');
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('nav-menu-open');
        });
    }
});
