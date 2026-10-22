SELECT
    q."ItemCode" AS "item_code",
    i."ItemName" AS "item_name",
    q."WhsCode" AS "warehouse_code",
    w."WhsName" AS "warehouse_name",
    i."InvntryUom" AS "current_inventory_unit",
    q."OnHand" AS "on_hand_quantity",
    q."IsCommited" AS "committed_quantity",
    q."OnOrder" AS "on_order_quantity",
    CAST(q."OnHand"-q."IsCommited"+q."OnOrder" AS DECIMAL(19,6)) AS "projected_available_quantity",
    q."Locked" AS "warehouse_item_locked"
FROM "oitw" q
LEFT JOIN "oitm" i ON i."ItemCode"=q."ItemCode"
LEFT JOIN "owhs" w ON w."WhsCode"=q."WhsCode"
