# Record Relationship Explorer

Odoo 19 Owl/JavaScript addon that turns the Action menu on any saved form record into a visual relationship explorer.

## What it does

- Adds **Explore Relationships** to the Action menu of saved form records.
- Opens a modern Owl/SVG graph without writing relationship data to the database.
- Makes every node clickable; clicking opens that record's form view.
- Adds a quick search box for the visible graph.
- Keeps large diagrams inside a scrollable viewport with vertical and horizontal scrolling.
- Provides a generic fallback for readable `many2one`, `one2many`, and `many2many` fields.
- Provides a curated Sale Order flow:
  - Customer -> Sale Order
  - Sale Order -> Invoice
  - Invoice -> Payment
  - Sale Order -> Delivery / Picking

The graph intentionally stays shallow and permission-aware. It shows up to eight related records per relationship, respects Odoo access rights, and avoids chatter/follower noise.

## Installation

1. Copy this folder into the Odoo 19 addons path.
2. Restart Odoo, update the Apps list, and install **Record Relationship Explorer**.
3. Open any saved record, use the top-right **Action** menu, and select **Explore Relationships**.
4. Refresh assets with `Ctrl+F5` if the browser still shows the old backend bundle.

For the Sale Order example, install the Sales, Invoicing, and Inventory features so invoice and delivery relationships exist.

## Technical structure

- `models/relationship_explorer.py` builds a safe graph response through the ORM.
- `static/src/js/relationship_explorer.js` registers the client action and patches the Odoo 19 FormController action menu.
- `static/src/xml/relationship_explorer.xml` defines the Owl UI.
- `static/src/scss/relationship_explorer.scss` provides the graph canvas, node styling, search toolbar, and responsive layout.

## Validation status

The addon is source-created for the local Odoo 19 workspace. Run an Odoo module upgrade and browser smoke test before treating it as production-ready.
