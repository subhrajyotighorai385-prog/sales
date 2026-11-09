/**
 * HIGH VALUE SALES — CHART.JS ANALYTICS ENGINE
 * Renders real database transaction analytics:
 * 1. Revenue Timeline Chart (Line with gradient fill)
 * 2. Premium vs Regular Sales Distribution (Doughnut)
 * 3. Category Revenue Distribution (Bar / Polar)
 * 4. Monthly Comparison (Bar with High-Value Overlay)
 */

document.addEventListener('DOMContentLoaded', () => {
    const revenueLineCtx = document.getElementById('chart-revenue-line');
    const premiumRatioCtx = document.getElementById('chart-premium-ratio');
    const categoryBarCtx = document.getElementById('chart-category-bar');
    const monthlyComparisonCtx = document.getElementById('chart-monthly-comparison');

    if (!revenueLineCtx && !premiumRatioCtx && !categoryBarCtx && !monthlyComparisonCtx) {
        return;
    }

    // Chart.js global dark theme defaults
    if (window.Chart) {
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 23, 42, 0.95)';
        Chart.defaults.plugins.tooltip.borderColor = 'rgba(6, 182, 212, 0.4)';
        Chart.defaults.plugins.tooltip.borderWidth = 1;
        Chart.defaults.plugins.tooltip.padding = 12;
        Chart.defaults.plugins.tooltip.cornerRadius = 8;
        Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
        Chart.defaults.plugins.tooltip.bodyColor = '#e2e8f0';
    }

    // Fetch live user analytics from backend API
    fetch('/api/analytics')
        .then(res => res.json())
        .then(data => {
            if (data.status !== 'success') return;

            const curr = data.currency || '₹';
            const kpis = data.kpis;
            const monthly = data.monthly || [];
            const categories = data.categories || [];

            // 1. REVENUE TIMELINE CHART (Line Chart)
            if (revenueLineCtx) {
                const ctx = revenueLineCtx.getContext('2d');
                const gradientCyan = ctx.createLinearGradient(0, 0, 0, 320);
                gradientCyan.addColorStop(0, 'rgba(6, 182, 212, 0.35)');
                gradientCyan.addColorStop(1, 'rgba(6, 182, 212, 0.0)');

                const gradientPurple = ctx.createLinearGradient(0, 0, 0, 320);
                gradientPurple.addColorStop(0, 'rgba(139, 92, 246, 0.25)');
                gradientPurple.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

                const labels = monthly.map(m => m.label);
                const totalRevenues = monthly.map(m => m.revenue);
                const premiumRevenues = monthly.map(m => m.premium_revenue);

                new Chart(revenueLineCtx, {
                    type: 'line',
                    data: {
                        labels: labels.length ? labels : ['Current Period'],
                        datasets: [
                            {
                                label: 'Total Revenue',
                                data: totalRevenues.length ? totalRevenues : [kpis.total_revenue],
                                borderColor: '#06b6d4',
                                backgroundColor: gradientCyan,
                                borderWidth: 3,
                                fill: true,
                                tension: 0.38,
                                pointBackgroundColor: '#06b6d4',
                                pointBorderColor: '#ffffff',
                                pointBorderWidth: 2,
                                pointRadius: 5,
                                pointHoverRadius: 8
                            },
                            {
                                label: 'High-Value Revenue',
                                data: premiumRevenues.length ? premiumRevenues : [kpis.premium_revenue],
                                borderColor: '#f59e0b',
                                backgroundColor: 'transparent',
                                borderDash: [5, 5],
                                borderWidth: 2,
                                fill: false,
                                tension: 0.38,
                                pointBackgroundColor: '#f59e0b',
                                pointBorderColor: '#ffffff',
                                pointBorderWidth: 2,
                                pointRadius: 4,
                                pointHoverRadius: 7
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            intersect: false,
                            mode: 'index'
                        },
                        scales: {
                            x: {
                                grid: { color: 'rgba(255, 255, 255, 0.04)' },
                                ticks: { color: '#94a3b8' }
                            },
                            y: {
                                grid: { color: 'rgba(255, 255, 255, 0.04)' },
                                ticks: {
                                    color: '#94a3b8',
                                    callback: val => curr + Number(val).toLocaleString()
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: { color: '#e2e8f0', usePointStyle: true, boxWidth: 8 }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(ctx) {
                                        return `${ctx.dataset.label}: ${curr}${Number(ctx.raw).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
                                    }
                                }
                            }
                        }
                    }
                });
            }

            // 2. PREMIUM VS REGULAR SALES (Doughnut)
            if (premiumRatioCtx) {
                const premRev = kpis.premium_revenue;
                const regRev = kpis.regular_revenue;

                new Chart(premiumRatioCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['High-Value (Premium)', 'Regular Sales'],
                        datasets: [{
                            data: [premRev, regRev],
                            backgroundColor: [
                                '#f59e0b', // Glowing Amber Gold
                                '#3b82f6'  // Neon Blue
                            ],
                            borderColor: '#070913',
                            borderWidth: 4,
                            hoverOffset: 8
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '72%',
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { color: '#e2e8f0', usePointStyle: true, padding: 15 }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(ctx) {
                                        const total = premRev + regRev;
                                        const pct = total > 0 ? ((ctx.raw / total) * 100).toFixed(1) : 0;
                                        return ` ${ctx.label}: ${curr}${Number(ctx.raw).toLocaleString(undefined, {minimumFractionDigits: 2})} (${pct}%)`;
                                    }
                                }
                            }
                        }
                    }
                });
            }

            // 3. CATEGORY DISTRIBUTION (Bar or Doughnut)
            if (categoryBarCtx) {
                const catLabels = categories.map(c => c.category);
                const catRevenues = categories.map(c => c.revenue);
                const neonColors = [
                    '#06b6d4', '#8b5cf6', '#3b82f6', '#10b981',
                    '#f59e0b', '#ec4899', '#6366f1', '#14b8a6'
                ];

                new Chart(categoryBarCtx, {
                    type: 'bar',
                    data: {
                        labels: catLabels,
                        datasets: [{
                            label: 'Revenue by Category',
                            data: catRevenues,
                            backgroundColor: neonColors.slice(0, catLabels.length),
                            borderRadius: 8,
                            borderSkipped: false
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        indexAxis: 'y', // Horizontal bars for clean category titles
                        scales: {
                            x: {
                                grid: { color: 'rgba(255, 255, 255, 0.04)' },
                                ticks: {
                                    color: '#94a3b8',
                                    callback: val => curr + Number(val).toLocaleString()
                                }
                            },
                            y: {
                                grid: { display: false },
                                ticks: { color: '#cbd5e1', font: { weight: 500 } }
                            }
                        },
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: function(ctx) {
                                        return ` Revenue: ${curr}${Number(ctx.raw).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
                                    }
                                }
                            }
                        }
                    }
                });
            }

            // 4. MONTHLY COMPARISON CHART
            if (monthlyComparisonCtx) {
                const months = monthly.map(m => m.label);
                const totals = monthly.map(m => m.revenue);
                const counts = monthly.map(m => m.count);

                new Chart(monthlyComparisonCtx, {
                    type: 'bar',
                    data: {
                        labels: months,
                        datasets: [
                            {
                                type: 'bar',
                                label: 'Monthly Revenue',
                                data: totals,
                                backgroundColor: 'rgba(139, 92, 246, 0.65)',
                                borderColor: '#8b5cf6',
                                borderWidth: 1,
                                borderRadius: 6,
                                yAxisID: 'y'
                            },
                            {
                                type: 'line',
                                label: 'Deal Volume',
                                data: counts,
                                borderColor: '#22d3ee',
                                backgroundColor: '#22d3ee',
                                borderWidth: 2,
                                pointRadius: 4,
                                yAxisID: 'y1'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: { grid: { color: 'rgba(255, 255, 255, 0.04)' } },
                            y: {
                                position: 'left',
                                grid: { color: 'rgba(255, 255, 255, 0.04)' },
                                ticks: { callback: val => curr + Number(val).toLocaleString() }
                            },
                            y1: {
                                position: 'right',
                                grid: { display: false },
                                ticks: { color: '#22d3ee', stepSize: 1 }
                            }
                        },
                        plugins: {
                            legend: {
                                labels: { color: '#e2e8f0', usePointStyle: true }
                            }
                        }
                    }
                });
            }
        })
        .catch(err => {
            console.warn("Analytics chart fetch error:", err);
        });
});
