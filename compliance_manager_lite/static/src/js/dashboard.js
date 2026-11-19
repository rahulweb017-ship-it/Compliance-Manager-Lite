/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { useChart } from "@web/core/utils/chart_hook";
import { standardActionServiceProps } from "@web/webclient/actions/action_plugin";
import { Component, onWillStart, proxy, useProps } from "@odoo/owl";

export class ComplianceDashboard extends Component {
    static template = "compliance_manager_lite.Dashboard";
    props = useProps({
        ...standardActionServiceProps,
    });

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = proxy({
            total: 0,
            valid: 0,
            expiring: 0,
            expired: 0,
            expiring_this_month: 0,
            expired_this_month: 0,
            categories: [],
            upcoming: [],
            recent_expired: [],
            loading: true,
        });

        // useChart loads web.chartjs_lib, (re)builds each chart after every
        // render and destroys it on unmount; the template binds the canvases
        // with t-ref="this.statusChart.ref" / "this.categoryChart.ref".
        this.statusChart = useChart(() => this.getStatusChartConfig());
        this.categoryChart = useChart(() => this.getCategoryChartConfig());

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            const data = await this.orm.call("compliance.record", "get_dashboard_data", []);
            this.state.total = data.total;
            this.state.valid = data.valid;
            this.state.expiring = data.expiring;
            this.state.expired = data.expired;
            this.state.expiring_this_month = data.expiring_this_month || 0;
            this.state.expired_this_month = data.expired_this_month || 0;
            this.state.categories = data.categories || [];
            this.state.upcoming = data.upcoming || [];
            this.state.recent_expired = data.recent_expired || [];
        } catch (e) {
            console.error("Failed to load compliance dashboard data", e);
        } finally {
            this.state.loading = false;
        }
    }

    getStatusChartConfig() {
        return {
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
        };
    }

    getCategoryChartConfig() {
        const labels = this.state.categories.map((c) => c.name);
        const ctx = this.categoryChart.ref().getContext("2d");

        const makeGradient = (from, to) => {
            const g = ctx.createLinearGradient(0, 0, 0, 300);
            g.addColorStop(0, from);
            g.addColorStop(1, to);
            return g;
        };

        return {
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
        };
    }

    openRecords(domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name,
            res_model: "compliance.record",
            domain: domain,
            views: [
                [false, "list"],
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
                [false, "list"],
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

    _monthBounds() {
        const today = new Date();
        const pad = (n) => String(n).padStart(2, "0");
        const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
        return {
            today: iso(today),
            monthStart: iso(new Date(today.getFullYear(), today.getMonth(), 1)),
            nextMonthStart: iso(new Date(today.getFullYear(), today.getMonth() + 1, 1)),
        };
    }

    openExpiringThisMonth() {
        const { today, nextMonthStart } = this._monthBounds();
        this.openRecords(
            [
                ["expiry_date", ">=", today],
                ["expiry_date", "<", nextMonthStart],
            ],
            "Expiring This Month"
        );
    }

    openExpiredThisMonth() {
        const { today, monthStart } = this._monthBounds();
        this.openRecords(
            [
                ["expiry_date", ">=", monthStart],
                ["expiry_date", "<", today],
            ],
            "Expired This Month"
        );
    }
}

registry.category("actions").add("compliance_dashboard", ComplianceDashboard);
