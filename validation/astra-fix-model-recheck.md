# Astra 模型修补独立复审

日期：2026-10-22。范围：模板 `0.8.1` 本轮三个主数据模型的字段及说明、两条新增关系、中英文说明、参考契约、兼容性及既有验证证据。本代理只新增本报告；未修改模型、代码、P1、发布内容或 SAP 数据，也未新增 SAP 业务数据连接。

**结论：本轮范围内无新增确认问题，无需增加 P1/P2 修复项。** 原 G01–G04 对应的价格解释字段、最近采购币种、启停用字段和成本中心关系已按本轮目标补齐。以下“已修正确”只针对明确列出的语义，不等同完整报价、状态计算或成本分摊验收。两个当前余额 View 由另一审查分工覆盖。

## 审查基线及证据

- 公共模板：101 模型、3,104 选列、372 关系。`template.json:39` 为 `0.8.1`。
- 本轮冻结草稿：109 模型、3,257 选列、410 关系、16 View、325 View 输出列、0 Cube。冻结证据为 `/tmp/tbi-astra-rereview-20261022-pr35ut2q/before.json`；父代理提供的 `scope.json`、`source_native_fields.json` 记录了源文件与原生草稿一致性。该持久化比较由父代理独立完成，本报告没有冒称重新连接 P1 验证。
- 已读[修补记录](review-fixes-application.md)与[原覆盖审查](astra-model-coverage-review.md)，仅用于确定范围和历史，不把其结论当作正确性证明。本次重新打开 SAP 官方数据库表参考、DI API 参考及业务帮助。
- 只读复核原始 `source-preflight.json`、`result.json`、`isolated.json`、`plan.json`、`tests.log`，以及保存脚本的断言范围；这些文件位于 `/tmp/tbi-sap-review-fixes-20261022/`。13 个新增源列的存在、类型及可空性来自既有元数据证据，未重新查询 SAP。
- V18 仍是既有发布版本；本轮修补保存在草稿。未发布是交付状态，不列为业务缺陷。

## 已修正确

| 项目与准确位置 | 正常业务场景及复核结论 | 官方依据 |
| --- | --- | --- |
| `models/itm1.json:43`、`:55`、`:67` | 用户指定某价目表，解释其中不同物料的保存价格。`Currency` 明确属于本行 `Price`；`UomEntry` 保留原单位键；`PriceType` 的 I/P/M/O 分别对应库存单位价格、计价单位价格、两者和其他单位价格。中文与英文均未把 M 解释为两笔金额，也未把价格自动折算为库存单位。 | [ITM1 表参考](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITM1.html) |
| `models/itm1.json:34`、`:78`；`relationships/itm1_ouom.json:2` | 单价仍为 `(ItemCode, PriceList)` 粒度，没有因新增单位而伪造第三个主键分量；价目表编号由请求明确选择，旧的编号 1 暗示已删除。`itm1 → ouom` 为多对一，条件覆盖目标唯一主键 `UomEntry`，无需另加物料或单位组键。该关系解释保存单位，不提供换算比率。 | [ITM1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITM1.html)、[OUOM 主键](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OUOM.html) |
| `models/oitm.json:217`、`:515` | 展示物料当前保存的最近采购价格时，可以配对读取价格、币种和日期；没有以公司本币替换 `LastPurCur`，也没有用当前价格推算历史工单领料成本。现有说明未承诺反查最后一张采购单，因此没有把三个快照字段误用为历史单据身份。 | [OITM 的 LastPurPrc / LastPurCur / LastPurDat](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITM.html) |
| `models/oitm.json:456`、`:527`；`models/ocrd.json:384`、`:420` 及各后续期间列 | 查询启用、停用设置及设置期间时，两组各三列均可读取。数据库 Y/N 与 DI API 枚举分开解释；没有添加“仅凭 validFor 判断今天可用”的公式、期间优先级或历史事实过滤。当前标题与说明表达的是设置，而非已计算的业务可用性。 | [OITM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITM.html)、[OCRD](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCRD.html)、[Items.Frozen](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Items~Frozen.html)、[BusinessPartners.Valid](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~BusinessPartners~Valid.html) |
| `relationships/ocr1_oprc.json:2`；`models/ocr1.json:106` | 同一分配规则包含两个成本中心，并在下一期间调整分配值。`ocr1 → oprc` 多对一条件使用 `PrcCode`，覆盖 OPRC 完整主键；OCR1 的 `(OcrCode, PrcCode, ValidFrom)` 仍保留。目标键不含 `DimCode` 或期间，不应为了“完整”而追加这些条件。关系没有筛选当前停用成本中心，也没有复制分录金额进行分摊。 | [OCR1 字段与复合键](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OCR1.html)、[OPRC 主键](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OPRC.html)、[DistributionRuleLine](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DistributionRuleLine_members.html) |

两条关系的 `MANY_TO_ONE` 是基数声明，不独立证明所有消费查询都使用保留左侧记录的连接。当前联查测试显式使用 LEFT JOIN，编译证据覆盖了两条关系；不能由此断言所有任意生成 SQL 都已验收。反过来，也没有用“源字段可空”或人为孤立记录推导正常业务必定丢行。

## 语言包、来源及兼容性

逐项读过 `locales/en.json:1481` 的 ITM1、`:2847` 的 OCRD 状态、`:4628` 的 OITM 状态及最近采购币种，以及 `:13711`、`:13715` 两条关系。新增与修改文字在两个语言中保留相同字段角色、枚举和限制；未发现反向翻译或仍默认价目表 1 的说明。技术标识覆盖测试和 `validation/en-source-text.json:2` 的源文本指纹均通过。

`validation/reference-contract.json` 是允许字段清单与主键契约，不是独立的官方类型/枚举判定器。构建通过只能证明模型符合该契约；本轮字段语义另外对照官方来源，源类型另外依据元数据证据。官方表参考的单字符文本与目标 SQL Server 的 `char(1)` 在这里并不构成语义冲突；模板使用 `CHAR(1)` 有现场元数据支持。

与修补前 `source-before/models/` 的三个模型逐字段比较：只追加 13 列，没有删除旧列，已有列类型、主键和旧列相对顺序不变；旧列仅调整已列明的显示标题或说明。两条新增关系不更改原关系条件。结构消费者仍可按原技术名取值；启停用显示标题改变可能影响依赖中文标题的外部脚本。新增列会扩大 `SELECT *` 或按全部发现字段生成结果的字段集合，这是增量接口的兼容影响，不能表述为输出形状完全不变。没有发现本轮直接破坏原技术字段或键的变更。

## 验证有效性与边界

本代理实际重跑以下只读本地检查，未执行 Bench 测试或访问开发站点：

| 检查 | 本次结果 | 能证明什么 |
| --- | --- | --- |
| `python3 build.py --check` | 通过；101 模型、372 关系；无产物写入 | 模板组装、字段契约、声明主键、关系端点及列引用符合构建规则；不证明业务金额正确 |
| `test_locales.py` | 4/4 通过 | 英文覆盖、原技术标识保留、源文本指纹一致；本次另人工阅读修补文字核对含义 |
| `test_master_data_review.py` | 2/2 通过 | 指定价目表 2 的两种币种/单位原值得以保留；两成本中心、两期间四条明细解析名称后不放大行数且保留分配值 |

上述价格场景的业务前提成立：SAP 允许物料在价目表中维护不同币种及不同单位价格，见 [Price Lists](https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/452365399e152b31e10000000a1553f7.html?q=lead+time)。分配规则多成本中心、按生效日期修改配比的场景亦有官方业务说明，见 [SAP Business One… To Go 9.3，第 75 页](https://help.sap.com/doc/45e5277ba6584a59aa2f2b86969b5535/9.3/en-US/SAP_Business_One_To_Go_Release_9.3.pdf)，其字段和键另经当前 10.0 SDK 核对。SQLite 夹具是这些场景的最小查询投影，没有经过 SAP 创建流程；本次仅用来验证连接与原值保留，不用来证明所有主数据约束、价格选择算法或真实分摊结果。

既有 `tests.log` 记录全套 88 项通过，本代理没有重复跑全套。原 `plan.json` 明确为 `compile_only=true`，包含三个目标模型、两条关系及三个相关 View 的 8 条引擎计划；`isolated.json` 记录隔离保存和回滚；`result.json` 记录新事务重读与无关对象保护。它们有效支持保存、发现与编译层面的结论，不等于 SAP 报价、冻结期或成本会计对账通过。修补记录已披露该限制，没有夸大测试结果。

## 待证事项（非本轮确认缺陷）

1. **指定日期可用性。** 位置：OITM/OCRD 的 `valid* / frozen*` 六列及其说明。触发场景是未来需要直接回答“某日能否开单”，而非列出设置。还需依据目标版本业务规则核对期间端点、空日期和两组设置的组合，并与 SAP 行为验证。最小建议是继续保留现有原值，不在验证前新增 `is_active_on_date` 或默认过滤。官方 [Items.Frozen](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~Items~Frozen.html) 与 [BusinessPartners.Frozen](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~BusinessPartners~Frozen.html) 支持期间字段职责，但不能替代目标版本全部组合规则验收。
2. **特殊/手工单位值的实际显示。** 位置：`models/itm1.json:58`、`relationships/itm1_ouom.json:11`。现说明只称特殊值“可能”无单位匹配，没有承诺某一负值必定存在或规定它的文本。本次未读取目标价格记录，不认定存在实际缺单位数据，也不将其列为缺陷。若后续要自动补单位名称，先验证目标版本的手工单位配置和保存值；不能仅根据可空元数据推导回填规则。

## 可选整理与扩展（不阻断本轮）

- **报价范围说明。** 位置：`models/itm1.json:84` 及英文对应项。正常场景是同一物料还维护附加币种价格或其他单位价格。官方 [ITM1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITM1.html) 另有 `AddPrice1/2`、`Currency1/2`；[ITM9](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/ITM9.html) 以物料、价目表、单位三者为键。现模型正确解释已选择的 `Price/Currency`，且明确不提供完整定价规则，故不是本轮漏修。最小建议是有实际报价需求时再决定是否补充这些能力；可先在模型总说明中明确“当前精选主价格，不列举全部附加币种及单位报价”，不因补了 UomEntry 就声称完整多单位报价已支持。
- **旧成本术语整理。** 位置：`models/ocr1.json:26` 的“维度代码”、`:37` 的“维度总额”，及 `relationships/ocr1_oocr.json:3` 的“维度值 → 维度”。正常场景是用户区分分配规则、所属成本维度和成本中心。官方 [DistributionRule](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~DistributionRule_members.html) 分别定义规则键 `OcrCode`、维度键 `DimCode` 和分配总基数 `OcrTotal`。可把旧显示名整理为“分配规则代码”“分配总基数”“分配规则明细 → 分配规则”，并同步英文；这是原审查已提及的可选术语项，不是本轮新增关系方向、完整键或基数错误，不增加新的确认修复项。

本次没有基于人为删除工单、缺主数据、字段可空或 LEFT JOIN 形式提出业务缺陷，也没有要求覆盖 SAP 全字段。未来如扩展定价、期间可用性或实际成本分摊，应按具体业务问题另明确规格和验收，再增加计算或字段。
