# tools

## deposit_report.py

生成每日沉淀日报：今天改了哪些文件、git 状态、今日提交、需要确认的事项。

```bash
python3 tools/deposit_report.py            # 打印
python3 tools/deposit_report.py --write    # 写入 reports/YYYY-MM-DD.md
```

它只读文件名和 git 元数据，不读 `private/` 内容。

没有 Python 也能用：手动复制 `templates/日报模板.md`，每天写一份。
