SELECT
    q."AbsEntry" AS "balance_entry",
    q."ItemCode" AS "item_code",
    i."ItemName" AS "item_name",
    q."WhsCode" AS "warehouse_code",
    q."BinAbs" AS "bin_entry",
    n."BinCode" AS "bin_code",
    q."OnHandQty" AS "on_hand_quantity",
    i."InvntryUom" AS "current_inventory_unit"
FROM "oibq" q
LEFT JOIN "obin" n ON n."AbsEntry"=q."BinAbs"
LEFT JOIN "oitm" i ON i."ItemCode"=q."ItemCode"
