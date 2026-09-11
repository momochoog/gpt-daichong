"""AIXiamo: offline interpretation of synthetic, manually recorded usage windows."""

import argparse
import json
import math
from datetime import datetime, timedelta, timezone

BEIJING = timezone(timedelta(hours=8))
DEFAULT_AS_OF = "2026-09-11T15:00:00+08:00"
MAX_UNIX_SECONDS = 9_999_999_999  # Example input bound; rejects current 13-digit ms.


def parse_as_of(value):
    """Require an explicit offset; never depend on the computer's local timezone."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("as-of 必须带时区，例如 2026-09-11T15:00:00+08:00")
    return parsed.astimezone(BEIJING)


def valid_used(value):
    return (type(value) in (int, float) and 0 <= value <= 100
            and math.isfinite(value))


def valid_reset(value):
    return type(value) is int and 1 <= value <= MAX_UNIX_SECONDS


def classify_window(record, as_of):
    """Classify one observation; no account access and no cross-window arithmetic."""
    if not isinstance(as_of, datetime) or as_of.utcoffset() is None:
        raise ValueError("as_of 必须是带时区的 datetime")
    result = dict(name="未命名窗口", usedPercent=None, remainingPercent=None,
                  resetsAtBeijing=None, status="数据异常", detail="记录必须是对象")
    if not isinstance(record, dict):
        return result
    name = record.get("name")
    if isinstance(name, str) and name.strip():
        result["name"] = name.strip()
    used, reset = record.get("usedPercent"), record.get("resetsAt")
    errors = []
    if used is not None and not valid_used(used):
        errors.append("usedPercent 必须是 0–100 的有限数字，不能是布尔或字符串")
    if reset is not None and not valid_reset(reset):
        errors.append("resetsAt 必须是 1–9999999999 的整数 Unix 秒，不能填毫秒")
    if valid_used(used):
        result["usedPercent"] = used
    if valid_reset(reset):
        result["resetsAtBeijing"] = datetime.fromtimestamp(reset, BEIJING).isoformat()
    if errors:
        result["detail"] = "；".join(errors)
    elif not isinstance(name, str) or not name.strip() or used is None or reset is None:
        result.update(status="信息缺失", detail="需补齐窗口名称、已用百分比和重置时间")
    elif as_of.timestamp() >= reset:
        result.update(status="到重置时间，需刷新", detail="旧窗口记录已到期，不能推断额度已恢复")
    else:
        result.update(status="已用完" if used == 100 else "当前未用完",
                      remainingPercent=100 - used,
                      detail="仅此窗口的人工记录；不能代表其他窗口或整体可用性")
    return result


def classify_many(records, as_of):
    if not isinstance(records, list) or not records:
        raise ValueError("records 必须是非空数组")
    return [classify_window(record, as_of) for record in records]


def synthetic_cases():
    """All values are invented for the fixed September 11, 2026 demonstration."""
    future = int(parse_as_of("2026-09-11T17:00:00+08:00").timestamp())
    weekly = int(parse_as_of("2026-09-14T10:00:00+08:00").timestamp())
    past = int(parse_as_of("2026-09-11T14:59:59+08:00").timestamp())
    return {
        "A：5 小时用完，周窗口未用完": [
            dict(name="5 小时", usedPercent=100, resetsAt=future),
            dict(name="周窗口", usedPercent=40, resetsAt=weekly)],
        "B：5 小时未用完，周窗口用完": [
            dict(name="5 小时", usedPercent=20, resetsAt=future),
            dict(name="周窗口", usedPercent=100, resetsAt=weekly)],
        "C：旧时间、缺失和非法数据": [
            dict(name="旧窗口", usedPercent=100, resetsAt=past),
            dict(name="缺失记录", usedPercent=None, resetsAt=future),
            dict(name="毫秒误填", usedPercent=40, resetsAt=future * 1000)],
    }


def cell(value):
    text = "—" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def render_table(results):
    lines = ["| 窗口 | 已用 % | 剩余 % | 重置时间（北京时间） | 记录判定 |",
             "| --- | ---: | ---: | --- | --- |"]
    for result in results:
        values = [result[key] for key in
                  ("name", "usedPercent", "remainingPercent", "resetsAtBeijing", "status")]
        lines.append("| " + " | ".join(map(cell, values)) + " |")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="逐窗口核验人工记录；不连接账号或网络")
    parser.add_argument("--as-of", default=DEFAULT_AS_OF, help="核验时间，必须带时区")
    parser.add_argument("--records", help="人工构造的 JSON 数组；省略时显示内置案例")
    args = parser.parse_args(argv)
    try:
        as_of = parse_as_of(args.as_of)
        cases = ({"人工记录": json.loads(args.records)} if args.records is not None
                 else synthetic_cases())
        tables = [(title, render_table(classify_many(records, as_of)))
                  for title, records in cases.items()]
    except (ValueError, TypeError, OverflowError) as error:
        parser.error(str(error))
    print("核验时间（北京时间）：", as_of.isoformat())
    print("合成示例 / 人工记录；不是官方接口，也不代表真实账号诊断。")
    for title, table in tables:
        print("\n" + title + "\n" + table)


if __name__ == "__main__":
    main()
