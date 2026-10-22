# 常用查询视图工作区扩展

此扩展把常用多表关联保存为 tBI 查询视图。源定义为 [pack.json](pack.json) 与 `sql/` 中的 Semantic SQL；[load_pack.py](load_pack.py) 只读取文件，不连接、修改或发布任何工作区。四个新增表模型与十四条直接关系也保存在同一清单。

它是工作区的增量扩展，**不属于当前 template.json 的默认导入范围**，公共模板版本为 0.8.1。不得将这个不含基础模型的清单作为独立完整 MDL 导入；实施时保留目标原有模型、关系、资产和权限，经原生保存及依赖检查追加对象。当前实施和验证状态统一见 [SAP 测试映射](../../../../docs/应用/tbi/SAP业务语义/SAP业务语义-测试映射.md#常用查询视图2026-10-22)。

| 视图 | 每行含义及用途 |
| --- | --- |
| `sales_order_to_cash_trace` | 一个订单行的物流、发票及收款应用关联路径；销售订单到收款追溯 |
| `purchase_order_to_payment_trace` | 一个采购订单行的收货、发票及付款应用关联路径 |
| `sales_invoice_receipt_applications` | 一条应收发票收款应用，`DocNum+InvoiceId` |
| `purchase_invoice_payment_applications` | 一条应付发票付款应用，`DocNum+InvoiceId` |
| `sales_invoice_current_balance` | 一张应收发票的当前头记录总额、已付和差额 |
| `purchase_invoice_current_balance` | 一张应付发票的当前头记录总额、已付和差额 |
| `production_issue_detail` | 一条 `BaseType=202` 的共享库存发货行，含原始工单组件 |
| `production_receipt_detail` | 一条 `BaseType=202` 的共享库存收货行，保留收货类型 |
| `inventory_batch_serial_movements` | 一条批序列分配日志的现存量影响，`LogEntry+ItemCode+SysNumber` |
| `sales_delivery_batch_serial_detail` | 作为日志单据的交货行对应的现存量批序列明细 |
| `inventory_bin_movements` | 一条 `OBTL.AbsEntry` 的库位事务，批序列和库位来自同一事实 |
| `inventory_bin_current_balance` | 一个物料、库位的当前总量 |
| `inventory_batch_serial_bin_current_balance` | 一个管理类型、余额记录的当前批序列库位分量 |
| `inventory_batch_serial_warehouse_current_balance` | 一个管理类型、余额记录的当前批序列仓库分量 |
| `inventory_warehouse_current_balance` | 一个物料、仓库的当前总量和预计可用量 |
| `finance_journal_line_detail` | 一条 `TransId+Line_ID` 的凭证分录及科目名称 |

## 查询与汇总约定

追溯视图覆盖订单到物流再开票、订单直接开票、订单到预留发票再物流，并保留无后续单据的订单行。来源关系始终使用对象类型和完整原始行键；同物料多行不合并。它只输出身份、日期和状态，**不含金额或数量字段**。付款与发票商品行存在多对多展开，不能据路径行数计单据数，也不能把应用额归到每个订单后求和。没有订单来源的独立发票不在订单追溯中，仍可查询发票余额和应用视图。

收付款应用视图独立保持应用行粒度，仅包含目标应收或应付发票类型。付款父键采用官方对象与主键定义组合支持的内部键解释；异号真实样本仍需补验，依据见 [单据链研究](../document-chain-view-research.md)。FC 依目标发票币种，LC/SC 另读取同公司 OADM；付款头币种不能覆盖应用外币。折扣、预扣税、在账收付、预付抵扣和内部核销不是同一指标。头记录已付差额是当前状态，不代替历史账龄或纯现金回款。

批序列收发只取 `StockEff=1`，承诺/订购日志不当实际收发。原始带符号数量不强制 ABS。交货视图明确以 `Doc*` 日志单据角色定位，保留 Apply 角色，不能推定覆盖仅 Apply 匹配的特殊流程。库位事务直接使用 OBTL 的原分配行，动作方向不改写数量符号；未匹配主数据及普通物料记录保留。当前总量与批序列分量分开，二者不相加。依据和未决事项见 [批次库位研究](../batch-bin-view-research.md)。

生产使用共享库存单据和 `BaseType=202`；收货还可能是退回或拆卸组件，不能一律统计成品产量。金额、单位、取消及冲销沿原模型含义，不新建工单成本或历史库存算法。

SQL 不写死具体单号、客户、物料或日期。输出列由 tBI 原生保存推断类型，并保留清单中的业务标题；发布后 Agent 可直接发现字段并使用结构化查询。查看或保存草稿不改变发布版本。

0.8.3 起，四个配套模型的字段 `type` 使用不带长度/精度的大写基础类型，与公共模型及 tBI 编辑器一致。此前逐列标注保存在 [source-field-types.json](source-field-types.json)，已有未知参数不补猜；该文件不进入加载结果或 MDL。16 份 View SQL、CAST 和业务说明保持，未重新导入或发布已有工作区。范围与校验见[模板类型规格](../模板类型-规格契约.md)。

2026-10-22审查修补：两个批序列当前余额 View 在既有输出末尾增加 `current_inventory_unit`，按物料左连接当前 OITM.InvntryUom，保留原数量及复合身份；单位为当前配置，不代表历史交易单位。凭证分录的三个独立行日期保留，生产 View 的已撤回项不实施。公共模板0.8.1另补共享主数据字段与关系，仍不将本扩展变成默认导入内容。

财务凭证分录的 `posting_date/document_date/due_date` 为 OJDT 凭证头日期，`line_posting_date/line_document_date/line_due_date` 为 JDT1 分录行日期。头日期与行日期分别提供查询口径，不互相回填；三个行日期追加在原输出末尾，已有技术字段、顺序及金额含义保持兼容。适用场景与验证状态见 SAP41。

## 英文语言包

[locales/en.json](locales/en.json) 覆盖4个新增模型的名称、23个字段标题及已有字段说明、14条关系名称和说明，以及16个View名称、325个字段标题和全部View业务说明。沿用显示元数据覆盖格式：`displayName / description / columns`；加载器将View的显示名与列显示名映射到本扩展的 `title / columnTitles`。

`pack.json` 声明默认语言 `zh-CN` 和英文包路径。默认调用保持中文，英文及英文地区代码显式选择英文，未支持的语言回退到中文；各次调用独立读取，不修改源文件或前一次结果。

```python
pack = load_pack()          # Chinese source display text
english = load_pack("en")
english_us = load_pack("en-US")  # Falls back to the English pack
```

翻译只覆盖显示名和说明，不改变SQL、技术字段名、列顺序、类型、主键、关系条件、分组代码或业务存储值。保留日期角色、数量粒度、LC/FC/SC、当前/历史单位、取消/冲销及范围限制；不将“已付”“应用金额”“现金”混为同一指标。语言包不能注入SQL或类型，且资源路径限制在扩展目录内。

[源文字指纹](locales/source-text.json)与覆盖检查用于发现后续中文文字变更及漏译，变更说明时应同步审阅英文。此包仍是独立工作区扩展，不自动进入默认模板导入，也不依据Frappe界面语言实时改写已经保存的P1中文名称；后续导入/保存时选择相应语言，不自动发布。

## 验证

在仓库根运行：

```bash
python3 -m unittest discover -s tests -p test_workspace_views.py -v
```

测试执行实际 SQL，覆盖拆分链路、预留路径、对象/行号碰撞、异号付款父键、批序列主键碰撞、承诺日志排除、批次分库位、普通物料及缺失主数据保留、当前总分量隔离、共享生产单据和负向分录。SQLite 测试证明这些自造场景，不能代替 SQL Server 引擎编译、目标库对账或真实自然语言问答验收。

英文包验证：`python3 -m unittest discover -s tests -p test_workspace_view_locales.py -v`，覆盖完整翻译、地区回退、SQL与结构保持、技术标识保留及源说明指纹。本轮模板全套93项通过；另以英文包运行全部15项View SQL场景通过。加载器与新测试的Ruff检查通过，16份SQL文件摘要与实施前一致；没有修改P1或执行发布。
