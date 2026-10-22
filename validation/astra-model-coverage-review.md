# SAP B1 模型覆盖与 View 可消费性独立审查

审查日期：2026-10-22。依据 SAP Business One 10.0 官方 SDK、数据库表参考和当前工作区只读快照。本文只记录发现及建议，没有修改模型、SQL、数据库或发布版本。

后续修补状态（2026-10-22）：G01–G05均已修复源码及P1草稿，新增13字段、2关系和2个View单位列；中英文说明同步，隔离保存、88项回归、8条引擎编译及独立重读通过，未发布。详见[修补记录](review-fixes-application.md)。以下缺失描述及计数保留原审查快照含义。

## 结论与证据边界

当前工作区为 **109 个 Model、3,244 个字段、408 条关系、16 个 View、320 个 View 字段、0 个 Cube**。主要事实域已经形成销售、采购、库存、生产和财务的可追溯结构。本审查确认 5 项 P2：两类价格缺少解释维度、主数据启停用信息不完整、成本中心关系断开、两个批序列余额 View 缺单位。没有据此确认 P1 级数据计算错误。跨模块详细金额、来源边和库存 SQL 另由领域审查承担。

本次判定以实际工作区快照为准，公共默认模板 0.8.0 的 101 个模型不代表工作区全部内容；新增工作区扩展也不属于默认模板完整导入包。16 个 View 的当前保存 SQL 与本目录 `workspace-views/sql/` 对应文件逐一一致。当前发布 V18 未包含这些新 View，保存存在不能视为 Agent 已在生产发布版本中可用。

证据等级：

- **A：定义与结构确认**——本次打开 SAP 官方直接来源，核对当前保存对象，并以当前实际源列结构确认字段存在及类型。证明语义缺口存在，不表示已确认客户发生过错误答案。
- **B：静态消费能力确认**——核对 View 实际 SELECT、输出字段和描述；证明单个 View 的能力边界，不等同现场业务报表对账。
- **C：业务选择或核验项**——需要明确使用场景、适用本地化或业务样例后再定实施优先级。

私有审查证据为 `before.json`、本次重新读取全部 109 张表的 `current-physical-columns.json`，以及本代理生成的 `coverage-static-checks.json`。公共报告不包含公司库连接、凭据、客户业务记录或具体单号。

## 确认发现

### G01 · P2 · ITM1 报价只提供数值，缺币种与计价单位

**位置：** [models/itm1.json](../models/itm1.json) 第 18 行 `Price` 定义及第 29 行 `PriceList` 定义。实际 Model 只有 `ItemCode / Price / PriceList` 三列，源码与快照一致。

**触发问题：** “指定价目表中，各物料报价是多少、什么币种、按哪个单位报价？”当前只能返回价格数值和价目表编号。即使补上价目表名称，也不能用公司本币、业务伙伴币种或物料库存单位替代每条价格自身的币种和单位；不同币种或计价单位的数字比较会产生误导。

**官方与现场证据：** [ITM1 表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITM1.html) 明确提供 `Currency`、`UomEntry` 和 `PriceType`。当前实际源库中三列分别为 `nvarchar(3)`、`int`、`char(1)`，均存在，当前语义字段清单均缺少。证据等级 **A**。

**最小修复：** 为现有价格增加 `Currency / UomEntry / PriceType`，单位键连接既有 OUOM；说明手工或特殊单位值可能无匹配，不要求所有价格行都有单位主数据。价目表主数据本身见后文 C01，不以 OPLN 默认币种覆盖 ITM1 保存币种。仅补这组解释字段，不扩大到特殊价格或完整定价引擎。

**验证：** 用两条不同币种、不同计价单位的报价核对 SAP 显示值；结构化查询必须同时返回价格、币种、单位角色，未知单位保留空值；不得默认 `PriceList=1`，也不得把报价命名为历史库存成本。

### G02 · P2 · OITM 最近采购价格缺少对应采购币种

**位置：** [models/oitm.json](../models/oitm.json) 第 203 行 `LastPurDat`、第 214 行 `LastPurPrc`。

**触发问题：** “这批物料各自最近一次采购价格是多少？”当前已专门暴露日期和价格，却没有 `LastPurCur`。不同物料的最近采购价格可能属于不同币种，不能据 `OADM.MainCurncy` 或当前供应商设置给价格补币种；简单按价格高低排序也不代表可比采购成本。

**官方与现场证据：** [OITM 表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITM.html) 将 `LastPurPrc / LastPurCur / LastPurDat` 分别定义为最近采购价格、币种、日期。当前源 `LastPurCur` 为 `nvarchar(3)`，语义模型缺列。证据等级 **A**。

**最小修复：** 增加 `LastPurCur` 并在 `LastPurPrc` 说明中要求配对解释；保留“不是库存估价或历史生产领料成本”的现有限制。不从该快照反推具体最后采购单来源。

**验证：** 用同币种及异币种的最近采购样例，与 SAP 物料主数据核对三元组；无币种时不猜测。若要跨币种比较，应另行指定换算日期及汇率口径。

### G03 · P2 · 业务伙伴和物料启停用字段选择不完整

**位置：** [models/ocrd.json](../models/ocrd.json) 第 2 行字段清单；[models/oitm.json](../models/oitm.json) 第 453 行 `validFor` 及随后两项有效期。

**触发问题：** “列出当前停用的供应商及停用期间”“哪些有库存的物料在指定日期被冻结？”OCRD 六项 `validFor / validFrom / validTo / frozenFor / frozenFrom / frozenTo` 全缺；OITM 已有 `valid*` 三项，但没有 `frozen*` 三项。模型无法准确筛选这些状态。反过来，只见 `validFor` 的消费者容易误把它当成完整可用性结论。

**官方与现场证据：** [OCRD 表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCRD.html) 和 [OITM 表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITM.html) 均将启用、停用及各自期间分开。[Items.Frozen](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Items~Frozen.html) 说明物料可设置停用期间；[BusinessPartners 对象成员](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~BusinessPartners_members.html) 对应定义 BP 停用期间。实际源列均存在，标志为 `char(1)`，日期为 `datetime`。证据等级 **A**。

**最小修复：** 补齐上述状态和期间字段，明确数据库标志为 `Y/N`；DI API 的 `BoYesNoEnum` 不直接等于数据库存储值。先暴露原始含义，再按确认的 SAP 期间规则决定是否增加“指定日期可用”计算字段。不把当前停用状态默认应用为历史单据过滤条件。

**验证：** 覆盖持续启用、持续停用、限期启用、限期停用、期间首尾日期及空日期；与 SAP 当日状态对照。历史交易统计在未明确要求时应保留当前已经停用的对象。

### G04 · P2 · 成本中心模型存在，但分配规则到成本中心的关系断开

**位置：** [models/ocr1.json](../models/ocr1.json) 第 59 行 `PrcCode`；[models/oprc.json](../models/oprc.json) 第 79 行 `PrcCode`；[relationships/ocr1_oocr.json](../relationships/ocr1_oocr.json) 第 2 行仅连接规则头。

**触发问题：** “这条分配规则在某个有效期覆盖哪些成本中心，它们叫什么？”OCR1 已有成本中心代码与有效期，OPRC 已有名称和状态，但 408 条关系中没有 `OCR1.PrcCode → OPRC.PrcCode`，OPRC 是孤立模型。结构化语义关系无法完成已存在两表间最直接的名称解释，消费者需另查并人工拼接。

**官方与现场证据：** [OCR1 表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCR1.html) 明确标记 `PrcCode` 关联 OPRC；[OPRC 表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRC.html) 指定 `PrcCode` 为主键。两端实际源列和模型均存在，均为文本键。证据等级 **A**。

**最小修复：** 增加 `ocr1.PrcCode = oprc.PrcCode` 的多对零或一关系；名称解释不增加 OCR1 行数，历史规则不因成本中心当前停用或有效期而被删掉。将现有 `ocr1_oocr` 显示名“维度值 → 维度”改成准确的“分配规则明细 → 分配规则”可随之整理，但这不是本发现的核心。

**验证：** 同一规则、两个成本中心、两个有效期间应保持原规则行数及完整复合键；缺失主数据时保留代码。此关系只解决维度解释，不证明分录金额已按规则正确分摊。

**相关能力边界：** JDT1 已保存 `ProfitCode / OcrCode2..5`，但当前没有到 OOCR 的对应关系；销售部分行也未暴露所有分配规则维度。若要回答“按成本中心分摊后的费用”，需另明确多维选择、有效期间、权重和实际历史分配规则。不能直接把分录金额按 OCR1 行复制求和，也不能将规则代码当成成本中心代码。此后续能力按 **C** 处理。

### G05 · P2 · 两个批序列当前余额 View 缺少库存单位

**位置：** [inventory_batch_serial_bin_current_balance.sql](workspace-views/sql/inventory_batch_serial_bin_current_balance.sql) 第 11–17 行；[inventory_batch_serial_warehouse_current_balance.sql](workspace-views/sql/inventory_batch_serial_warehouse_current_balance.sql) 第 11–16 行。两者都输出物料及数量，但没有库存单位；相邻物料库位总量、物料仓库总量 View 已提供 `current_inventory_unit`。

**触发问题：** “列出各物料批次的当前库存，显示数量与单位。”单独消费这两个 View 时只能得到裸数量。特别是多个物料以不同库存单位管理时，不能把数字视为可直接相加的同一种量。模型层能另查 OITM 不代表单个已封装 View 已提供这一消费维度。

**官方与现场证据：** [OBBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OBBQ.html)、[OSBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OSBQ.html)、[OBTQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTQ.html)、[OSRQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRQ.html) 均保存物料维度的余额；[OITM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITM.html) 定义 `InvntryUom / IUoMEntry`。当前 OITM 已暴露这两列。缺口由实际 SELECT 和保存输出字段确认。证据等级 **B**；没有判定余额公式错误。

**最小修复：** 在保持 `management_type + balance_entry` 粒度的前提下，按物料键左连接当前 OITM，增加当前库存单位名称，可同时保留单位内部键；缺主数据时保留余额行和空单位。描述要求按物料及单位解释，批次、序列分量不能与物料总量再相加。

**验证：** 用两个不同库存单位的物料、同号的批次与序列余额键、缺物料主数据和零/负余额验证；加单位前后行数与各原始数量必须一致。当前单位只适用于这两个当前余额 View，不因此覆盖历史交易单位。

## 覆盖建议、过度暴露候选与非缺陷

### C01 · 共享字典覆盖建议：OCTG / OPLN / OSHP

当前 109 个模型均不含这三表。付款条件、价目表、运输方式应归共享主数据，这与既有分组选择一致；本审查不把“归共享”解释成已批准新增所有字段。

| 常用问题 | 已有键与源码位置 | 缺少的最小字典 | 建议 |
| --- | --- | --- | --- |
| 哪些客户或单据使用指定名称的付款条件 | `OCRD.GroupNum`，`models/ocrd.json:293`；单据也有各自保存值 | OCTG：`GroupNum / PymntGroup` | 支持名称解析；当前默认付款条件不替代历史单据实际到期日 |
| 客户所属价目表叫什么，报价含税还是不含税 | `OCRD.ListNum`，`models/ocrd.json:305`；`ITM1.PriceList` | OPLN：`ListNum / ListName / IsGrossPrc`，需要有效性时再加 `Valid*` | 含税角色是当前报价解释维度；默认币种不能覆盖价格行保存币种 |
| 订单、交货或采购使用什么运输方式 | `ORDR.TrnspCode`，`models/ordr.json:463` 等 | OSHP：`TrnspCode / TrnspName` | 优先连接各业务单据保存键，不用当前物料默认运输方式回填历史 |

以上键与含义已直接核对 [OCTG](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCTG.html)、[OPLN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPLN.html)、[OSHP](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSHP.html) 官方定义。三张待新增表不在当前 109 张源结构采集范围内，实施前需另核实际结构和版本。这是 **C 级能力覆盖建议**，没有把分期功能重新纳入本次范围。

### C02 · 字段多不等于字段无用，优先缩小默认展示而非删除

共享主数据中 OACT 有 110 列、OITB 有 79 列、OBIN 有 56 列、OEXD 有 32 列，全部标记可见；业务说明覆盖密度分别为 22、8、0、0 列。完整保留来源字段可用于追溯，但在普通经营问答中会混入大量配置、维护和本地化字段。

候选包括 OACT 的 DATEV、PCN874 配置，OITB 的本地化税务分类和大量默认科目，以及多个表的 `logInstanc / UserSign* / Transfered` 等维护字段。现有证据没有证明目标业务永远不使用它们，因此**不判为应删除的确定缺陷**。应按确认的本地化及业务问题决定普通展示、详细展开和隐藏策略，保留字段及已有资产兼容性。不能只因源样本全空、全零或列数多就判多余。

一个可直接清理的旧说明是 `models/itm1.json:34` 中“1 为库存明细原 SQL 使用的价目表”。它与同模型“价目表编号由业务明确指定，不默认选取某一编号”的规则并存，容易给 Agent 不必要的默认暗示。建议去掉这一历史实现备注，不改变字段或任何实际价目表选择行为。

### C03 · 未清与退货路径是复用 View 覆盖空位，已有 Model 仍可回答部分问题

16 个 View 没有专门的销售/采购未清行清单，也没有统一退货、贷项和退款追溯 View。已有销售及采购原模型包含行状态、未清量/金额和多个退货/贷项来源关系，因此不能断言这些业务“完全不支持”。

若要扩展首批常用查询，优先考虑“按行交期显示未清订单数量/服务金额”和“原始单据到退货请求、实际退货、贷项的独立路径”。不要向当前追溯 View 直接塞入重复的订单量或金额后宣称可合计；退货、贷项、现金退款是不同事实。新增范围需由常用问题驱动，不要求为了覆盖 SAP 全部表而新增。

## 全 16 个 View 的消费检查

“通过”仅表示本次检查的身份、日期、币种、单位、粒度说明未发现该类新缺陷，不代表 SQL、客户余额或发布运行全部通过。

| View | 当前消费契约与本次结论 |
| --- | --- |
| `sales_order_to_cash_trace` | 原订单行、物流行、发票行、收款应用身份及阶段日期状态明确；没有数量金额，路径行数不得当单据数。未清、退货、贷项范围见 C03。 |
| `purchase_order_to_payment_trace` | 同上；采购独立发票不在订单路径中，已有说明，属于已知边界。 |
| `sales_invoice_receipt_applications` | 应用行键、目标类型、收款与发票日期、取消状态和发票外币均提供；不等同现金实收或完整内部核销。LC/SC 需另查同公司 OADM，描述已经说明。 |
| `purchase_invoice_payment_applications` | 与收款应用对称；付款币种与发票币种分开，没有发现强制用付款币种解释发票 FC 的新缺陷。 |
| `sales_invoice_current_balance` | 单票当前差额；取消/状态/预留标志、到期日和单据币种提供。禁止贴到历史截止日，当前描述明确。 |
| `purchase_invoice_current_balance` | 同上，当前头差额不能代替包含所有贷项及结算路径的历史账龄。 |
| `production_issue_detail` | 保留历史单位、单位转换参数、类型、取消状态和实际单据日期；LC 代码需 OADM。原人为缺失工单的反例未证明输入可在正常业务中发生，相关缺陷判定已撤回。 |
| `production_receipt_detail` | 同上，保留完成/拒收类型，并说明组件退回和拆卸，未把全部收货宣称成品产量。原缺工单反例不作为业务缺陷证据。 |
| `inventory_batch_serial_movements` | 保留日志键、管理类型、Doc/Apply 两种角色、地点类型、日期、原始库存数量；没有历史单位名称。跨物料比较或展示单位前需补查原单据单位语义，不应直接使用当前名称冒充历史单位。 |
| `sales_delivery_batch_serial_detail` | 保留交货行、批序列日志键、取消状态、Doc/Apply 角色；仅覆盖交货作为 Doc 角色的库存影响，已有范围说明。历史交货单位未输出，属于单 View 能力限制。 |
| `inventory_bin_movements` | 原始库位事实键、动作、累加类型和日期均保留；数量符号尚未统一验证，当前描述没有错误承诺为净收发量。历史单位不在输出中。 |
| `inventory_bin_current_balance` | 当前总量、物料、库位、仓库、当前库存单位均提供；不是历史库存或可拣货量。 |
| `inventory_batch_serial_bin_current_balance` | 管理类型区分同号键、保留零/负数与缺维度事实；单位缺口见 G05。批次到期日/状态需另查主数据，不能把在手量称为可用量。 |
| `inventory_batch_serial_warehouse_current_balance` | 当前批序列仓库余额和承诺量分开；单位缺口见 G05。与库位层级不是相加关系。 |
| `inventory_warehouse_current_balance` | 当前物料仓库总量、当前单位和预计可用公式齐备；描述明确它不是即时可拣货或历史库存。 |
| `finance_journal_line_detail` | 分录复合键和 FC 币种齐备，LC/SC 另查 OADM。原三个日期取凭证头；后续已在源码及P1草稿追加三个独立行日期，详见[修补记录](journal-line-dates-fix.md)，不改变本报告原审查快照计数。 |

对独立金额 View 增加 `local_currency / system_currency` 可提高单次结果的完整性，但现有描述已经明确其取值来自同公司 OADM，且公司配置有独立模型，不能仅因没把币种重复放在每行就判计算缺陷。实现时也不能未经单记录约束验证就无条件连接 OADM 放大事实。

各 View 的筛选状态不等于权限边界。本次仅检查语义字段及描述，没有验证跨工作区授权、行级权限或实际 Agent 发布发现；这些属于可信执行层验证，不以描述文本代替。

## 109 个模型与关系检查清单

| 分组 | 表数 / 字段数 | 本次纳入结构与覆盖检查的全部表 |
| --- | --- | --- |
| 共享主数据 | 26 / 553 | CRD1, ITM1, OACT, OBIN, OBTN, OCR1, OCRD, OCRG, OEXD, OHEM, OITB, OITM, OMRC, OOCR, OPRC, OPRJ, ORSB, ORSC, OSLP, OSRN, OUDP, OUGP, OUOM, OVTG, OWHS, UGP1 |
| 其他 | 3 / 43 | NNM1, OADM, ORTT |
| 销售 | 22 / 851 | DLN1, DPI1, INV1, INV11, INV3, INV9, ODLN, ODPI, OINV, OQUT, ORDN, ORDR, ORIN, ORRR, QUT1, RDN1, RDR1, RIN1, RIN11, RIN3, RIN9, RRR1 |
| 采购 | 24 / 1009 | DPO1, ODPO, OPCH, OPDN, OPOR, OPQT, OPRQ, OPRR, ORPC, ORPD, PCH1, PCH11, PCH3, PCH9, PDN1, POR1, PQT1, PRQ1, PRR1, RPC1, RPC11, RPC3, RPC9, RPD1 |
| 库存 | 20 / 422 | IGE1, IGN1, ITL1, IVL1, OBBQ, OBTL, OBTQ, OIBQ, OIGE, OIGN, OILM, OITL, OITW, OIVL, OSBQ, OSRQ, OWTQ, OWTR, WTQ1, WTR1 |
| 生产 | 4 / 93 | ITT1, OITT, OWOR, WOR1 |
| 财务 | 10 / 273 | ITR1, JDT1, OITR, OJDT, ORCT, OVPM, RCT2, RCT4, VPM2, VPM4 |

静态结果：

- 当前实际源结构覆盖 **109/109** 张表，**3,244/3,244** 个选列均存在；按引擎归一类型族比较，没有发现数值/文本/日期跨类别冲突。`nvarchar → VARCHAR`、`char → VARCHAR`、SQL Server `datetime → TIMESTAMP` 不单列为缺陷。未以此宣称精度、字符排序规则、连接器往返和每个枚举均已验收。
- **408/408** 条关系所引用的模型和列均存在；其中 **383** 条多对一关系都包含目标声明的完整主键，另 **25** 条一对多关系。没有相同端点和完全相同条件的重复关系。此检查不能证明所有多态来源类型正确，也不能证明业务数据中从不出现孤儿记录。
- OADM 与 ORTT 没有默认关系是合理的边界：公司配置不应盲目扩大事实；每日汇率不能只按币种连接多个日期。OPRC 的孤立则有已确认的直接官方键可补，见 G04。
- 快照有 16 个源端 NOT NULL 主键字段仍标成语义 `notNull=false`。主键本身已声明，且本次没有证明该元数据差异造成结果错误，因此只作为一致性维护项，不提升为 P2。修复需确认源约束及导入生成逻辑，避免只是改导出文件后再次被覆盖。
- 全部 16 个 View 的 SQL 与保存快照一致；逐个检查了身份、日期角色、金额/数量口径和描述边界。没有因 0 个 Cube 而判缺陷。

## 未覆盖与后续验收

本代理没有重新运行所有客户业务表查询、完整历史对账、真实多币报价、冻结期实际样例、自然语言回放或生产发布验收；没有证明每个字段在目标公司业务中都使用或不用，也没有证明全部 408 条关系的业务完整性。源列结构读取得以确认的内容与业务样例未核验的内容分别列明。

保留已明确范围：INV9/INV11/RIN9/RIN11 继续保留；整单附加费用已纳入；不把商机、拣货、草稿审批、定制收入、特殊价格扩展、框架协议或暂缓的分期功能当成缺陷。共享付款条件、价目表、运输方式不移入销售专属分组。G01–G05已完成源码与草稿修补；C01–C03仍按常用问题选择，不自动扩围。保存及编译已验证，后续发布和业务验收独立记录。
