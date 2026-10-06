from typing import Any, Dict, List, Optional
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.tools.file_tools import CSVReaderTool

class OrderLookupTool(BaseTool):
    name = "order_lookup"
    description = "Searches the order database by Order ID or customer email."

    def run(self, identifier: str, **kwargs) -> ToolResult:
        ident_clean = str(identifier).strip().lower()
        if not ident_clean:
            return ToolResult(success=False, error="Order identifier cannot be empty.")

        # Load from sample orders CSV
        csv_tool = CSVReaderTool()
        res = csv_tool.run(file_path="sample_data/orders.csv")
        orders: List[Dict[str, Any]] = res.data if res.success else []

        # Find matching order
        matched = None
        for ord_item in orders:
            ord_id = str(ord_item.get("order_id", "")).strip().lower()
            email = str(ord_item.get("customer_email", "")).strip().lower()
            if ord_id == ident_clean or email == ident_clean:
                matched = ord_item
                break

        if not matched:
            return ToolResult(
                success=False,
                data=None,
                error=f"No order found matching identifier '{identifier}'. Please check the order ID or customer email."
            )

        return ToolResult(
            success=True,
            data=matched,
            message=f"Order '{matched.get('order_id')}' found successfully."
        )


class ShipmentLookupTool(BaseTool):
    name = "shipment_lookup"
    description = "Retrieves real-time carrier shipment and tracking details for an order."

    def run(self, order_data: Dict[str, Any], **kwargs) -> ToolResult:
        tracking_num = order_data.get("tracking_number")
        carrier = order_data.get("shipment_carrier")
        status = order_data.get("shipment_status", order_data.get("status", "Processing"))
        est_delivery = order_data.get("estimated_delivery")

        if not tracking_num or str(tracking_num).strip().lower() in ("none", "", "nan"):
            return ToolResult(
                success=True,
                data={
                    "carrier": carrier or "N/A",
                    "tracking_number": "Pending Generation",
                    "shipment_status": status,
                    "estimated_delivery": est_delivery or "To be determined",
                    "tracking_url": None
                },
                message="Order is currently in preparation; tracking number not yet assigned."
            )

        return ToolResult(
            success=True,
            data={
                "carrier": carrier,
                "tracking_number": tracking_num,
                "shipment_status": status,
                "estimated_delivery": est_delivery,
                "tracking_url": f"https://track.{str(carrier).lower()}.com/{tracking_num}"
            },
            message=f"Shipment {tracking_num} via {carrier} is '{status}'."
        )
