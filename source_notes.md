# 来源与模板边界

## 证据顺序

1. SAP Business One 数据库参考确定标准表、字段、键和存储枚举。
2. DI API 说明用于解释字段的业务角色、日期、金额、单位、分录与单据关系。
3. 实际公司库结构可用于制作工作区适配层，不能把某一实例的字段缺失或样本通过推广成通用结论。

使用的 SDK 归档标签为 `SAP Business One SDK 10.0 FP2508`，DI API 页眉版本为 `10.00.300`。两者均不证明目标公司库的实际安装版本。`SDK_EN.chm` 是综合帮助入口；数据库参考及 DI API 详细内容还分别位于 `REFDB.chm`、`REFDI.chm`。

表级来源在 `source-provenance.json` 记录官方地址、HTML 内容哈希和可用的 SDK 相对路径。部分独立数据库页未打包在本地参考文件中，使用 SAP 在线参考补充；这不表示数据库中不存在对应表。

官方入口：[SAP Business One SDK Help](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/index.html)。示例字段说明：[Document Lines / LineTotal](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~LineTotal.html)。

## 未机械复制的定义

- DI API 枚举序号与数据库存储值可能不同。例如生产行的物料/资源类型应使用数据库字段枚举，不能直接将 API 枚举序号写入 SQL 条件。
- `DocEntry` 是内部单据键，`DocNum` 通常是显示单号；支付应用表中的同名字段有不同职责，不能按名称拼接。
- `DocDate`、`TaxDate`、创建日期和核销日期分别描述不同事件。
- 交易数量、库存单位数量、交易金额、估价层金额，以及本币、外币、系统币金额分别使用。
- 生产入库可能涉及完成、拒收、组件退回和拆卸，不能全部计为成品产量。
- 当前价格、库存和核销余额不直接回答历史期间发生额或余额；金额 `NULL` 不能自动变成已确认的零成本。
- `ProfitCode` 所代表的分配规则与成本中心分开，分配明细可能有多个成本中心或有效期。

## 从工作区候选提取为模板时的处理

保留经过官方定义对照的标准模型和字段。移除实例级描述、5 个 Views、5 个 Cubes；原候选没有 UDF 或计算列，构建器仍会拒绝它们进入模板。重置逻辑 catalog 为 `sap_b1`，物理引用仅保留 `schema: dbo` 和标准表名，不含实际公司库、连接和访问凭据。

字段 `OITM.LEADTIME` 统一为官方拼写 `LeadTime`。价目表不再默认选择编号 1。每日汇率说明不再包含某客户的字段数量。`OOCR`、`OCR1` 明确为分配规则及其明细，并保留其成本中心和生效期粒度。

原运行实例为兼容而保留的关系不一定适合作为通用模板默认。这里移除 `DPI1 → DLN1`、`RCT2 → ORCT`、`VPM2 → OVPM` 三条仍待业务复核的旧边，并移除无类别过滤的两条收付款到业务伙伴关系，保留带 `DocType` 与 `CardType` 条件的客户、供应商分支。全部清单见 `validation/deferred.json`。

首版没有将特定公司库放行的三条估价来源路径及退货后再次交货路径直接升级为模板默认。本次只补充下节明确审查的发料组件与发货估价来源两条标准键路径，其余候选继续待审。没有把实际业务抽样记录、金额、交易编号或公司名称复制进仓库。首版结构范围来自已整理的标准模型；没有据此声称未包含的标准表在所有公司库都不存在。

## 工单发料来源与金额职责修正

2026-10-20 结合官方字段和唯一键定义、目标生产业务的手工与倒冲来源核对，增加以下标准来源关系。它们只定义键路径及基数，不构成所有生产流程、估价方法或历史金额已经验收的声明。

| 来源关系 | 条件与基数 | 验证边界 |
| --- | --- | --- |
| `IGE1 → WOR1` | `BaseType=202`，`BaseEntry=DocEntry`，`BaseLine=LineNum`；多对一 | 同物料可存在于不同工单及同工单不同组件行，不能按物料编码连接；当前发料 `LineNum` 不能代替 `BaseLine`。来源特殊值保留未匹配。 |
| `OIVL → IGE1` | `TransType=60`，`CreatedBy=DocEntry`，`DocLineNum=LineNum`；多对一 | 发料行反向可有零条、一条或多条估价交易。非库存费用可能没有 OIVL；无估价不能解释为零成本。 |

官方依据为 [IGE1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IGE1.html)、[WOR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WOR1.html)、[OIVL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIVL.html) 的字段、类型及主键定义，以及 DI API 的 [BaseLine](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Document_Lines~BaseLine.html)。条件由这些官方定义组合并通过目标来源核对，并非宣称官方文档逐字提供了这两条完整 SQL。

字段职责明确分开：

- `IGE1.StockValue` 与 `IGN1.StockValue` 的官方定义是 **Total COGS Value（总销货成本值）**；不是通用的库存过账金额。生产发料可出现该字段为零而真实库存过账非零，因此更正旧的泛化中文名称。
- 新增 `IGE1.StockSum`、`IGN1.StockSum`，官方名称为 **Stock Sum**。它们用于单据行库存金额核对，不因某些样本和 `LineTotal` 相等就定义恒等式；缺估价时不能自动回退到任一单据金额。
- `OIVL.SumStock` 保留库存价值增减方向，常规发料为负；明确展示正向发料成本时取负值，不能用 `ABS` 吞掉冲回。`OIVL.Currency` 是 **Price Currency**，不是该库存金额的币种标签；库存本币口径以 `OADM.MainCurncy` 解释并与库存科目核对。
- `IGE1.StockPrice` 是现成的单据行库存单价，`IVL1.CalcPrice` 是估价层计算单价。过账折算单价为明确口径的发料成本除以库存单位数量，可能因金额与价格舍入而不同于已存单价。计算多行综合折算单位成本时，在同币种且同库存数量单位范围内用总成本除总数量；零数量或未知金额不生成该折算值。记录单价的算术平均是另一个统计量，明确请求时可以 AVG，并标明记录粒度，不能称为综合单位成本。
- 新增 `OIVL.InvntAct/WipAct/WipVal` 便于区分库存及在制品核对。财务对账应使用完整来源单据、库存科目和对应分录，不能将单一工单子集与整张多工单凭证比较。

数量和日期同样需要保留角色：`InvQty` 是库存单位数量，不能与使用其他单位的 `Quantity` 混算；跨单位数量分组展示。实际发料过账日期取 `OIGE.DocDate`，`IGE1.DocDate` 可以为空。先限定工单，再求实际日期范围或一次按月分组，不能将工单 `OWOR.PostDate` 当作发料起点，也不能仅按物料编码扫描无关历史。

本次标准来源、字段及金额职责的有限复核记录由使用方在私有环境保留。公共仓库只包含规则和完全自造的回归数据，不含原始客户金额、物料分类编码或查询结果。生产退料、拆卸、拒收、取消、关闭差异及多层真实金额仍需相应目标样本和 SAP 报表验收。不得把全部生产收货直接从发料中扣除，或把材料发料成本称为工单最终总成本。

### 可执行查询示例

2026-10-20 继续核实价格与单位后，采用以下有条件的解释，并保留证据等级：

- **官方直接规则**：[永续库存初始化](https://help.sap.com/docs/SAP_BUSINESS_ONE/87e1767ca7584b8f8d60775347637b07/0336ba3eb7d346c0958a10d4b5b554b6.html?locale=en-US)明确物料成本以本币计算；[DI LocalCurrency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~AdminInfo~LocalCurrency.html)将本币映射为 OADM.MainCurncy，并说明正常账套在产生规定业务记录后不能修改本币。
- **历史单位来源**：[官方发料窗口](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/4522e93573c80108e10000000a114a6b.html?locale=en-US)说明使用库存单位时行数量就是出库库存数量，换算数为 1。结合 [IGE1 字段](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ige1.html)与 [DI MeasureUnit](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/SAPbobsCOM~Document_Lines~MeasureUnit.html)，UseBaseUn=Y、NumPerMsr=1 且 unitMsr 非空的历史行，可使用该行保存的单位名称；不需要用当前物料名称替代。UseBaseUn=N、单位缺失或矛盾时仍须核实历史映射。unitMsr2 是使用基础单位时的采购/销售单位，不能代作库存单位。
- **价格字段的组合解释**：在 OADM.ContInvnt=Y 的正常库存物料发料中，根据官方成本规则采用本币；仅对 UseBaseUn=Y、NumPerMsr=1 且历史 unitMsr 明确的行，将 IGE1.StockPrice 解释为本币/该库存单位。对应发料估价层 IVL1.CalcPrice 可作同范围解释，但其字段级依据较弱。UseBaseUn=N 时价格分母及换算规则仍待核，不能认为只缺单位名称。SDK 分别只称库存价格和计算价格，本模板不宣称 SDK 直接逐字给出了这条完整映射，也不宣称库存审计报告某列恒等于 CalcPrice。实际币种与单位必须查询相应配置和正确关联的历史行。
- **仍不覆盖的范围**：资源和非库存物料、多层综合价格、重估、零数量、负库存调整、特殊冲销及非标准账套迁移，不能直接套用上述字段解释。单据头 DocCur 不通用于所有金额；单据行 Currency 与 OIVL.Currency 仍各自解释原始交易价格，不为库存成本提供币种。StockPrice、CalcPrice 和金额/数量的折算单价保持独立，数值相近不建立定义等价。

上述依据属于业务语义；通用 Agent 无须添加 SAP 字段判断。模板没有写入实例币种、单位、金额或工单答案。

`validation/production-issue-query.sql` 演示限定工单、按 `TransSeq` 聚合层后按来源行聚合交易，再返回每条发料行。它是验证资料，不会被模板自动导入为 View。参数 `@production_order_entry` 必须绑定已解析的内部键；不要把外部显示单号直接填入。

输出将 `stored_inventory_unit_price` 与 `effective_unit_cost` 分开，同时保留层计算价的最小值和最大值以表达多层范围。无估价的非库存物料标为 `not_inventory_valued`，库存物料缺估价标为 `missing_valuation`，金额不完整标为 `incomplete_valuation_value`，相应金额保持 `NULL`；`available` 只表示交易金额字段齐全，不表示业务报表已经验收。汇总时需同时报告未估价/不完整行数，不能用 SQL `SUM` 忽略 `NULL` 后声称得到全部组件成本。

业务分类由工作区确认，例如“钢板”的集合、数量单位、期间与退料范围应使用业务规则或明确选择；公共模板没有内置任何客户物料清单。库存科目对账和标准报告选择还须遵循 [永久盘存指南](https://help.sap.com/doc/b23e727e45434829a926e6ab06d4b69e/10.0/en-US/How_to_Set_Up_and_Manage_a_Perpetual_Inventory_System.pdf#page=85) 的本币、日期模式和公司/仓库成本范围。

## 销售模块语义与字段来源

2026-10-20 的第一轮销售整理覆盖现有 18 张销售表，共用 `OADM` 的公司币种配置。核心金额保留本币、外币与系统币职责；普通销售头行的币种映射证据等级沿用[币种研究](validation/sales-currency-research.md)，不把行价格 `Currency` 推广为所有金额的币种。

`0.4.0` 增加 121 个标准字段，逐表核对官方存在性和类型；补齐七组头行的税费、舍入、行含税金额及价格，完善服务单据与历史描述字段。11 条新维度关系包括退货/预付款的销售员、编号系列，以及七种销售行的科目。系列关系保留对象类型；科目关系不证明会计过账。新增字段、直接官方链接和页面哈希由 `source-provenance.json` 记录。

[价格税费研究](validation/sales-amounts-research.md)区分数据库直接定义与定价规则的组合解释；[流程研究](validation/sales-lifecycle-research.md)区分逐表取消枚举和实际取消流程、手工关闭和履约、日期职责及预付款阶段。既有 11 条直接营销来源关系保留，退货后再交货及 `RIN9 → ODPI` 等待审路径继续隔离；`RIN9.BaseAbs` 文字提示不自动放行关系。

`ODPI.DpmAmntFC/DpmApplFc` 和抵扣附属表部分 FC 字段的具体币种来源仍待核实。模板没有新增客户净销售额、提成、历史账龄或通用税费重算公式。新字段要求目标库存在相应标准列；不修改 SAP 数据库 schema，不改变已有字段名、类型和主键。目标验证和正常导入发布单独执行，公开仓库只保存通用依据与自造场景，见[销售测试映射](validation/销售语义-测试映射.md)。

## 验证含义

校验和测试验证字段引用、官方主键、分文件组装的可复现性、实例数据隔离，以及代表性的类型和复合键连接行为。新增自造样本覆盖不同工单同物料、来源行号与本行号不同、多交易多层防重复、零 COGS 对应非零过账、缺估价、部分 NULL、冲回符号及零数量单价。它们证明示例查询的边界行为，不替代真实 SAP 多层/退料业务验收。模板版本由清单与分文件源共同组成，不依赖已提交的 MDL 产物；本地导出只在明确传入输出路径时执行。工作区导入还需执行 tBI 的 MDL 校验和数据源适配。此仓库未附带已经全面通过业务验收的库存成本、工单发料或历史财务报表结果。
