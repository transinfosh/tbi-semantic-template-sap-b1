SELECT
    l."LogEntry" AS "log_entry",
    t."ItemCode" AS "item_code",
    t."SysNumber" AS "system_number",
    t."MdAbsEntry" AS "master_entry",
    l."ManagedBy" AS "management_type",
    COALESCE(b."DistNumber",s."DistNumber") AS "batch_serial_number",
    l."DocType" AS "document_type",
    l."DocEntry" AS "document_entry",
    l."DocLine" AS "document_line",
    l."ApplyType" AS "apply_document_type",
    l."ApplyEntry" AS "apply_document_entry",
    l."ApplyLine" AS "apply_document_line",
    l."DocDate" AS "posting_date",
    l."LocCode" AS "warehouse_code",
    l."LocType" AS "location_type",
    l."StockEff" AS "stock_effect",
    t."Quantity" AS "signed_inventory_quantity"
FROM "oitl" l
JOIN "itl1" t ON t."LogEntry"=l."LogEntry" AND t."ItemCode"=l."ItemCode"
LEFT JOIN "obtn" b ON l."ManagedBy"=10000044 AND b."ItemCode"=t."ItemCode" AND b."SysNumber"=t."SysNumber"
LEFT JOIN "osrn" s ON l."ManagedBy"=10000045 AND s."ItemCode"=t."ItemCode" AND s."SysNumber"=t."SysNumber"
WHERE l."StockEff"=1 AND l."ManagedBy" IN (10000044,10000045)
