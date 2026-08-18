/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState, useEffect, useRef } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";

export class ComplianceDashboard extends Component {
    static template = "compliance_manager_lite.Dashboard";
    static props = {
        "*": true,
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            total: 0,
            valid: 0,
            expiring: 0,
            expired: 0,
            categories: [],
            upcoming: [],
            recent_expired: [],
            loading: true,
        });

        this.statusChartRef = useRef("statusPieChart");
        this.categoryChartRef = useRef("categoryBarChart");
        this.statusChart = null;
        this.categoryChart = null;

        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this.loadDashboardData();
        });

        useEffect(() => {
            if (!this.state.loading) {
                this.renderCharts();
            }
            return () => this.destroyCharts();
        });
    }

    destroyCharts() {
        if (this.statusChart) {
            this.statusChart.destroy();
            this.statusChart = null;
        }
        if (this.categoryChart) {
            this.categoryChart.destroy();
            this.categoryChart = null;
        }
    }

    async loadDashboardData() {
        try {
            const data = await this.orm.call("compliance.record", "get_dashboard_data", []);
            this.state.total = data.total;
            this.state.valid = data.valid;
            this.state.expiring = data.expiring;
            this.state.expired = data.expired;
            this.state.categories = data.categories || [];
            this.state.upcoming = data.upcoming || [];
            this.state.recent_expired = data.recent_expired || [];
        } catch (e) {
            console.error("Failed to load compliance dashboard data", e);
        } finally {
            this.state.loading = false;
        }
    }

    renderCharts() {
        this.destroyCharts();

        const statusCanvas = this.statusChartRef.el;
        if (statusCanvas) {
            // Devoria-inspired vibrant pastel colors:
            // Valid (neon emerald/blue gradient), Expiring (purple/indigo), Expired (rose/coral red)
            this.statusChart = new Chart(statusCanvas, {
                type: "doughnut",
                data: {
                    labels: ["Valid", "Expiring Soon", "Expired"],
                    datasets: [
                        {
                            data: [this.state.valid, this.state.expiring, this.state.expired],
                            backgroundColor: ["#3b82f6", "#a855f7", "#f43f5e"],
                            borderWidth: 2,
                            borderColor: "#ffffff",
                            hoverOffset: 4,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "75%",
                    plugins: {
                        legend: {
                            display: false,
                        },
                    },
                },
            });
        }

        const categoryCanvas = this.categoryChartRef.el;
        if (categoryCanvas && this.state.categories.length > 0) {
            const labels = this.state.categories.map((c) => c.name);
            const ctx = categoryCanvas.getContext("2d");

            const makeGradient = (from, to) => {
                const g = ctx.createLinearGradient(0, 0, 0, 300);
                g.addColorStop(0, from);
                g.addColorStop(1, to);
                return g;
            };

            this.categoryChart = new Chart(categoryCanvas, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Valid",
                            data: this.state.categories.map((c) => c.valid),
                            backgroundColor: makeGradient("#60a5fa", "#3b82f6"),
                            borderRadius: 8,
                            borderSkipped: false,
                            maxBarThickness: 26,
                        },
                        {
                            label: "Expiring Soon",
                            data: this.state.categories.map((c) => c.expiring),
                            backgroundColor: makeGradient("#c084fc", "#a855f7"),
                            borderRadius: 8,
                            borderSkipped: false,
                            maxBarThickness: 26,
                        },
                        {
                            label: "Expired",
                            data: this.state.categories.map((c) => c.expired),
                            backgroundColor: makeGradient("#fb7185", "#f43f5e"),
                            borderRadius: 8,
                            borderSkipped: false,
                            maxBarThickness: 26,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: { padding: { top: 10 } },
                    scales: {
                        x: {
                            stacked: true,
                            grid: {
                                display: false,
                            },
                            ticks: {
                                color: "#475569",
                                font: {
                                    weight: "600",
                                    size: 12,
                                },
                            },
                        },
                        y: {
                            stacked: true,
                            beginAtZero: true,
                            border: { dash: [4, 4], display: false },
                            grid: {
                                color: "rgba(15, 23, 42, 0.06)",
                                drawTicks: false,
                            },
                            ticks: {
                                precision: 0,
                                color: "#94a3b8",
                                padding: 8,
                                font: {
                                    weight: "500",
                                },
                            },
                        },
                    },
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: {
                                color: "#334155",
                                usePointStyle: true,
                                pointStyle: "circle",
                                boxWidth: 8,
                                padding: 18,
                                font: {
                                    weight: "600",
                                    size: 12,
                                },
                            },
                        },
                        tooltip: {
                            backgroundColor: "rgba(15, 23, 42, 0.92)",
                            padding: 12,
                            cornerRadius: 10,
                            titleFont: { weight: "700", size: 13 },
                            bodyFont: { size: 12 },
                            usePointStyle: true,
                        },
                    },
                },
            });
        }
    }

    openRecords(domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name,
            res_model: "compliance.record",
            domain: domain,
            views: [
                [false, "tree"],
                [false, "form"],
            ],
            target: "current",
        });
    }

    openRecordDetail(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "compliance.record",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openCategories() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Categories",
            res_model: "compliance.category",
            views: [
                [false, "tree"],
                [false, "form"],
            ],
            target: "current",
        });
    }

    openAll() {
        this.openRecords([], "Compliance Records");
    }

    openValid() {
        this.openRecords([["status", "=", "valid"]], "Valid Records");
    }

    openExpiring() {
        this.openRecords([["status", "=", "expiring"]], "Expiring Soon");
    }

    openExpired() {
        this.openRecords([["status", "=", "expired"]], "Expired Records");
    }
}

registry.category("actions").add("compliance_dashboard", ComplianceDashboard);
