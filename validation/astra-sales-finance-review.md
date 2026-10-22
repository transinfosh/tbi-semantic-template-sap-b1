# SAP B1 销售、采购与财务独立审查

后续状态更新（2026-10-22）：SF-01 已补三个分录行日期并明确凭证头日期标题，源码及 P1 草稿均已同步；原技术名、取值、列顺序及金额保持，21→24 列。隔离保存、14 项 SQL 测试、引擎编译及独立重读通过，V18 未变。详见[修补记录](journal-line-dates-fix.md)。以下审查计数及反例描述保留其原始快照含义。

审查日期：2026-10-22。依据为当日 P1 原生完整草稿快照，包含 109 个 Model、3244 个字段、408 条关系、16 个 View、320 个 View 字段、0 个 Cube。本报告审查销售、采购、财务字段选择及其中七个 View；不把 V18 已发布模型或公共模板默认导入内容当作 P1 当前状态。

结论：确认一项 P2 查询能力缺口：财务分录 View 缺少行级日期；另确认预留发票到后续交货／采购收货的直接关系尚未覆盖，但这两条边已明确列入待现场核验清单，不作为本次新发现的实现错误。未确认 P1 级计算错误。六个销售采购 View 在各自声明范围内未发现可复现的错误连接或金额倍增。付款父键仍缺现场有判别力证据；发票头差额不足以充当完整往来余额或历史账龄，但不能据此直接判定差额算式错误。

本次仅写审查报告和私有合成验证脚本，没有修改 Model、关系、View SQL、工作区、发布版本或 SAP 数据。已重新打开本文所引 SAP 官方页面；旧研究只用于定位待核问题，未作为放行依据。

## 一、确认的查询能力缺口与已知待验证项

### SF-01／P2：分录明细缺少行级日期，不能支持按实际行日期归期

**对象与位置：** `finance_journal_line_detail`；[SQL](workspace-views/sql/finance_journal_line_detail.sql) 第 5–7 行；[字段标题](workspace-views/pack.json) 第 994–996 行。

当前三个日期分别来自 `OJDT.RefDate/TaxDate/DueDate`，标题也写作“凭证过账／单据／到期日期”。这些取值作为**凭证头日期本身正确**。问题在于这是一个以 `JDT1.TransId+Line_ID` 为粒度的通用分录明细入口，却没有任何 `JDT1.RefDate/TaxDate/DueDate` 输出，也没有在日期标题或描述中强调“表头”。当头行日期不同，使用者不能通过本 View 查询行过账期间或行到期日。

**官方依据：** SAP 的 [Document Settings: Per Document Tab](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/45071a63f61941dee10000000a1553f6.html) 明确说明，取消 `Block Posting Date Editing Per Row` 可为各分录行输入不同过账日期，并另有阻止过账后修改头／行单据日期的选项；[JDT1 表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html) 分别列出三种行日期；[JournalEntries_Lines.DueDate](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~DueDate.html) 明确该属性属于分录行。另见 [Web Client 日记账 Excel 字段映射](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/39de79e28e17476cba4da8a30d72292a.html)，头日期映射 OJDT，行日期分别映射 JDT1。

**可构造场景及影响：** 凭证头过账日为 9 月 30 日，借方行金额 100、行过账日为 10 月 1 日；贷方行金额 100、行过账日为 9 月 30 日。按现有 View 的 `posting_date` 查询 10 月得到 0，按行 `RefDate` 得到借减贷 100。类似地，头到期日 10 月 10 日、某行到期日 11 月 15 日时，View 只能返回前者。这是合法配置下的查询能力缺口，不表示应以行日期覆盖所有凭证头报表。

**独立复现：** 本轮用 P1 的实际 SQL 在内存 SQLite 中执行上述数据，实得 `october_by_header_date=0`、`october_by_line_date=100`；两个 View 行的日期均为表头日期。以下简化查询可独立复现取值差异，不连接业务库：

```sql
WITH h(TransId, RefDate, TaxDate, DueDate) AS (
  VALUES (1, '2026-09-30', '2026-09-30', '2026-10-10')
), l(TransId, Line_ID, Debit, Credit, RefDate, TaxDate, DueDate) AS (
  VALUES (1, 0, 100, 0, '2026-10-01', '2026-10-02', '2026-11-15'),
         (1, 1, 0, 100, '2026-09-30', '2026-09-30', '2026-10-10')
)
SELECT l.Line_ID, h.RefDate AS current_view_posting_date,
       l.RefDate AS line_posting_date, h.DueDate AS current_view_due_date,
       l.DueDate AS line_due_date
FROM l JOIN h ON h.TransId=l.TransId;
```

**最小建议：** 保留现有三个字段以兼容已有查询，将显示名明确为“凭证头…日期”，再增加 `line_posting_date`、`line_document_date`、`line_due_date`。无需新增表，JDT1 已有原始字段。验证同时覆盖头行同日、异日跨月、不同到期日；按凭证日期与按行日期应是两个明确用途。

### SF-02／已知覆盖边界：预留发票到后续物流的反向来源关系尚未放行

**对象与位置：** `DLN1↔INV1`、`PDN1↔PCH1` 关系覆盖。现有 [dln1_inv1.json](../relationships/dln1_inv1.json) 第 2 行只有 `INV1.BaseType=15`；[sap_pch1_pdn1.json](../relationships/sap_pch1_pdn1.json) 第 2 行只有 `PCH1.BaseType=20`。P1 的全部 408 条关系中，同一对模型各只有这条正常物流后开票关系。[deferred.json](deferred.json) 第 330、828 行已经记录反向边，明确要求结合现场样本及来源头 `isIns` 审核后启用。因此这是既有未放行范围，不应被表述为本次新增缺陷。尚未激活的条件如下：

```sql
dln1.BaseType = 13
AND dln1.BaseEntry = inv1.DocEntry
AND dln1.BaseLine = inv1.LineNum

pdn1.BaseType = 18
AND pdn1.BaseEntry = pch1.DocEntry
AND pdn1.BaseLine = pch1.LineNum
```

**官方依据：** [DLN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/DLN1.html) 的 BaseType 包括 13，[PDN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PDN1.html) 包括 18，两表都独立保存 BaseEntry 与 BaseLine。官方 [A/R Reserve Invoice](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44fd93cb93202463e10000000a1553f7.html) 区分付款关闭与后续交货完成库存；[A/R Reserve Invoices](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/9d51cbe39d5040d0aeab1027b48e82d0.html?locale=en-US&state=PRODUCTION&version=10.0_SP_2602) 和 [Managing A/P Reserve Invoices](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/54e4e23f6e25459e991de55d8f327d07.html?locale=en) 均说明可复制到后续交货或采购收货。

**可构造场景及影响：** 一张直接创建、无订单来源的预留发票 `DocEntry=100, LineNum=0, BaseType=-1`，随后有物流行 `DocEntry=200, LineNum=3, BaseEntry=100, BaseLine=0`。销售物流 BaseType 为 13，采购物流为 18。现有正常关系均匹配 0 行；正确反向关系各匹配 1 行。按现有关系导航查询“这张预留发票后来交了／收了哪些货”存在缺口。

**与 View 范围的区别：** [销售追溯 SQL](workspace-views/sql/sales_order_to_cash_trace.sql) 第 17–18 行、[采购追溯 SQL](workspace-views/sql/purchase_order_to_payment_trace.sql) 第 17–18 行已经正确实现订单来源的预留反向路径。但它们从订单行开始，且描述明确排除独立单据。上述独立预留发票在两个追溯 View 中各得 0 行，是已声明范围，**不是这两个 View 的错误**；它仍暴露了整个模型关系覆盖不足。

**独立复现：** 本轮在 P1 实际关系条件和 View SQL 上执行上述销售、采购两例，结果均为“现有边 0、反向边 1、订单 View 0”。销售侧最小检验如下；采购侧将 `inv1/dln1/13` 替换为 `pch1/pdn1/18`，现有正常关系的类型为 20：

```sql
WITH inv1(DocEntry, LineNum, BaseType, BaseEntry, BaseLine) AS (
  VALUES (100, 0, -1, -1, -1)
), dln1(DocEntry, LineNum, BaseType, BaseEntry, BaseLine) AS (
  VALUES (200, 3, 13, 100, 0)
)
SELECT 'normal_edge' AS role, COUNT(*) AS matches
FROM dln1 JOIN inv1
  ON dln1.DocEntry=inv1.BaseEntry
 AND dln1.LineNum=inv1.BaseLine AND inv1.BaseType=15
UNION ALL
SELECT 'reserve_edge', COUNT(*)
FROM dln1 JOIN inv1
  ON dln1.BaseEntry=inv1.DocEntry
 AND dln1.BaseLine=inv1.LineNum AND dln1.BaseType=13;
```

**后续补验建议：** 先补现场预留发票与物流样本，并核实来源头 `isIns`；再考虑启用两条带完整三元组的物流行到预留发票行多对一关系。保留正常关系并赋予不同角色名，不用 `OR` 合并成含混关系。覆盖一发票多批物流、同物料多行、类型和内部编号碰撞；验证 Engine 对同一对模型的不同角色选择。无需新增表或修改订单 View 范围；本轮不因合成匹配成功跳过原待验证要求。

## 二、七个 View 的核验结果

七个 View 的 P1 `statement` 与 `validation/workspace-views/sql/` 对应文件逐一比对一致。以下“通过”仅指本轮明确覆盖的结构与合成场景，不表示已经完成 SAP 公司账簿业务验收。

| View | 本轮判断 | 已核要点与剩余限制 |
| --- | --- | --- |
| `sales_order_to_cash_trace` | 声明范围内未发现确定计算缺陷 | 两个分支分别处理订单经交货开票、订单直接开票及预留后交货；完整 Base 三元组；同物料多行不合并；订单孤立行保留；付款应用会展开路径但不携带可求和金额。独立单据、退货贷项、预付抵扣及递归同类复制链不在范围。 |
| `purchase_order_to_payment_trace` | 同上 | 使用 22→20→18 与 22→18→20；不是套用销售类型编码。无订单来源的采购预留发票应由模型关系补覆盖，见 SF-02。 |
| `sales_invoice_receipt_applications` | 应用行粒度正确；父键仍待现场判别 | `InvType='13'`，不连商品行；每个 `DocNum+InvoiceId` 一行，保留取消及未匹配事实；不能把应用金额解释为客户全部现金收入。 |
| `purchase_invoice_payment_applications` | 同上 | `InvType='18'`；不把收款表中对 AP 对象的应用混入本 View，也不宣称覆盖全部支付方式和内部核销。 |
| `sales_invoice_current_balance` | 头差额计算按声明实现；不是完整往来余额 | 一发票一行，三币分别相减，未知值未补零；保留取消／预留状态。需使用者明确筛选用途；不能重建历史账龄。 |
| `purchase_invoice_current_balance` | 同上 | 单据头差额不等于供应商所有未清项净额；不能由无 VPM2 行认定未支付或未结清。 |
| `finance_journal_line_detail` | 分录粒度与带符号金额正确；SF-01 后续已修补草稿 | `TransId+Line_ID`，头和 OACT 左连接不扩行；取行项目、行外币，借减贷不使用 ABS。已补独立行日期；不包含核销行、现金流或冲销配对算法。 |

独立组合验证在销售与采购两侧各构造：同物料来自两个订单行，合并到一张发票，再形成两次付款应用，其中一次取消。实际得到 4 条追溯路径、2 条应用记录；原始应用金额 30+20=50，筛选有效付款后为 30；View 未把它摊到两个订单，且没有在路径上暴露可误加总金额。单张发票头差额 LC/FC/SC 分别为 50/10/40，未跨币种混算。另构造父付款头和目标发票均未匹配的应用行，原始金额 12 及内部键仍保留，名称、日期、币种保持 NULL。

这证明当前 SQL 对所造场景的行为，不证明 SAP 一定产生所有合成组合，也不证明现场字段含义。尤其异号付款父键的合成数据是按候选键写入的，不能反过来证明候选键的实际数据库契约。

## 三、付款父键：保留高可信推断，不能写成现场通过

[RCT2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html) 与 [VPM2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM2.html) 将子表 DocNum 标为 Document Number、关联 ORCT／OVPM，主键为 DocNum+InvoiceId；没有在该表格中直接写出父列名。目标发票的 DocEntry 则明确是发票键，见 [Payments_Invoices.DocEntry](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices~DocEntry.html)。父 [Payments.DocEntry](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments~DocEntry.html) 唯一标识付款对象，[Payments.DocNum](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments~DocNum.html) 是单据编号。

据父对象身份、官方 ORCT／OVPM 主键及子对象归属，将 `RCT2.DocNum→ORCT.DocEntry`、`VPM2.DocNum→OVPM.DocEntry` 解释为父内部键合理，当前未找到足以推翻它的官方证据。不能仅因子列同名就改成父 DocNum。

既有私有源探针的 38 条 RCT2、200 条 VPM2 相关父记录均为 `DocEntry=DocNum`。本轮没有扩查 SAP 业务表；这些样本不能区分候选映射，也不能被称为异号验证通过。后续最小验证应在只读条件下找到 `DocEntry<>DocNum` 的父记录，比较两种连接，并将同一个父对象的官方 API 子集合与数据库子行核对；若父显示号可能重复，还需确认不会因显示号连接扩行。没有此证据时，状态继续写“官方组合推断；现场异号未验证”，而非“确定缺陷”或“完全验收”。

`AppliedFC` 的官方属性页说明未使用外币的发票应填零；这支持以目标发票的外币适用性解释应用 FC，而不是因付款头为某币种就替换标签。本轮通过直读官方 HTML 核实该说明，见 [Payments_Invoices.AppliedFC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices~AppliedFC.html)。具体多币混合支付仍需真实样本验证，不以自造币种标签代替业务验收。

## 四、当前头差额与金额名称

当前余额 SQL 第 12–20 行只计算 `DocTotal-PaidToDate`、`DocTotalFC-PaidFC`、`DocTotalSy-PaidSys`。官方 [OINV](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OINV.html) 分别定义这些保存列，但字段名本身不构成“所有业务场景均等于完整未清往来”的证明。因此本轮不凭表结构断言算式一定少减预付款、少减贷项或一定错误；也不宣称已与全部 JDT1 业务伙伴余额对平。

用途应明确分开：

| 常用问题 | 当前视图能否独立回答 | 原因 |
| --- | --- | --- |
| 某张发票当前头总额、已付及两者差额 | 可以，需看币种与取消状态 | 这正是 SQL 的投影和算式。 |
| 客户／供应商当前所有欠款净额 | 不足 | 还可能有独立贷项、挂账付款、手工凭证、期初等未清项目，不能只汇总 OINV／OPCH。 |
| 截止上月末尚欠多少 | 不足 | 当前 PaidToDate 与当前差额不是历史快照；仅筛选发票日期不能回滚后续支付、核销及取消。 |
| 本发票实际收／付了多少现金或银行款 | 不足 | 账面已付、支付应用、付款方式金额、折扣、税和核销是不同保存事实。 |
| 有无付款应用行是否等于已结清／未结清 | 不成立 | 挂账款之后可另行内部核销；抵扣预付款也有独立桥表。 |

上述边界由官方 [Internal Reconciliations](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44f3e89dc4b80486e10000000a155369.html?locale=en-us)、[往来未清项与余额对账](https://help.sap.com/docs/SAP_BUSINESS_ONE/3c3b1c0fbaa44074936934be48b06b68/d7dfa0422209472285d276fd92ef83d0.html)、[Down Payment Request Process](https://help.sap.com/docs/SAP_BUSINESS_ONE/83c8536b097040a3b0d459de2ce00d44/3b3fb8e76b224804bd2ddac718b88694.html) 支持。最后一个来源涉及明确地区／流程，其“抵扣影响最终发票总额”不能未经核验推广成所有本地化的统一新公式。

**命名建议而非计算缺陷：** 当前中文字段标题“头记录已付”“当前头记录未结差额”已比技术名 `settled_amount`、`current_open_amount` 收敛。建议 View 标题也统一为“应收／应付发票当前头记录差额”，避免“账面未结”被读成全量往来报表；兼容保留现有技术名，并在其字段说明中给出公式和范围。原始关系 [rct2_oinv.json](../relationships/rct2_oinv.json) 第 11 行、[vpm2_opch.json](../relationships/vpm2_opch.json) 第 11 行以及 [rct2_odpi.json](../relationships/rct2_odpi.json) 第 11 行仍使用“实收／实付分析”措辞，应与当前 Model／View 的“支付应用”口径统一，避免不同入口给出冲突提示。此处未把词语不精确扩大为已证明的数值错误。

## 五、多余与缺失表／字段的取舍

### 已有表不建议为精简而删除

销售、采购和财务三组的 56 个 Model 分别承担报价／申请、订单、物流、退货请求、退货、发票、贷项、预付款、费用、支付或核销角色。没有因表名相近而认定重复。用户明确要求保留的 `INV9/INV11/RIN9/RIN11` 应保留；9 系列和 11 系列主键粒度不同，后者增加 LineSeq，不能合并后直接重复加总。官方 [INV9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV9.html)、[INV11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV11.html) 对这些键和净额／税额／含税额作了区分。

`INV3/RIN3/PCH3/RPC3` 是发票／贷项的整单附加费用事实，不应以头 `TotalExpns` 已存在为由删除。`DocEntry+LineNum` 为费用记录身份，ExpnsCode 是费用类型；费用不能与商品行机械按 LineNum 连接。该判断由重新读取的 [INV3](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV3.html)、[PCH3](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PCH3.html) 支持。

### 可收起的字段，不建议直接删除

共享 `OACT` 当前有 110 列全部暴露。常见科目识别、层级、可过账状态、币种和发生额查询不需要所有技术或地区专用列。可优先将 `DatevAcct/DatevAutoA/DatevFirst`、`PCN874Rpt`、`SnapShotId`、`Free_2` 放入高级或地区扩展选择，而不是默认发现列表。源码位置：`models/oact.json` 第 267、278、289、793、1071、513 行；官方 [OACT 表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OACT.html) 对这些字段的用途或技术名称有明确区分。

这是**可选精简**，不是断言这些字段在所有公司无用。变更前应检查已有资产依赖，保留源数据和兼容读取。科目内部码、显示码、名称、父科目、分类、币种及现有参考字段不应一起裁剪。

### 后续按问答需求补齐的字段与表

下表是有官方字段依据的候选，不把它们全部列为本轮必须修复的缺陷，也不追求 SAP 全字段覆盖：

| 候选 | 常用问题／实际缺口 | 最小范围与注意点 |
| --- | --- | --- |
| `INV1/RIN1.OcrCode/OcrCode2…5` | 销售行按保存的分配规则筛选；当前采购行已有五维规则，销售行缺失 | 先暴露原始规则码；规则不等于单个部门，不能无权重直接展开成利润中心金额。依据 [INV1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV1.html)；共享规则到成本中心的关系另见全模型覆盖审查。 |
| `INV11/RIN11/PCH11/RPC11.VatGroup/VatPrcnt` | 解释同一预付款抵扣记录为何按不同税组／税率拆行；当前只保留多族税额而缺税率维度 | 用原保存值，不用税额÷净额反推或用当前税配置覆盖历史。首个直接依据为 [INV11](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/INV11.html)，其余表实施前逐表再核。 |
| 付款应用 View 的 `WtAppldFC/SC`、`ExpAppld*`、`Rounddiff/RounddifFc/RounddifSc`、`DocTransId` | 查看应用金额的外币预扣税、费用、舍入及会计来源 | 基础 Model 已有，View 当前仅投影本币预扣税及三币折扣。可以小幅补字段，不需要新表，也不能把这些分量全部相加发明恒等式。依据 [RCT2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html)、[VPM2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM2.html)。 |
| `PCH3/RPC3.Stock` 及费用来源字段 | 采购运费是否计入库存、费用从哪张单据复制 | 当需要这些问答时，优先考虑保存的 Stock 和 `BaseAbsEnt/BaseType/BaseLnNum`；当前费用类型主数据默认值不能代替历史事实。依据 [PCH3](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/PCH3.html)；完整费用分摊到物料另属规则范围。 |
| `RDR3/POR3`，按需要扩至 `DLN3/PDN3` 等 | “未开票订单运费按费用类型多少”“收货运费为何不同于发票” | 当前整单费用覆盖仅发票与贷项四表，不能称已覆盖所有销售采购单据费用。若本次目标仅是发票／贷项费用则属于后续扩展；若要求所有订单物流单据，则是范围仍待补齐。依据 [DocumentsAdditionalExpenses](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~DocumentsAdditionalExpenses.html)、[RDR3](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RDR3.html)。 |

付款条件、价目表和运输方式应由共享主数据负责，避免为销售和采购分别复制同一维度。商机、拣货、草稿审批、定制收入、特殊价格扩展、框架协议和分期均按用户范围暂缓；未将其缺表列为本轮缺陷。

## 六、覆盖清单与证据边界

**字段清单检查覆盖：** P1 销售 22 表／851 字段、采购 24 表／1009 字段、财务 10 表／273 字段；另检查共享 OACT 的 110 字段及与本审查有关的币种、项目、费用、税组关系。已取得上述表的当前精选列清单，重点审查本文涉及的字段族与关系；关键日期、来源三元组、应用身份、金额族和新费用表重新对照了本文列出的官方页面。没有声称逐字段核实所有表、所有地区的运行语义。

| 范围 | 当前表清单 |
| --- | --- |
| 销售 | `OQUT/QUT1`、`ORDR/RDR1`、`ODLN/DLN1`、`ORRR/RRR1`、`ORDN/RDN1`、`OINV/INV1/INV3/INV9/INV11`、`ORIN/RIN1/RIN3/RIN9/RIN11`、`ODPI/DPI1` |
| 采购 | `OPRQ/PRQ1`、`OPQT/PQT1`、`OPOR/POR1`、`OPDN/PDN1`、`OPRR/PRR1`、`ORPD/RPD1`、`OPCH/PCH1/PCH3/PCH9/PCH11`、`ORPC/RPC1/RPC3/RPC9/RPC11`、`ODPO/DPO1` |
| 财务 | `OJDT/JDT1`、`ORCT/RCT2/RCT4`、`OVPM/VPM2/VPM4`、`OITR/ITR1` |
| 七个 View | `sales_order_to_cash_trace`、`purchase_order_to_payment_trace`、`sales_invoice_receipt_applications`、`purchase_invoice_payment_applications`、`sales_invoice_current_balance`、`purchase_invoice_current_balance`、`finance_journal_line_detail` |

**本轮已执行：** P1 与源 SQL 比对；内存 SQLite 执行 P1 实际 SQL 的日期差异、独立预留发票关系缺口、跨订单多应用、取消保留、三币分别计算及未匹配事实保留案例。均成功得到本文记载结果。

**仍未覆盖：** 新增源业务库样本、完整现金／银行对账、与 SAP 标准账龄的逐单一致性、真实异号付款父键、真实预扣税／折扣／预付抵扣组合、多币付款完整样本、各地修正发票和税务特性、Engine 多关系角色的执行选择、真实 UI 自然语言验收、发布后查询。库存、生产和其余九个 View 由平行审查覆盖，不在本报告重复判定。

SF-01 已修复源码及 P1 草稿、尚未发布；SF-02 仍是已知待补验范围。源码可编译、元数据结构一致或合成断言通过，都不能替代上述未覆盖的 SAP 业务核账。
