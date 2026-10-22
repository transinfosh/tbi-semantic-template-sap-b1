# SAP B1 库存与生产语义独立审查

审查日期：2026-10-22。范围：P1 草稿中的库存、生产及关联主数据，重点为新增 OBTL/OIBQ/OBBQ/OSBQ、8 个库存与生产 View，以及销售交货批序列 View。用户确认的官方依据为 SAP Business One SDK 与数据库表参考。本报告仅审查，没有修改模型、关系、View、P1 或 SAP 数据。

## 结论与证据范围

保留 **2 项 P2 问题，没有获得足够证据认定 P1 问题**：OITM 最近采购价格缺配套币种；OITM 启停状态仅保留启用字段，缺停用字段。原生产来源键项仅基于人为缺失工单的输入，未证明其在 SAP 正常业务中可发生，现已撤回。保留两项属于常用业务所需信息缺失，不是要求补齐全部 SAP 字段；全局覆盖审查亦已发现，汇总时应去重。

新增四表的 23 个字段和 14 条关系未发现确定的错误目标键；9 个 View 的冻结 SQL 与仓库文件逐一一致。独立合成执行中，7 组库存检查通过；两个刻意缺失工单的案例不作为业务缺陷证据。合成执行结果仅证明给定输入的 SQL 行为，**不代表输入合法或真实 SAP 业务已完成对账**。

建议保留共享库存收发四表 `OIGE/IGE1/OIGN/IGN1` 和新增库位四表：前者承载普通库存与生产的不同来源，后者分别承载历史分配、物料总量与批序列分量，不能互相替代。未发现应因“用途重叠”删除这些表的依据。

实际审查对象是审查开始时保存的 P1 完整只读快照：109 表、3,244 表字段、408 关系、16 View、320 View 字段、0 Cube。公共默认模板 0.8.0 与工作区扩展包、P1 草稿、V18 冻结发布是不同对象；本文不把默认模板未包含扩展包称为导入遗漏。库存与生产的 8 个 View 共 144 列，加销售交货批序列 View 共审查 169 个 View 列。

证据分级如下：

| 等级 | 含义与本次用途 |
| --- | --- |
| A | 本次直接读取的 SAP 官方 SDK 表参考、DI API 属性或业务帮助；用于证明字段、索引、枚举及业务角色 |
| B | 冻结 P1 原生文档、MDL、当前仓库定义；用于证明实际存在、缺失或采用的 SQL |
| C | 仅使用合成数据执行冻结 SQL；用于证明指定输入下的结果、连接粒度和最小建议效果 |
| D | 已有只读源结构和受限业务样本；仅证明所采样目标库的结果，不能推广为所有 SAP 流程 |

本次重新检查了既有源结构证据中的四表主键及所选字段类型，也重新计算了既有 30 条交货日志的数量核对结果；没有新增查询 SAP 业务表。公开报告只记录结构和汇总判断，不复制客户数据库名、客户编码或原始业务记录。

## 已确认的问题

### 已撤回 INV-PROD-01：人为缺失工单不构成业务缺陷证据

原合成场景保留来源为生产工单的库存行，却刻意不创建对应 OWOR。它只证明了未匹配关联时 LEFT JOIN 的行为，没有证明这种输入可以在 SAP 正常业务中发生。根据用户反馈，撤回此项 P2 判定，不要求修改两个生产 View 的工单键投影；相关 SQL 和 P1 保持现状。

后续应先以官方规则或现场证据确认场景满足 SAP 正常业务约束，再用合成数据检验逻辑；不能只凭人为制造的缺失记录要求增加防御性处理。

### INV-PROD-02 · P2：保留最近采购价格，却遗漏其币种

**对象与位置：** P1 `oitm`；[models/oitm.json](../models/oitm.json) 第 213–224 行，`LastPurPrc`。模型保留 `LastPurDat` 与 `LastPurPrc`，没有 `LastPurCur`；价格描述也未声明币种缺口。

触发场景是用户询问“物料最近采购价是多少”或比较不同物料的最近采购价。模型可返回数值和日期，但不能回答该价格是何种货币；若消费者默认使用公司本币或直接比较裸数值，会产生错误的价格解释。OADM 本币不能替代最近采购记录保存的币种。

SAP 官方将 `LastPurPrc` 与 `LastPurCur` 分别定义为最近采购价格及最近采购币种。既有目标结构证据也包含 `LastPurCur`，类型为 `nvarchar(3)`，因此不是目标库无此字段。[SAP OITM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITM.html)。证据等级：A+B+D。

**核验法：** 静态检查 P1 和模板的列集合，应能同时找到价格、币种、日期。使用两条合成记录 `10 USD` 与 `10 EUR`，当前投影均只有 `10`；现有模型中没有可用于恢复差异的配套字段。无需读取真实价格即可证明信息丢失。

**最小建议：** 增加 `LastPurCur`，名称为“最近采购币种”；在价格说明中要求按此币种解释、跨币种比较需明确换算基准。不要同时扩展成完整价格历史模型，也不要用最近采购价替代库存计价。本项与全局覆盖报告合并为一个问题。

### INV-PROD-03 · P2：物料启停字段不完整，无法回答停用期间查询

**对象与位置：** P1 `oitm`；[models/oitm.json](../models/oitm.json) 第 452–486 行。已暴露 `validFor/validFrom/validTo`，其中 `validFor` 标题为“是否有效”，却没有 `frozenFor/frozenFrom/frozenTo`。

触发场景是“列出今天处于停用期的物料”或“库存中哪些物料设置了停用期间”。当前启用标志与日期不能代替独立停用设置，查询无法完整表达；“是否有效”又容易让消费者误以为一个字段就代表当前可用性。这里确认的是字段缺口，并未根据不完整资料发明启用／停用冲突时的优先级算法。

SAP 表参考分别列出启用和停用字段；DI API 的 Frozen、FrozenFrom、FrozenTo 进一步说明停用标志及起止时间。目标结构证据中三字段均存在，分别为 `char(1)` 和两个 `datetime`。[SAP OITM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITM.html)、[SAP Items.Frozen](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Items~Frozen.html)、[SAP Items.FrozenFrom](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Items~FrozenFrom.html)、[SAP Items.FrozenTo](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Items~FrozenTo.html)。证据等级：A+B+D。

**核验法：** 固定同一组启用字段，构造不同的停用标志／期间，当前模型投影无法区分这些设置，也不能筛选“已设置停用但尚未到开始日期”的物料。该信息差异不需要推定 SAP 对冲突配置的最终有效状态。

**最小建议：** 增加三项停用字段，将 `validFor` 标为“启用标志”并明确起止日期语义。若后续增加“指定日可用”计算字段，另核 SAP 的日期边界、空日期和启停组合规则；本次不建议仅凭字段名直接写 CASE。

## 已核对且未发现确定缺陷的核心设计

### 新增四表与关系

| 对象 | 实际字段／关系核对 | 结论 |
| --- | --- | --- |
| OBTL | 6 个官方字段；主键 AbsEntry；MessageID→OILM，BinAbs→OBIN，ITLEntry→OITL，共 3 关系 | 三种 ID 的职责分开，没有把 MessageID 当 LogEntry。SnBMDAbs 与管理类型配合在 View 中连接，不做无类型双连 |
| OIBQ | 5 个精选字段；主键 AbsEntry；ItemCode+BinAbs 为官方唯一组合；物料／库位／仓库共 3 关系 | 当前物料库位总量；官方另有冻结字段，未将精选 5 字段说成完整物理结构 |
| OBBQ | 6 个字段；主键 AbsEntry；SnBMDAbs+BinAbs 为官方唯一组合；批次／物料／库位／仓库共 4 关系 | SnBMDAbs 定位 OBTN.AbsEntry，附加 ItemCode 一致性条件不增加行数 |
| OSBQ | 6 个字段；主键 AbsEntry；SnBMDAbs+BinAbs 为官方唯一组合；序列／物料／库位／仓库共 4 关系 | SnBMDAbs 定位 OSRN.AbsEntry，没有误用 SysNumber |

四表的结构、关系目标和唯一索引均有直接官方依据；目标库既有结构证据确认所选 23 字段和 4 个 AbsEntry 主键存在。[SAP OBTL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTL.html)、[SAP OIBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIBQ.html)、[SAP OBBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OBBQ.html)、[SAP OSBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OSBQ.html)。证据等级：A+B+D。**结构核对不等于库位真实数量验收。**

### 9 个 View 的逐项判断

| View | 核对结果 | 剩余限制 |
| --- | --- | --- |
| `inventory_batch_serial_movements` | 事实粒度 ITL1 三字段主键；StockEff=1 排除承诺／订购；按 ManagedBy 及 ItemCode+SysNumber 连接相应主表；缺主数据仍保留数量 | 只覆盖已分配批序列的现存量日志，不是全部物料流水；不能将 30 个交货样本推广为所有业务的符号证明 |
| `sales_delivery_batch_serial_detail` | DocType=15 与 DocEntry/DocLine/ItemCode 绑定原交货行；不用显示单号；输出明细分量，未重复投影单据整行数量 | 明确采用 Doc 角色的窄范围；Apply-only、预留、取消等仍待证实完整覆盖 |
| `inventory_bin_movements` | 每个 OBTL.AbsEntry 一行；直接沿原分配行关联库位与批序列；保留普通物料、缺主数据、缺消息；没有批次×库位交叉展开 | raw_bin_quantity 未标准化方向，不能直接当净收发；实际库位样本为空 |
| `inventory_bin_current_balance` | 物料库位总量；LEFT JOIN 名称／单位；保留零值、负值和缺主数据 | 不包含未启用库位仓库，不代表可拣量，也没有历史截止日能力 |
| `inventory_batch_serial_bin_current_balance` | OBBQ/OSBQ 分类型 UNION ALL，复合行键保留管理类型；没有与 OIBQ 再相加 | 当前库存单位未输出，消费者展示单位仍需补充；不应强制分量始终等于物料总量 |
| `inventory_batch_serial_warehouse_current_balance` | OBTQ/OSRQ 使用 MdAbsEntry→相应主表，覆盖未启用库位的仓库；两分支复合行键防重号 | 当前库存单位未输出；只能解释已分配批序列的当前数量，不能替代仓库完整总量 |
| `inventory_warehouse_current_balance` | OITW.ItemCode+WhsCode 粒度；预计可用量公式与当前字段含义一致；输出库存单位 | 预计可用量不是立即可拣量；不支持直接查历史时点 |
| `production_issue_detail` | BaseType=202，来源组件连接使用 BaseEntry+BaseLine；保留 ItemType、历史单位、取消和工单类型；没有将资源无类型关联物料 | 原 INV-PROD-01 已撤回；不能把所有类型的发料都解释为普通标准工单材料耗用 |
| `production_receipt_detail` | BaseType=202；保存工单类型、产品编码、来源行、ItemType 与 TranType；不把拒收自动排除 | 原 INV-PROD-01 已撤回；未提供经过验证的成品／退料／副产品／拆卸分类指标 |

OITL 官方区分 Doc、Base、Apply 角色和不同库存累计类别；ITL1 主键为 LogEntry+ItemCode+SysNumber。OBTN/OSRN 各自的 ItemCode+SysNumber 是唯一组合，而显示号索引不是唯一，因此当前带类型连接具有索引依据；MdAbsEntry 被保留用于追溯，没有错误地把它等同 SysNumber。[SAP OITL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITL.html)、[SAP ITL1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITL1.html)、[SAP OBTN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTN.html)、[SAP OSRN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRN.html)。

OILM 的 ActionType 1/2 为入／出，19/20 为库位转入／转出；AccumType 是另一维度。现有 View 的方向 CASE 没有颠倒这四种枚举，也没有把 OILM.Quantity、EffectQty 或金额复制到每个库位求和。官方 OBTL.Quantity 只有数量定义，没有给出所有动作下一律带符号或一律取绝对值的契约，所以不能据当前 CASE 再乘一次正负号。[SAP OILM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OILM.html)、[SAP 库位分配数量属性](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DocumentLinesBinAllocations~Quantity.html)。

OBTQ/OSRQ 的主键、物料系统编号仓库唯一组合及 MdAbsEntry 指向均支持现有仓库余额 View。批号、序列号与各表 AbsEntry 重号时仍保留类型，不依赖显示号唯一。[SAP OBTQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTQ.html)、[SAP OSRQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRQ.html)。

### 生产、调拨和成本粒度

- BOM 行使用 Father+ChildNum，工单行使用 DocEntry+LineNum；相同组件重复出现不被按物料合并。ITT1/WOR1 的物料、资源、文本类型有官方枚举，当前物料和资源关系分别限定类型。当前 BOM 与实际工单结构保持区分。[SAP OITT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OITT.html)、[SAP ITT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ITT1.html)、[SAP WOR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/WOR1.html)。
- 生产收货不是单一成品入库。官方说明包含拆卸产出、返回组件、副产品，完成与拒收都会入库存并影响库存计价。因此不能仅筛 `TranType='C'` 就称为全部合格成品产量，更不能把 R 视为已报废出库。现有 View 描述已有这个限制，未据此登记新 SQL 缺陷。[SAP 生产收货窗口](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/44f292f1df7365fbe10000000a1553f7.html?locale=en-US)。
- 调拨执行对申请的关系保留类型 1250000001、来源内部键和行；FromWhsCod 与 WhsCode 都保留在原模型，没有把申请未清差直接当实际移动。现有流水保留转出、转入两条事实；按公司汇总的净变动与调拨作业量是不同指标。[SAP WTR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/WTR1.html)、[SAP WTQ1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/WTQ1.html)。
- OIVL.TransSeq 是交易粒度，IVL1.TransSeq+LayerID 是估价层粒度；现有关系没有将层号当单据行，也未在两个生产 View 中直接连接估价层造成数量扩张。OIVL 原始价格币种、交易金额，单据行 StockPrice/StockSum 与层价应继续分开；`StockPrice × 数量` 不能无条件视为最终工单成本。[SAP OIVL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OIVL.html)、[SAP IVL1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/IVL1.html)。
- 两个生产 View 使用历史单据单位、换算字段、ItemType，并把保存单价与金额分开。这比仅从 OITM 当前单位解释历史记录可靠；但未完成资源、非永续、非库存物料及非基本单位场景的币种／单位实证。`document_stock_sum_lc` 的显示名不能代替这些业务条件核验，不能宣称所有生产金额口径已经验收。[SAP IGE1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/IGE1.html)、[SAP IGN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ign1.html)。

## 已知边界与待证实事项

1. **Doc／Apply 完整性仍待证实。** 重新计算既有 30 条交货样本，批序列日志量全部等于对应库存单位量的相反数，且全部 Doc 与 Apply 同键；既有角色汇总同时存在 StockEff 1 和 2。这支持普通交货样本和排除承诺日志，但不区分两个角色的候选连接。官方字段字典没有发布“全部交货只用 Doc”或“Apply-only 一定为实物出库”的完整算法；当前 View 已声明窄范围，不能仅凭字段字典把其改为 OR 或 UNION 后全量累计。
2. **StockEff=1 是在手影响类别，不是完整数量正确性证书。** 对已限定的实物批序列流水排除 2/3 合理；若查询任务是预留、承诺或订购分配，这个 View 有意不回答。要完整回答库存分配状态，应另查原日志字段，而非取消过滤后将所有 Quantity 混加。
3. **仅发出时管理批序列号会造成完整性差异。** SAP 允许收货时暂不指定批序列号。批序列明细总量不能在所有配置下强制等于 OITW/OIBQ，也不能把尚未定义的序列号当缺主数据连接错误。OITM.MngMethod 已有，但描述尚未解释 A/R；应补充这一条件，必要时再选自动创建相关字段。[SAP 序列号仅发出时管理](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/452366399e152b31e10000000a1553f7.html?locale=en-us)、[SAP 批次管理设置](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/a965187391ed47e0bcf9f12e3066f17a.html)。
4. **库位业务方向尚缺真实对账。** 既有 `bin_actions` 结果为空，原实施记录中的 3 个库位 View 和 2 个生产 View 也为空。不能把成功编译、取到空结果或合成输入得到预期符号当真实公司验收；跨仓调拨、同仓转库位、负数、退货与盘点仍需样本。
5. **生产净耗用与产量尚未形成完整业务指标。** 既有明细保留原值，没有定义统一净额；对退组件、拆卸父项、资源、拒收、副产品等，应先建立角色与单位规则再汇总。IGN1 官方还列出 BaseType=60；是否存在需沿发货单进一步追溯生产来源的目标业务路径，本次没有样本，不认定 `BaseType=202` 已漏真实生产记录，也不认定它覆盖全部冲回。[SAP IGN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ign1.html)。
6. **来源字段和当前主数据的时间边界。** 现有 View 的 OITM 单位和 OWOR 当前状态是当前配置，不等于某历史交易日的主数据状态。历史库存单位未确定时，应保留不确定性；不能从 Quantity=InvQty 推出单位名称。

以上是边界与待证实项，不计入已确认缺陷数量。进一步源验证应有明确单据集合、日期边界和返回行数；本次没有发起这些额外业务查询。

## 字段和表的取舍建议

| 分类 | 对象／建议 | 原因及边界 |
| --- | --- | --- |
| 必要修补 | LastPurCur；frozenFor/frozenFrom/frozenTo | 对应保留问题；生产来源键项已撤回，不实施该修改 |
| 常用展示缺口 | 两个批序列当前余额 View 补当前库存单位；位置在 `pack.json` 第 931–963 行及对应 SQL 输出列 | 同类物料总余额 View 已输出单位，批序列余额缺失会影响直接展示；由全局 View 可消费性审查主列，汇总去重。新增当前单位仍须标“当前”，不能替代历史单位 |
| 条件补充 | OIBQ.Freezed、FreezeDoc | 当问题是盘点冻结／可操作库存时有用；仅回答在手数量时非必需。当前 View 没有声称提供即时可拣量，因此不以这两个字段缺失认定当前数量错误。[SAP OIBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIBQ.html) |
| 条件补充 | UGP1.BaseUdfFtr、BaseWgtFtr，以及因子引用的解释 | 当前只选 UdfFactor/WghtFactor；动态换算两侧可能有配置。官方另列基准侧字段；开展复杂动态换算前必须核对，不能只看一侧是否为默认值。普通固定换算不因此要求整批扩表。[SAP UGP1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/UGP1.html) |
| 条件补充 | OSRN.MnfSerial、LotNumber、GrntStart、GrntExp；批序列 View 的状态／有效期 | 售后按厂家序号、保修或临期库存查询时有价值；目前 OBTN/OSRN 已有内部键与基础追溯能力，不把这些场景一律算成必加。[SAP OSRN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRN.html) |
| 条件补充 | WTR1/WTQ1 的调出仓库角色关系，生产收货到组件行的带类型关系 | 原字段足以手写连接，但稳定角色关系可减少 AI 猜测；需要确认角色命名与关系消费方式，不以“没有第二条关系”认定当前流水丢失一边 |
| 条件扩表 | 盘点、库存过账、库存期初、重估、工序与资源产能实体 | 这些是独立业务能力；用户需要盘点差异、重估来源或产能计划时再按对象增加。OIVL 已可保留部分相关交易类型，不等于相应单据明细已建模，也不意味必须立即补齐所有业务表 |
| 暂不需要 | 为当前四表和 9 个 View 全量增加单据库位子表或更多消息细节表 | 当前 OBTL 已保留批序列与库位的原始组合，不能为了“表齐全”再引入第二条未验证的多行展开路径 |
| 候选降噪 | OBIN.Attr1–10 的内部 ID／值、Instance／Transfered；OBTN 的保修／跟踪技术字段；OUOM/OUGP.LogInstanc | 作为可选字段或隐藏字段可能更合适。尚无使用统计和完整消费者依赖证据，不建议直接删除；特殊仓储、追溯或维护场景可能依赖它们 |

OUOM 使用 UomEntry、OUGP 使用其内部键，UGP1 使用 UgpEntry+LineNum 的当前建模与官方键相符；单位名称不是键。P1 中的字段集合也不应仅按模板文件反推：例如本次 P1 已包含 UGP1.IsActive，而当前模板所选列与其并非完全相同。[SAP OUOM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OUOM.html)、[SAP OUGP](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OUGP.html)、[SAP UGP1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/UGP1.html)。资源当前单位和内部键则来自 ORSC，不应将其单位默认为物料库存单位。[SAP ORSC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ORSC.html)。

“多余”的判断应依据查询用途和依赖，不能以某字段在有限样本中全空就删除。尤其不要删除 `ItemType`、管理类型、StockEff、AccumType、ActionType、原始内部键、来源行、历史单位、取消标志或价格币种等约束字段；它们看似技术字段，却决定业务结果能否正确解释。

## 验证记录

| 检查 | 本次结果 | 能证明的范围 |
| --- | --- | --- |
| P1 冻结 SQL 对仓库文件 | 9/9 一致 | 报告中的 SQL 行号确实对应本次 P1 审查对象 |
| 新四表所选字段及关系 | 23 字段、14 关系已核；四主键与既有源结构一致 | 结构与直接连接依据，不代表数量业务正确 |
| 批序列流水合成案例 | StockEff 1/2 分离、按类型连接、缺主数据保留通过 | 给定输入下没有承诺混入或错误类型连接 |
| 交货合成案例 | 承诺日志排除，实际日志原符号保留通过 | 不覆盖 Apply-only 或真实取消流程 |
| 库位合成案例 | 单消息多分配、批次跨库位、批序列重号、普通物料、缺消息／维度通过 | 给定输入每 OBTL.AbsEntry 仍一行，无批次×库位膨胀 |
| 余额合成案例 | 分类型联合键、总量／分量、缺维度及负库存通过 | 没有声称所有配置下分量与总量相等 |
| 人为缺失工单的合成案例 | 原缺陷判定已撤回 | 未证明输入满足 SAP 正常业务约束，不作为修改依据 |
| 既有真实交货样本复算 | 30/30 与行库存量反号，且 Doc/Apply 全同键 | 仅该样本；无法判断两角色不相同时的处理 |
| SAP 标准报表／界面对账 | 本次未执行 | 不得标为真实业务验收完成 |

合成脚本与结果保留在本次私有审查证据目录中，文件名分别为 `inventory-production-counterexamples.py` 和 `inventory-production-counterexamples.json`。脚本从冻结快照创建 SQLite 内存表，执行原 SQL；建议修复仅在内存字符串中演示，不回写仓库或工作区。

## 覆盖对象与未覆盖事项

已检查 24 个库存／生产模型的列选择、身份键、主要数量／价格字段、关系及其实际 P1 元数据：`OIGE/IGE1`、`OIGN/IGN1`、`OWTR/WTR1`、`OWTQ/WTQ1`、`OITW`、`OBTQ/OSRQ`、`OITL/ITL1`、`OILM`、`OIVL/IVL1`、`OITT/ITT1`、`OWOR/WOR1`、`OBTL/OIBQ/OBBQ/OSBQ`。共享范围包括 `OITM`、`OWHS`、`OBIN`、`OBTN/OSRN`、`OUOM/OUGP/UGP1`、`ORSC`，以及相应关系；销售侧仅覆盖 `sales_delivery_batch_serial_detail` 所需交货字段。对关键键、枚举与业务断言直接核查官方来源；这不是全部物理字段逐字段认证。

未覆盖：SAP 自定义字段和插件业务含义；所有历史单据路径；全部版本及地区化差异；真实库位盘点／转移数量对账；真实生产退料、拆卸、拒收、副产品、资源行及成本结算对账；完整库存审计报表重建；历史单位变更；所有价格币种／单位组合；自然语言 Agent 端到端回放；P1 新版发布与启用。其余销售、采购、财务及全局覆盖由并行审查报告负责。
