from odoo import api, models
from odoo.exceptions import AccessError, MissingError


class RecordRelationshipExplorer(models.AbstractModel):
    _name = 'record.relationship.explorer'
    _description = 'Record Relationship Explorer'

    _MAX_RELATED = 8

    @api.model
    def get_graph(self, model_name, record_id):
        """Return a safe, read-only graph for one record.

        Sale Orders use a curated business-flow graph. Other models fall back
        to their readable relational fields, which keeps the explorer useful
        from any saved form without trying to recursively crawl the database.
        """
        if not model_name or not record_id or model_name not in self.env:
            return {'nodes': [], 'edges': [], 'title': 'Relationship Explorer'}

        record = self.env[model_name].browse(int(record_id)).exists()
        if not record:
            raise MissingError('The selected record no longer exists.')
        record.check_access('read')
        record.ensure_one()

        graph = {
            'nodes': [],
            'edges': [],
            'title': record.display_name or model_name,
            'model': model_name,
            'record_id': record.id,
        }
        seen = set()

        def add_node(value, role=None, level=1, side='right'):
            if not value:
                return None
            value = value[0] if len(value) > 1 else value
            key = (value._name, value.id)
            if key in seen:
                return f'{value._name}:{value.id}'
            try:
                value.check_access('read')
                display_name = value.display_name or f'{value._name},{value.id}'
            except (AccessError, MissingError):
                return None
            seen.add(key)
            graph['nodes'].append({
                'id': f'{value._name}:{value.id}',
                'model': value._name,
                'res_id': value.id,
                'label': display_name,
                'role': role or self._model_label(value._name),
                'level': level,
                'side': side,
            })
            return f'{value._name}:{value.id}'

        root_id = add_node(record, role=self._model_label(model_name), level=0, side='center')
        if not root_id:
            return graph

        def connect(source, target, label=''):
            if source and target and source != target:
                graph['edges'].append({
                    'source': source,
                    'target': target,
                    'label': label,
                })

        if model_name == 'sale.order':
            self._build_sale_order_graph(record, root_id, add_node, connect)
        else:
            self._build_generic_graph(record, root_id, add_node, connect)
        return graph

    def _build_sale_order_graph(self, order, root_id, add_node, connect):
        customer = add_node(order.partner_id, role='Customer', level=1, side='left')
        connect(customer, root_id, 'customer')

        invoices = order.invoice_ids._filtered_access('read')[:self._MAX_RELATED]
        for invoice in invoices:
            invoice_id = add_node(invoice, role='Invoice', level=1, side='right')
            connect(root_id, invoice_id, 'invoice')
            payments = (invoice.reconciled_payment_ids | invoice.matched_payment_ids)._filtered_access('read')
            for payment in payments[:self._MAX_RELATED]:
                payment_id = add_node(payment, role='Payment', level=2, side='right')
                connect(invoice_id, payment_id, 'payment')

        pickings = order.picking_ids._filtered_access('read')[:self._MAX_RELATED]
        for picking in pickings:
            picking_id = add_node(picking, role='Delivery / Picking', level=1, side='right')
            connect(root_id, picking_id, 'delivery')

    def _build_generic_graph(self, record, root_id, add_node, connect):
        fields = sorted(
            record._fields.values(),
            key=lambda field: (field.type not in ('many2one', 'one2many', 'many2many'), field.string or field.name),
        )
        relation_count = 0
        for field in fields:
            if field.type not in ('many2one', 'one2many', 'many2many'):
                continue
            if field.name in {'message_follower_ids', 'message_ids', 'activity_ids', 'access_token'}:
                continue
            try:
                related = record[field.name]
                related = related._filtered_access('read') if related else related
            except (AccessError, MissingError, KeyError):
                continue
            if not related:
                continue
            side = 'left' if field.type == 'many2one' else 'right'
            for value in related[:self._MAX_RELATED]:
                related_id = add_node(value, role=field.string or field.name, level=1, side=side)
                connect(root_id, related_id, field.string or field.name)
                relation_count += 1
                if relation_count >= self._MAX_RELATED * 2:
                    return

    def _model_label(self, model_name):
        try:
            return self.env['ir.model']._get(model_name).name or model_name
        except (AccessError, MissingError):
            return model_name
