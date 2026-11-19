# SAP Business One 销售工作区模板包

`sales/` 是独立发布的工作区 ZIP 源。它需要 SQL Server 版 SAP Business One 公司库，连接账号应通过 tBI 的只读检查。模板包含三个物理来源模型、一个语义视图、一个分析模型、六张图表、一张仪表板和三条 Knowledge。它使用 `OINV`、`ORIN` 和 `OADM`，并通过现有语义模板格式维护英文原文及中文语言包。

从此目录运行以下命令生成 ZIP。发布新内容时先更新 `sales/workspace-template.json` 中的版本。

```sh
cd sales
python3 -m zipfile -c ../sap-b1-sales-1.0.0.zip workspace-template.json semantic charts dashboards knowledge questions.json verification.json
```

在 tBI 的工作区列表点「新增工作区」，上传 ZIP，填写公司库和 schema，依次检查来源和包内容，最后点「创建并初始化」。安装了 tAI 的站点在确认页选择要发布的 Knowledge。初始化成功后打开销售概览，或从结果页发起 AI 验证。应收单据净额按公司本币汇总有效发票和有效贷项，确认上线口径前请与目标公司库的相应报表核对。
