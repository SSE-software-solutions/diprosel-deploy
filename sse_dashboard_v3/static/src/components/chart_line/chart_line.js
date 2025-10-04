/** @odoo-module */
import { Component, useRef, onMounted, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

export class ChartLine extends Component {
    static template = "sse_dashboard.ChartLine";

    setup() {
        this.chartRef = useRef("chart");
        this.chartInstance = null;

        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js");
            await loadJS("https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0");
        });

        onMounted(() => this.renderChart());

        onWillUpdateProps((nextProps) => this.updateChart(nextProps.chartData));
    }

    getProcessedData() {
        const chartData = this.props.chartData || {};
        const hasData = Array.isArray(chartData.labels) && chartData.labels.length > 0;

        if (!hasData) {
            // 🎯 Datos de fallback si están vacíos o no definidos
            return {
                labels: ["Enero", "Febrero", "Marzo"],
                datasets: [{
                    label: chartData.label || "Datos de Prueba",
                    data: [100, 200, 300],
                    borderColor: chartData.color || "#28a745",
                    backgroundColor: chartData.bgColor || "rgba(40,167,69,0.2)",
                    fill: true,
                    pointBackgroundColor: chartData.color || "#28a745",
                    pointBorderColor: "#fff",
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            };
        }

        return {
            labels: chartData.labels,
            datasets: [{
                label: chartData.label,
                data: chartData.data,
                borderColor: chartData.color,
                backgroundColor: chartData.bgColor,
                fill: true,
                pointBackgroundColor: chartData.color,
                pointBorderColor: "#fff",
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        };
    }

    renderChart() {
        if (!this.chartRef.el) {
            console.warn("⚠️ Canvas no disponible");
            return;
        }

        const chartData = this.getProcessedData();

        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        this.chartInstance = new Chart(this.chartRef.el, {
            type: "line",
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    datalabels: {
                        anchor: "end",
                        align: "top",
                        color: "#333",
                        font: { weight: "bold", size: 12 },
                        formatter: (value) => value
                    }
                },
                scales: {
                    y: { beginAtZero: true },
                    x: { ticks: { autoSkip: false } }
                }
            },
            plugins: [ChartDataLabels]
        });
    }

    updateChart(newChartData) {
        if (!this.chartInstance || !newChartData) return;

        const chartData = this.getProcessedData();

        this.chartInstance.data.labels = chartData.labels;
        this.chartInstance.data.datasets[0] = chartData.datasets[0];

        this.chartInstance.update();
    }
}
