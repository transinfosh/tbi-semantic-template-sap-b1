# 生产模块字段与关系审查

审查日期：2026-10-22。范围为公共模板生产四表及其跨库存执行与估价路径。仅读取模板、既有合成测试与 SAP 官方资料；未读取业务数据、未改模型、未发布。下列 JSON 为实施候选清单，须与目标物理列核对；本报告不是已实施清单或真实成本验收结论。

## 结论与本轮建议

生产主链已经包含 BOM、工单、物料/资源组件、实际发料与收货以及库存估价。主要缺口是工单产品仓库、名称与单位快照、开始和下达日期、组件项目与在制品科目，以及 BOM 资源组件关系。生产四表没有需要为了精简而删除的现有字段；已有金额和数量职责多数正确。

存在一处确定的错误：`OWOR.CmpltQty/RjctQty` 的描述把 SDK 枚举数值 `0/1` 当作数据库 `IGN1.TranType` 的值。数据库列实际列举 `C/R`，本轮应修正元数据以防生成错误 SQL。字段类型与物理数据无需改动。[数据库 IGN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ign1.html)、[SDK 枚举](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Enumerations~BoTransactionTypeEnum_EN.html)、[完成量属性](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~ProductionOrders~CompletedQuantity.html)、[拒收量属性](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~ProductionOrders~RejectedQuantity.html)。

建议先补字段与明确的多对一维度关系。暂不默认增加工序、产能分配、工序排程或成本分解表；增加 `StageId` 可保留工序判别，但不能宣称已经具备工序分析。共享资源和分配规则主数据继续归共享主数据。

## 现有四表全部字段的去留

以下清单覆盖本次读取的四表全部 54 列（8 + 12 + 20 + 14）。现有主键保持不变。表名、字段拼写、大小写均保留源系统约定。

| 模型 | 保留的全部现有字段 | 解释与修正 |
|---|---|---|
| OITT | Code、CreateDate、PriceList、Project、Qauntity、ToWH、TreeType、UpdateDate | 每个父项编码一条当前 BOM；`Qauntity` 是源表真实拼写。TreeType 保留装配、销售、生产、模板各型，不能把全部 BOM 数量算作生产需求。 |
| ITT1 | ChildNum、Code、Comment、Currency、Father、IssueMthd、Price、Project、Quantity、Type、Uom、Warehouse | `(Father,ChildNum)` 唯一组件行，不能按组件编码去重；价格、币种保留为 BOM 配置，不解释为历史实际成本。Uom 长度按官方 100 扩容。 |
| OWOR | CardCode、CloseDate、CmpltQty、CreateDate、DocEntry、DocNum、DueDate、ItemCode、OriginAbs、OriginNum、OriginType、PlannedQty、PostDate、Project、RjctQty、Series、Status、Type、UomEntry、UpdateDate | DocEntry 为工单内部键。生产类型、来源与状态保留；完成和拒收累计量修正数据库枚举说明。工单计划日期不是发料期间边界。 |
| WOR1 | AdditQty、BaseQty、CompTotal、DocEntry、IssuedQty、IssueType、ItemCode、ItemType、LineNum、PlannedQty、UomCode、UomEntry、VisOrder、wareHouse | `(DocEntry,LineNum)` 行键；保留已发数量与源完成金额。`CompTotal` 不能改称实际发料成本，不能默认删去它。 |

上述字段、主键及新增字段类型据 [OITT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OITT.html)、[ITT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html)、[OWOR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html)、[WOR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html) 核对。`VARCHAR` 是模板对 SAP 字符串的现有表达方式；SAP nVarChar 的 Unicode 属性应由数据源保留，不能据模板类型对数据库做窄字符迁移。SAP Date 沿用模板 TIMESTAMP，不能由此承诺带实际时刻。

`OWOR.Type` 的标准、特殊、拆卸以及 `WOR1.ItemType` 的物料 4、资源 290、文本 -18 必须用于选择业务口径。数据库类型不同于 DI API 组件枚举。现有 WOR1→OITM 与 WOR1→ORSC 已按类型过滤，应保留。BOM 组件尚缺相同的资源路径。[WOR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html)、[ITT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html)。

## 数量、单位与生产成本职责

- 父项计划量、完成量与拒收量分开；累计已发量不能当本期用量。组件计划量由父项计划量、BaseQty、AdditQty 组成，但分析应优先读取保存的 PlannedQty，避免用当前 BOM 重建历史工单。[计划量](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~ProductionOrders_Lines~PlannedQuantity.html)。
- 附加用量须保留；副产品附加用量限制以及零基数的手工发料规则不能推广到所有组件。资源 BaseQty 不允许负值；不同单位资源不能与物料数量一起求和。[附加量](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~ProductionOrders_Lines~AdditionalQuantity.html)、[基准量](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~ProductionOrders_Lines~BaseQuantity.html)。
- `IssueType=M/B` 是工单实际选择的手工/倒冲方式；当前主数据默认方式不能覆盖它。资源容量单位已由 ORSC.UnitOfMsr 提供，单位名称与单位编号应同时可读。[资源表](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORSC.html)。
- 实际生产收货既可能是产品，也可能是组件退回、副产品或拆卸产出；不能把全部 IGN1 从发料量/成本直接扣除。负组件用量可代表副产品；拆卸订单改变父项和组件的库存角色。[生产收货窗口](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44f292f1df7365fbe10000000a1553f7.html?locale=en-US)。
- `IGE1/IGN1.StockSum`、`StockValue`、`LineTotal`、`StockPrice`、`OIVL.SumStock/WipVal` 职责不同；不按名称相近替换。现有参考查询先聚合估价层，再聚合交易到发料行；保留 NULL、冲回符号和零数量的无单价语义。它证明查询边界，不证明真实最终工单成本。[IGE1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/IGE1.html)、[IGN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ign1.html)、[OIVL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIVL.html)。
- 不把 ORSC 当前标准成本、BOM 价格或工单 CompTotal 当作历史领料总成本。生产汇总还区分物料、资源、非库存附加成本、产品、副产品与关闭差异；材料发料金额只是其中一部分。[生产汇总页](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44f292ebdf7365fbe10000000a1553f7.html)。

官方汇总页面与生产指南对于“资源退回”措辞并不完全一致：本审查不把普通组件退料规则自动推广到资源，保留版本及现场验收项。[生产与资源指南，第62页](https://help.sap.com/doc/10311afc90c643b3aaceeaa87a52bf5f/10.0/en-US/How_to_Work_with_Resources_and_Production_in_SAP_Business_One.pdf#page=62)。

## 现有关系逐项审查与待审项

保留：OITT→OITM、OITT→ITT1、ITT1→OITM（Type=4）、ITT1→OWHS；OWOR→OITM/OCRD/NNM1/OUOM、OWOR→WOR1；WOR1→OITM（ItemType=4）/ORSC（290）/OWHS/OUOM；IGE1→OWOR/WOR1、IGN1→OWOR；OIVL→IGE1。

- 工单与组件、BOM 与组件都是一对多；不得同查工单组件、发料、收货、分层估价等多个明细分支后直接汇总工单数量。
- IGE1→WOR1 必须 `(BaseEntry,BaseLine)` 对 `(DocEntry,LineNum)` 且 BaseType=202；发料自身 LineNum 和物料编码不能代替来源行号。现有连接正确。
- OIVL→IGE1 必须 TransType=60 且 CreatedBy/DocLineNum 对当前发料单 DocEntry/LineNum；同一行可多条估价交易。现有连接正确。
- OIVL→IGN1 仍在 deferred；按 TransType=59 的候选不等于已经通过产品/组件退回/拆卸/副产品成本对账，本轮不解除。
- IGN1→WOR1 的组件退回路径需按来源和角色核验，不能把产品收货行的 BaseLine=-1 等特殊值猜成组件。
- OWOR.OriginAbs 连接销售订单时应加来源类型；本轮先保留 LinkToObj 判别，来源追溯与工单层级自关联需角色别名及真实流程验证，暂不增加默认连接。

证据为仓库既有 [参考查询](production-issue-query.sql)、[延后关系](deferred.json)、[合成回归](../tests/test_production_issue.py) 与 [OIVL 官方定义](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIVL.html)。本轮只审阅这些证据，未运行测试或执行数据对账。

## 本轮不默认增加的表与字段

| 候选 | 业务用途与决定 | 唯一键与关系 |
|---|---|---|
| WOR4 + ORST | 需要工序名称、状态、计划开始结束、等待天数时成套增加。当前先保存 StageId，不把整套工序排程作为常用生产必需能力。ORST 归共享主数据。 | WOR4 `(DocEntry,StageId)`；WOR1→WOR4 用这两个键；WOR4.StgEntry→ORST.AbsEntry。不能 WOR1.StageId→ORST.AbsEntry。 |
| ITT2 | 需要 BOM 工艺路线定义时加入，不能用于替代历史工单工艺。 | `(Father,StageId)`；ITT1 两键匹配，StgEntry→ORST.AbsEntry。 |
| WOR1.StartDate/EndDate/Status/ReqDays/ResAlloc | 与工序及资源排程一起评估；单独字段无法证明实际生产报工、实际工时或完整产能负荷。 | 行状态是 P/I/C，不是表头 P/R/L/C。 |
| ITT1/WOR1.LineText | 文本行需要完整叙述时补；不能把 SAP Text 16 当作 VARCHAR(16)，须先验证引擎长文本类型支持。 | 保留原行主键及 Type=-18，不能以文本数量计算物料。 |
| ORSC.StdCost1…10 与产能表 | 资源当前成本与产能配置属共享资源专题。当前实际历史成本不依赖补这些字段来“重建”。 | 必须区分当前配置、日期分配与已发生事实。 |
| OIVL.WipVarAcc/WipVarVal 等金额族 | 对关闭差异有价值，交库存/财务口径联审；只暴露源列不代表最终成本公式获验收。 | 不跨估价层重复累加交易金额。 |

工序及键据 [WOR4](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR4.html)、[ORST](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORST.html)、[ITT2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT2.html)；组件日期与状态据 [WOR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html)。

## 可实现动作清单

下列 JSON 明确新增、修改、删除和关系；新增字段均可空、非计算、非隐藏，不改业务值。SAP 官方长度与旧目标库可能不同，类型扩容应在目标元数据确认后进行。它们属于 compatible widening，保持名称及下游引用。

分配规则 5 维列按完整族保存，便于解释工单/组件成本归属；本轮不机械建立 20 条同目标关系，避免在尚无角色区分时生成混乱路径。以后接入 OOCR 必须分别区分维度，规则不同于成本中心；历史实际分配仍看当时会计事实。与全模块公共维度改动合并去重。

```json
{
  "scope": "production_safe_candidate",
  "status": "research_only_physical_schema_check_required",
  "add": [
    {
      "model": "oitt",
      "name": "Name",
      "type": "VARCHAR(200)",
      "displayName": "BOM产品名称",
      "displayName_en": "BOM Product Description",
      "description": "BOM自身保存的产品描述；当前BOM描述，不代替历史工单产品名称。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OITT.html",
      "notNull": false,
      "description_en": "Product description stored on the BOM; current BOM configuration does not replace the historical production-order product description."
    },
    {
      "model": "itt1",
      "name": "VisOrder",
      "type": "INTEGER",
      "displayName": "组件显示顺序",
      "displayName_en": "Component Visual Order",
      "description": "界面行顺序，不能替代ChildNum作为组件主键。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html",
      "notNull": false,
      "description_en": "Display order; does not replace ChildNum as the component key."
    },
    {
      "model": "itt1",
      "name": "ItemName",
      "type": "VARCHAR(200)",
      "displayName": "BOM组件名称",
      "displayName_en": "BOM Component Description",
      "description": "BOM保存的组件描述；物料、资源和文本行均按Type解释，不从当前主数据覆盖。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html",
      "notNull": false,
      "description_en": "Component description stored on the BOM; interpret item, resource, and text rows by Type without replacing their description from current master data."
    },
    {
      "model": "itt1",
      "name": "AddQuantit",
      "type": "DECIMAL(19,6)",
      "displayName": "BOM附加用量",
      "displayName_en": "BOM Additional Quantity",
      "description": "BOM附加组件量；字段拼写保留源表AddQuantit，不改为工单的AdditQty。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html",
      "notNull": false,
      "description_en": "Additional component quantity on the BOM. Preserve the source spelling AddQuantit, distinct from AdditQty on the production-order component."
    },
    {
      "model": "itt1",
      "name": "WipActCode",
      "type": "VARCHAR(15)",
      "displayName": "BOM在制品科目编码",
      "displayName_en": "BOM WIP Account Code",
      "description": "BOM组件在制品科目配置，不代表历史交易最终过账科目。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html",
      "notNull": false,
      "description_en": "WIP account configuration of the BOM component; not the final account posted by historical transactions."
    },
    {
      "model": "itt1",
      "name": "StageId",
      "type": "INTEGER",
      "displayName": "BOM工序内部序号",
      "displayName_en": "BOM Stage ID",
      "description": "工序在当前BOM内的标识；不是ORST主键，须与Father一起定位ITT2。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html",
      "notNull": false,
      "description_en": "Stage identifier within the current BOM; not the ORST primary key. Use Father together with this identifier to locate ITT2."
    },
    {
      "model": "owor",
      "name": "Warehouse",
      "type": "VARCHAR(8)",
      "displayName": "产品仓库编码",
      "displayName_en": "Product Warehouse Code",
      "description": "生产订单产品仓库；区别于组件行wareHouse与实际收发货行WhsCode。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Product warehouse on the production order; distinct from component wareHouse and actual transaction-row WhsCode."
    },
    {
      "model": "owor",
      "name": "Uom",
      "type": "VARCHAR(100)",
      "displayName": "产品单位名称快照",
      "displayName_en": "Product UoM Snapshot",
      "description": "生产订单保存的库存单位名称；不因当前物料或单位主数据修改而覆盖。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Inventory-unit description saved on the production order; retain it when current item or UoM master data changes."
    },
    {
      "model": "owor",
      "name": "ProdName",
      "type": "VARCHAR(200)",
      "displayName": "产品名称快照",
      "displayName_en": "Product Description Snapshot",
      "description": "生产订单保存的产品描述；不以当前BOM或物料名称替代。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Product description saved on the production order; do not substitute the current BOM or item description."
    },
    {
      "model": "owor",
      "name": "StartDate",
      "type": "TIMESTAMP",
      "displayName": "计划开始日期",
      "displayName_en": "Planned Start Date",
      "description": "工单计划开始日期；不代表首笔实际发料或实际生产开工。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Planned production-order start date; does not establish the first actual issue or actual production start."
    },
    {
      "model": "owor",
      "name": "RlsDate",
      "type": "TIMESTAMP",
      "displayName": "下达日期",
      "displayName_en": "Release Date",
      "description": "工单下达日期；区别于订单日期、创建日期及实际收发料日期。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Production-order release date; distinct from order date, creation date, and actual issue or receipt dates."
    },
    {
      "model": "owor",
      "name": "Comments",
      "type": "VARCHAR(254)",
      "displayName": "生产订单备注",
      "displayName_en": "Production Order Remarks",
      "description": "生产订单业务备注，不作为稳定编码或关系键。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Production-order business remarks; not a stable code or relationship key."
    },
    {
      "model": "owor",
      "name": "TransId",
      "type": "INTEGER",
      "displayName": "生产订单会计分录内部标识",
      "displayName_en": "Production Order Journal Entry ID",
      "description": "源表保存的会计分录关联标识；不代表工单全部收发料和关闭相关分录集合。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Journal-entry reference stored on the production order; does not represent all issues, receipts, and closing entries of the order."
    },
    {
      "model": "owor",
      "name": "LinkToObj",
      "type": "VARCHAR(20)",
      "displayName": "关联来源对象类型",
      "displayName_en": "Linked Source Object Type",
      "description": "官方列举17销售订单、202生产订单；与OriginAbs及OriginType共同判别，不按来源显示单号建立关系。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Official values include 17 for sales orders and 202 for production orders. Interpret together with OriginAbs and OriginType; do not join by the displayed origin document number."
    },
    {
      "model": "wor1",
      "name": "ItemName",
      "type": "VARCHAR(200)",
      "displayName": "组件名称快照",
      "displayName_en": "Component Description Snapshot",
      "description": "工单保存的组件描述；不以当前物料、资源或BOM描述覆盖。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html",
      "notNull": false,
      "description_en": "Component description saved on the production order; do not replace it with the current item, resource, or BOM description."
    },
    {
      "model": "wor1",
      "name": "Project",
      "type": "VARCHAR(20)",
      "displayName": "组件项目编码",
      "displayName_en": "Component Project Code",
      "description": "工单组件行项目；不假定恒等于表头项目。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html",
      "notNull": false,
      "description_en": "Project saved on the component row; not assumed to equal the header project."
    },
    {
      "model": "wor1",
      "name": "WipActCode",
      "type": "VARCHAR(15)",
      "displayName": "组件在制品科目编码",
      "displayName_en": "Component WIP Account Code",
      "description": "工单组件在制品科目配置；执行时的实际科目仍由交易单据和分录核对。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html",
      "notNull": false,
      "description_en": "WIP account configuration saved on the production-order component. Actual posted accounts must be checked against transaction documents and journal entries."
    },
    {
      "model": "wor1",
      "name": "StageId",
      "type": "INTEGER",
      "displayName": "工单工序内部序号",
      "displayName_en": "Production Order Stage ID",
      "description": "工单内工序标识；须与DocEntry一起定位WOR4，不能直接连接ORST.AbsEntry。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html",
      "notNull": false,
      "description_en": "Stage identifier within the production order. Use DocEntry together with this identifier to locate WOR4; do not join directly to ORST.AbsEntry."
    },
    {
      "model": "oitt",
      "name": "OcrCode",
      "type": "VARCHAR(8)",
      "displayName": "第1维分配规则编码",
      "displayName_en": "Dimension 1 Distribution Rule Code",
      "description": "所属对象保存的第1维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OITT.html",
      "notNull": false,
      "description_en": "Dimension 1 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "oitt",
      "name": "OcrCode2",
      "type": "VARCHAR(8)",
      "displayName": "第2维分配规则编码",
      "displayName_en": "Dimension 2 Distribution Rule Code",
      "description": "所属对象保存的第2维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OITT.html",
      "notNull": false,
      "description_en": "Dimension 2 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "oitt",
      "name": "OcrCode3",
      "type": "VARCHAR(8)",
      "displayName": "第3维分配规则编码",
      "displayName_en": "Dimension 3 Distribution Rule Code",
      "description": "所属对象保存的第3维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OITT.html",
      "notNull": false,
      "description_en": "Dimension 3 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "oitt",
      "name": "OcrCode4",
      "type": "VARCHAR(8)",
      "displayName": "第4维分配规则编码",
      "displayName_en": "Dimension 4 Distribution Rule Code",
      "description": "所属对象保存的第4维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OITT.html",
      "notNull": false,
      "description_en": "Dimension 4 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "oitt",
      "name": "OcrCode5",
      "type": "VARCHAR(8)",
      "displayName": "第5维分配规则编码",
      "displayName_en": "Dimension 5 Distribution Rule Code",
      "description": "所属对象保存的第5维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OITT.html",
      "notNull": false,
      "description_en": "Dimension 5 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "itt1",
      "name": "OcrCode",
      "type": "VARCHAR(8)",
      "displayName": "第1维分配规则编码",
      "displayName_en": "Dimension 1 Distribution Rule Code",
      "description": "所属对象保存的第1维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html",
      "notNull": false,
      "description_en": "Dimension 1 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "itt1",
      "name": "OcrCode2",
      "type": "VARCHAR(8)",
      "displayName": "第2维分配规则编码",
      "displayName_en": "Dimension 2 Distribution Rule Code",
      "description": "所属对象保存的第2维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html",
      "notNull": false,
      "description_en": "Dimension 2 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "itt1",
      "name": "OcrCode3",
      "type": "VARCHAR(8)",
      "displayName": "第3维分配规则编码",
      "displayName_en": "Dimension 3 Distribution Rule Code",
      "description": "所属对象保存的第3维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html",
      "notNull": false,
      "description_en": "Dimension 3 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "itt1",
      "name": "OcrCode4",
      "type": "VARCHAR(8)",
      "displayName": "第4维分配规则编码",
      "displayName_en": "Dimension 4 Distribution Rule Code",
      "description": "所属对象保存的第4维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html",
      "notNull": false,
      "description_en": "Dimension 4 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "itt1",
      "name": "OcrCode5",
      "type": "VARCHAR(8)",
      "displayName": "第5维分配规则编码",
      "displayName_en": "Dimension 5 Distribution Rule Code",
      "description": "所属对象保存的第5维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html",
      "notNull": false,
      "description_en": "Dimension 5 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "owor",
      "name": "OcrCode",
      "type": "VARCHAR(8)",
      "displayName": "第1维分配规则编码",
      "displayName_en": "Dimension 1 Distribution Rule Code",
      "description": "所属对象保存的第1维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Dimension 1 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "owor",
      "name": "OcrCode2",
      "type": "VARCHAR(8)",
      "displayName": "第2维分配规则编码",
      "displayName_en": "Dimension 2 Distribution Rule Code",
      "description": "所属对象保存的第2维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Dimension 2 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "owor",
      "name": "OcrCode3",
      "type": "VARCHAR(8)",
      "displayName": "第3维分配规则编码",
      "displayName_en": "Dimension 3 Distribution Rule Code",
      "description": "所属对象保存的第3维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Dimension 3 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "owor",
      "name": "OcrCode4",
      "type": "VARCHAR(8)",
      "displayName": "第4维分配规则编码",
      "displayName_en": "Dimension 4 Distribution Rule Code",
      "description": "所属对象保存的第4维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Dimension 4 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "owor",
      "name": "OcrCode5",
      "type": "VARCHAR(8)",
      "displayName": "第5维分配规则编码",
      "displayName_en": "Dimension 5 Distribution Rule Code",
      "description": "所属对象保存的第5维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWOR.html",
      "notNull": false,
      "description_en": "Dimension 5 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "wor1",
      "name": "OcrCode",
      "type": "VARCHAR(8)",
      "displayName": "第1维分配规则编码",
      "displayName_en": "Dimension 1 Distribution Rule Code",
      "description": "所属对象保存的第1维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html",
      "notNull": false,
      "description_en": "Dimension 1 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "wor1",
      "name": "OcrCode2",
      "type": "VARCHAR(8)",
      "displayName": "第2维分配规则编码",
      "displayName_en": "Dimension 2 Distribution Rule Code",
      "description": "所属对象保存的第2维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html",
      "notNull": false,
      "description_en": "Dimension 2 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "wor1",
      "name": "OcrCode3",
      "type": "VARCHAR(8)",
      "displayName": "第3维分配规则编码",
      "displayName_en": "Dimension 3 Distribution Rule Code",
      "description": "所属对象保存的第3维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html",
      "notNull": false,
      "description_en": "Dimension 3 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "wor1",
      "name": "OcrCode4",
      "type": "VARCHAR(8)",
      "displayName": "第4维分配规则编码",
      "displayName_en": "Dimension 4 Distribution Rule Code",
      "description": "所属对象保存的第4维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html",
      "notNull": false,
      "description_en": "Dimension 4 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    },
    {
      "model": "wor1",
      "name": "OcrCode5",
      "type": "VARCHAR(8)",
      "displayName": "第5维分配规则编码",
      "displayName_en": "Dimension 5 Distribution Rule Code",
      "description": "所属对象保存的第5维分配规则；规则不同于成本中心，不据当前规则分配明细追算历史实际成本。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html",
      "notNull": false,
      "description_en": "Dimension 5 distribution rule saved on this object. Distribution rules are distinct from cost centers; current rule details cannot reconstruct historical actual costs."
    }
  ],
  "change": [
    {
      "model": "itt1",
      "name": "Uom",
      "type": "VARCHAR(100)",
      "compatibility": "compatible widening; confirm target physical schema and preserve names/values",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITT1.html"
    },
    {
      "model": "orsc",
      "name": "ResCode",
      "type": "VARCHAR(50)",
      "compatibility": "compatible widening; confirm target physical schema and preserve names/values",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORSC.html"
    },
    {
      "model": "orsc",
      "name": "VisResCode",
      "type": "VARCHAR(50)",
      "compatibility": "compatible widening; confirm target physical schema and preserve names/values",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORSC.html"
    },
    {
      "model": "orsc",
      "name": "ResName",
      "type": "VARCHAR(200)",
      "compatibility": "compatible widening; confirm target physical schema and preserve names/values",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ORSC.html"
    },
    {
      "model": "owor",
      "name": "CmpltQty",
      "displayName": "已完成数量",
      "displayName_en": "Completed Quantity",
      "description": "已从生产收货的完成产品累计量。数据库IGN1.TranType使用字符C表示完成；DI API的botrntComplete数值0不是SQL筛选值。期间数量、退料、副产品和取消须另按业务角色核验。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~ProductionOrders~CompletedQuantity.html",
      "additional_source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ign1.html",
      "compatibility": "metadata correction only; no value/key/type changes",
      "description_en": "Cumulative completed-product quantity received from production. Database IGN1.TranType uses character C for complete; DI API botrntComplete numeric value 0 is not a SQL filter value. Period quantities, component returns, by-products, and cancellations require their own business-role validation."
    },
    {
      "model": "owor",
      "name": "RjctQty",
      "displayName": "拒收数量",
      "displayName_en": "Rejected Quantity",
      "description": "已从生产收货的拒收产品累计量。数据库IGN1.TranType使用字符R表示拒收；DI API的botrntReject数值1不是SQL筛选值。拒收产品仍可能有库存和成本，不自动等同报废出库。",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~ProductionOrders~RejectedQuantity.html",
      "additional_source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ign1.html",
      "compatibility": "metadata correction only; no value/key/type changes",
      "description_en": "Cumulative rejected-product quantity received from production. Database IGN1.TranType uses character R for reject; DI API botrntReject numeric value 1 is not a SQL filter value. Rejected products may still carry inventory and cost and do not automatically imply a scrap issue."
    }
  ],
  "remove": [],
  "relationships_add": [
    {
      "name": "sap_itt1_orsc",
      "models": [
        "itt1",
        "orsc"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "itt1.Code = orsc.ResCode AND itt1.Type = 290",
      "description": "只连接BOM资源组件；不使用资源显示编号，当前资源成本不替代历史实际成本。",
      "description_en": "Only BOM resource components. Use the resource internal code rather than its displayed number; current resource cost does not replace historical actual cost."
    },
    {
      "name": "sap_oitt_owhs",
      "models": [
        "oitt",
        "owhs"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "oitt.ToWH = owhs.WhsCode",
      "description": "BOM产品默认仓库。",
      "description_en": "Default product warehouse configured on the BOM."
    },
    {
      "name": "sap_owor_owhs",
      "models": [
        "owor",
        "owhs"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "owor.Warehouse = owhs.WhsCode",
      "description": "工单产品仓库，不等同组件与实际收发货仓库。",
      "description_en": "Production-order product warehouse, distinct from component and actual issue or receipt warehouses."
    },
    {
      "name": "sap_oitt_oprj",
      "models": [
        "oitt",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "oitt.Project = oprj.PrjCode",
      "description": "所属对象项目维度；保留表头与组件项目差异。",
      "description_en": "Project of this object; preserve differences between header and component projects."
    },
    {
      "name": "sap_itt1_oprj",
      "models": [
        "itt1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "itt1.Project = oprj.PrjCode",
      "description": "所属对象项目维度；保留表头与组件项目差异。",
      "description_en": "Project of this object; preserve differences between header and component projects."
    },
    {
      "name": "sap_owor_oprj",
      "models": [
        "owor",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "owor.Project = oprj.PrjCode",
      "description": "所属对象项目维度；保留表头与组件项目差异。",
      "description_en": "Project of this object; preserve differences between header and component projects."
    },
    {
      "name": "sap_wor1_oprj",
      "models": [
        "wor1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "wor1.Project = oprj.PrjCode",
      "description": "所属对象项目维度；保留表头与组件项目差异。",
      "description_en": "Project of this object; preserve differences between header and component projects."
    },
    {
      "name": "sap_itt1_oact_wip",
      "models": [
        "itt1",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "itt1.WipActCode = oact.AcctCode",
      "description": "在制品科目配置；不是所有实际会计过账的替代路径。",
      "description_en": "WIP account configuration; not a substitute for the paths to all actual accounting postings."
    },
    {
      "name": "sap_wor1_oact_wip",
      "models": [
        "wor1",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "wor1.WipActCode = oact.AcctCode",
      "description": "在制品科目配置；不是所有实际会计过账的替代路径。",
      "description_en": "WIP account configuration; not a substitute for the paths to all actual accounting postings."
    },
    {
      "name": "sap_owor_ojdt",
      "models": [
        "owor",
        "ojdt"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "owor.TransId = ojdt.TransId",
      "description": "仅源表明确保存的分录引用，空键保持未匹配，不解释为工单全部成本分录。",
      "description_en": "Only the journal-entry reference explicitly saved on the source table. Preserve missing keys without a match; do not interpret this as all production-order cost entries."
    }
  ],
  "tables_add": []
}
```

## 实施后的必要验证

1. 核验新增列的存在、大小写、类型长度及日期语义；不以官方最新字段直接推定旧目标库具备所有列。
2. 对父项/组件不同仓库、不同项目、同物料重复组件行与资源内部编码不同于显示编号建立合成验证。
3. 用数据库 C/R 与 SDK 0/1 两类示例约束生成语义；不能由字符串/整数自动转换掩盖错误。
4. 保持现有发料测试中多交易多层、非库存缺估价、部分 NULL、冲回、零数量案例；补字段不应改已有查询结果。
5. 待审业务实际对账应包含退料、副产品、拆卸、拒收、倒冲和工单关闭差异；未执行前不宣称工单最终成本已验收。

当前状态：已完成源码与一手资料审查；动作清单尚未实施。无生产四表字段删除，无业务数据变更。
