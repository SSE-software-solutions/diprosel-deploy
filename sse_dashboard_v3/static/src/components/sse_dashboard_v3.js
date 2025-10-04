/** @odoo-module */
import { registry } from "@web/core/registry";
import { KpiCard } from "./kpi_card/kpi_card";
import { DataTable } from "./data_table/data_table";
import { ChartLine } from "./chart_line/chart_line";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

const { Component, onWillStart, onMounted, onWillUnmount, useState } = owl;

export class SseDashboard extends Component {
  static template = "sse_dashboard.SseDashboard";
  static components = { KpiCard, DataTable, ChartLine };

  setup() {
    this.bus = useService("bus_service");

    this.state = useState({
      selectedPeriod: "Mensual",
      tablas: {
        bajoStock: {
          title: "Productos con Bajo Stock",
          headers: ["Producto", "Stock"],
          rows: [],
        },
        bajaRotacion: {
          title: "Productos de Baja Rotación",
          headers: ["Producto", "Ventas en el Mes"],
          rows: [],
        },
        masVendidos: {
          title: "Productos Más Vendidos",
          headers: ["#", "Producto", "Cantidad"],
          rows: [],
        },
        categoriasVendidas: {
          title: "Categorías Más Vendidas",
          headers: ["Categoría", "Cantidad"],
          rows: [],
        },
        negociosTop: {
          title: "Negocios que Más Venden",
          headers: ["Negocio", "Pedidos"],
          rows: [],
        },
        diaGiro: {
          title: "Día Giro de Productos",
          headers: [
            "Producto",
            "Promedio Diario",
            "Stock (unidades) ",
            "Día Giro",
            "Necesario X 20 días (paquetes)",
            "Necesario X 40 días (paquetes)",
          ],
          rows: [],
        },
        topClientes: {
          title: "Top Clientes",
          headers: ["Cliente", "Total Comprado"],
          rows: [],
        },
        topMarcas: {
          title: "Top Marcas",
          headers: ["Marca", "Ventas"],
          rows: [],
        },
      },
      evolutivoVentas: {
        labels: [],
        data: [],
        label: "Ventas Mensuales (S/.)",
        color: "#28a745",
        bgColor: "rgba(40,167,69,0.2)",
      },
      evolutivoPedidos: {
        labels: [],
        data: [],
        label: "Cantidad de Pedidos",
        color: "#007bff",
        bgColor: "rgba(0,123,255,0.2)",
      },
    });

    this.kpis = [];

    onWillStart(async () => {
      // Preparar suscripción al bus
      this.bus.addChannel("broadcast");
      this.bus.subscribe("sse_dashboard.update", this.onBusUpdate);
      this.bus.start();

      await this.fetchKpis();
      await this.fetchTablas();
      await this.fetchEvolutivos();
    });

    onMounted(() => {
      // noop por ahora
    });

    onWillUnmount(() => {
      try {
        this.bus.unsubscribe("sse_dashboard.update", this.onBusUpdate);
        this.bus.deleteChannel && this.bus.deleteChannel("broadcast");
      } catch (e) {
        console.warn("Unsubscribe bus error", e);
      }
    });
  }

  fetchKpis = async () => {
    try {
      const period = this.state.selectedPeriod;
      const data = await rpc("/loan_dashboard/kpis", { period });

      if (data.error) {
        console.error("❌ Error en los KPIs:", data.error);
        return;
      }

      this.kpis = data.kpis.map((kpi) => ({
        title: kpi.title,
        value: kpi.value,
        icon: kpi.icon,
        color: kpi.color,
        trend: kpi.trend,
      }));

      this.render();
    } catch (error) {
      console.error("❌ Error al obtener KPIs:", error);
    }
  };

  fetchTablas = async () => {
    try {
      const data = await rpc("/loan_dashboard/tablas", {});

      this.state.tablas.bajoStock.rows = data.bajo_stock || [];
      this.state.tablas.bajaRotacion.rows = data.baja_rotacion || [];
      this.state.tablas.masVendidos.rows = data.mas_vendidos || [];
      this.state.tablas.categoriasVendidas.rows =
        data.categorias_vendidas || [];
      this.state.tablas.negociosTop.rows = data.negocios_top || [];
      this.state.tablas.diaGiro.rows = data.dia_giro || [];
      this.state.tablas.topClientes.rows = data.clientes_top || [];
      this.state.tablas.topMarcas.rows = data.top_marcas || [];

      this.render();
    } catch (error) {
      console.error("❌ Error al obtener tablas:", error);
    }
  };

  fetchEvolutivos = async () => {
    try {
      const data = await rpc("/loan_dashboard/evolutivos", {});

      if (data.error) {
        console.error("❌ Error en evolución:", data.error);
        return;
      }

      // Verifica si los datos están vacíos, si es así, asigna valores predeterminados
      if (
        !data.evolutivoVentas.labels.length ||
        !data.evolutivoVentas.data.length
      ) {
        data.evolutivoVentas.labels = ["Enero", "Febrero", "Marzo"];
        data.evolutivoVentas.data = [100, 200, 300];
      }

      if (
        !data.evolutivoPedidos.labels.length ||
        !data.evolutivoPedidos.data.length
      ) {
        data.evolutivoPedidos.labels = ["Enero", "Febrero", "Marzo"];
        data.evolutivoPedidos.data = [100, 200, 300];
      }

      this.state.evolutivoVentas = data.evolutivoVentas;
      this.state.evolutivoPedidos = data.evolutivoPedidos;

      this.render();
    } catch (error) {
      console.error("❌ Error al obtener datos evolutivos:", error);
    }
  };

  onBusUpdate = async (payload) => {
    try {
      await Promise.all([
        this.fetchKpis(),
        this.fetchTablas(),
        this.fetchEvolutivos(),
      ]);
    } catch (e) {
      console.error("❌ Error refrescando tras evento de bus:", e, payload);
    }
  };

  selectPeriod = async (period) => {
    this.state.selectedPeriod = period;
    await this.fetchKpis();
    await this.fetchTablas();
    await this.fetchEvolutivos();
  };
}

registry.category("actions").add("sse.dashboard", SseDashboard);
