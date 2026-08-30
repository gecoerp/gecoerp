/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
const { Component, onWillStart, onMounted, useState, useRef } = owl;

export class GecoAiDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        
        this.trendChartRef = useRef("trendChart");
        this.moduleChartRef = useRef("moduleChart");
        
        this.trendChart = null;
        this.moduleChart = null;
        
        this.state = useState({
            stats: {
                kpis: {
                    total_tokens_month: 0,
                    token_limit: 0,
                    average_daily: 0,
                    projected_month: 0,
                    projected_year: 0,
                    total_cost_usd: 0,
                },
                charts: { trend: { labels: [], data: [] }, modules: { labels: [], data: [] } }
            }
        });

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.loadStatistics();
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    async loadStatistics() {
        const data = await this.orm.call("geco.ai.dashboard", "get_statistics", []);
        this.state.stats = data;
        
        // Update charts if they are already mounted
        if (this.trendChart && this.moduleChart) {
            this.updateCharts();
        }
    }

    renderCharts() {
        // Trend Chart
        const trendCtx = this.trendChartRef.el.getContext('2d');
        
        // Create a nice gradient
        let gradient = trendCtx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(113, 75, 103, 0.5)'); // Gecoerp purple-ish
        gradient.addColorStop(1, 'rgba(113, 75, 103, 0.0)');
        
        this.trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: this.state.stats.charts.trend.labels,
                datasets: [
                    {
                        label: 'Consumo Real',
                        data: this.state.stats.charts.trend.data_actual,
                        backgroundColor: gradient,
                        borderColor: '#714B67',
                        borderWidth: 3,
                        pointBackgroundColor: '#fff',
                        pointBorderColor: '#714B67',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Predicción MLP (Redes Neuronales)',
                        data: this.state.stats.charts.trend.data_predicted,
                        backgroundColor: 'transparent',
                        borderColor: '#017E84',
                        borderWidth: 3,
                        borderDash: [5, 5],
                        pointBackgroundColor: '#fff',
                        pointBorderColor: '#017E84',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        fill: false,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true, position: 'top' }
                },
                scales: {
                    y: { beginAtZero: true, grid: { borderDash: [2, 4] } },
                    x: { grid: { display: false } }
                },
                interaction: {
                    intersect: false,
                    mode: 'index',
                },
            }
        });

        // Module Chart
        const moduleCtx = this.moduleChartRef.el.getContext('2d');
        this.moduleChart = new Chart(moduleCtx, {
            type: 'doughnut',
            data: {
                labels: this.state.stats.charts.modules.labels,
                datasets: [{
                    data: this.state.stats.charts.modules.data,
                    backgroundColor: [
                        '#714B67', '#017E84', '#F06050', '#8F8F8F', '#F8A13F', '#E2DCDA'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: { position: 'bottom', labels: { padding: 20, usePointStyle: true } }
                }
            }
        });
    }
    
    updateCharts() {
        this.trendChart.data.labels = this.state.stats.charts.trend.labels;
        this.trendChart.data.datasets[0].data = this.state.stats.charts.trend.data_actual;
        this.trendChart.data.datasets[1].data = this.state.stats.charts.trend.data_predicted;
        this.trendChart.update();
        
        this.moduleChart.data.labels = this.state.stats.charts.modules.labels;
        this.moduleChart.data.datasets[0].data = this.state.stats.charts.modules.data;
        this.moduleChart.update();
    }
}

GecoAiDashboard.template = "geco_ai_core.Dashboard";

registry.category("actions").add("geco_ai_dashboard_action", GecoAiDashboard);
