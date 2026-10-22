SELECT
    p."DocEntry" AS "production_order_entry",
    p."DocNum" AS "production_order_no",
    p."Type" AS "production_order_type",
    p."Status" AS "production_order_status",
    p."ItemCode" AS "order_product_code",
    h."DocEntry" AS "document_entry",
    h."DocNum" AS "document_no",
    l."LineNum" AS "document_line",
    h."DocDate" AS "posting_date",
    h."CANCELED" AS "cancellation_status",
    l."BaseLine" AS "source_component_line",
    l."ItemType" AS "item_type",
    l."ItemCode" AS "item_code",
    l."Dscription" AS "item_description",
    l."WhsCode" AS "warehouse_code",
    l."Quantity" AS "document_quantity",
    l."InvQty" AS "inventory_quantity",
    l."unitMsr" AS "historical_document_unit",
    l."UomCode" AS "historical_uom_code",
    l."UseBaseUn" AS "use_base_unit",
    l."NumPerMsr" AS "items_per_unit",
    l."StockSum" AS "document_stock_sum_lc",
    l."StockPrice" AS "stored_inventory_price",
    l."Project" AS "line_project_code",
    w."ItemCode" AS "component_code",
    w."IssueType" AS "issue_method"
FROM "ige1" l
JOIN "oige" h ON h."DocEntry"=l."DocEntry"
LEFT JOIN "owor" p ON p."DocEntry"=l."BaseEntry"
LEFT JOIN "wor1" w ON w."DocEntry"=l."BaseEntry" AND w."LineNum"=l."BaseLine"
WHERE l."BaseType"=202
