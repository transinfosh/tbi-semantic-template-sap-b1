# 库存语义模型复核与优化建议

审查日期：2026-10-22。范围：本地模板当前库存组15个模型，以及物料、仓库、批次、序列号、库位、单位等既有共享主数据。本文件是研究与修改建议，不代表已写入模型、已部署或已完成业务对账。未读取业务记录；不能据此判断任何企业是否使用某功能。

## 结论与职责

常用收货、发货、调拨及调拨申请已覆盖。主要缺口是**序列号仓库当前数量OSRQ**、现有批次数量到批次主记录/仓库的连接、日志判别字段，以及库存单据默认字段中混入的销售结算语义。OITW已经在库存组，OWTQ/WTQ1及WTR1来源关系也已存在，不应重复新增。物料、仓库、单位、批次/序列号主记录、库位定义仍属于共享主数据；数量余额与交易记录属于库存。

必须分开以下三类事实：

| 事实 | 已有或建议模型 | 边界 |
|---|---|---|
| 当前数量/价值余额 | OITW，OBTQ，新增OSRQ | 当前快照，不能直接回答历史某日余额 |
| 单据和库存影响日志 | OIGN/IGN1、OIGE/IGE1、OWTR/WTR1、OWTQ/WTQ1，OITL/ITL1、OILM | 申请、承诺、订购、实物变动并非同一事实 |
| 库存估价与成本层 | OIVL/IVL1 | 带符号库存金额、估价方法和层粒度；不是销售金额或当前平均价 |

OITW的物料+仓库复合主键及当前数量/价值来源见[SAP OITW](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITW.html)。日志分类见[SAP OITL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITL.html)、[SAP OILM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OILM.html)；估价交易与层见[SAP OIVL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIVL.html)、[SAP IVL1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/IVL1.html)。

## 15个现有模型逐项取舍

以下采用“列出变更，未列出的现有列保留”的完整选择规则，不以物理字段很多为理由全量导入，也不因为样本零值而删除。

| 模型 | 现状与保留 | 本轮建议 |
|---|---|---|
| OIGE | 主键、编号/系列、状态、过账/凭证/创建/更新日期、单据金额三币、会计TransId和必要业务上下文保留 | 删除累计Paid三字段、毛利、CancelDate、JrnlMemo、GroupNum |
| OIGN | 同上；普通收货与生产收货/退料共用单据 | 同OIGE；不能把所有生产来源收货都当产品完工 |
| OWTR | 实际调拨；头行、会计、编号关系保留 | 同OIGE；保留不同仓库方向，单据头金额不当全公司收发净额 |
| OWTQ | 申请头，已有模型与编号/业务伙伴关系 | 同上并删TransId；申请不承担实际库存估价和会计过账事实 |
| IGE1 | 行主键、typed来源三键、数量/库存数量/历史单位、单据价格/金额、StockPrice/StockSum/StockValue对照、账户及其他现有上下文保留 | 去GrossBuyPr，补Project；保持已有工单与组件来源关系 |
| IGN1 | 同IGE1并保留TranType | 去GrossBuyPr，补Project，修TranType数据库C/R语义 |
| WTR1 | 现有来源申请三键、调出/调入仓、数量和单位保留 | 去GrossBuyPr、StockValue，补StockSum和Project |
| WTQ1 | 申请行数量、OpenQty/OpenInvQty、日期及方向、价格上下文保留 | 去GrossBuyPr、StockPrice、StockValue，补ShipDate和Project |
| OITW | 已有当前库存模型，主键ItemCode+WhsCode正确 | 保留全部当前11列与既有物料/仓库关系；Counted是数量，不是是否已盘点标志 |
| OBTQ | 已有批次仓库数量，AbsEntry主键正确 | 保留全部11列及已有系统唯一键元数据；补到OBTN与OWHS关系 |
| OITL | 已有Doc/Base/Apply三组不同来源及ManagedBy、StockEff | 补LocType/CreateDate，ItemCode改50字符；不把所有日志当实物收发 |
| ITL1 | 主键LogEntry+ItemCode+SysNumber、数量分配字段正确 | ItemCode改50字符；关联批/序列主记录必须保留父日志ManagedBy判别 |
| OILM | MessageID主键；既有DocAction不能代替ActionType | 补AccumType/ActionType/LocType，ItemCode改50字符 |
| OIVL | TransSeq主键、原始价格/估价方法、数量、SumStock及会计上下文保留 | 补PostStatus；不能拿状态字段擅自默认过滤已完成 |
| IVL1 | TransSeq+LayerID主键与8个现有字段一致 | 全部保留；汇总层金额后再连接交易数量 |

四个头表的Paid、毛利等字段确实存在于SAP数据库，但存在不等于适合作为当前库存模块默认分析字段。移除理由是业务范围和误用风险，不是宣称这些字段永远为零；兼容检查必须覆盖既有视图、立方体、指标和实例扩展。[OIGE](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIGE.html)、[OIGN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIGN.html)、[OWTR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWTR.html)、[OWTQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWTQ.html)

GroupNum不能按字段同名统一解释：OWTR官方为价目表，OWTQ为付款条件；OIGE/OIGN官方说明的Price List与Related OCTG存在冲突。当前无需用它新增共享主数据关系。CancelDate也不能代替真实冲销/取消过账事件。

行字段来源见[IGE1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IGE1.html)、[IGN1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IGN1.html)、[WTR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WTR1.html)、[WTQ1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WTQ1.html)。IGN1页通过直接HTTP读取，TranType物理类型为VarChar1、值C完成/R拒收；旧描述混入DI API枚举0/1，属于明确错误。SQL过滤应使用字符，且完成/拒收并不自动解决退料或拆卸分类。

## 当前数量及追溯关系

[SAP OSRQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRQ.html)是序列号仓库数量，主键AbsEntry，系统唯一键ItemCode+SysNumber+WhsCode。建议新增8个核心字段，CCD等地域专项字段不默认导入。现有OSRN无仓库粒度，Status也不表示序列当前位于某仓库。[OSRN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRN.html)

现有[OBTQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTQ.html)缺到批次号名称和仓库名称的模型关系。优先使用MdAbsEntry→OBTN.AbsEntry；不能以SysNumber单字段跨物料连接。OSRQ对OSRN同理。OBTN和OSRN的AbsEntry是各自表内键，数值可以重合；ITL1连接它们必须限定OITL.ManagedBy，不能无条件双连。

批次状态0已释放/1不可访问/2锁定，序列状态0可用/1不可用/2已分配；名称相同Status却不是同一枚举。[OBTN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTN.html)、[OSRN](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRN.html)

OITL/ITL1/OILM/OSRN的ItemCode当前模型为VARCHAR20，但SAP 10.0数据库表参考为nvarchar50，建议与OITM统一为VARCHAR50。旧DI属性页部分长度仍写20，物理数据库模型优先使用目标库元数据和当前数据库表参考；不能让旧API说明覆盖物理长度。[OITL](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITL.html)、[ITL1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITL1.html)、[OILM](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OILM.html)

## 按场景扩展，当前不整族新增

| 场景 | 候选与准确粒度 | 取舍 |
|---|---|---|
| 普通物料当前库位余额 | OIBQ，AbsEntry主键；ItemCode+BinAbs唯一 | OBIN只有位置定义，无数量；明确需要“某库位剩多少”时优先补OIBQ |
| 批次当前库位余额 | OBBQ，AbsEntry主键；SnBMDAbs+BinAbs唯一，SnBMDAbs→OBTN.AbsEntry | 有库位批次余额需求才补；不得将仓库OBTQ复制到每个库位 |
| 序列当前库位余额 | OSBQ，同上，SnBMDAbs→OSRN.AbsEntry | 不与OBBQ混用类型 |
| 盘点过程与盘盈盘亏 | OINC/INC1盘点；OIQR/IQR1库存过账 | CountDate与实际DocDate分开；盘点不是已过账调整；不因OITW有Counted就宣称盘点全流程已覆盖 |
| 期初录入追溯 | OIQI/IQI1 | 对初始化追溯有要求再补；与盘点表不同，不从OITW当前量推期初 |
| 库位交易历史/批序列明细 | OBTL及各单据分配子表 | 与当前库位数量是不同问题；需有消息键、批/序列类型与单据行映射再扩展 |

候选来源：[OIBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIBQ.html)、[OBBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OBBQ.html)、[OSBQ](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OSBQ.html)、[OINC](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OINC.html)、[INC1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/INC1.html)、[OIQR](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OIQR.html)、[IQR1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/IQR1.html)、[OIQI](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/OIQI.html)、[IQI1](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKhelp/IQI1.html)。

盘点的INC1主键DocEntry+LineNum；IQR1、IQI1主键实际叫DocEntry+DocLineNum，不能套用所有子表LineNum。IQR1→INC1若将来启用，需BaseType=1470000065，BaseEntry=DocEntry及BaseLine=LineNum。OIQR对象类型10000071，OIQI对象类型310000001；同样不能用显示编号代替内部键。

共享OBIN现有库位定义和OWHS关系保留，不把54个配置字段当库存事实；可在后续共享主数据整理时按业务配置需求裁剪，不借本轮变更库存模块修改整套主数据。

## 已有边界与禁止误放行

1. 既有`ige1→wor1`保留BaseType=202、BaseEntry=DocEntry、BaseLine=LineNum；同物料在同一工单重复出现时仍须分组件行。
2. `oivl→ige1`已经获准：TransType=60、CreatedBy=DocEntry、DocLineNum=LineNum。一个发料行可有多条估价交易，每条交易可有多个IVL1层。层金额先按TransSeq汇总，再汇总到来源行；不能把交易InQty/OutQty乘层行数。
3. `OIVL→IGN1`与`OIVL→WTR1`仍在`deferred.json`。本报告确认表字段、增加StockSum或补齐日志判别，不解除待审状态。调拨单一行对应不同仓库方向的估价交易，不能将两边全加为一笔库存变化。
4. `OIVL.MessageID→OILM.MessageID`已有，不等于`OITL.LogEntry`；两个日志系统不能用数字相等猜连接。
5. ITL1批序列分配、IVL1估价层是不同的一对多。一起展开会造成乘法重复，按各自业务粒度聚合后再连接。分配/预留可能不代表已实际收发，StockEff/AccumType不可省略。
6. 当前模型只有一个OWHS角色，WTR1/WTQ1的WhsCode对应目的仓库，FromWhsCod为调出仓库。官方DI说明明确FromWarehouseCode为取出仓库；第二个仓库维度要通过角色别名或查询视图实现，不能让名称相同的Warehouse混用。[StockTransfer Lines](https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/SAPbobsCOM~StockTransfer_Lines_members.html)
7. OIGE/OIGN.CardCode的官方名称是费用/收入科目，但Related列又指OCRD。现有两条OCRD关系不是本轮新建；不要因此推导客户销售归属，也不要直接改连OACT。保持原关系兼容并标明待核，新增分析优先用行AcctCode及已确认会计路径。
8. 现有`production-issue-query.sql`和`test_production_issue.py`正确保留原始发料行、NULL/缺估价、带符号冲销及过账/创建日期。库存优化不得覆写这些行为；`StockValue=0`不等于发料成本为零。

## 可执行修改清单

下面是提案数据，不是模板文件本身。每表`source`适用于所属字段；英文label供语言包同步使用，description为中文语义源。所有未列出现有字段保留；字段删除须先查下游依赖，不删除SAP物理列。新增字段应由目标库元数据验证可用性与类型，模板DATE继续按现有约定使用TIMESTAMP。下列关系仅默认加入明确的单向主数据引用，不跨越上述待审边。

```json
{
  "status": "proposal_not_applied",
  "keep_unlisted_columns": true,
  "remove": {
    "oige": {
      "columns": [
        "PaidToDate",
        "PaidFC",
        "PaidSys",
        "GrosProfit",
        "CancelDate",
        "JrnlMemo",
        "GroupNum"
      ],
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIGE.html",
      "reason": "当前范围为库存收发或调拨；累计收付、销售毛利、通用取消日期、定价条件及低优先级记账备注不作为默认分析字段；不推断底层值为零。"
    },
    "oign": {
      "columns": [
        "PaidToDate",
        "PaidFC",
        "PaidSys",
        "GrosProfit",
        "CancelDate",
        "JrnlMemo",
        "GroupNum"
      ],
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIGN.html",
      "reason": "当前范围为库存收发或调拨；累计收付、销售毛利、通用取消日期、定价条件及低优先级记账备注不作为默认分析字段；不推断底层值为零。"
    },
    "owtr": {
      "columns": [
        "PaidToDate",
        "PaidFC",
        "PaidSys",
        "GrosProfit",
        "CancelDate",
        "JrnlMemo",
        "GroupNum"
      ],
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWTR.html",
      "reason": "当前范围为库存收发或调拨；累计收付、销售毛利、通用取消日期、定价条件及低优先级记账备注不作为默认分析字段；不推断底层值为零。"
    },
    "owtq": {
      "columns": [
        "PaidToDate",
        "PaidFC",
        "PaidSys",
        "GrosProfit",
        "CancelDate",
        "JrnlMemo",
        "GroupNum",
        "TransId"
      ],
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OWTQ.html",
      "reason": "当前范围为库存收发或调拨；累计收付、销售毛利、通用取消日期、定价条件及低优先级记账备注不作为默认分析字段；不推断底层值为零。"
    },
    "ige1": {
      "columns": [
        "GrossBuyPr"
      ],
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IGE1.html",
      "reason": "毛利基础价不是历史库存估价单价，当前库存分析不需要该默认字段。"
    },
    "ign1": {
      "columns": [
        "GrossBuyPr"
      ],
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IGN1.html",
      "reason": "毛利基础价不是历史库存估价单价，当前库存分析不需要该默认字段。"
    },
    "wtr1": {
      "columns": [
        "GrossBuyPr",
        "StockValue"
      ],
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WTR1.html",
      "reason": "毛利基础价不是历史库存估价单价，当前库存分析不需要该默认字段。 以新增StockSum解释单据行库存金额；保留IGE1/IGN1已建立的StockValue对照契约。"
    },
    "wtq1": {
      "columns": [
        "GrossBuyPr",
        "StockPrice",
        "StockValue"
      ],
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WTQ1.html",
      "reason": "毛利基础价不是历史库存估价单价，当前库存分析不需要该默认字段。 申请价格上下文已有Price/Currency；申请不产生实际库存估价。"
    }
  },
  "change": {
    "osrn": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRN.html",
      "columns": [
        {
          "name": "ItemCode",
          "type": "VARCHAR(50)",
          "description": "按SAP 10.0数据库表参考的nvarchar(50)统一，避免以旧DI属性页20字符限制物料编码。",
          "description_en": "Use nvarchar(50) from the SAP 10.0 database table reference; the older DI property page length of 20 characters must not restrict item codes in the database model."
        },
        {
          "name": "Status",
          "description": "序列号状态：0=可用，1=不可用，2=已分配；不能仅凭该状态判断当前在哪个仓库。",
          "description_en": "Serial number status: 0=Available, 1=Unavailable, 2=Allocated. This status alone does not identify the warehouse that currently holds the serial number."
        }
      ]
    },
    "oitl": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITL.html",
      "columns": [
        {
          "name": "ItemCode",
          "type": "VARCHAR(50)",
          "description": "按SAP 10.0数据库表参考的nvarchar(50)统一，避免以旧DI属性页20字符限制物料编码。",
          "description_en": "Use nvarchar(50) from the SAP 10.0 database table reference; the older DI property page length of 20 characters must not restrict item codes in the database model."
        }
      ]
    },
    "itl1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/ITL1.html",
      "columns": [
        {
          "name": "ItemCode",
          "type": "VARCHAR(50)",
          "description": "按SAP 10.0数据库表参考的nvarchar(50)统一，避免以旧DI属性页20字符限制物料编码。",
          "description_en": "Use nvarchar(50) from the SAP 10.0 database table reference; the older DI property page length of 20 characters must not restrict item codes in the database model."
        }
      ]
    },
    "oilm": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OILM.html",
      "columns": [
        {
          "name": "ItemCode",
          "type": "VARCHAR(50)",
          "description": "按SAP 10.0数据库表参考的nvarchar(50)统一，避免以旧DI属性页20字符限制物料编码。",
          "description_en": "Use nvarchar(50) from the SAP 10.0 database table reference; the older DI property page length of 20 characters must not restrict item codes in the database model."
        }
      ]
    },
    "ign1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IGN1.html",
      "columns": [
        {
          "name": "TranType",
          "type": "VARCHAR(1)",
          "displayName": "生产收货完成或拒收类型",
          "displayName_en": "Production Receipt Completion or Rejection Type",
          "description": "数据库C=完成、R=拒收；DI API枚举0/1不可直接作为TranType过滤值。仍需区分产品收货、组件退回及拆卸业务角色。",
          "description_en": "Database values are C=Complete and R=Reject. DI API enumeration values 0/1 must not be used directly as TranType filters. Product receipts, component returns, and disassembly roles still require separate classification."
        }
      ]
    },
    "obtn": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OBTN.html",
      "columns": [
        {
          "name": "Status",
          "description": "批次状态：0=已释放，1=不可访问，2=锁定；与序列号状态枚举不同，不代替仓库在手数量。",
          "description_en": "Batch status: 0=Released, 1=Not Accessible, 2=Locked. These values differ from serial number statuses and do not replace warehouse on-hand quantities."
        }
      ]
    }
  },
  "add": {
    "ige1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IGE1.html",
      "columns": [
        {
          "name": "Project",
          "type": "VARCHAR(20)",
          "displayName": "行项目编码",
          "displayName_en": "Line Project Code",
          "description": "本单据行保存的项目编码；与头项目或当前物料信息分别解释。",
          "description_en": "Project code stored on this document line; interpret it separately from the header project and current item master data."
        }
      ]
    },
    "ign1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/IGN1.html",
      "columns": [
        {
          "name": "Project",
          "type": "VARCHAR(20)",
          "displayName": "行项目编码",
          "displayName_en": "Line Project Code",
          "description": "本单据行保存的项目编码；与头项目或当前物料信息分别解释。",
          "description_en": "Project code stored on this document line; interpret it separately from the header project and current item master data."
        }
      ]
    },
    "wtr1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WTR1.html",
      "columns": [
        {
          "name": "Project",
          "type": "VARCHAR(20)",
          "displayName": "行项目编码",
          "displayName_en": "Line Project Code",
          "description": "本单据行保存的项目编码；与头项目或当前物料信息分别解释。",
          "description_en": "Project code stored on this document line; interpret it separately from the header project and current item master data."
        },
        {
          "name": "StockSum",
          "type": "DECIMAL(19,6)",
          "displayName": "调拨行库存合计",
          "displayName_en": "Transfer Line Stock Sum",
          "description": "单据行已存库存金额；与LineTotal及估价交易SumStock分别解释，不由它自动重建调出调入两方过账。",
          "description_en": "Stored stock amount on the document line. Interpret it separately from LineTotal and valuation transaction SumStock; it does not by itself reconstruct the postings for both the source and destination warehouses."
        }
      ]
    },
    "wtq1": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/WTQ1.html",
      "columns": [
        {
          "name": "Project",
          "type": "VARCHAR(20)",
          "displayName": "行项目编码",
          "displayName_en": "Line Project Code",
          "description": "本单据行保存的项目编码；与头项目或当前物料信息分别解释。",
          "description_en": "Project code stored on this document line; interpret it separately from the header project and current item master data."
        },
        {
          "name": "ShipDate",
          "type": "TIMESTAMP",
          "displayName": "行需求交付日期",
          "displayName_en": "Line Required Delivery Date",
          "description": "申请行的需求日期；不是实际调拨过账日期。",
          "description_en": "Required delivery date on the transfer request line; this is not the posting date of an executed transfer."
        }
      ]
    },
    "oitl": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OITL.html",
      "columns": [
        {
          "name": "LocType",
          "type": "INTEGER",
          "displayName": "位置类型",
          "displayName_en": "Location Type",
          "description": "与LocCode共同解释位置；未核实枚举时不自动将位置全部连接仓库。",
          "description_en": "Interpret the location together with LocCode. Do not treat every location as a warehouse before verifying the location type values."
        },
        {
          "name": "CreateDate",
          "type": "TIMESTAMP",
          "displayName": "日志创建日期",
          "displayName_en": "Log Creation Date",
          "description": "系统创建日期，与DocDate交易过账日期分别使用。",
          "description_en": "System creation date; use it separately from the transaction posting date DocDate."
        }
      ]
    },
    "oilm": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OILM.html",
      "columns": [
        {
          "name": "AccumType",
          "type": "INTEGER",
          "displayName": "库存累计类别",
          "displayName_en": "Inventory Accumulator Type",
          "description": "0空、1在手、2承诺、3订购、4寄售、5盘点；各类别不能混合求和。",
          "description_en": "0=Empty, 1=On Hand, 2=Committed, 3=On Order, 4=Consignment, 5=Counted. Quantities from different accumulator types must not be summed together."
        },
        {
          "name": "ActionType",
          "type": "INTEGER",
          "displayName": "库存交易动作",
          "displayName_en": "Inventory Transaction Action",
          "description": "按官方枚举区分入、出、设置、重估、负库存调整和库位转移；与DocAction为不同字段。",
          "description_en": "Use the official enumeration to distinguish receipts, issues, quantity setting, revaluation, negative inventory adjustments, and bin transfers. ActionType and DocAction are different fields."
        },
        {
          "name": "LocType",
          "type": "INTEGER",
          "displayName": "位置类型",
          "displayName_en": "Location Type",
          "description": "与LocCode共同解释位置范围。",
          "description_en": "Interpret the location scope together with LocCode."
        }
      ]
    },
    "oivl": {
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OIVL.html",
      "columns": [
        {
          "name": "PostStatus",
          "type": "CHAR(1)",
          "displayName": "估价过账状态",
          "displayName_en": "Valuation Posting Status",
          "description": "N无、P部分、C完成；保留状态，不能未经报表口径确认就默认只取C。",
          "description_en": "N=None, P=Partial, C=Complete. Preserve the status; do not default to C without confirming the applicable reporting rules."
        }
      ]
    }
  },
  "new_models": [
    {
      "name": "osrq",
      "displayName": "序列号仓库当前数量",
      "displayName_en": "Current Serial Number Quantities by Warehouse",
      "group": "inventory",
      "primaryKey": "AbsEntry",
      "uniqueKeys": [
        [
          "ItemCode",
          "SysNumber",
          "WhsCode"
        ]
      ],
      "source": "https://help.sap.com/doc/089315d8d0f8475a9fc84fb919b501a3/10.0/en-US/SDKHelp/OSRQ.html",
      "description": "每个物料、系统序列号和仓库组合的当前数量记录；不是历史时点库存，也不是收发流水。",
      "columns": [
        {
          "name": "AbsEntry",
          "type": "INTEGER",
          "displayName": "内部标识",
          "displayName_en": "Internal ID",
          "description": "记录主键。",
          "description_en": "Primary key of the quantity record."
        },
        {
          "name": "ItemCode",
          "type": "VARCHAR(50)",
          "displayName": "物料编码",
          "displayName_en": "Item Code",
          "description": "与SysNumber及WhsCode组成系统唯一键。",
          "description_en": "Together with SysNumber and WhsCode, forms the system unique key."
        },
        {
          "name": "SysNumber",
          "type": "INTEGER",
          "displayName": "系统序列编号",
          "displayName_en": "Serial System Number",
          "description": "须在物料上下文使用。",
          "description_en": "Use this number within its item context."
        },
        {
          "name": "WhsCode",
          "type": "VARCHAR(8)",
          "displayName": "仓库编码",
          "displayName_en": "Warehouse Code",
          "description": "当前数量所属仓库。",
          "description_en": "Warehouse to which the current quantity belongs."
        },
        {
          "name": "Quantity",
          "type": "DECIMAL(19,6)",
          "displayName": "当前序列号在手数量",
          "displayName_en": "Current Serial Quantity",
          "description": "当前仓库数量，不按日期直接累加为期间收发。",
          "description_en": "Current quantity in the warehouse. Summing dated snapshots does not produce receipts or issues for a period."
        },
        {
          "name": "CommitQty",
          "type": "DECIMAL(19,6)",
          "displayName": "当前承诺数量",
          "displayName_en": "Current Committed Quantity",
          "description": "与实际在手数量分开。",
          "description_en": "Committed quantity; keep it separate from actual on-hand quantity."
        },
        {
          "name": "CountQty",
          "type": "DECIMAL(19,6)",
          "displayName": "盘点数量",
          "displayName_en": "Counted Quantity",
          "description": "数量字段不等于完整盘点单据历史。",
          "description_en": "This quantity field does not provide the complete history of inventory counting documents."
        },
        {
          "name": "MdAbsEntry",
          "type": "INTEGER",
          "displayName": "序列号主记录标识",
          "displayName_en": "Serial Master Record ID",
          "description": "关联OSRN.AbsEntry。",
          "description_en": "References OSRN.AbsEntry."
        }
      ],
      "description_en": "Current quantity record for each item, system serial number, and warehouse combination. This is neither inventory at a historical date nor a receipt or issue transaction log."
    }
  ],
  "relationships_add": [
    {
      "name": "sap_osrq_osrn",
      "models": [
        "osrq",
        "osrn"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "osrq.MdAbsEntry = osrn.AbsEntry",
      "description": "序列当前数量指向序列主记录；MdAbsEntry不是SysNumber。",
      "description_en": "Links the current serial quantity to its serial master record. MdAbsEntry is not SysNumber."
    },
    {
      "name": "sap_osrq_oitm",
      "models": [
        "osrq",
        "oitm"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "osrq.ItemCode = oitm.ItemCode",
      "description": "当前数量的物料。",
      "description_en": "Item associated with the current quantity."
    },
    {
      "name": "sap_osrq_owhs",
      "models": [
        "osrq",
        "owhs"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "osrq.WhsCode = owhs.WhsCode",
      "description": "当前数量的仓库。",
      "description_en": "Warehouse associated with the current quantity."
    },
    {
      "name": "sap_obtq_obtn",
      "models": [
        "obtq",
        "obtn"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "obtq.MdAbsEntry = obtn.AbsEntry",
      "description": "批次仓库数量关联批次主记录，避免单独SysNumber碰撞。",
      "description_en": "Links the batch warehouse quantity to its batch master record, avoiding collisions from joining on SysNumber alone."
    },
    {
      "name": "sap_obtq_owhs",
      "models": [
        "obtq",
        "owhs"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "obtq.WhsCode = owhs.WhsCode",
      "description": "批次当前数量的仓库。",
      "description_en": "Warehouse associated with the current batch quantity."
    },
    {
      "name": "sap_ige1_oprj",
      "models": [
        "ige1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "ige1.Project = oprj.PrjCode",
      "description": "单据行项目；不把当前主数据反推为历史项目。",
      "description_en": "Project stored on the document line; do not infer a historical project from current master data."
    },
    {
      "name": "sap_ign1_oprj",
      "models": [
        "ign1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "ign1.Project = oprj.PrjCode",
      "description": "单据行项目；不把当前主数据反推为历史项目。",
      "description_en": "Project stored on the document line; do not infer a historical project from current master data."
    },
    {
      "name": "sap_wtr1_oprj",
      "models": [
        "wtr1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "wtr1.Project = oprj.PrjCode",
      "description": "单据行项目；不把当前主数据反推为历史项目。",
      "description_en": "Project stored on the document line; do not infer a historical project from current master data."
    },
    {
      "name": "sap_wtq1_oprj",
      "models": [
        "wtq1",
        "oprj"
      ],
      "joinType": "MANY_TO_ONE",
      "condition": "wtq1.Project = oprj.PrjCode",
      "description": "单据行项目；不把当前主数据反推为历史项目。",
      "description_en": "Project stored on the document line; do not infer a historical project from current master data."
    }
  ],
  "relationships_defer": [
    {
      "models": [
        "wtr1",
        "owhs"
      ],
      "role": "from_warehouse",
      "condition": "wtr1.FromWhsCod = owhs.WhsCode",
      "reason": "字段和官方角色已确认；与已有WhsCode到同一表的关系需要角色别名支持，不能混为同一Warehouse。",
      "description_en": "The field and its official warehouse role are confirmed. A separate role alias is required alongside the existing WhsCode relationship to the same warehouse table; the two roles must not be conflated."
    },
    {
      "models": [
        "wtq1",
        "owhs"
      ],
      "role": "from_warehouse",
      "condition": "wtq1.FromWhsCod = owhs.WhsCode",
      "reason": "同上，源仓和目标仓角色必须可区分。",
      "description_en": "The source and destination warehouse roles must remain distinguishable through separate role aliases."
    },
    {
      "models": [
        "itl1",
        "obtn"
      ],
      "condition": "itl1.MdAbsEntry = obtn.AbsEntry AND oitl.ManagedBy = 10000044",
      "reason": "第三表判别不应直接塞入仅含两模型的关系；需要可表达父日志ManagedBy的过滤视图或角色模型。",
      "description_en": "A discriminator from a third table must not be placed directly in a relationship containing only two models. Use a filtered view or role model that can express ManagedBy from the parent log."
    },
    {
      "models": [
        "itl1",
        "osrn"
      ],
      "condition": "itl1.MdAbsEntry = osrn.AbsEntry AND oitl.ManagedBy = 10000045",
      "reason": "同上。不得同时启用两条无类型过滤的MdAbsEntry关系。",
      "description_en": "Use a filtered view or role model that expresses ManagedBy from the parent log. Do not enable both MdAbsEntry relationships without management type filters."
    }
  ]
}
```

OBTQ已有`uniqueKeys: [["ItemCode", "SysNumber", "WhsCode"]]`及AbsEntry主键，均保留。OSRN/OBTN已有系统唯一键语义也继续保留；本轮不把业务显示批号/序列号声明唯一。

## 验证与剩余风险

本研究未运行模板测试、未查真实库存、未编译目标SQL、未更新实例。实施者应至少验证：

- 模型字段与真实元数据一致；所有删列无视图/立方体/指标依赖；英文语言包完整。
- 人工构造跨物料相同SysNumber、批次/序列AbsEntry碰撞，验证typed或专用主数据关系不串行。
- 人工构造一个物料行跨两个批次、两个估价交易/三层，验证数量和金额不因连接翻倍。
- 调拨申请一行分两次执行，按BaseType+BaseEntry+BaseLine正确归属，申请未清与已执行分开；调出、调入方向明确。
- 一笔跨币种、多计量单位、创建晚于过账的收发，验证币种单位历史上下文和日期不被现行主数据覆盖。
- 取消/冲销、零数量重估、缺估价和部分NULL保留其业务区别；不得用ABS、COALESCE为0或当前平均价静默补成本。
- 目标业务报表对账完成前，历史余额、库存审计金额、生产退料/拆卸净额，以及deferred的两条估价来源边仍为待验收。
