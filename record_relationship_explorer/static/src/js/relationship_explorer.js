import { Component, onWillStart, useState } from "@odoo/owl";

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";


export class RecordRelationshipExplorer extends Component {
    static template = "record_relationship_explorer.RecordRelationshipExplorer";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
        this.onNodeClick = async (event) => {
            const button = event.currentTarget;
            const model = button.dataset.model;
            const recordId = Number(button.dataset.resId);
            await this.actionService.doAction({
                type: "ir.actions.act_window",
                name: button.dataset.label,
                res_model: model,
                res_id: recordId,
                views: [[false, "form"]],
                target: "current",
            });
        };
        this.state = useState({
            graph: { nodes: [], edges: [], title: _t("Relationship Explorer") },
            loading: true,
            error: false,
            query: "",
        });
        onWillStart(() => this.loadGraph());
    }

    async loadGraph() {
        const context = this.props.action.context || {};
        const model = context.active_model || this.props.action.res_model;
        const recordId = context.active_id || this.props.action.res_id;
        if (!model || !recordId) {
            this.state.loading = false;
            this.state.error = true;
            return;
        }
        try {
            this.state.graph = await this.orm.call(
                "record.relationship.explorer",
                "get_graph",
                [model, recordId],
            );
        } catch (error) {
            this.state.error = true;
            this.notification.add(_t("The relationship graph could not be loaded."), {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
    }

    get nodes() {
        return this.state.graph.nodes || [];
    }

    get visibleNodes() {
        const query = this.state.query.trim().toLowerCase();
        if (!query) {
            return this.nodes;
        }
        return this.nodes.filter((node) =>
            [node.label, node.role, node.model].some((value) =>
                (value || "").toLowerCase().includes(query)
            )
        );
    }

    get visibleEdges() {
        const visibleIds = new Set(this.visibleNodes.map((node) => node.id));
        return (this.state.graph.edges || []).filter(
            (edge) => visibleIds.has(edge.source) && visibleIds.has(edge.target)
        );
    }

    get canvasHeight() {
        const deepest = Math.max(0, ...this.nodes.map((node) => node.level || 0));
        const sideCounts = ["left", "right"].map(
            (side) => this.nodes.filter((node) => node.side === side).length
        );
        return Math.max(700, Math.max(...sideCounts, 1) * 145 + 100, deepest > 1 ? 850 : 700);
    }

    nodePosition(nodeId) {
        const node = this.nodes.find((item) => item.id === nodeId);
        if (!node) {
            return { x: 0, y: 0 };
        }
        if (node.side === "center") {
            return { x: 560, y: this.canvasHeight / 2 };
        }
        const peers = this.nodes.filter(
            (item) => item.side === node.side && item.level === node.level
        );
        const index = Math.max(0, peers.findIndex((item) => item.id === node.id));
        const y = 90 + index * 145;
        const x = node.side === "left" ? 140 : node.level > 1 ? 1110 : 850;
        return { x, y };
    }

    nodeStyle(node) {
        const position = this.nodePosition(node.id);
        return `left: ${position.x - 105}px; top: ${position.y - 45}px;`;
    }

    nodeCenter(nodeId) {
        return this.nodePosition(nodeId);
    }

    nodeClass(node) {
        return `rre-node rre-node-${node.side || "right"} ${node.level === 0 ? "rre-node-root" : ""}`;
    }

    setQuery(event) {
        this.state.query = event.target.value;
    }

}

registry.category("actions").add("record_relationship_explorer", RecordRelationshipExplorer);

patch(FormController.prototype, {
    getStaticActionMenuItems() {
        const items = super.getStaticActionMenuItems(...arguments);
        items.exploreRelationships = {
            isAvailable: () => !this.model.root.isNew && Boolean(this.model.root.resId),
            sequence: 20,
            icon: "fa fa-sitemap",
            description: _t("Explore Relationships"),
            callback: () => this.actionService.doAction({
                type: "ir.actions.client",
                tag: "record_relationship_explorer",
                name: _t("Relationship Explorer"),
                context: {
                    ...this.model.root.context,
                    active_model: this.model.root.resModel,
                    active_id: this.model.root.resId,
                },
            }),
        };
        return items;
    },
});
