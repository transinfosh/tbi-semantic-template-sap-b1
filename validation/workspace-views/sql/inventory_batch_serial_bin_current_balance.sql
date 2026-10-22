WITH balances AS (
SELECT batch_balance."AbsEntry" AS balance_entry, 10000044 AS management_type, batch_balance."ItemCode" AS item_code, batch_balance."SnBMDAbs" AS master_entry, batch_master."DistNumber" AS batch_serial_number, batch_balance."WhsCode" AS warehouse_code, batch_balance."BinAbs" AS bin_entry, batch_bin."BinCode" AS bin_code, batch_balance."OnHandQty" AS on_hand_quantity
FROM "obbq" batch_balance LEFT JOIN "obtn" batch_master ON batch_master."AbsEntry"=batch_balance."SnBMDAbs" AND batch_master."ItemCode"=batch_balance."ItemCode" LEFT JOIN "obin" batch_bin ON batch_bin."AbsEntry"=batch_balance."BinAbs"
UNION ALL
SELECT serial_balance."AbsEntry" AS balance_entry, 10000045 AS management_type, serial_balance."ItemCode" AS item_code, serial_balance."SnBMDAbs" AS master_entry, serial_master."DistNumber" AS batch_serial_number, serial_balance."WhsCode" AS warehouse_code, serial_balance."BinAbs" AS bin_entry, serial_bin."BinCode" AS bin_code, serial_balance."OnHandQty" AS on_hand_quantity
FROM "osbq" serial_balance LEFT JOIN "osrn" serial_master ON serial_master."AbsEntry"=serial_balance."SnBMDAbs" AND serial_master."ItemCode"=serial_balance."ItemCode" LEFT JOIN "obin" serial_bin ON serial_bin."AbsEntry"=serial_balance."BinAbs"
)
SELECT
    CAST(balance_rows.balance_entry AS INTEGER) AS "balance_entry",
    CAST(balance_rows.management_type AS INTEGER) AS "management_type",
    balance_rows.item_code AS "item_code",
    CAST(balance_rows.master_entry AS INTEGER) AS "master_entry",
    balance_rows.batch_serial_number AS "batch_serial_number",
    balance_rows.warehouse_code AS "warehouse_code",
    CAST(balance_rows.bin_entry AS INTEGER) AS "bin_entry",
    balance_rows.bin_code AS "bin_code",
    CAST(balance_rows.on_hand_quantity AS DECIMAL(19,6)) AS "on_hand_quantity",
    i."InvntryUom" AS "current_inventory_unit"
FROM balances balance_rows
LEFT JOIN "oitm" i ON i."ItemCode"=balance_rows.item_code
