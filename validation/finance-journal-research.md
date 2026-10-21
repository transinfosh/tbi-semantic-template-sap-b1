# 财务凭证与项目维度官方核对

核对日期：2026-10-21。盘点基线：`c727ef4b919210d74f5418451db21c43b81584c0`。范围：`OJDT / JDT1 / OACT / OPRJ / OADM` 及现有凭证、科目、项目关系。本文只记录研究证据与建议；不表示模型已修改、公司账簿已对账、实例已发布或业务验收已通过。

本次实际浏览 SAP Business One SDK 10.0 Database Tables Reference、DI API 属性页及 SAP Business One 10.0 应用帮助。只采用 SAP 官方来源；没有访问客户数据，没有从客户样本推导公共规则。字段、键、粒度、币种和聚合规则属于模板语义定义；不建议增加按 SAP 表名触发的通用 Data Agent 或运行时特判。

## 1. 证据层级与官方资料冲突

数据库模型的字段拼写、长度及索引以表参考为主要依据，DI API 和应用帮助补充业务行为。官方文档自身也有不一致，不能把任意属性页的一句话当成完整数据库契约：

| 项目 | 实际看到的差异 | 本文采用的解释 |
| --- | --- | --- |
| `ShortName` | DI 属性页称 account name/description；REFDB 称 BP/Account Code，Web Client 导入说明也将其明确映射为 BP/Account Code | 使用代码语义；不能解释成科目名称。[DI ShortName](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~ShortName.html)、[官方导入字段说明](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/39de79e28e17476cba4da8a30d72292a.html?locale=es-CO&state=PRODUCTION&version=10.0_SP_2605) |
| 系统币配置 | DI SystemCurrency 页正文描述并行系统币，但 Field name 写为 `BankCountr`；REFDB 将 `SysCurrncy` 定义为 System Currency | 数据库字段绑定采用 `OADM.SysCurrncy`。[DI SystemCurrency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~AdminInfo~SystemCurrency.html)、[OADM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OADM.html) |
| 项目代码长度 | DI ProjectCode 页仍写 8 字符；OJDT、JDT1、OPRJ 表参考均为 20 | 维持数据库模型 `VARCHAR(20)`；不因旧属性文案缩短字段。[DI 行项目](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~ProjectCode.html)、[OPRJ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRJ.html) |
| 行过账日 | DI ReferenceDate1 页称 Not used；REFDB 将 `JDT1.RefDate` 定义为 Posting Date，应用窗口也列出行日期 | 解释已存字段为行过账日；不据该 DI 属性页删除字段，也不承诺该 API 可写。[DI ReferenceDate1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~ReferenceDate1.html)、[JDT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html) |

## 2. 键、编号及来源关系

| 规则 | 状态与官方依据 | 模板建议 |
| --- | --- | --- |
| `OJDT.TransId` 是分录主键；`Series + Number` 是另一唯一索引 | 已确认，REFDB 索引区直接列出；Number 按编号系列分配。[OJDT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OJDT.html)、[分录窗口 Number](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/45114b0d29fc4805e10000000a1553f6.html) | 现有主键和唯一键正确；关联继续使用 TransId，Number 用于显示及按系列查找。不能宣称 Number 单列跨系列唯一。 |
| `JDT1` 行键为 `(TransId, Line_ID)` | 已确认，REFDB PRIMARY；Line_ID 的默认值为 0。[JDT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html) | 现有复合键正确；0 是可用行号，不能按 `Line_ID > 0` 排除。核销等行关系必须携带完整行键。 |
| `OJDT.BaseRef` 与 `CreatedBy` 不同 | 已确认，DI BaseReference 对应来源单据 DocNum，Original 对应来源 DocEntry，OriginalJournal 对应类型。[JournalEntries 成员](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_members.html) | 保留“来源显示号 / 来源内部标识”的区分；CreatedBy 结合 TransType 使用。来源单据已有 TransId 时优先沿该键到分录，不从相似编号猜关系。 |
| `JDT1.SourceLine` 是任意营销行的 LineNum | 待核实；表参考仅称 Source Row Number，没有给所有业务对象的固定映射。[JDT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html) | 保持当前不自动建关系；即使组合了 TransType、CreatedBy，也不能证明所有来源都是普通商品行。 |

`ojdt_jdt1` 为头到行的一对多。其关系说明应明确连接后头字段重复出现；金额在头粒度或行粒度各自聚合，不能汇总连接结果中的重复头金额。该限制由已确认的键和一对多粒度推导，不是 SAP 提供的额外金额公式。

## 3. 账户、科目名称及成本辅助字段

| 字段 | 已确认含义、证据及限制 | 最小修正 |
| --- | --- | --- |
| `JDT1.Account` | 控制科目或总账科目代码，指向 ChartOfAccounts；DI 明确给出字段名 Account。[AccountCode](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines_members.html) | 现有语义正确；完善 `jdt1_oact` 的说明，按内部 `AcctCode` 取科目名称，不从 ShortName 猜总账科目。 |
| `OACT.AcctCode / AcctName / FormatCode` | AcctCode 为主键；AcctName 为名称；FormatCode 为分段科目号码。[OACT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OACT.html)、[Code](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~ChartOfAccounts~Code.html)、[FormatCode](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~ChartOfAccounts~FormatCode.html) | 当前方向正确；名称仅作当前主数据展示，不当键，不承诺历史名称。FormatCode 不是 Account 的替代连接键，REFDB 未将它列为唯一索引。 |
| `JDT1.ShortName` | BP/Account Code；导入字段中 Account Type 可为 GL/BP，Account 字段在 BP 场景对应控制科目。[官方导入字段说明](https://help.sap.com/docs/SAP_BUSINESS_ONE_WEB_CLIENT/2554bf7e9aa347729b0547a737e123ac/39de79e28e17476cba4da8a30d72292a.html?locale=es-CO&state=PRODUCTION&version=10.0_SP_2605) | 保留双重代码语义。BP 路径应有适用范围，不能通过内连接 OCRD 删除普通科目行；不凭 Account 与 ShortName 是否相等定义所有版本的 BP 判别器。 |
| `JDT1.ContraAct` | DI 只称 offsetting account code；REFDB 未声明 OACT 外键。[ContraAccount](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~ContraAccount.html) | 当前“对方会计科目编码”过强，建议“对方账户标识”；不默认建 OACT 外键。详见下述证据边界。 |
| `JDT1.DebCred` | 已确认枚举 `D` 借、`C` 贷。[JDT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html) | 补枚举，不依据该标记给已带借贷侧和符号的金额再翻转一次。 |
| `ProfitCode / OcrCode2…5` | DI CostingCode 系列是维度 1…5 的分摊规则，能够分配到一个或多个利润中心。[CostingCode](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~CostingCode.html)、[其他维度属性](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines_members.html) | **明确纠错**：从“利润中心编码”改为“维度 n 分摊规则代码”。本轮不必扩展成本分摊明细或新增利润中心关系。 |
| `OACT.RealAcct` | REFDB 定义为 Indexed Account，枚举 Y/N。[OACT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OACT.html) | **明确纠错**：删除“实际科目通常用于资产、负债和权益”；建议“指数化科目标记”。不据其生成资产负债表或损益分类。 |
| `OACT.ActCurr` | 账户币种配置可包含多币种值 `##`。[AcctCurrency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~ChartOfAccounts~AcctCurrency.html) | 补充 `##` 是多币配置值，不能作为真实货币单位给历史行 FC 金额赋值。 |

关于 ContraAct：官方分录窗口允许从本单已过账的账户中指定对方账户；斯洛伐克 Cash Report 明确其 offset account 可以是业务伙伴或总账科目。[分录窗口](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/45114b0d29fc4805e10000000a1553f6.html)、[斯洛伐克 Cash Report](https://help.sap.com/docs/SAP_BUSINESS_ONE/d6857707057349e9ade176fa9a3d4de1/3d625154d778439f9cb3b06b4993c390.html?locale=en-US&state=PRODUCTION&version=10.0)。这足以反对“对方账户必为纯总账科目”的通用假设；但地区报表说明没有逐字段声明 ContraAct 的存储映射，**本次仍未证实所有地区、版本下 BP 代码进入 ContraAct 的完整规则**。一个标量对方账户字段也不等于完整的多借多贷配对明细，不应据此复制金额到所有其他行。

## 4. 项目维度与历史保留

| 事项 | 已确认依据 | 模板建议 |
| --- | --- | --- |
| 代码及名称 | OPRJ 主键为 PrjCode，PrjName 是名称；没有 PrjName 唯一索引。[OPRJ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRJ.html) | 按代码关联，当前名称用于显示；同名项目不能合并成同一实体，不能承诺历史过账时名称。 |
| 头、行项目相互独立 | DI 明确修改头项目不影响行项目，必须显式设置 Lines.ProjectCode。[ProjectCode](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~ProjectCode.html) | 现有两条项目关系都保留；按凭证头项目或分录行项目分别筛选/分组，不用头项目自动补行项目。 |
| 启用、锁定、有效期 | OPRJ 有 Active、Locked、ValidFrom、ValidTo；Active 为 Y/N，Locked 为 Y/N。[OPRJ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRJ.html) | 不在历史项目关系隐含增加当前 Active、Locked 或日期过滤。这是历史保留的模型决策，不是证明每个历史过账场景都允许停用项目。 |
| 空项目及未匹配 | 本次所查官方资料没有给出 NULL、空串、空白字符在所有版本的统一存储契约 | 保留源值与事实行，不将空代码当成一个真实项目；可在回答/展示层标识未分配或未匹配，并保留两者差异。不能自动回填头项目，也不能用名称补键。 |

当前模板已经有 OJDT→OPRJ、JDT1→OPRJ 两条按代码的多对一关系；重点是补齐字段说明及查询验证，不需要另加同义关系。代码是当前主数据关系，不包含项目名称历史版本，也不是独立项目管理对象的阶段/任务关联。

## 5. 日期、金额及三币口径

### 5.1 日期

OJDT 与 JDT1 均保存 RefDate（过账日期）、TaxDate（单据日期）、DueDate（到期日期）；CreateDate 是系统记录创建日期，不能替代过账日期。[OJDT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OJDT.html)、[JDT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html)。DI 将行 TaxDate 用于税计算/支付日期说明，仍不应将其并入 RefDate。[TaxDate](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~TaxDate.html)。

最小建议：将三个日期角色写清；行查询选行日期，头查询选头日期。账龄先说明截止时点与日期口径，不能把当前 BalDue* 值直接称为任意历史日未清余额。历史账龄重建及核销时间关系本次未研究，不新增公式。

### 5.2 金额

| 金额组 | 币种角色与依据 | 模型使用边界 |
| --- | --- | --- |
| `JDT1.Debit / Credit` | 本币借、贷发生额；与 FC、SC 列分别保存。LC 角色由应用默认本币显示、三组列与公司本币定义组合解释。[分录窗口](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/45114b0d29fc4805e10000000a1553f6.html)、[LocalCurrency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~AdminInfo~LocalCurrency.html) | 借方为正净额可定义为 Debit−Credit；这是选定的代数口径，不能自动等同收入、成本、利润或现金流。 |
| `JDT1.FCDebit / FCCredit` | DI 明确外币借、贷；FCCurrency 是**该行**外币。[行成员](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines_members.html)、[FCCurrency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~FCCurrency.html) | 先按行外币限定/分组再汇总；不能从 OJDT.TransCurr、当前 OACT.ActCurr 或 OADM.SysCurrncy 无条件补值。 |
| `JDT1.SYSDeb / SYSCred` | DI 明确系统币借、贷。[行成员](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines_members.html) | 对应同一公司 OADM.SysCurrncy，不能与 LC/FC 混加。 |
| `OJDT.LocTotal / FcTotal / SysTotal` | REFDB 直接区分头级 LC/FC/SC 总额。[OJDT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OJDT.html) | 不能当作行金额，更不能在一对多连接后重复累计；本次未证实所有交易的头总额生成算法、FcTotal 单一币种适用范围。 |
| `JDT1.BalDue* / BalFc* / BalSc*` | REFDB 为 Balance Due 三币借贷余额，与发生额分别保存。[JDT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html) | 不能替代发生额；本次未验证历史日余额重建。 |

公司本币来自 OADM.MainCurncy，系统币来自 OADM.SysCurrncy；系统币与本币可相同或不同，系统同时保存两种记账金额。[OADM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OADM.html)、[LocalCurrency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~AdminInfo~LocalCurrency.html)、[SystemCurrency](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~AdminInfo~SystemCurrency.html)。跨公司统计仍需公司范围及币种标签；不能把每库的 LC 当作相同币种直接累加。

**NULL/空外币代码仍待核实**：本次打开的 FCCurrency、FCDebit/FCCredit 说明没有给出“空即本币”“空即系统币”或“空即全币”的通用规则。多币种分录是可配置的功能，[MultiCurrencyCheck](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~AdminInfo~MultiCurrencyCheck.html) 进一步否定“整张分录天然只有一种外币”的未经核实假设。建议保留缺失标签，不自动将 FC 金额映射为 LC，不把缺失代码下的非零金额默认为可跨行汇总。OACT 的 `##` 多币配置值也不能迁移成 FCCurrency 的缺失值解释。

## 6. 冲销与调整

| 事项 | 状态与依据 | 最小建议 |
| --- | --- | --- |
| `AutoStorno` | 已确认是按 StornoDate 进行反向交易的设置。[UseAutoStorno](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries~UseAutoStorno.html) | 当前“不能据此断言已经冲销”的边界正确。 |
| `StornoDate` | 已确认是创建反向交易的日期设定，DI 默认下一月首日。[StornoDate](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries~StornoDate.html) | 日期存在不是执行成功证据，不以日期筛掉原凭证。 |
| `StornoToTr` | REFDB 仅称 Reverse Transaction，未给完整方向、无值哨兵及重复反转规则。[OJDT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OJDT.html) | **待核实**；保留当前保守说明，不新增方向未经证实的自关联，不生成统一已冲销标记。 |
| 冲销金额符号 | 官方取消帮助直接说明，可原借贷侧记录负数，或在相反借贷侧记录正数；由公司设置决定。[取消日记账分录](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/451148db29fc4805e10000000a1553f6.html) | 保留已存金额的符号；不 ABS，不按冲销标记统一再乘 −1。冲销发生额是否纳入期间取决于问题范围与日期，不能默认删除原分录和反向分录。 |
| `AdjTran` 与 `TransType` | REFDB 区分调整标记及来源类型；来源包含期初/期末及多种业务对象。[OJDT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OJDT.html) | 不把 TransType=30 等同“用户手工创建”，API 创建也可为 Journal Entry；调整、期初、期末筛选应显式。 |

取消帮助针对手工 JE 的操作，并指出业务单据生成的分录可用反向业务单据或手工分录反转。它不能证明所有业务取消都通过同一种 StornoToTr 存储方式完成，也不能把交易摘要中的“Reversal”文字当成权威状态字段。

## 7. 现有字段优先，新增候选分层处理

本轮建议首先纠正既有定义，不要求为了字段数补齐整张表：

1. 修正 ProfitCode/OcrCode2…5 与 RealAcct 的明确错释；补充 DebCred 枚举、ActCurr 的 `##`、ContraAct 非确定外键边界。
2. 完善 Account→AcctCode→AcctName 的名称路径、头行项目独立性、日期和三币角色；现有关系名、键与字段名不改。
3. 在模型说明保留负金额冲销及 FC 缺失标签边界；禁止把待核实事项写成默认计算公式。

下列确有官方标准字段，但缺失不自动意味着本轮必须新增：

| 候选 | 用途及依据 | 优先级与限制 |
| --- | --- | --- |
| `OJDT.Ref1 / Ref2 / Ref3`，`JDT1.Ref1 / Ref2 / Ref3Line` | 六列 REFDB 类型均为 `nVarChar(200)`；参考文本检索。[OJDT](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OJDT.html)、[JDT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html) | 可本轮补充为 `VARCHAR(200)`，仍应核对目标源结构可空性；不能当来源稳定键；引用字段映射受配置影响。 |
| `JDT1.FinncPriod / AdjTran / RevSource` | 行过账期间、调整标记、重估来源，表参考存在。[JDT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html) | 需要行粒度期间或重估分析时再补；本次不把 RevSource 当已实现财务报表分类。 |
| `JDT1.DocArr / DocLine / DocEntry / DocNum / DocType` | 新版参考有来源追溯字段；应用帮助仅列部分支持的来源。[JDT1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/JDT1.html)、[分录窗口 Source of Posting](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/45114b0d29fc4805e10000000a1553f6.html) | 延后；必须先逐版本核对真实 schema、支持的来源及组合映射，不能把 SourceLine 机械换成 DocLine。 |

新增字段时应同步 `reference-contract.json`、来源记录与相应功能文档，并核对目标标准版本；本文只证明所浏览的 10.0 官方参考包含该列，不证明任意补丁版本、数据库或客户 schema 都已具备它。

### 六个参考字段的精确 API 映射

| 数据库字段 | DI 属性与用途 | 实际打开的官方来源 |
| --- | --- | --- |
| `OJDT.Ref1` | `JournalEntries.Reference`，分录头第一参考代码 | [Reference](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries~Reference.html) |
| `OJDT.Ref2` | `JournalEntries.Reference2`，分录头第二参考代码 | [Reference2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries~Reference2.html) |
| `OJDT.Ref3` | `JournalEntries.Reference3`，分录头第三参考代码 | [Reference3](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries~Reference3.html) |
| `JDT1.Ref1` | `JournalEntries_Lines.Reference1`，分录行第一参考代码 | [Reference1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~Reference1.html) |
| `JDT1.Ref2` | `JournalEntries_Lines.Reference2`，分录行第二参考代码 | [Reference2](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~Reference2.html) |
| `JDT1.Ref3Line` | `JournalEntries_Lines.AdditionalReference`，分录行附加/第三参考编号；不能映射到头 Ref3 | [AdditionalReference](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~JournalEntries_Lines~AdditionalReference.html) |

上述 DI 页分别仍写 100 字符或 27 字符（AdditionalReference），与 10.0 REFDB 六列的 200 字符不一致。数据库只读语义模型按 REFDB 及实际源结构保留 200，不因较旧 API 文案截断；本次不证明 DI API 写入的最大长度。参考字段的业务值受 Reference Field Links 配置影响，不能把 Ref1 固定解释为发票号、Ref2 固定为客户订单号，或 Ref3Line 固定为分期号；官方窗口给出的只是默认及对象相关映射。[分录窗口参考字段说明](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/45114b0d29fc4805e10000000a1553f6.html)。

## 8. 建议验证与未完成边界

| 验证场景 | 要求的证据 | 当前状态 |
| --- | --- | --- |
| 同凭证多个分录行、相同行号跨凭证 | 完整复合键、头行连接计数、Account→OACT 后不放大 | 设计建议；本文未执行数据测试 |
| 科目内部代码与分段展示码不同 | 根据 Account 仍能得到正确 AcctCode、AcctName，FormatCode 单独显示 | 设计建议；本文未执行数据测试 |
| BP 行与普通科目行混合 | 不误把 ShortName 当名称，不因 BP 路径丢掉普通分录 | 设计建议；本文未执行数据测试 |
| 头项目与行项目不同、空项目、停用项目、同名项目 | 按指定粒度筛选，名称关联不合并，历史事实保留 | 设计建议；本文未执行数据测试 |
| LC/SC 不同、多行外币、空/NULL FC 代码 | 三币标签明确；按行外币分组；不猜缺失代码 | 官方角色已核对；存储边界待验证 |
| 原侧负金额与借贷对调两种反转 | 直接存储额参与计算，不重复翻号；日期范围明确 | 官方行为已确认；模板回归待执行 |
| 已设置反转但尚未执行、已执行、重复反转 | 分开设置/日期/关联证据；不得仅据 AutoStorno 判断 | StornoToTr 方向和哨兵待核实 |

兼容影响：现有字段与关系描述更新不改公司库结构、接口签名及模型键；会改变发布后的语义内容版本及 Agent 理解。新增字段或关系另行验证列存在、目标唯一性和结果粒度。本文没有触发迁移、导入、发布或运行数据修改，也没有将这些建议标为业务验收通过。
