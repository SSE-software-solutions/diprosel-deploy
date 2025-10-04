from odoo import fields, http
from odoo.http import request
from datetime import datetime, timedelta
import calendar
import math
import logging

_logger = logging.getLogger(__name__)

class LoanDashboardController(http.Controller):

    @http.route('/loan_dashboard/kpis', type='json', auth='user')
    def get_kpis(self, period=None, gestor_id=None):
        """Obtiene KPIs personalizados para el inventario, facturación y clientes"""
        _logger.info(f"Obteniendo KPIs para el periodo: {period}")

        try:
            # Validar el parámetro 'period'
            if period not in ['Diario', 'Semanal', 'Mensual', 'Anual']:
                return {'error': 'Periodo no soportado. Por favor elige entre: Diario, Semanal, Mensual, Anual.'}

            # Productos con stock
            stocked_products = request.env['product.product'].search_count([('qty_available', '>', 0)])
            # Productos totales
            total_products = request.env['product.product'].search_count([])
            # Facturas emitidas
            facturado = request.env['account.move'].search_count([('move_type', '=', 'out_invoice')])
            # Boletas emitidas
            boletas = request.env['account.move'].search_count([('move_type', '=', 'out_receipt')])
            # Total de clientes
            total_clientes = request.env['res.partner'].search_count([('customer_rank', '>', 0)])
            # Clientes atendidos (ventas realizadas)
            clientes_atendidos = request.env['sale.order'].read_group(
                [('state', 'in', ['sale', 'done'])],
                ['partner_id'], ['partner_id']
            )
            
            kpis = [
                {
                    "title": "Productos con Stock",
                    "value": stocked_products,
                    "trend": 5,
                    "icon": "fa-box",
                    "color": "#28a745"
                },
                {
                    "title": "Productos Totales",
                    "value": total_products,
                    "trend": 2,
                    "icon": "fa-cubes",
                    "color": "#007bff"
                },
                {
                    "title": "Indicador de Facturado",
                    "value": facturado,
                    "trend": 3,
                    "icon": "fa-file-invoice-dollar",
                    "color": "#ffc107"
                },
                {
                    "title": "Indicador de Boletas",
                    "value": boletas,
                    "trend": -1,
                    "icon": "fa-receipt",
                    "color": "#dc3545"
                },
                {
                    "title": "Clientes Totales",
                    "value": total_clientes,
                    "trend": 4,
                    "icon": "fa-users",
                    "color": "#6f42c1"
                },
                {
                    "title": "Clientes Atendidos",
                    "value": len(clientes_atendidos),
                    "trend": 6,
                    "icon": "fa-handshake",
                    "color": "#17a2b8"
                }
            ]

            return {"kpis": kpis}

        except Exception as e:
            _logger.error(f"Error en /loan_dashboard/kpis: {str(e)}", exc_info=True)
            return {'error': str(e)}

    @http.route('/loan_dashboard/tablas', type='json', auth='user')
    def get_tablas(self):
        """Devuelve datos de tablas para el dashboard."""
        try:

            # Agrupar por product_id y sumar las cantidades
            stock_quant_records = request.env['stock.quant'].read_group(
                [('inventory_date', '!=', False), ('quantity', '<=', 20)],  # Filtros
                ['product_id', 'quantity'],  # Campos para agrupar
                ['product_id']  # Agrupar por product_id
            )

            data_bajo_stock = []
            for record in stock_quant_records:
                product = request.env['product.product'].browse(record['product_id'][0])  # Obtener el producto
                total_stock = record['quantity']  # Ya está sumado por el ORM de Odoo
                data_bajo_stock.append([product.name, total_stock])

            # Buscar ventas de este mes
            start_date = fields.Date.today().replace(day=1)  # Primer día del mes actual
            ventas = request.env['account.move.line'].search([
                ('move_id.move_type', 'in', ['out_invoice', 'out_receipt']),
                ('move_id.invoice_date', '>=', start_date)
            ])

            # Categoría más vendida
            categorias = request.env['account.move.line'].read_group(
                [('move_id.move_type', 'in', ['out_invoice', 'out_receipt'])],
                ['product_id', 'quantity'],
                ['product_id'],
            )

            categoria_data = {}
            for v in categorias:
                if not v['product_id']:
                    continue
                # Usamos product.template en lugar de product.product
                product = request.env['product.product'].browse(v['product_id'][0])
                product_template = product.product_tmpl_id
                
                # Accedemos al campo categoria_productos en product.template
                categoria_productos = product_template.categoria_productos.name if product_template.categoria_productos else 'Sin Categoría'
                
                if categoria_productos not in categoria_data:
                    categoria_data[categoria_productos] = 0
                categoria_data[categoria_productos] += v['quantity']  # Se suma la cantidad vendida

            # Ordenamos y obtenemos las 10 categorías más vendidas
            data_categorias = sorted(
                [[categ, qty] for categ, qty in categoria_data.items()], key=lambda x: x[1], reverse=True
            )[:10]

            # Mapeo de las ventas por producto y su cantidad total
            product_sales = {}
            for venta in ventas:
                product = venta.product_id
                quantity = venta.quantity * venta.product_uom_id.factor  # Multiplicamos por el factor de la UOM
                if product.id not in product_sales:
                    product_sales[product.id] = 0
                product_sales[product.id] += quantity

            # Filtrar los productos de baja rotación (p.ej., menos de 10 unidades vendidas en el mes)
            low_rotation_products = [
                (request.env['product.product'].browse(pid), qty)
                for pid, qty in product_sales.items() if qty < 10  # Definir umbral de baja rotación
            ]
            data_baja_rotacion = [
                [prod.product_tmpl_id.name, qty] for prod, qty in low_rotation_products  # List format [nombre, cantidad]
            ]

            # Filtrar los productos más vendidos
            top_selling_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]
            data_mas_vendidos = [
                [index+1, request.env['product.product'].browse(pid).product_tmpl_id.name, qty] 
                for index, (pid, qty) in enumerate(top_selling_products)
            ]

           

            # Negocio que más vende (product.business)
            ventas_por_producto = request.env['account.move.line'].search([
                ('move_id.move_type', 'in', ['out_invoice', 'out_receipt']),  # Filtramos solo ventas y boletas
                ('product_id.product_tmpl_id.negocio', '!=', False)  # Aseguramos que el producto tiene un negocio
            ])

            # Crear un diccionario para contar la cantidad vendida por negocio
            negocio_sales = {}

            # Contabilizar las ventas por negocio
            for venta in ventas_por_producto:
                negocio = venta.product_id.product_tmpl_id.negocio  # Obtener el negocio relacionado
                cantidad_vendida = venta.quantity * venta.product_uom_id.factor  # Multiplicamos por el factor de la UOM

                if negocio:  # Asegurarnos de que el negocio no sea nulo
                    if negocio not in negocio_sales:
                        negocio_sales[negocio] = 0
                    negocio_sales[negocio] += cantidad_vendida

            # Ordenamos los negocios por la cantidad vendida (de mayor a menor) y seleccionamos los 10 principales
            data_negocios_sorted = sorted(negocio_sales.items(), key=lambda x: x[1], reverse=True)[:10]

            # Crear los datos de negocios en el formato deseado
            data_negocios = [
                [negocio.name, cantidad] for negocio, cantidad in data_negocios_sorted
            ]

            # Día Giro de Productos
            productos = request.env['product.product'].search([], limit=20)
            dia_giro_data = []

            for producto in productos:
                # Obtener las líneas de factura asociadas al producto
                lineas_venta = request.env['account.move.line'].search([
                    ('product_id', '=', producto.id),
                    ('move_id.move_type', 'in', ['out_invoice', 'out_receipt']),  # Solo ventas y boletas
                    ('create_date', '!=', False)
                ])

                if not lineas_venta:
                    continue

                # Calcular el total de ventas
                total_ventas = sum(line.quantity * line.product_uom_id.factor for line in lineas_venta)  # Multiplicamos por el factor de la UOM

                # Obtener las fechas de las ventas
                fechas = [line.create_date.date() for line in lineas_venta]
                
                # Calcular los días entre la primera y última venta
                dias_vendidos = (max(fechas) - min(fechas)).days or 1  # Evita la división por cero

                # Promedio de ventas diarias
                promedio_diario = total_ventas / dias_vendidos

                # Obtener el stock actual del producto según la UOM (paquetes)
                stock_actual = producto.qty_available  # Usamos el factor para convertir a la unidad base

                # Calcular el Día de Giro
                dias_giro = round(stock_actual / promedio_diario, 2) if promedio_diario > 0 else "∞"

                # Calcular la cantidad necesaria para 20 y 40 días
                cantidad_20_dias = round((promedio_diario * 20) * producto.uom_po_id.factor, 2)
                cantidad_40_dias = round((promedio_diario * 40) * producto.uom_po_id.factor, 2)

                dia_giro_data.append([
                    producto.name,
                    round(promedio_diario, 2),
                    stock_actual,  # Mostrar el stock en paquetes
                    dias_giro,
                    cantidad_20_dias,
                    cantidad_40_dias
                ])
            

            # Top Clientes (Clientes que más han comprado)
            top_clientes = request.env['account.move.line'].read_group(
                [('move_id.move_type', 'in', ['out_invoice', 'out_receipt'])],
                ['partner_id', 'quantity'],
                ['partner_id'],
            )
            cliente_data = {}
            for v in top_clientes:
                if not v['partner_id']:
                    continue
                cliente_id = v['partner_id'][0]
                if cliente_id not in cliente_data:
                    cliente_data[cliente_id] = 0
                cliente_data[cliente_id] += v['quantity']

            # Obtener los 10 clientes con más compras
            sorted_clientes = sorted(cliente_data.items(), key=lambda x: x[1], reverse=True)[:10]
            data_top_clientes = [
                [request.env['res.partner'].browse(cliente_id).name, qty] for cliente_id, qty in sorted_clientes
            ]

            # Top Marcas (Marcas de productos más vendidas)
            top_marcas = request.env['account.move.line'].read_group(
                [('move_id.move_type', 'in', ['out_invoice', 'out_receipt'])],
                ['product_id', 'quantity'],
                ['product_id'],
            )
            marca_data = {}
            for v in top_marcas:
                if not v['product_id']:
                    continue
                product = request.env['product.product'].browse(v['product_id'][0])
                product_template = product.product_tmpl_id
                marca = product_template.brand_id.name if product_template.brand_id else 'Sin Marca'
                if marca not in marca_data:
                    marca_data[marca] = 0
                marca_data[marca] += v['quantity']

            data_top_marcas = sorted(
                [[marca, qty] for marca, qty in marca_data.items()], key=lambda x: x[1], reverse=True
            )[:10]


            return {
                "bajo_stock": data_bajo_stock,
                "baja_rotacion": data_baja_rotacion,
                "mas_vendidos": data_mas_vendidos,
                "categorias_vendidas": data_categorias,
                "negocios_top": data_negocios,
                "dia_giro": dia_giro_data,
                "clientes_top": data_top_clientes,
                "top_marcas": data_top_marcas,
            }

        except Exception as e:
            _logger.error(f"Error en /loan_dashboard/tablas: {str(e)}", exc_info=True)
            return {'error': str(e)}

    @http.route('/loan_dashboard/evolutivos', type='json', auth='user')
    def get_evolutivos(self):
        """Devuelve datos mensuales para evolución de ventas y pedidos."""
        try:
            today = fields.Date.today()
            start_date = today.replace(month=1, day=1)

            # Agrupar facturas por mes en soles
            ventas = request.env['account.move'].read_group(
                [('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('invoice_date', '>=', start_date)],
                ['amount_total', 'invoice_date'],
                ['invoice_date:month']
            )

            ventas_por_mes = {}
            for v in ventas:
                fecha = v['invoice_date:month']
                label = fecha.strftime('%B')
                ventas_por_mes[label] = ventas_por_mes.get(label, 0) + v['amount_total']

            # Agrupar número de pedidos (facturas + boletas) por mes
            pedidos = request.env['account.move'].read_group(
                [('move_type', 'in', ['out_invoice', 'out_receipt']), ('state', '=', 'posted'), ('invoice_date', '>=', start_date)],
                ['id'],
                ['invoice_date:month']
            )

            pedidos_por_mes = {}
            for p in pedidos:
                fecha = p['invoice_date:month']
                label = fecha.strftime('%B')
                pedidos_por_mes[label] = pedidos_por_mes.get(label, 0) + p['__count']

            def ordenar_labels(data_dict):
                orden = list(calendar.month_name)[1:]
                return sorted(data_dict.items(), key=lambda x: orden.index(x[0]))

            evolutivo_ventas = ordenar_labels(ventas_por_mes)
            evolutivo_pedidos = ordenar_labels(pedidos_por_mes)

            return {
                "evolutivoVentas": {
                    "labels": [v[0] for v in evolutivo_ventas],
                    "data": [v[1] for v in evolutivo_ventas],
                    "label": "Ventas Mensuales (S/.)",
                    "color": "#28a745",
                    "bgColor": "rgba(40,167,69,0.2)"
                },
                "evolutivoPedidos": {
                    "labels": [v[0] for v in evolutivo_pedidos],
                    "data": [v[1] for v in evolutivo_pedidos],
                    "label": "Cantidad de Pedidos",
                    "color": "#007bff",
                    "bgColor": "rgba(0,123,255,0.2)"
                }
            }

        except Exception as e:
            _logger.error(f"Error en /loan_dashboard/evolutivos: {str(e)}", exc_info=True)
            return {'error': str(e)}

    @http.route('/loan_dashboard/notify', type='json', auth='user')
    def notify(self, channel='broadcast', event='sse_dashboard.update', payload=None):
        """Publica una notificación en el bus para actualizar el dashboard en tiempo real.

        - channel: canal del bus (por defecto 'broadcast' para todos)
        - event: tipo de evento (por defecto 'sse_dashboard.update')
        - payload: dict opcional con datos adicionales
        """
        try:
            if payload is None:
                payload = {"timestamp": fields.Datetime.now().isoformat()}

            request.env['bus.bus']._sendone(channel, event, payload)
            _logger.info("Notificación enviada por bus: canal=%s evento=%s payload=%s", channel, event, payload)
            return {"status": "ok"}
        except Exception as e:
            _logger.error(f"Error en /loan_dashboard/notify: {str(e)}", exc_info=True)
            return {'error': str(e)}