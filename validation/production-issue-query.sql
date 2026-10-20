-- Reference query, not a default workspace View or a completed SAP report.
-- Resolve the requested work order to its internal DocEntry before binding this parameter.
-- Scope all issue lines first; derive actual dates from OIGE, without guessing monthly boundaries.
-- Amounts retain inventory movement signs; issue_cost explicitly reverses that sign, never ABS.
-- stored_inventory_unit_price is the document field; effective_unit_cost is the rounded posting
-- amount divided by inventory quantity, not the valuation layer calculation price or AVG(row price).
-- Interpret stock movement value in the company local currency after target accounting validation.
-- Read OADM configuration separately; do not cross join company configuration with facts.
-- Material categories, reporting dates and return/cancellation policies belong to the workspace.
WITH issue_scope AS (
    SELECT
        ige1.*, owor.Type AS production_order_type,
        oige.DocDate AS posting_date, oige.CreateDate AS creation_date,
        oige.CANCELED AS cancellation_status,
        wor1.LineNum AS component_line_num, wor1.IssueType AS issue_method,
        oitm.InvntItem AS inventory_item
    FROM dbo.IGE1 ige1
    JOIN dbo.OWOR owor ON ige1.BaseEntry = owor.DocEntry AND ige1.BaseType = 202
    JOIN dbo.OIGE oige ON oige.DocEntry = ige1.DocEntry
    LEFT JOIN dbo.WOR1 wor1
        ON ige1.BaseEntry = wor1.DocEntry AND ige1.BaseLine = wor1.LineNum AND ige1.BaseType = 202
    LEFT JOIN dbo.OITM oitm ON ige1.ItemCode = oitm.ItemCode AND ige1.ItemType = 4
    WHERE owor.DocEntry = @production_order_entry
), valuation_scope AS (
    SELECT oivl.*
    FROM dbo.OIVL oivl
    JOIN issue_scope ige1
        ON oivl.CreatedBy = ige1.DocEntry AND oivl.DocLineNum = ige1.LineNum AND oivl.TransType = 60
), layer_totals AS (
    SELECT
        oivl.TransSeq,
        COUNT(ivl1.TransSeq) AS layer_count,
        COUNT(ivl1.TransValue) AS valued_layer_count,
        SUM(ivl1.TransValue) AS raw_layer_value,
        MIN(ivl1.CalcPrice) AS minimum_layer_calculation_price,
        MAX(ivl1.CalcPrice) AS maximum_layer_calculation_price
    FROM valuation_scope oivl
    LEFT JOIN dbo.IVL1 ivl1 ON ivl1.TransSeq = oivl.TransSeq
    GROUP BY oivl.TransSeq
), issue_valuation AS (
    SELECT
        oivl.CreatedBy, oivl.DocLineNum,
        COUNT(*) AS valuation_transactions,
        SUM(layer_totals.layer_count) AS valuation_layers,
        CASE WHEN COUNT(oivl.OutQty) = COUNT(*) AND COUNT(oivl.InQty) = COUNT(*)
             THEN SUM(oivl.OutQty - oivl.InQty) END AS valuation_issue_quantity,
        CASE WHEN COUNT(oivl.SumStock) = COUNT(*)
             THEN SUM(oivl.SumStock) END AS stock_movement_value,
        CASE WHEN MIN(layer_totals.layer_count) > 0
                  AND SUM(layer_totals.valued_layer_count) = SUM(layer_totals.layer_count)
             THEN SUM(layer_totals.raw_layer_value) END AS layer_movement_value,
        MIN(layer_totals.minimum_layer_calculation_price) AS minimum_layer_calculation_price,
        MAX(layer_totals.maximum_layer_calculation_price) AS maximum_layer_calculation_price
    FROM valuation_scope oivl
    JOIN layer_totals ON layer_totals.TransSeq = oivl.TransSeq
    GROUP BY oivl.CreatedBy, oivl.DocLineNum
)
SELECT
    issue_scope.BaseEntry AS production_order_entry,
    issue_scope.production_order_type,
    issue_scope.DocEntry AS issue_doc_entry, issue_scope.LineNum AS issue_line_num,
    issue_scope.BaseLine AS source_component_line_num, issue_scope.component_line_num,
    issue_scope.posting_date, issue_scope.creation_date, issue_scope.cancellation_status,
    issue_scope.ItemCode AS item_code, issue_scope.ItemType AS item_type,
    issue_scope.WhsCode AS warehouse_code, issue_scope.issue_method,
    issue_scope.inventory_item,
    issue_scope.Quantity AS document_quantity, issue_scope.InvQty AS inventory_quantity,
    issue_scope.unitMsr AS document_unit, issue_scope.UomCode AS document_unit_code,
    issue_scope.UseBaseUn AS use_base_unit, issue_scope.NumPerMsr AS items_per_document_unit,
    issue_scope.StockSum AS document_stock_sum,
    issue_scope.StockValue AS source_cogs_value,
    issue_scope.LineTotal AS source_line_total,
    issue_scope.StockPrice AS stored_inventory_unit_price,
    COALESCE(issue_valuation.valuation_transactions, 0) AS valuation_transactions,
    COALESCE(issue_valuation.valuation_layers, 0) AS valuation_layers,
    issue_valuation.valuation_issue_quantity,
    issue_valuation.stock_movement_value,
    issue_valuation.layer_movement_value,
    issue_valuation.minimum_layer_calculation_price,
    issue_valuation.maximum_layer_calculation_price,
    -issue_valuation.stock_movement_value AS issue_cost,
    -issue_valuation.stock_movement_value / NULLIF(1.0 * issue_scope.InvQty, 0)
        AS effective_unit_cost,
    CASE
        WHEN issue_valuation.valuation_transactions IS NULL AND issue_scope.inventory_item = 'N'
            THEN 'not_inventory_valued'
        WHEN issue_valuation.valuation_transactions IS NULL THEN 'missing_valuation'
        WHEN issue_valuation.stock_movement_value IS NULL THEN 'incomplete_valuation_value'
        ELSE 'available'
    END AS valuation_status
FROM issue_scope
LEFT JOIN issue_valuation
    ON issue_valuation.CreatedBy = issue_scope.DocEntry
   AND issue_valuation.DocLineNum = issue_scope.LineNum
ORDER BY issue_scope.posting_date, issue_scope.DocEntry, issue_scope.LineNum;
