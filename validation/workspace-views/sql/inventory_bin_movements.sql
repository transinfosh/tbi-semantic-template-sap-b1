SELECT
    t."AbsEntry" AS "bin_transaction_entry",
    t."MessageID" AS "message_entry",
    t."ITLEntry" AS "batch_serial_log_entry",
    m."TransType" AS "document_type",
    m."DocEntry" AS "document_entry",
    m."DocLineNum" AS "document_line",
    m."SubLineNum" AS "document_subline",
    m."DocDate" AS "posting_date",
    m."ItemCode" AS "item_code",
    m."ActionType" AS "action_type",
    m."AccumType" AS "accumulator_type",
    m."SnBType" AS "management_type",
    t."SnBMDAbs" AS "master_entry",
    COALESCE(b."DistNumber",s."DistNumber") AS "batch_serial_number",
    t."BinAbs" AS "bin_entry",
    n."BinCode" AS "bin_code",
    n."WhsCode" AS "warehouse_code",
    m."LocCode" AS "message_location_code",
    m."LocType" AS "message_location_type",
    t."Quantity" AS "raw_bin_quantity",
    CAST(CASE WHEN m."ActionType" IN (1,19) THEN 'in' WHEN m."ActionType" IN (2,20) THEN 'out' ELSE 'other' END AS VARCHAR(8)) AS "movement_direction"
FROM "obtl" t
LEFT JOIN "oilm" m ON m."MessageID"=t."MessageID"
LEFT JOIN "obin" n ON n."AbsEntry"=t."BinAbs"
LEFT JOIN "obtn" b ON m."SnBType"=10000044 AND b."AbsEntry"=t."SnBMDAbs" AND b."ItemCode"=m."ItemCode"
LEFT JOIN "osrn" s ON m."SnBType"=10000045 AND s."AbsEntry"=t."SnBMDAbs" AND s."ItemCode"=m."ItemCode"
