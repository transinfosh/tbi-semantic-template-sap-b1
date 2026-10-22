# 常用批次、序列号与库位语义视图研究

研究日期：2026-10-22。本文记录首批视图建议和实施前的核验条件，**未新增或发布任何模型、视图、分析模型，也未查询客户业务数据**。来源限 SAP 官方 SDK 数据库表参考及对象说明；字段页能够证明键与枚举，不能替代目标库业务样本和运行验证。

## 建议范围

| 建议语义视图 | 用途与行粒度 | 当前准备情况 |
| --- | --- | --- |
| 销售交货批次与序列号明细 | 查询某张交货单、某一原始行对应的批次/序列号、仓库和分配数量；保留日志 ID，不把同物料多行合并 | 已有 ODLN/DLN1、OITL/ITL1、OBTN/OSRN；Doc 与 Apply 角色仍需目标样本验证 |
| 库存收发批次与序列号明细 | 按事务类型、单据内部号、原始行、日志、批序列、仓库观察真实收发；生产发料/收货保留生产来源 | 已有主要底表；需核验各事务的方向、冲销、调拨双边和单位 |
| 库存收发与库位明细 | 每个 OBTL.AbsEntry 一行，直接保留该条库位分配的批序列主记录 ID 和数量；可按单据过滤 | 缺 OBTL，需补充并验证后才能实施 |
| 当前批次/序列号库位库存 | 查询物料、批次或序列号目前在哪个库位以及数量 | 缺 OIBQ/OBBQ/OSBQ；与历史收发分开，不从流水临时反推余额 |

这些都是候选**明细视图**。查询某张单据不要求先建分析模型；按月、仓库、物料的数量汇总，应在方向、单位和粒度验证后再决定分析模型指标。本文不设计客户专用成本或历史余额算法。

## 官方键与角色

### 日志与批序列主数据

- OITL 主键是 LogEntry；ManagedBy 为批次 10000044、序列号 10000045、普通物料 4。DocType/DocEntry/DocLine 与 ApplyType/ApplyEntry/ApplyLine 各有独立索引，分别描述日志单据与被应用单据；Base 字段又是来源单据角色。StockEff=1 代表现存量影响，2/3 分别为承诺/订购，**不是入库与出库方向**。原始子行亦有独立字段。[SAP OITL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OITL.html)
- ITL1 的主键为 LogEntry+ItemCode+SysNumber，LogEntry 关联 OITL，MdAbsEntry 指向相应批序列主记录。Quantity、AllocQty、ReleaseQty、PickedQty、OrderedQty 是不同字段，不能把分配/释放数量当作实际交货数量。[SAP ITL1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ITL1.html)
- OBTN 与 OSRN 分别以 AbsEntry 为主键，并分别有 ItemCode+SysNumber 唯一键。DistNumber 是业务显示批号/序列号，相关索引不保证唯一。按 MdAbsEntry 或 SysNumber 连接时须保留物料与管理类型判别，不能无条件同时连接两种主数据。[SAP OBTN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/obtn.html)、[SAP OSRN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/osrn.html)

SDK 批次对象将 OBTN/OBTQ/OITL/ITL1 列为源表，并明确销售订单与预留发票存在分配、解除分配情形。因此“与该单据有关的批次日志”和“本次实际交货批次”不能直接等同。[SAP BatchNumbers](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~BatchNumbers.html)

**交货关联的研究边界：** 官方字段页没有给出覆盖所有来源链、退货、冲销与调拨业务的 Doc/Apply 选取算法。可以分别提出按 Doc 三元组或 Apply 三元组定位的候选查询，但必须先核对真实单据的日志与 SAP 界面结果。不能用 OR 合并两个角色后直接累计，也不能选一组字段就宣称全部交货路径已通过。

### 库位事实与方向

- OBTL 主键 AbsEntry；全部六个字段为 AbsEntry、MessageID、BinAbs、SnBMDAbs、Quantity、ITLEntry。其中 MessageID 关联 OILM、BinAbs 关联 OBIN、ITLEntry 关联 OITL；SnBMDAbs 与 ITLEntry 默认值均可为 -1。该记录已在同一行保存库位和批序列主记录 ID。[SAP OBTL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OBTL.html)
- OILM 以 MessageID 为主键，文档定位使用 TransType/DocEntry/DocLineNum；SnBType 明确区分普通物料、批次和序列号。AccumType=1 为现存量影响；ActionType=1/2 为入/出，19/20 为库位转入/转出，还存在重估、设置、完成、撤销等其他动作。Quantity 与 EffectQty 含义不同。[SAP OILM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OILM.html)
- OBIN 以 AbsEntry 为主键，BinCode 为库位显示编码，WhsCode 为所属仓库。[SAP OBIN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OBIN.html)

由上述官方键**推导**，库存库位明细适合以 OBTL 为事实起点，连接 OILM.MessageID 和 OBIN.AbsEntry，再按 OILM.SnBType、ItemCode 与 OBTL.SnBMDAbs 补批序列名称。这避免把行级批次和行级库位分别展开；普通物料、-1 或缺失主数据应保留原事实并标明关联状态，不能因内连接而消失。OBTL.Quantity 才是该分配行的数量，OILM.Quantity/EffectQty 不可复制到每个库位后再求和。

如需带出 ITL1 信息，应以 OBTL.ITLEntry 和 SnBMDAbs、物料、管理类型共同核验分配关系；不能把 OILM.MessageID 当成 OITL.LogEntry。ILM1 是可选的库存消息批序列明细，其主键 MessageID+ItemCode+SysNumber，并有 MdAbsEntry；按 MessageID 单字段连接会再次产生一对多。[SAP ILM1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ILM1.html)

**方向边界：** ActionType 可支持明确的入/出分类，但官方表参考未完整定义所有事件下 Quantity 的正负约定。未验证前宜展示原始数量和动作，不能使用一条通用 ABS 或再次乘负号的公式生成已核实的净收发量。调拨保留两边仓库/库位事实，避免只按整张调拨单标记为入库或出库。

## 可选的单据库位分配表

官方还提供 DLN19、IGN19、IGE19、WTR19，分别服务交货、收货、发货、调拨；都以 DocEntry+BinAllocSe 为主键，并有 LineNum、SubLineNum、SnBType、SnBMDAbs、BinAbs、Quantity、ItemCode、WhsCode 与 BinActTyp。BinActTyp 区分入、出及其他分配动作。

它们可作为“这张单据保存的库位分配”候选实现，而 OBTL 路径用于“库存库位事务”候选实现。不能仅凭字段类似就同时导入全部 19 表；也不能将单据分配记录与库存日志 UNION 后重复计算。针对首批统一历史收发视图，优先核验 OBTL；针对单据分配的 SAP 界面核对，再决定是否需要相应 19 表。

来源：[SAP DLN19](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/DLN19.html)、[SAP IGN19](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/IGN19.html)、[SAP IGE19](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/IGE19.html)、[SAP WTR19](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/WTR19.html)。SDK 的 DocumentLinesBinAllocations 对象也明确表示物料、序列号及批次物料的库位分配。[SAP 对象说明](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DocumentLinesBinAllocations.html)

## 当前余额表与最小字段

| 待补表 | 首批最小字段 | 唯一粒度与作用 |
| --- | --- | --- |
| OBTL | 全部 6 字段 | AbsEntry；历史库位分配事实 |
| OIBQ | AbsEntry、ItemCode、BinAbs、OnHandQty、WhsCode | 主键 AbsEntry；ItemCode+BinAbs 唯一；物料库位总现存量，包含批次/序列号物料 |
| OBBQ | AbsEntry、ItemCode、SnBMDAbs、BinAbs、OnHandQty、WhsCode | 主键 AbsEntry；SnBMDAbs+BinAbs 唯一；批次库位现存量 |
| OSBQ | AbsEntry、ItemCode、SnBMDAbs、BinAbs、OnHandQty、WhsCode | 主键 AbsEntry；SnBMDAbs+BinAbs 唯一；序列号库位现存量 |

余额表关联分别由官方表参考明确给出，OBBQ.SnBMDAbs→OBTN、OSBQ.SnBMDAbs→OSRN，BinAbs→OBIN；不把 OIBQ 总量与批序列分量作为可直接相加的同一种事实。[SAP OIBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OIBQ.html)、[SAP OBBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OBBQ.html)、[SAP OSBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OSBQ.html)

本地 `models/` 清单核对：上述四表、ILM1 以及 DLN19/IGN19/IGE19/WTR19 当前均未建模。OITL、ITL1、OILM、OBIN、OBTN、OSRN 和主要单据对已存在。首批日志视图所需主要现有字段已在模型中；若采用 Apply 或复杂子行路径，OITL.AppSubLine、ActBase* 等额外字段应由样本证明需要后再补。当前报告未将这些候选字段全部提升为必加字段。

## 实施前必须完成的核验

1. 只读核对目标 SAP 版本及上述最小表/字段的实际类型、长度、可空性与键；官方 10.0 文档不是目标库结构证明。
2. 交货至少包含直接交货、基于订单/预留发票交货、同物料多原始行、多批次、序列号、退货/冲销；核对 Doc/Apply 定位和数量与 SAP 界面一致。
3. 库位至少包含一个批次分多个库位、多批次落不同库位、普通物料、未启用库位仓库、跨仓调拨和同仓库位移动；证明没有批次×库位组合膨胀，且原 OBTL.AbsEntry 不重复。
4. 生产沿共享 OIGE/IGE1、OIGN/IGN1 的生产来源定位；组件退回、拆卸不能仅按收货单据类型标为成品产出。此处仅沿用当前模型边界，不引入新生产统计口径。
5. 区分原始单据数量、库存单位数量、批序列分配数量、库位分配数量；测试负数、冲销及数量符号，确认后才定义可加指标。
6. 语义视图声明字段类型、中文名称、行粒度、数量含义、单据定位字段和适用范围；通过原生保存、依赖检查与引擎编译/查询验证。不得将本文候选 SQL 路径标为已验证视图。

本轮产出仅为研究建议。P1 草稿保存、视图实施、发布状态需由实际工作区检查和后续实施结果分别确认。

## 实施补充核对：2026-10-22

下列 SQL 是依据上文官方键提出的**设计推导**，用于实现与验证，不是 SAP 发布的标准报表 SQL。本次补充只改本文，不修改模型或 P1。

### 交货查询先保留日志角色

本次再次检索 SAP Help 的表参考、SDK 属性和业务说明，未找到证明“所有交货均只用 DocType=15”或“ApplyType=15 的数量可直接累计为交货量”的官方算法。特别是 `ApplyType=15 AND DocType<>15`，官方字段定义允许两种角色独立表达，但未给出完整场景表；不能凭社区示例判定它必然表示实际发货、释放或后续开票。建议先落地“销售交货关联批序列日志”，同时保留两个角色的三元组、StockEff 和原始数量。

可用以下关联框架兼顾两个角色；OR 在同一 JOIN 中不会因为一个日志同时满足两组条件而生成两个相同匹配。必须再校验物料，输出 `MatchesDoc`、`MatchesApply` 两个独立标记，不能用 COALESCE 掩盖角色差异。

```sql
FROM dln1 d
JOIN oitl l ON l.ItemCode = d.ItemCode AND (
    (l.DocType = 15 AND l.DocEntry = d.DocEntry AND l.DocLine = d.LineNum)
 OR (l.ApplyType = 15 AND l.ApplyEntry = d.DocEntry AND l.ApplyLine = d.LineNum)
)
JOIN itl1 a ON a.LogEntry = l.LogEntry AND a.ItemCode = l.ItemCode
LEFT JOIN obtn b ON l.ManagedBy = 10000044
 AND b.ItemCode = a.ItemCode AND b.SysNumber = a.SysNumber
LEFT JOIN osrn s ON l.ManagedBy = 10000045
 AND s.ItemCode = a.ItemCode AND s.SysNumber = a.SysNumber
```

此处采用两种主数据各自有官方唯一索引的 `ItemCode+SysNumber`，保留 `a.MdAbsEntry` 供一致性核查；日志粒度至少是交货原始行加 ITL1 主键。只有匹配日志才出现，不把没有日志的交货行伪装成已分配批次。SQL 不选 `d.Quantity` 或 `l.StockQty` 作为可累计批次数量；它们会在每个批次重复。`a.Quantity` 标为“批序列日志原始数量”，并同时给出 AllocQty、ReleaseQty、PickedQty；StockEff=1 可供筛选现存量影响日志，但不自动证明全部发货数量口径已经验收。

若目标样本证明 Doc 路径足以代表本次实际出库，可以另建明确范围的实际出库视图；若需要 Apply 角色，须保留本节双角色证据，不能先 UNION 两个查询再累计。依据仍为上文 [OITL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OITL.html)、[ITL1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ITL1.html) 与批序列主数据索引。

### 库位流水的单一事实起点

```sql
FROM obtl t
LEFT JOIN oilm m ON m.MessageID = t.MessageID
LEFT JOIN obin n ON n.AbsEntry = t.BinAbs
LEFT JOIN obtn b ON m.SnBType = 10000044
 AND b.AbsEntry = t.SnBMDAbs AND b.ItemCode = m.ItemCode
LEFT JOIN osrn s ON m.SnBType = 10000045
 AND s.AbsEntry = t.SnBMDAbs AND s.ItemCode = m.ItemCode
```

主键为 `t.AbsEntry`，采用 LEFT JOIN 保留无消息、无主数据或 -1 标记事实。输出原始 `t.Quantity`、m.ActionType、m.AccumType、m.SnBType、m.TransType/DocEntry/DocLineNum、仓库与库位，另输出 ITLEntry 以便回查。类别可以将动作 1/2/19/20 分别显示为入、出、库位转入、库位转出，其他动作显示原始代码；**不计算** `ABS(Quantity)`、再次乘 -1 或统一净额。OILM.EffectQty、TotalLC 等消息级数量/金额不作为库位事实的可加字段。依据：[OBTL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OBTL.html)、[OILM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OILM.html)。

OBTL 表页和 DI 库位 Quantity 属性都未规定所有事件的正负。DI 属性只说明该库位的分配数量，也不能代替数据库日志的符号约定。[SAP 库位 Quantity 属性](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DocumentLinesBinAllocations~Quantity.html)

### 当前库位库存拆成两种可加范围

1. “物料库位总库存”以 OIBQ 为事实起点，LEFT JOIN OBIN.AbsEntry=BinAbs。其 OnHandQty 包含批序列物料；不能称为普通物料专用，也不要与下一视图合并累计。
2. “批次/序列号库位库存”分别以 OBBQ、OSBQ 为事实起点，使用 `SnBMDAbs=OBTN.AbsEntry` 或 `OSRN.AbsEntry`，并校验 ItemCode，再连 OBIN。两分支 UNION ALL 时加固定管理类型与来源表；键使用来源表加 AbsEntry，避免两表同号碰撞。输出 OnHandQty 原值，零库存是否显示由查询过滤决定；保留库位、仓库和主数据关联状态。

四个待补表中的 ID 字段均为 Int(11)，数量为 Num(19.6)，ItemCode 为 nVarChar(50)，WhsCode 为 nVarChar(8)。这些是 SDK 10.0 的预期结构；仍由父任务核对目标库实际类型与可空性。OIBQ 另有冻结相关字段，不因“最小视图字段”而声称它只含五列。依据：[OIBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OIBQ.html)、[OBBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OBBQ.html)、[OSBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OSBQ.html)。

本地现有 OITL/ITL1/OILM 模型已具备上述 JOIN 字段和主要角色字段；ITL1.OrderedQty 不在公共模板选择中，若使用需单独检查实例并补齐。上述方案不要求把其他候选 OITL 扩展字段一次性全部加入。
