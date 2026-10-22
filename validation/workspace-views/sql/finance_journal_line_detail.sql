SELECT
    l."TransId" AS "journal_entry",
    l."Line_ID" AS "journal_line",
    h."Number" AS "journal_no",
    h."RefDate" AS "posting_date",
    h."TaxDate" AS "document_date",
    h."DueDate" AS "due_date",
    l."Account" AS "account_code",
    a."FormatCode" AS "account_display_code",
    a."AcctName" AS "account_name",
    l."ShortName" AS "partner_or_account_code",
    l."LineMemo" AS "line_memo",
    l."Project" AS "line_project_code",
    l."Debit" AS "debit_lc",
    l."Credit" AS "credit_lc",
    CAST(l."Debit"-l."Credit" AS DECIMAL(19,6)) AS "net_debit_lc",
    l."FCDebit" AS "debit_fc",
    l."FCCredit" AS "credit_fc",
    l."FCCurrency" AS "foreign_currency",
    l."SYSDeb" AS "debit_sc",
    l."SYSCred" AS "credit_sc",
    h."TransType" AS "transaction_type",
    l."RefDate" AS "line_posting_date",
    l."TaxDate" AS "line_document_date",
    l."DueDate" AS "line_due_date"
FROM "jdt1" l
LEFT JOIN "ojdt" h ON h."TransId"=l."TransId"
LEFT JOIN "oact" a ON a."AcctCode"=l."Account"
