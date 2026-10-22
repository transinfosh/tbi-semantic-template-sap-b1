WITH routes AS (
    SELECT r."DocEntry" AS order_entry, r."LineNum" AS order_line,
           d."DocEntry" AS logistics_entry, d."LineNum" AS logistics_line,
           i."DocEntry" AS invoice_entry, i."LineNum" AS invoice_line,
           CAST('order_logistics_invoice' AS VARCHAR(32)) AS path_kind
    FROM "rdr1" r
    LEFT JOIN "dln1" d ON d."BaseType" = 17 AND d."BaseEntry" = r."DocEntry" AND d."BaseLine" = r."LineNum"
    LEFT JOIN "inv1" i ON i."BaseType" = 15 AND i."BaseEntry" = d."DocEntry" AND i."BaseLine" = d."LineNum"
    WHERE d."DocEntry" IS NOT NULL OR NOT EXISTS (
        SELECT 1 FROM "inv1" direct_invoice WHERE direct_invoice."BaseType" = 17
        AND direct_invoice."BaseEntry" = r."DocEntry" AND direct_invoice."BaseLine" = r."LineNum"
    )
    UNION ALL
    SELECT r."DocEntry", r."LineNum", d."DocEntry", d."LineNum", i."DocEntry", i."LineNum",
           CAST(CASE WHEN d."DocEntry" IS NULL THEN 'order_invoice' ELSE 'order_invoice_logistics' END AS VARCHAR(32))
    FROM "rdr1" r
    JOIN "inv1" i ON i."BaseType" = 17 AND i."BaseEntry" = r."DocEntry" AND i."BaseLine" = r."LineNum"
    LEFT JOIN "dln1" d ON d."BaseType" = 13 AND d."BaseEntry" = i."DocEntry" AND d."BaseLine" = i."LineNum"
)
SELECT
    CAST(p.path_kind AS VARCHAR(32)) AS "path_kind",
    CAST(p.order_entry AS INTEGER) AS "order_entry",
    o."DocNum" AS "order_no",
    CAST(p.order_line AS INTEGER) AS "order_line",
    o."DocDate" AS "order_date",
    o."DocDueDate" AS "order_due_date",
    o."CANCELED" AS "order_cancellation",
    o."DocStatus" AS "order_status",
    o."CardCode" AS "partner_code",
    o."CardName" AS "partner_name",
    r."ItemCode" AS "item_code",
    r."Dscription" AS "item_description",
    r."LineStatus" AS "order_line_status",
    r."LinManClsd" AS "order_line_manual_close",
    CAST(p.logistics_entry AS INTEGER) AS "logistics_entry",
    h."DocNum" AS "logistics_no",
    CAST(p.logistics_line AS INTEGER) AS "logistics_line",
    h."DocDate" AS "logistics_date",
    h."CANCELED" AS "logistics_cancellation",
    CAST(p.invoice_entry AS INTEGER) AS "invoice_entry",
    ih."DocNum" AS "invoice_no",
    CAST(p.invoice_line AS INTEGER) AS "invoice_line",
    ih."DocDate" AS "invoice_date",
    ih."CANCELED" AS "invoice_cancellation",
    ih."isIns" AS "reserve_invoice_flag",
    a."DocNum" AS "payment_entry",
    ph."DocNum" AS "payment_no",
    a."InvoiceId" AS "payment_application_line",
    a."InstId" AS "installment_id",
    ph."DocDate" AS "payment_date",
    ph."Canceled" AS "payment_cancellation"
FROM routes p
JOIN "rdr1" r ON r."DocEntry"=p.order_entry AND r."LineNum"=p.order_line
JOIN "ordr" o ON o."DocEntry"=p.order_entry
LEFT JOIN "odln" h ON h."DocEntry"=p.logistics_entry
LEFT JOIN "oinv" ih ON ih."DocEntry"=p.invoice_entry
LEFT JOIN "rct2" a ON a."InvType"='13' AND a."DocEntry"=p.invoice_entry
LEFT JOIN "orct" ph ON ph."DocEntry"=a."DocNum"
