# 财务收付款、分录与核销表审查

审查日期：2026-10-22。范围为财务分组现有10表及共享科目、项目和币种维度。本轮只读模板、既有研究与 SAP 官方来源，没有查询业务数据、修改模型、执行测试或发布。动作清单为研究候选，不表示模型已实施或 SAP 账簿已对账。

## 结论

常用总账、收付款和内部核销事实已具备主干。主要补充是收付款方式的完整三币金额、银行转账日期/参考、支付方式对应的资金科目、应用行费用及舍入差额、核销费用的 FC/SC。应从默认精选移除美国1099专用 PaidSum；不删除物理数据。

安全候选合计：42 个新增字段、19 个字段元数据/类型修改、2 个精选删除、0 条新增关系（6 条资金科目角色关系待审）、0 张新表。类型与列存在仍由目标元数据复核。付款头与应用行的父子关系仍因缺少 DocEntry≠DocNum 的有判别力样本而待审，不能以补字段宣称完整收款到发票链已经验收。

## 现有覆盖与全部字段去留

本次读取基线共233字段，按下列粒度分别保留。除 RCT2/VPM2.PaidSum 外不为减少数量而删字段；字段完整清单见本报告末尾。后续实施可能改变计数，本节描述审查读取时的基线。

| 模型 | 字段数 | 唯一键 | 本轮判断 |
|---|---:|---|---|
| ORCT / OVPM | 28 / 28 | DocEntry | 现有头总额、取消、日期、三币余额、对象类别、项目和分录键保留；补方式金额与银行事实。 |
| RCT2 / VPM2 | 22 / 22 | DocNum + InvoiceId | 保留目标类型、内部键、分录行/分期、三币应用额、折扣和预扣税；PaidSum 从默认精选移除；补费用及舍入。 |
| RCT4 / VPM4 | 16 / 16 | DocNum + LineId | 直接科目收付款事实已有金额/税额三币族；保留科目行项目、名称快照及税额基础；名称扩到200。 |
| OJDT | 27 | TransId | 过账/单据/到期日、参考文本、头项目、三币头总额、来源与冲销字段齐备；无需重复添加已有字段。 |
| JDT1 | 37 | TransId + Line_ID | 三币借贷发生额和当前余额、行币种、行日期、科目/BP、五维分配规则及项目齐备，保留。 |
| OITR | 17 | ReconNum | 核销日、取消关联、对象类别、发起类型、核销币种和生成分录齐备；历史重建不能仅看当前取消标记。 |
| ITR1 | 20 | ReconNum + LineSeq | 分录复合键、参与来源类型、借贷方向、三币核销与预扣税保留；仅补现有 ExpSum 费用族的FC/SC。 |

表结构及键据 [ORCT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html)、[OVPM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html)、[RCT2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html)、[VPM2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM2.html)、[RCT4](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RCT4.html)、[VPM4](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM4.html)、[OJDT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OJDT.html)、[JDT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html)、[OITR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITR.html)、[ITR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITR1.html)。现有分录字段职责继续遵循[财务凭证与项目维度核对](finance-journal-research.md)，不将相邻列或相似名称当作同一财务指标。

## 明确取舍

1. **付款方式三币族**：CashSum、CheckSum、CreditSum、TrsfrSum、NoDocSum 已有本币。补齐FC/SC，保留信用卡前缀差异：本币是 CreditSum，另外两列是 CredSumFC/CredSumSy，不能生成不存在的 CreditSumFC。金额各自属于表头；不在连接多条应用行后重复累计。[收款头](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html)、[付款头](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html)。
2. **银行事实与资金科目**：TrsfrDate、TrsfrRef 是银行转账方式的保存事实；参考信息不保证唯一，日期不是银行对账确认日。CashAcct、CheckAcct、TrsfrAcct 指向 OACT，分别对应三种资金科目角色；三列先保留，重复目标关系待原生角色别名查询验证后启用；不是 RCT4/VPM4 直接收付款的目标科目。[转账日期](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments~TransferDate.html)、[转账参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments~TransferReference.html)。
3. **应用额、费用、折扣与预扣税分开**：SumApplied、AppliedFC、AppliedSys 是目标对象应用行金额；ExpAppld 等是其中独立保存的费用事实，不能据名称发明“全部字段相加等于发票或付款金额”的恒等式。Rounddiff 与FC/SC舍入各保留。附加费用应用额不是承运商物流成本。[支付应用成员](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices_members.html)。
4. **PaidSum 不作通用已付款**：DI 明确其用于 US1099；从本轮通用精选去掉两列，保留通用三币应用额。删除前检查既有 View/Cube/实例依赖；不能删除 SAP 物理字段或历史值。[PaidSum](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices~PaidSum.html)。
5. **核销费用补齐**：ITR1 已有 ExpSum；官方有 ExpSumFC、ExpSumSC，补齐同一保存事实的三币族。OITR.ReconCurr 解释 SumMthCurr，不能无条件替代 ITR1.FrgnCurr。[ITR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITR1.html)。
6. **兼容类型**：RCT2.AppliedSys 应按官方 Num19.6 声明 DECIMAL(19,6)，不是允许数据库自动采用缺省精度。RCT4/VPM4.AcctName 从100扩到200，保留完整名称快照；这是 compatible widening，不迁移源数据库。

## 币种和状态边界

LC 币种来自同一公司 OADM.MainCurncy，SC 来自 OADM.SysCurrncy。头级FC配付款头 DocCurr；发票应用行的FC须按 InvType 与目标对象解析，不能自动用付款头币种覆盖。不同来源币种无法统一确认时保留未解释状态，不用零、空或当前主数据币种猜测。ITR1.FC 配 FrgnCurr，核销币种金额另配 OITR.ReconCurr。[OADM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OADM.html)、[支付应用成员](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices_members.html)、[ITR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITR1.html)。

ORCT/OVPM.DocType 常用 C/S/A 不是完整枚举，官方还列 P/T/D 等税务或地区类别。保持源值；C/S类才沿当前有类型限制的 BP 关系，不能把A类或地区类型强归客户/供应商。Canceled 的 N/Y/C 与 OITR.Canceled 的 Y/N 分属不同事实；不把全部取消单剔除后宣称取得总账净发生额。

## 关系逐类审查及仍未完成的路径

- 收付款头→OJDT 由保存的 TransId 连接；应用行→OJDT 则是 DocTransId，分别代表付款自身与被支付对象分录。现有关系保留，不混换两个编号。
- RCT2/VPM2→目标发票、贷项、预付款用 InvType + DocEntry。同编号不同对象不能串联；InstId、DocLine、InvoiceId 三种行标识不互换。
- RCT4/VPM4→OACT 和 OPRJ 由行保存的科目、项目连接；付款头项目和目标单据项目不回填本行。
- OJDT→JDT1、OITR→ITR1 为一对多；头金额、借贷两侧核销行、支付应用行各自有粒度，不在多分支明细展开后求和。
- ITR1→JDT1 保留 `(TransId,TransRowId)=(TransId,Line_ID)` 完整复合键。SrcObjTyp/SrcObjAbs 是参与来源，InitObjTyp/InitObjAbs 是发起来源；两者不能合并为统一付款编号。[ITR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITR1.html)。
- 当前 jdt1_ocrd 使用 ShortName=CardCode；ShortName 可是 BP/科目代码。缺少统一 BP 行判别时，不虚构 Account!=ShortName 条件、不把普通科目行强制内连删除，也不宣称这条路径在全部数据上无需范围约束。原路径保留兼容，业务范围及潜在代码冲突仍须核验。
- **Partial**：ORCT→RCT2、OVPM→VPM2，以及对应科目行父子键，仍待 DocEntry 与 DocNum 不同的判别样本。官方“相关表”标签不能替代该证据；不解除 [deferred](deferred.json)，不将候选连接加入本轮动作。
- 历史未清账龄、取消核销方向、StornoToTr 完整方向及事件时间还原仍需专项验收；当前余额加历史日期筛选不构成历史余额重建。

## 可实现动作 JSON

金额新增统一 DECIMAL(19,6)；可空、非隐藏、非计算。源列拼写保留，不迁移业务数据。删除是精选字段移除，存在依赖时须先安全处理兼容，不能强删引用。JSON 的 relationships_defer 只记录待审资金科目角色边，不能直接按新增关系执行。清单不启用已延期父子关系，不新增财务专题表或金额推导公式。

```json
{
  "scope": "finance_payments_and_reconciliation",
  "status": "research_candidates_not_implemented",
  "add": [
    {
      "model": "orct",
      "name": "CashSumFC",
      "type": "DECIMAL(19,6)",
      "displayName": "现金金额（外币）",
      "displayName_en": "Cash Amount (FC)",
      "description": "现金金额（外币），属于收付款表头粒度。按同一付款头DocCurr解释，不与目标发票的应用行外币无条件统一；不跨币种累计。",
      "description_en": "Cash amount (FC) at payment-header grain. Interpret using the payment header DocCurr; do not automatically assign this currency to invoice-application FC amounts or aggregate different currencies.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "CashSumSy",
      "type": "DECIMAL(19,6)",
      "displayName": "现金金额（系统币）",
      "displayName_en": "Cash Amount (SC)",
      "description": "现金金额（系统币），属于收付款表头粒度。币种取同公司OADM.SysCurrncy；不与本币或外币金额混加。",
      "description_en": "Cash amount (SC) at payment-header grain. Currency is the same company OADM.SysCurrncy; keep separate from LC and FC amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "CheckSumFC",
      "type": "DECIMAL(19,6)",
      "displayName": "支票金额（外币）",
      "displayName_en": "Check Amount (FC)",
      "description": "支票金额（外币），属于收付款表头粒度。按同一付款头DocCurr解释，不与目标发票的应用行外币无条件统一；不跨币种累计。",
      "description_en": "Check amount (FC) at payment-header grain. Interpret using the payment header DocCurr; do not automatically assign this currency to invoice-application FC amounts or aggregate different currencies.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "CheckSumSy",
      "type": "DECIMAL(19,6)",
      "displayName": "支票金额（系统币）",
      "displayName_en": "Check Amount (SC)",
      "description": "支票金额（系统币），属于收付款表头粒度。币种取同公司OADM.SysCurrncy；不与本币或外币金额混加。",
      "description_en": "Check amount (SC) at payment-header grain. Currency is the same company OADM.SysCurrncy; keep separate from LC and FC amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "CredSumFC",
      "type": "DECIMAL(19,6)",
      "displayName": "信用卡金额（外币）",
      "displayName_en": "Credit Card Amount (FC)",
      "description": "信用卡金额（外币），属于收付款表头粒度。按同一付款头DocCurr解释，不与目标发票的应用行外币无条件统一；不跨币种累计。",
      "description_en": "Credit Card amount (FC) at payment-header grain. Interpret using the payment header DocCurr; do not automatically assign this currency to invoice-application FC amounts or aggregate different currencies.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "CredSumSy",
      "type": "DECIMAL(19,6)",
      "displayName": "信用卡金额（系统币）",
      "displayName_en": "Credit Card Amount (SC)",
      "description": "信用卡金额（系统币），属于收付款表头粒度。币种取同公司OADM.SysCurrncy；不与本币或外币金额混加。",
      "description_en": "Credit Card amount (SC) at payment-header grain. Currency is the same company OADM.SysCurrncy; keep separate from LC and FC amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "TrsfrSumFC",
      "type": "DECIMAL(19,6)",
      "displayName": "银行转账金额（外币）",
      "displayName_en": "Bank Transfer Amount (FC)",
      "description": "银行转账金额（外币），属于收付款表头粒度。按同一付款头DocCurr解释，不与目标发票的应用行外币无条件统一；不跨币种累计。",
      "description_en": "Bank Transfer amount (FC) at payment-header grain. Interpret using the payment header DocCurr; do not automatically assign this currency to invoice-application FC amounts or aggregate different currencies.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "TrsfrSumSy",
      "type": "DECIMAL(19,6)",
      "displayName": "银行转账金额（系统币）",
      "displayName_en": "Bank Transfer Amount (SC)",
      "description": "银行转账金额（系统币），属于收付款表头粒度。币种取同公司OADM.SysCurrncy；不与本币或外币金额混加。",
      "description_en": "Bank Transfer amount (SC) at payment-header grain. Currency is the same company OADM.SysCurrncy; keep separate from LC and FC amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "NoDocSumFC",
      "type": "DECIMAL(19,6)",
      "displayName": "未指定单据金额（外币）",
      "displayName_en": "On-Account Amount (FC)",
      "description": "未指定单据金额（外币），属于收付款表头粒度。按同一付款头DocCurr解释，不与目标发票的应用行外币无条件统一；不跨币种累计。",
      "description_en": "On-Account amount (FC) at payment-header grain. Interpret using the payment header DocCurr; do not automatically assign this currency to invoice-application FC amounts or aggregate different currencies.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "NoDocSumSy",
      "type": "DECIMAL(19,6)",
      "displayName": "未指定单据金额（系统币）",
      "displayName_en": "On-Account Amount (SC)",
      "description": "未指定单据金额（系统币），属于收付款表头粒度。币种取同公司OADM.SysCurrncy；不与本币或外币金额混加。",
      "description_en": "On-Account amount (SC) at payment-header grain. Currency is the same company OADM.SysCurrncy; keep separate from LC and FC amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "TrsfrDate",
      "type": "TIMESTAMP",
      "displayName": "银行转账日期",
      "displayName_en": "Bank Transfer Date",
      "description": "支付方式中保存的银行转账日期；不替代单据过账日、银行对账确认日或核销日。",
      "description_en": "Stored transfer date for the bank-transfer payment means; not a substitute for posting date, bank reconciliation date, or internal reconciliation date.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "TrsfrRef",
      "type": "VARCHAR(27)",
      "displayName": "银行转账参考信息",
      "displayName_en": "Bank Transfer Reference",
      "description": "银行转账方式的参考信息或用途；不是保证唯一的银行流水号，不作连接键。",
      "description_en": "Reference information or intended purpose of the bank transfer; not guaranteed to be a unique bank transaction ID or a join key.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "CashAcct",
      "type": "VARCHAR(15)",
      "displayName": "现金科目编码",
      "displayName_en": "Cash Account Code",
      "description": "现金支付方式使用的总账科目代码，关联OACT.AcctCode；不等同科目收付款行的目标AcctCode。",
      "description_en": "G/L account used by cash payment means, joined by OACT.AcctCode; distinct from the target account AcctCode on account-payment rows.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "CheckAcct",
      "type": "VARCHAR(15)",
      "displayName": "支票科目编码",
      "displayName_en": "Check Account Code",
      "description": "支票支付方式使用的总账科目代码，关联OACT.AcctCode；不等同支票明细或清算事件。",
      "description_en": "G/L account used by check payment means, joined by OACT.AcctCode; not a substitute for individual checks or their clearing events.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "TrsfrAcct",
      "type": "VARCHAR(15)",
      "displayName": "银行转账科目编码",
      "displayName_en": "Bank Transfer Account Code",
      "description": "银行转账支付方式使用的总账科目代码，关联OACT.AcctCode；不是银行主数据编号或账号。",
      "description_en": "G/L account used by bank-transfer payment means, joined by OACT.AcctCode; not a bank master key or bank account number.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "CashSumFC",
      "type": "DECIMAL(19,6)",
      "displayName": "现金金额（外币）",
      "displayName_en": "Cash Amount (FC)",
      "description": "现金金额（外币），属于收付款表头粒度。按同一付款头DocCurr解释，不与目标发票的应用行外币无条件统一；不跨币种累计。",
      "description_en": "Cash amount (FC) at payment-header grain. Interpret using the payment header DocCurr; do not automatically assign this currency to invoice-application FC amounts or aggregate different currencies.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "CashSumSy",
      "type": "DECIMAL(19,6)",
      "displayName": "现金金额（系统币）",
      "displayName_en": "Cash Amount (SC)",
      "description": "现金金额（系统币），属于收付款表头粒度。币种取同公司OADM.SysCurrncy；不与本币或外币金额混加。",
      "description_en": "Cash amount (SC) at payment-header grain. Currency is the same company OADM.SysCurrncy; keep separate from LC and FC amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "CheckSumFC",
      "type": "DECIMAL(19,6)",
      "displayName": "支票金额（外币）",
      "displayName_en": "Check Amount (FC)",
      "description": "支票金额（外币），属于收付款表头粒度。按同一付款头DocCurr解释，不与目标发票的应用行外币无条件统一；不跨币种累计。",
      "description_en": "Check amount (FC) at payment-header grain. Interpret using the payment header DocCurr; do not automatically assign this currency to invoice-application FC amounts or aggregate different currencies.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "CheckSumSy",
      "type": "DECIMAL(19,6)",
      "displayName": "支票金额（系统币）",
      "displayName_en": "Check Amount (SC)",
      "description": "支票金额（系统币），属于收付款表头粒度。币种取同公司OADM.SysCurrncy；不与本币或外币金额混加。",
      "description_en": "Check amount (SC) at payment-header grain. Currency is the same company OADM.SysCurrncy; keep separate from LC and FC amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "CredSumFC",
      "type": "DECIMAL(19,6)",
      "displayName": "信用卡金额（外币）",
      "displayName_en": "Credit Card Amount (FC)",
      "description": "信用卡金额（外币），属于收付款表头粒度。按同一付款头DocCurr解释，不与目标发票的应用行外币无条件统一；不跨币种累计。",
      "description_en": "Credit Card amount (FC) at payment-header grain. Interpret using the payment header DocCurr; do not automatically assign this currency to invoice-application FC amounts or aggregate different currencies.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "CredSumSy",
      "type": "DECIMAL(19,6)",
      "displayName": "信用卡金额（系统币）",
      "displayName_en": "Credit Card Amount (SC)",
      "description": "信用卡金额（系统币），属于收付款表头粒度。币种取同公司OADM.SysCurrncy；不与本币或外币金额混加。",
      "description_en": "Credit Card amount (SC) at payment-header grain. Currency is the same company OADM.SysCurrncy; keep separate from LC and FC amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "TrsfrSumFC",
      "type": "DECIMAL(19,6)",
      "displayName": "银行转账金额（外币）",
      "displayName_en": "Bank Transfer Amount (FC)",
      "description": "银行转账金额（外币），属于收付款表头粒度。按同一付款头DocCurr解释，不与目标发票的应用行外币无条件统一；不跨币种累计。",
      "description_en": "Bank Transfer amount (FC) at payment-header grain. Interpret using the payment header DocCurr; do not automatically assign this currency to invoice-application FC amounts or aggregate different currencies.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "TrsfrSumSy",
      "type": "DECIMAL(19,6)",
      "displayName": "银行转账金额（系统币）",
      "displayName_en": "Bank Transfer Amount (SC)",
      "description": "银行转账金额（系统币），属于收付款表头粒度。币种取同公司OADM.SysCurrncy；不与本币或外币金额混加。",
      "description_en": "Bank Transfer amount (SC) at payment-header grain. Currency is the same company OADM.SysCurrncy; keep separate from LC and FC amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "NoDocSumFC",
      "type": "DECIMAL(19,6)",
      "displayName": "未指定单据金额（外币）",
      "displayName_en": "On-Account Amount (FC)",
      "description": "未指定单据金额（外币），属于收付款表头粒度。按同一付款头DocCurr解释，不与目标发票的应用行外币无条件统一；不跨币种累计。",
      "description_en": "On-Account amount (FC) at payment-header grain. Interpret using the payment header DocCurr; do not automatically assign this currency to invoice-application FC amounts or aggregate different currencies.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "NoDocSumSy",
      "type": "DECIMAL(19,6)",
      "displayName": "未指定单据金额（系统币）",
      "displayName_en": "On-Account Amount (SC)",
      "description": "未指定单据金额（系统币），属于收付款表头粒度。币种取同公司OADM.SysCurrncy；不与本币或外币金额混加。",
      "description_en": "On-Account amount (SC) at payment-header grain. Currency is the same company OADM.SysCurrncy; keep separate from LC and FC amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "TrsfrDate",
      "type": "TIMESTAMP",
      "displayName": "银行转账日期",
      "displayName_en": "Bank Transfer Date",
      "description": "支付方式中保存的银行转账日期；不替代单据过账日、银行对账确认日或核销日。",
      "description_en": "Stored transfer date for the bank-transfer payment means; not a substitute for posting date, bank reconciliation date, or internal reconciliation date.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "TrsfrRef",
      "type": "VARCHAR(27)",
      "displayName": "银行转账参考信息",
      "displayName_en": "Bank Transfer Reference",
      "description": "银行转账方式的参考信息或用途；不是保证唯一的银行流水号，不作连接键。",
      "description_en": "Reference information or intended purpose of the bank transfer; not guaranteed to be a unique bank transaction ID or a join key.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "CashAcct",
      "type": "VARCHAR(15)",
      "displayName": "现金科目编码",
      "displayName_en": "Cash Account Code",
      "description": "现金支付方式使用的总账科目代码，关联OACT.AcctCode；不等同科目收付款行的目标AcctCode。",
      "description_en": "G/L account used by cash payment means, joined by OACT.AcctCode; distinct from the target account AcctCode on account-payment rows.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "CheckAcct",
      "type": "VARCHAR(15)",
      "displayName": "支票科目编码",
      "displayName_en": "Check Account Code",
      "description": "支票支付方式使用的总账科目代码，关联OACT.AcctCode；不等同支票明细或清算事件。",
      "description_en": "G/L account used by check payment means, joined by OACT.AcctCode; not a substitute for individual checks or their clearing events.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "TrsfrAcct",
      "type": "VARCHAR(15)",
      "displayName": "银行转账科目编码",
      "displayName_en": "Bank Transfer Account Code",
      "description": "银行转账支付方式使用的总账科目代码，关联OACT.AcctCode；不是银行主数据编号或账号。",
      "description_en": "G/L account used by bank-transfer payment means, joined by OACT.AcctCode; not a bank master key or bank account number.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "rct2",
      "name": "RounddifFc",
      "type": "DECIMAL(19,6)",
      "displayName": "舍入差异（外币）",
      "displayName_en": "Rounding Difference (FC)",
      "description": "应用行保存的外币舍入差额；与目标对象及其币种角色一起解释，不用付款头币种无条件回填。",
      "description_en": "Stored rounding difference (FC) on the application row. Interpret with the target object and its currency role; do not automatically backfill the payment-header currency.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html",
      "notNull": false
    },
    {
      "model": "rct2",
      "name": "RounddifSc",
      "type": "DECIMAL(19,6)",
      "displayName": "舍入差异（系统币）",
      "displayName_en": "Rounding Difference (SC)",
      "description": "应用行保存的系统币舍入差额，币种来自同公司OADM.SysCurrncy；不据此发明结算恒等式。",
      "description_en": "Stored rounding difference (SC) on the application row; currency is the same company OADM.SysCurrncy. Does not establish a universal settlement identity.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html",
      "notNull": false
    },
    {
      "model": "rct2",
      "name": "ExpAppld",
      "type": "DECIMAL(19,6)",
      "displayName": "已应用附加费用（本币）",
      "displayName_en": "Applied Freight Amount (LC)",
      "description": "应用到目标单据的附加费用金额（官方Freight），币种来自同公司OADM.MainCurncy；不是承运商实际成本，不与SumApplied无条件再次相加。",
      "description_en": "Freight amount applied to the target document (LC), using the same company OADM.MainCurncy; not actual carrier cost and not automatically an increment to SumApplied.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html",
      "notNull": false
    },
    {
      "model": "rct2",
      "name": "ExpAppldFC",
      "type": "DECIMAL(19,6)",
      "displayName": "已应用附加费用（外币）",
      "displayName_en": "Applied Freight Amount (FC)",
      "description": "应用行保存的外币附加费用金额；按目标对象与已保存外币角色解释，不无条件赋付款头DocCurr。",
      "description_en": "Stored applied freight amount (FC) on the application row. Interpret using the target object and stored FC role rather than automatically assigning payment-header DocCurr.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html",
      "notNull": false
    },
    {
      "model": "rct2",
      "name": "ExpAppldSC",
      "type": "DECIMAL(19,6)",
      "displayName": "已应用附加费用（系统币）",
      "displayName_en": "Applied Freight Amount (SC)",
      "description": "应用行保存的系统币附加费用金额，币种来自同公司OADM.SysCurrncy；与费用税额及现金支付额分开。",
      "description_en": "Stored applied freight amount (SC), using the same company OADM.SysCurrncy; distinct from freight tax and cash payment amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html",
      "notNull": false
    },
    {
      "model": "vpm2",
      "name": "RounddifFc",
      "type": "DECIMAL(19,6)",
      "displayName": "舍入差异（外币）",
      "displayName_en": "Rounding Difference (FC)",
      "description": "应用行保存的外币舍入差额；与目标对象及其币种角色一起解释，不用付款头币种无条件回填。",
      "description_en": "Stored rounding difference (FC) on the application row. Interpret with the target object and its currency role; do not automatically backfill the payment-header currency.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM2.html",
      "notNull": false
    },
    {
      "model": "vpm2",
      "name": "RounddifSc",
      "type": "DECIMAL(19,6)",
      "displayName": "舍入差异（系统币）",
      "displayName_en": "Rounding Difference (SC)",
      "description": "应用行保存的系统币舍入差额，币种来自同公司OADM.SysCurrncy；不据此发明结算恒等式。",
      "description_en": "Stored rounding difference (SC) on the application row; currency is the same company OADM.SysCurrncy. Does not establish a universal settlement identity.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM2.html",
      "notNull": false
    },
    {
      "model": "vpm2",
      "name": "ExpAppld",
      "type": "DECIMAL(19,6)",
      "displayName": "已应用附加费用（本币）",
      "displayName_en": "Applied Freight Amount (LC)",
      "description": "应用到目标单据的附加费用金额（官方Freight），币种来自同公司OADM.MainCurncy；不是承运商实际成本，不与SumApplied无条件再次相加。",
      "description_en": "Freight amount applied to the target document (LC), using the same company OADM.MainCurncy; not actual carrier cost and not automatically an increment to SumApplied.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM2.html",
      "notNull": false
    },
    {
      "model": "vpm2",
      "name": "ExpAppldFC",
      "type": "DECIMAL(19,6)",
      "displayName": "已应用附加费用（外币）",
      "displayName_en": "Applied Freight Amount (FC)",
      "description": "应用行保存的外币附加费用金额；按目标对象与已保存外币角色解释，不无条件赋付款头DocCurr。",
      "description_en": "Stored applied freight amount (FC) on the application row. Interpret using the target object and stored FC role rather than automatically assigning payment-header DocCurr.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM2.html",
      "notNull": false
    },
    {
      "model": "vpm2",
      "name": "ExpAppldSC",
      "type": "DECIMAL(19,6)",
      "displayName": "已应用附加费用（系统币）",
      "displayName_en": "Applied Freight Amount (SC)",
      "description": "应用行保存的系统币附加费用金额，币种来自同公司OADM.SysCurrncy；与费用税额及现金支付额分开。",
      "description_en": "Stored applied freight amount (SC), using the same company OADM.SysCurrncy; distinct from freight tax and cash payment amounts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM2.html",
      "notNull": false
    },
    {
      "model": "itr1",
      "name": "ExpSumFC",
      "type": "DECIMAL(19,6)",
      "displayName": "核销附加费用（外币）",
      "displayName_en": "Reconciliation Freight Amount (FC)",
      "description": "核销参与行保存的外币附加费用金额；外币由本行FrgnCurr解释，不以OITR.ReconCurr自动替代。不是新的现金流入，不在借贷两侧重复计作回款。",
      "description_en": "Stored reconciliation-row freight amount (FC); FC is labelled by the same row FrgnCurr, not automatically by OITR.ReconCurr. Not an additional cash inflow; do not count both debit and credit sides as receipts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITR1.html",
      "notNull": false
    },
    {
      "model": "itr1",
      "name": "ExpSumSC",
      "type": "DECIMAL(19,6)",
      "displayName": "核销附加费用（系统币）",
      "displayName_en": "Reconciliation Freight Amount (SC)",
      "description": "核销参与行保存的系统币附加费用金额；币种来自同公司OADM.SysCurrncy。不是新的现金流入，不在借贷两侧重复计作回款。",
      "description_en": "Stored reconciliation-row freight amount (SC); Currency is the same company OADM.SysCurrncy. Not an additional cash inflow; do not count both debit and credit sides as receipts.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITR1.html",
      "notNull": false
    }
  ],
  "change": [
    {
      "model": "orct",
      "name": "CashSum",
      "type": "DECIMAL(19,6)",
      "displayName": "现金金额（本币）",
      "displayName_en": "Cash Amount (LC)",
      "description": "现金支付或挂账金额（本币），属于付款表头粒度；币种来自同公司OADM.MainCurncy，不是可与全部应用行混加的独立增量。",
      "description_en": "Cash payment-means or on-account amount (LC), at payment-header grain; currency is the same company OADM.MainCurncy. Do not add it to invoice-application amounts as a separate increment.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "CheckSum",
      "type": "DECIMAL(19,6)",
      "displayName": "支票金额（本币）",
      "displayName_en": "Check Amount (LC)",
      "description": "支票支付或挂账金额（本币），属于付款表头粒度；币种来自同公司OADM.MainCurncy，不是可与全部应用行混加的独立增量。",
      "description_en": "Check payment-means or on-account amount (LC), at payment-header grain; currency is the same company OADM.MainCurncy. Do not add it to invoice-application amounts as a separate increment.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "CreditSum",
      "type": "DECIMAL(19,6)",
      "displayName": "信用卡金额（本币）",
      "displayName_en": "Credit Card Amount (LC)",
      "description": "信用卡支付或挂账金额（本币），属于付款表头粒度；币种来自同公司OADM.MainCurncy，不是可与全部应用行混加的独立增量。",
      "description_en": "Credit Card payment-means or on-account amount (LC), at payment-header grain; currency is the same company OADM.MainCurncy. Do not add it to invoice-application amounts as a separate increment.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "TrsfrSum",
      "type": "DECIMAL(19,6)",
      "displayName": "银行转账金额（本币）",
      "displayName_en": "Bank Transfer Amount (LC)",
      "description": "银行转账支付或挂账金额（本币），属于付款表头粒度；币种来自同公司OADM.MainCurncy，不是可与全部应用行混加的独立增量。",
      "description_en": "Bank Transfer payment-means or on-account amount (LC), at payment-header grain; currency is the same company OADM.MainCurncy. Do not add it to invoice-application amounts as a separate increment.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "NoDocSum",
      "type": "DECIMAL(19,6)",
      "displayName": "未指定单据金额（本币）",
      "displayName_en": "On-Account Amount (LC)",
      "description": "未应用到指定单据的挂账金额（本币），属于收付款表头粒度，独立于现金、转账等支付方式；币种取同公司OADM.MainCurncy，不与发票应用金额重复相加。",
      "description_en": "On-account amount (LC), at payment-header grain; currency is the same company OADM.MainCurncy. This is the amount not applied to specified documents, independent of the payment means; do not add it to invoice-application amounts as a separate increment.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "DocType",
      "type": "VARCHAR(1)",
      "displayName": "收付款对象类别",
      "displayName_en": "Payment Object Category",
      "description": "常用数据库值C客户、S供应商、A科目；官方还列有P/T/D等地区或税务类别，三类不是穷尽枚举。保持原值，不将未知类别强归业务伙伴；DI数字枚举不是数据库筛选值。",
      "description_en": "Common database values are C customer, S vendor, and A account. Official reference also lists P/T/D regional or tax categories; C/S/A is not exhaustive. Preserve source values and do not force other categories into business-partner joins or use DI numeric enum values as SQL filters.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "orct",
      "name": "PrjCode",
      "type": "VARCHAR(20)",
      "displayName": "收付款项目编码",
      "displayName_en": "Payment Project Code",
      "description": "收付款头项目代码，关联OPRJ.PrjCode；不覆盖目标发票、付款科目行或分录行的项目。",
      "description_en": "Project code on the payment header, joined to OPRJ.PrjCode; does not override projects on invoices, account-payment rows, or journal-entry rows.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "CashSum",
      "type": "DECIMAL(19,6)",
      "displayName": "现金金额（本币）",
      "displayName_en": "Cash Amount (LC)",
      "description": "现金支付或挂账金额（本币），属于付款表头粒度；币种来自同公司OADM.MainCurncy，不是可与全部应用行混加的独立增量。",
      "description_en": "Cash payment-means or on-account amount (LC), at payment-header grain; currency is the same company OADM.MainCurncy. Do not add it to invoice-application amounts as a separate increment.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "CheckSum",
      "type": "DECIMAL(19,6)",
      "displayName": "支票金额（本币）",
      "displayName_en": "Check Amount (LC)",
      "description": "支票支付或挂账金额（本币），属于付款表头粒度；币种来自同公司OADM.MainCurncy，不是可与全部应用行混加的独立增量。",
      "description_en": "Check payment-means or on-account amount (LC), at payment-header grain; currency is the same company OADM.MainCurncy. Do not add it to invoice-application amounts as a separate increment.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "CreditSum",
      "type": "DECIMAL(19,6)",
      "displayName": "信用卡金额（本币）",
      "displayName_en": "Credit Card Amount (LC)",
      "description": "信用卡支付或挂账金额（本币），属于付款表头粒度；币种来自同公司OADM.MainCurncy，不是可与全部应用行混加的独立增量。",
      "description_en": "Credit Card payment-means or on-account amount (LC), at payment-header grain; currency is the same company OADM.MainCurncy. Do not add it to invoice-application amounts as a separate increment.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "TrsfrSum",
      "type": "DECIMAL(19,6)",
      "displayName": "银行转账金额（本币）",
      "displayName_en": "Bank Transfer Amount (LC)",
      "description": "银行转账支付或挂账金额（本币），属于付款表头粒度；币种来自同公司OADM.MainCurncy，不是可与全部应用行混加的独立增量。",
      "description_en": "Bank Transfer payment-means or on-account amount (LC), at payment-header grain; currency is the same company OADM.MainCurncy. Do not add it to invoice-application amounts as a separate increment.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "NoDocSum",
      "type": "DECIMAL(19,6)",
      "displayName": "未指定单据金额（本币）",
      "displayName_en": "On-Account Amount (LC)",
      "description": "未应用到指定单据的挂账金额（本币），属于收付款表头粒度，独立于现金、转账等支付方式；币种取同公司OADM.MainCurncy，不与发票应用金额重复相加。",
      "description_en": "On-account amount (LC), at payment-header grain; currency is the same company OADM.MainCurncy. This is the amount not applied to specified documents, independent of the payment means; do not add it to invoice-application amounts as a separate increment.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "DocType",
      "type": "VARCHAR(1)",
      "displayName": "收付款对象类别",
      "displayName_en": "Payment Object Category",
      "description": "常用数据库值C客户、S供应商、A科目；官方还列有P/T/D等地区或税务类别，三类不是穷尽枚举。保持原值，不将未知类别强归业务伙伴；DI数字枚举不是数据库筛选值。",
      "description_en": "Common database values are C customer, S vendor, and A account. Official reference also lists P/T/D regional or tax categories; C/S/A is not exhaustive. Preserve source values and do not force other categories into business-partner joins or use DI numeric enum values as SQL filters.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "ovpm",
      "name": "PrjCode",
      "type": "VARCHAR(20)",
      "displayName": "收付款项目编码",
      "displayName_en": "Payment Project Code",
      "description": "收付款头项目代码，关联OPRJ.PrjCode；不覆盖目标发票、付款科目行或分录行的项目。",
      "description_en": "Project code on the payment header, joined to OPRJ.PrjCode; does not override projects on invoices, account-payment rows, or journal-entry rows.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "notNull": false
    },
    {
      "model": "rct2",
      "name": "AppliedFC",
      "type": "DECIMAL(19,6)",
      "displayName": "外币应用金额",
      "displayName_en": "Applied Amount (FC)",
      "description": "目标单据应用行保存的外币金额；应按InvType解析目标对象及币种，不能无条件用付款头DocCurr。外币金额为零不证明本币未支付。",
      "description_en": "Stored FC amount on the target-document application row. Resolve the target by InvType and its currency; do not automatically assign payment-header DocCurr. A zero FC amount does not establish that no LC payment occurred.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html",
      "notNull": false
    },
    {
      "model": "vpm2",
      "name": "AppliedFC",
      "type": "DECIMAL(19,6)",
      "displayName": "外币应用金额",
      "displayName_en": "Applied Amount (FC)",
      "description": "目标单据应用行保存的外币金额；应按InvType解析目标对象及币种，不能无条件用付款头DocCurr。外币金额为零不证明本币未支付。",
      "description_en": "Stored FC amount on the target-document application row. Resolve the target by InvType and its currency; do not automatically assign payment-header DocCurr. A zero FC amount does not establish that no LC payment occurred.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM2.html",
      "notNull": false
    },
    {
      "model": "rct2",
      "name": "AppliedSys",
      "type": "DECIMAL(19,6)",
      "displayName": "系统币应用金额",
      "displayName_en": "Applied Amount (SC)",
      "description": "应用行系统币金额，币种来自同公司OADM.SysCurrncy；按官方19,6精度明确类型，不把此行金额等同付款头总额。",
      "description_en": "Application-row amount (SC), using the same company OADM.SysCurrncy. Explicitly declare the official precision 19,6; not equivalent to the full payment-header total.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/RCT2.html",
      "notNull": false
    },
    {
      "model": "rct4",
      "name": "AcctName",
      "type": "VARCHAR(200)",
      "displayName": "科目名称快照",
      "displayName_en": "Account Name Snapshot",
      "description": "付款科目行保存的科目名称快照，保留至200字符；不由当前OACT名称覆盖，不作关系键。",
      "description_en": "Stored account-name snapshot on an account-payment row, preserved up to 200 characters. Do not replace it with the current OACT name or use it as a join key.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/RCT4.html",
      "notNull": false,
      "compatibility": "compatible widening from VARCHAR(100); no source schema migration"
    },
    {
      "model": "vpm4",
      "name": "AcctName",
      "type": "VARCHAR(200)",
      "displayName": "科目名称快照",
      "displayName_en": "Account Name Snapshot",
      "description": "付款科目行保存的科目名称快照，保留至200字符；不由当前OACT名称覆盖，不作关系键。",
      "description_en": "Stored account-name snapshot on an account-payment row, preserved up to 200 characters. Do not replace it with the current OACT name or use it as a join key.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/VPM4.html",
      "notNull": false,
      "compatibility": "compatible widening from VARCHAR(100); no source schema migration"
    }
  ],
  "remove": [
    {
      "model": "rct2",
      "name": "PaidSum",
      "reason": "US1099专用指标，不属于当前通用精选范围；SumApplied/AppliedFC/AppliedSys保留。",
      "reason_en": "US 1099-specific amount is outside the current general-purpose selection; retain SumApplied, AppliedFC, and AppliedSys.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices~PaidSum.html",
      "compatibility": "Removal from the curated template can affect downstream references; check views/cubes/workspace artifacts before removal. Never drop or rewrite the SAP physical column."
    },
    {
      "model": "vpm2",
      "name": "PaidSum",
      "reason": "US1099专用指标，不属于当前通用精选范围；SumApplied/AppliedFC/AppliedSys保留。",
      "reason_en": "US 1099-specific amount is outside the current general-purpose selection; retain SumApplied, AppliedFC, and AppliedSys.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Payments_Invoices~PaidSum.html",
      "compatibility": "Removal from the curated template can affect downstream references; check views/cubes/workspace artifacts before removal. Never drop or rewrite the SAP physical column."
    }
  ],
  "tables_add": [],
  "relationships_unresolved": [
    "ORCT→RCT2",
    "OVPM→VPM2",
    "ORCT→RCT4",
    "OVPM→VPM4"
  ],
  "relationships_defer": [
    {
      "name": "sap_orct_oact_cashacct",
      "models": [
        "orct",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "orct.CashAcct = oact.AcctCode",
      "displayName": "现金支付科目",
      "displayName_en": "Cash Payment Account",
      "description": "按支付方式区分资金科目角色；空值或无匹配保留，不以其他科目回填。",
      "description_en": "Keep a distinct funding-account role for each payment means. Preserve missing or unmatched values without substituting another account.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "status": "deferred_role_alias_query_not_verified",
      "reason": "资金科目角色列均保留，但当前MDL尚未证实可同时按三种角色安全取OACT名称。先不增加重复目标关系；待原生角色别名查询验证后再启用。",
      "reason_en": "Keep the funding-account columns. Concurrent OACT name lookup through three roles is not yet verified in the current MDL. Defer repeated-target relationships until native role-alias queries are validated."
    },
    {
      "name": "sap_orct_oact_checkacct",
      "models": [
        "orct",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "orct.CheckAcct = oact.AcctCode",
      "displayName": "支票支付科目",
      "displayName_en": "Check Payment Account",
      "description": "按支付方式区分资金科目角色；空值或无匹配保留，不以其他科目回填。",
      "description_en": "Keep a distinct funding-account role for each payment means. Preserve missing or unmatched values without substituting another account.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "status": "deferred_role_alias_query_not_verified",
      "reason": "资金科目角色列均保留，但当前MDL尚未证实可同时按三种角色安全取OACT名称。先不增加重复目标关系；待原生角色别名查询验证后再启用。",
      "reason_en": "Keep the funding-account columns. Concurrent OACT name lookup through three roles is not yet verified in the current MDL. Defer repeated-target relationships until native role-alias queries are validated."
    },
    {
      "name": "sap_orct_oact_trsfracct",
      "models": [
        "orct",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "orct.TrsfrAcct = oact.AcctCode",
      "displayName": "银行转账科目",
      "displayName_en": "Bank Transfer Account",
      "description": "按支付方式区分资金科目角色；空值或无匹配保留，不以其他科目回填。",
      "description_en": "Keep a distinct funding-account role for each payment means. Preserve missing or unmatched values without substituting another account.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORCT.html",
      "status": "deferred_role_alias_query_not_verified",
      "reason": "资金科目角色列均保留，但当前MDL尚未证实可同时按三种角色安全取OACT名称。先不增加重复目标关系；待原生角色别名查询验证后再启用。",
      "reason_en": "Keep the funding-account columns. Concurrent OACT name lookup through three roles is not yet verified in the current MDL. Defer repeated-target relationships until native role-alias queries are validated."
    },
    {
      "name": "sap_ovpm_oact_cashacct",
      "models": [
        "ovpm",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "ovpm.CashAcct = oact.AcctCode",
      "displayName": "现金支付科目",
      "displayName_en": "Cash Payment Account",
      "description": "按支付方式区分资金科目角色；空值或无匹配保留，不以其他科目回填。",
      "description_en": "Keep a distinct funding-account role for each payment means. Preserve missing or unmatched values without substituting another account.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "status": "deferred_role_alias_query_not_verified",
      "reason": "资金科目角色列均保留，但当前MDL尚未证实可同时按三种角色安全取OACT名称。先不增加重复目标关系；待原生角色别名查询验证后再启用。",
      "reason_en": "Keep the funding-account columns. Concurrent OACT name lookup through three roles is not yet verified in the current MDL. Defer repeated-target relationships until native role-alias queries are validated."
    },
    {
      "name": "sap_ovpm_oact_checkacct",
      "models": [
        "ovpm",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "ovpm.CheckAcct = oact.AcctCode",
      "displayName": "支票支付科目",
      "displayName_en": "Check Payment Account",
      "description": "按支付方式区分资金科目角色；空值或无匹配保留，不以其他科目回填。",
      "description_en": "Keep a distinct funding-account role for each payment means. Preserve missing or unmatched values without substituting another account.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "status": "deferred_role_alias_query_not_verified",
      "reason": "资金科目角色列均保留，但当前MDL尚未证实可同时按三种角色安全取OACT名称。先不增加重复目标关系；待原生角色别名查询验证后再启用。",
      "reason_en": "Keep the funding-account columns. Concurrent OACT name lookup through three roles is not yet verified in the current MDL. Defer repeated-target relationships until native role-alias queries are validated."
    },
    {
      "name": "sap_ovpm_oact_trsfracct",
      "models": [
        "ovpm",
        "oact"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "ovpm.TrsfrAcct = oact.AcctCode",
      "displayName": "银行转账科目",
      "displayName_en": "Bank Transfer Account",
      "description": "按支付方式区分资金科目角色；空值或无匹配保留，不以其他科目回填。",
      "description_en": "Keep a distinct funding-account role for each payment means. Preserve missing or unmatched values without substituting another account.",
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OVPM.html",
      "status": "deferred_role_alias_query_not_verified",
      "reason": "资金科目角色列均保留，但当前MDL尚未证实可同时按三种角色安全取OACT名称。先不增加重复目标关系；待原生角色别名查询验证后再启用。",
      "reason_en": "Keep the funding-account columns. Concurrent OACT name lookup through three roles is not yet verified in the current MDL. Defer repeated-target relationships until native role-alias queries are validated."
    }
  ]
}
```

## 审查读取时的全部字段清单

- **ORCT**：BPLId、CancelDate、Canceled、CardCode、CardName、CashSum、CheckSum、CreditSum、DocCurr、DocDate、DocDueDate、DocEntry、DocNum、DocRate、DocTotal、DocTotalFC、DocTotalSy、DocType、NoDocSum、ObjType、OpenBal、OpenBalFc、OpenBalSc、PayNoDoc、PrjCode、TaxDate、TransId、TrsfrSum。
- **RCT2**：AmtDifPst、AppliedFC、AppliedSys、DcntSum、DcntSumFC、DcntSumSy、DocEntry、DocLine、DocNum、DocRate、DocTransId、InstId、InvoiceId、InvType、LinkDate、ObjType、PaidSum、Rounddiff、SumApplied、WtAppld、WtAppldFC、WtAppldSC。
- **RCT4**：AcctCode、AcctName、AmntBase、AppliedFC、AppliedSys、Descrip、DocNum、GrossAmnt、GrssAmntFC、GrssAmntSC、LineId、Project、SumApplied、VatAmnt、VatAmntFC、VatAmntSC。
- **OVPM**：BPLId、CancelDate、Canceled、CardCode、CardName、CashSum、CheckSum、CreditSum、DocCurr、DocDate、DocDueDate、DocEntry、DocNum、DocRate、DocTotal、DocTotalFC、DocTotalSy、DocType、NoDocSum、ObjType、OpenBal、OpenBalFc、OpenBalSc、PayNoDoc、PrjCode、TaxDate、TransId、TrsfrSum。
- **VPM2**：AmtDifPst、AppliedFC、AppliedSys、DcntSum、DcntSumFC、DcntSumSy、DocEntry、DocLine、DocNum、DocRate、DocTransId、InstId、InvoiceId、InvType、LinkDate、ObjType、PaidSum、Rounddiff、SumApplied、WtAppld、WtAppldFC、WtAppldSC。
- **VPM4**：AcctCode、AcctName、AmntBase、AppliedFC、AppliedSys、Descrip、DocNum、GrossAmnt、GrssAmntFC、GrssAmntSC、LineId、Project、SumApplied、VatAmnt、VatAmntFC、VatAmntSC。
- **OJDT**：AdjTran、AutoStorno、BaseRef、CreateDate、CreatedBy、DueDate、FcTotal、FinncPriod、Indicator、LocTotal、Memo、Number、Project、Ref1、Ref2、Ref3、RefDate、Series、StornoDate、StornoToTr、SysTotal、TaxDate、TransCode、TransCurr、TransId、TransType、UpdateDate。
- **JDT1**：Account、BalDueCred、BalDueDeb、BalFcCred、BalFcDeb、BalScCred、BalScDeb、BaseRef、BPLId、ContraAct、CreatedBy、Credit、DebCred、Debit、DueDate、FCCredit、FCCurrency、FCDebit、Line_ID、LineMemo、OcrCode2、OcrCode3、OcrCode4、OcrCode5、ProfitCode、Project、Ref1、Ref2、Ref3Line、RefDate、ShortName、SourceLine、SYSCred、SYSDeb、TaxDate、TransId、TransType。
- **OITR**：BPLId、CancelAbs、Canceled、CreateDate、CreateTime、InitObjAbs、InitObjTyp、IsCard、IsMultiBP、IsSystem、OldMatNum、ReconCurr、ReconDate、ReconJEId、ReconNum、ReconType、Total。
- **ITR1**：Account、CashDisSum、ExpSum、FrgnCurr、IsCredit、LineSeq、netBefDisc、ReconNum、ReconSum、ReconSumFC、ReconSumSC、ShortName、SrcObjAbs、SrcObjTyp、SumMthCurr、TransId、TransRowId、WTSum、WTSumFC、WTSumSC。

## 实施验证要求与当前状态

实施后最小验证：目标列存在与类型、跨币种不混加、支付方式角色不同、目标类型相同键不串单、核销复合行键、多应用行和头金额不重复累计、无目标发票的挂账/科目付款、1099删除依赖、200字符名称兼容、三币0/NULL不互相覆盖。上述仅是待执行的验证要求，不是已通过结果。

已完成：十表字段与关系源码审查、官方字段与职责核对、精确候选清单。部分完成：收付款头/行闭环、历史核销与账龄。未实施：本报告所有JSON动作。未完成业务验收：真实金额与SAP报表对账。
