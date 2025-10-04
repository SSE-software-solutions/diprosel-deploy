/** @odoo-module **/
import { Component } from "@odoo/owl";

export class DataTable extends Component {
    static template = "sse_dashboard.DataTable";
    static props = ["title", "headers", "rows"];
}