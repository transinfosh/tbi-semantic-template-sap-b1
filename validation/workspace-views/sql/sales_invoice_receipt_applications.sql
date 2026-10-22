SELECT
    a."DocNum" AS "payment_entry",
    a."InvoiceId" AS "application_line",
    a."InvType" AS "target_object_type",
    a."DocEntry" AS "invoice_entry",
    a."InstId" AS "installment_id",
    a."DocLine" AS "target_document_line",
    p."DocNum" AS "payment_no",
    p."DocDate" AS "payment_date",
    p."Canceled" AS "payment_cancellation",
    p."DocCurr" AS "payment_currency",
    i."DocNum" AS "invoice_no",
    i."DocDate" AS "invoice_date",
    i."DocDueDate" AS "invoice_due_date",
    i."CANCELED" AS "invoice_cancellation",
    i."CardCode" AS "partner_code",
    i."CardName" AS "partner_name",
    i."DocCur" AS "invoice_currency",
    a."SumApplied" AS "applied_amount_lc",
    a."AppliedFC" AS "applied_amount_fc",
    a."AppliedSys" AS "applied_amount_sc",
    a."DcntSum" AS "cash_discount_lc",
    a."DcntSumFC" AS "cash_discount_fc",
    a."DcntSumSy" AS "cash_discount_sc",
    a."WtAppld" AS "withholding_applied_lc",
    a."LinkDate" AS "application_date"
FROM "rct2" a
LEFT JOIN "orct" p ON p."DocEntry"=a."DocNum"
LEFT JOIN "oinv" i ON i."DocEntry"=a."DocEntry"
WHERE a."InvType"='13'
