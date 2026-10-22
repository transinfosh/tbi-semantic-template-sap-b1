-- Read-only investigation at invoice-header grain; not an open-payables calculation.
-- Retain all statuses and nulls. MATCH does not establish semantic equivalence or settlement.
-- Confirm source schema/types and company currencies before use; never convert at current rates.
SELECT
    DocEntry, CANCELED, DocManClsd, DocStatus, DocCur,
    DocTotal, DocTotalFC, DocTotalSy,
    PaidSum, PaidSumFc, PaidSumSc,
    PaidToDate, PaidFC, PaidSys,
    PaidSum - PaidToDate AS PaidSumDifference,
    PaidSumFc - PaidFC AS PaidSumFcDifference,
    PaidSumSc - PaidSys AS PaidSumScDifference,
    CASE
        WHEN PaidSum IS NULL OR PaidToDate IS NULL THEN 'UNKNOWN_NULL'
        WHEN PaidSum = PaidToDate THEN 'MATCH'
        ELSE 'DIFFERENT'
    END AS PaidSumComparison,
    CASE
        WHEN PaidSumFc IS NULL OR PaidFC IS NULL THEN 'UNKNOWN_NULL'
        WHEN PaidSumFc = PaidFC THEN 'MATCH'
        ELSE 'DIFFERENT'
    END AS PaidSumFcComparison,
    CASE
        WHEN PaidSumSc IS NULL OR PaidSys IS NULL THEN 'UNKNOWN_NULL'
        WHEN PaidSumSc = PaidSys THEN 'MATCH'
        ELSE 'DIFFERENT'
    END AS PaidSumScComparison
FROM dbo.OPCH
ORDER BY DocEntry;
