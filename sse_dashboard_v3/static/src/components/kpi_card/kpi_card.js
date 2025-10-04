/** @odoo-module */

const { Component } = owl;

export class KpiCard extends Component {
    static template = "sse_dashboard.KpiCard";
    static props = ["title", "value", "icon", "color", "trend"];
}
