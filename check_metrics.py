#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_metrics.py —— 严格只读。不连数据库、不持任何凭据、不发起网络请求、不写任何文件。

为什么有这个脚本
----------------
本项目此前发生过 5 处「公开文档数字 ≠ 云端实际数字」的漂移（signals 70→79、id_max 71→80、
safety 0→2、top4 95.7%→84.8%、receipts 2→4、events 163→204），**没有一处是被任何机制
发现的**，全靠人手撞见。根因：机器纪律全在生产层（晨报选题/发信），承诺层（公开文档的数字）
一个自动化检查都没有。

本脚本把承诺层的最小一块变成系统：把 data/metrics.json 承诺的数字，与云端实测的数字，
做一次机器比对。漂移第一次由系统发现，而不是等人发现。

设计约束（三条，不可违反）
--------------------------
1. **只读**：不连接数据库、不写文件、不改数据。所有 SQL 由调用方（巡检任务）执行后
   以 JSON 形式喂进来。这样脚本本身永远拿不到写权限，也不需要任何凭据。
2. **单一真相源**：待比对的期望值全部来自 data/metrics.json，**本文件不硬编码第二份数字**。
   metrics.json 改了，本脚本自动跟着改。
3. **SQL 单一出处**：核对用 SQL 定义在下方 CHECKS 里（--emit-sql 可打印），
   与比对项一一对应，避免「文档里一套 SQL、脚本里另一套」。

用法
----
  python check_metrics.py --emit-sql
        打印全部核对 SQL（每行一条，供巡检任务逐条执行）

  python check_metrics.py --emit-template
        打印 actual.json 的字段结构模板

  python check_metrics.py --actual <actual.json> [--metrics <metrics.json>] [--max-age-days 3]
        执行比对。全部一致 → 退出码 0；存在漂移 → 退出码 1；脚本自身出错 → 退出码 2。

actual.json 结构
----------------
  {
    "scalars": { "signals_total": 79, "signals_id_max": 80, ... },
    "rows": {
      "category_distribution": [{"cat": "corp", "c": 20}, ...],
      "signal_events_kinds":   [{"kind": "view", "c": 157}, ...]
    }
  }
"""

import argparse
import datetime as _dt
import json
import os
import sys

# ---------------------------------------------------------------------------
# 核对项定义。
#   scalars: 单值指标，SQL 结果映射到 metrics.json 的同名键
#   rows:    多行结果，用于派生指标（分类分布、事件分 kind）
# ---------------------------------------------------------------------------

SCALAR_SQL = [
    {
        "id": "subs",
        "sql": "SELECT count(*) FILTER (WHERE status='active' AND is_internal IS NOT TRUE) AS external_subscribers, count(*) FILTER (WHERE status='active' AND is_internal IS TRUE) AS internal_subscribers, count(*) FILTER (WHERE status='active') AS active_subscribers_total, count(*) FILTER (WHERE status='unsubscribed') AS unsubscribed_external FROM subscribers",
        "keys": [
            "external_subscribers",
            "internal_subscribers",
            "active_subscribers_total",
            "unsubscribed_external",
        ],
    },
    {
        "id": "topic_requests",
        "sql": "SELECT count(*) AS topic_requests_total, count(*) FILTER (WHERE contact IS NULL OR length(contact) < 3) AS topic_requests_empty_contact, count(DISTINCT topic) AS topic_requests_distinct_topic FROM topic_requests",
        "keys": [
            "topic_requests_total",
            "topic_requests_empty_contact",
            "topic_requests_distinct_topic",
        ],
    },
    {
        "id": "filter_requests",
        "sql": "SELECT count(*) AS filter_requests FROM filter_requests",
        "keys": ["filter_requests"],
    },
    {
        "id": "signal_votes",
        "sql": "SELECT count(*) AS signal_votes FROM signal_votes",
        "keys": ["signal_votes"],
    },
    {
        "id": "receipts",
        "sql": "SELECT count(*) AS delivery_receipts_total, count(*) FILTER (WHERE NOT EXISTS (SELECT 1 FROM subscribers s WHERE s.email = dr.email AND s.is_internal IS TRUE)) AS external_delivery_receipts, count(DISTINCT dr.email) AS _distinct_email, max(dr.created_at) AS _last_at FROM delivery_receipts dr",
        "keys": ["delivery_receipts_total", "external_delivery_receipts"],
    },
    {
        "id": "signals",
        "sql": "SELECT count(*) AS signals_total, min(id) AS signals_id_min, max(id) AS signals_id_max FROM signals",
        "keys": ["signals_total", "signals_id_min", "signals_id_max"],
    },
    {
        "id": "signals_quality",
        "sql": "SELECT count(*) FILTER (WHERE src_url IS NULL OR length(src_url) < 5) AS signals_missing_src_url, count(*) FILTER (WHERE deep_verified IS TRUE) AS signals_deep_verified, count(*) FILTER (WHERE corrected IS TRUE) AS signals_corrected FROM signals",
        "keys": [
            "signals_missing_src_url",
            "signals_deep_verified",
            "signals_corrected",
        ],
    },
]

ROW_SQL = [
    {
        "id": "category_distribution",
        "sql": "SELECT cat, count(*) AS c FROM signals GROUP BY cat ORDER BY c DESC",
    },
    {
        "id": "signal_events_kinds",
        "sql": "SELECT kind, count(*) AS c FROM signal_events GROUP BY kind ORDER BY c DESC",
    },
]

# 需要从 scalars 里排除的辅助列（下划线开头 = 只记录不比对）
AUX_PREFIX = "_"


def _norm(v):
    """归一化以便比较：数字统一转 str，去掉浮点尾巴。"""
    if v is None:
        return None
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, float):
        if v == int(v):
            return str(int(v))
        return ("%.4f" % v).rstrip("0").rstrip(".")
    return str(v).strip()


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _derive_from_rows(rows):
    """从多行结果派生出可与 metrics.json 比对的指标。"""
    derived = {}

    cat = rows.get("category_distribution") or []
    if cat:
        total = 0
        counts = {}
        for r in cat:
            c = int(r.get("c", 0))
            counts[str(r.get("cat"))] = c
            total += c
        if "safety" in counts:
            derived["category_safety_count"] = counts["safety"]
        if total:
            top4 = sum(sorted(counts.values(), reverse=True)[:4])
            pct = top4 * 100.0 / total
            derived["category_top4_share"] = ("%.1f%%" % pct)
            derived["signals_total"] = derived.get("signals_total", total)

    ev = rows.get("signal_events_kinds") or []
    if ev:
        total = 0
        for r in ev:
            c = int(r.get("c", 0))
            total += c
            if str(r.get("kind")) == "sub_invalid":
                derived["signal_events_sub_invalid"] = c
        derived["signal_events_total"] = total

    return derived


def run_check(metrics_path, actual_path, max_age_days):
    metrics = _load_json(metrics_path)
    actual = _load_json(actual_path)

    m = metrics.get("metrics", {})
    scalars = dict(actual.get("scalars") or {})
    rows = actual.get("rows") or {}

    derived = _derive_from_rows(rows)
    # 实测优先取显式 scalars；派生值仅在 scalars 未给出时补齐
    actual_all = {}
    actual_all.update(derived)
    actual_all.update({k: v for k, v in scalars.items() if not k.startswith(AUX_PREFIX)})

    # 待比对清单 = metrics.json 里声明的、且我们真正拿到了实测值的键
    keys = [k for k in m.keys() if k in actual_all]

    drift = []
    ok = []
    for k in sorted(keys):
        exp = _norm(m[k])
        got = _norm(actual_all[k])
        if exp is None or got is None:
            continue
        if exp == got:
            ok.append((k, exp))
        else:
            drift.append((k, exp, got))

    # 新鲜度检查：metrics.json 的 data_as_of 不能太旧
    stale = None
    dao = metrics.get("data_as_of")
    if dao:
        try:
            d = _dt.date.fromisoformat(str(dao))
            age = (_dt.date.today() - d).days
            if age > max_age_days:
                stale = (dao, age)
        except ValueError:
            stale = (str(dao), None)

    print("=" * 68)
    print("check_metrics · 承诺层数字漂移核对（只读）")
    print("  期望源 : %s  (version %s, data_as_of %s)"
          % (os.path.basename(metrics_path), metrics.get("version"), dao))
    print("  实测源 : %s" % os.path.basename(actual_path))
    print("  已核对 : %d 项" % len(keys))
    print("=" * 68)

    for k, v in ok:
        print("  [OK]    %-34s %s" % (k, v))

    for k, exp, got in drift:
        print("  [DRIFT] %-34s 文档=%s  实测=%s" % (k, exp, got))

    if stale:
        dao_s, age = stale
        if age is None:
            print("  [STALE] data_as_of 无法解析：%s" % dao_s)
        else:
            print("  [STALE] data_as_of=%s，距今 %d 天（阈值 %d 天）"
                  % (dao_s, age, max_age_days))

    print("-" * 68)
    if drift:
        print("结论：发现 %d 项漂移 → 公开文档数字已与云端不一致，需人工修 metrics.json"
              % len(drift))
        return 1
    if stale:
        print("结论：数字一致，但数据基准日已过期，需重新回库复现")
        return 1
    print("结论：全部一致（%d 项），基准日在阈值内" % len(ok))
    return 0


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_metrics = os.path.join(here, "data", "metrics.json")

    ap = argparse.ArgumentParser(
        description="只读核对 data/metrics.json 与云端实测数字是否一致")
    ap.add_argument("--emit-sql", action="store_true",
                    help="打印全部核对 SQL 后退出")
    ap.add_argument("--emit-template", action="store_true",
                    help="打印 actual.json 模板后退出")
    ap.add_argument("--actual", help="实测结果 JSON 文件路径")
    ap.add_argument("--metrics", default=default_metrics,
                    help="metrics.json 路径（默认与本脚本同目录的 data/metrics.json）")
    ap.add_argument("--max-age-days", type=int, default=3,
                    help="data_as_of 距今天数的告警阈值，默认 3")
    args = ap.parse_args()

    if args.emit_sql:
        for item in SCALAR_SQL:
            print("# %s" % item["id"])
            print(item["sql"])
        for item in ROW_SQL:
            print("# %s" % item["id"])
            print(item["sql"])
        return 0

    if args.emit_template:
        scalars = {}
        for item in SCALAR_SQL:
            for k in item["keys"]:
                scalars[k] = 0
        print(json.dumps(
            {"scalars": scalars,
             "rows": {"category_distribution": [{"cat": "corp", "c": 0}],
                      "signal_events_kinds": [{"kind": "view", "c": 0}]}},
            ensure_ascii=False, indent=2))
        return 0

    if not args.actual:
        ap.error("需要 --actual <actual.json>，或用 --emit-sql / --emit-template")
        return 2

    try:
        return run_check(args.metrics, args.actual, args.max_age_days)
    except FileNotFoundError as e:
        print("文件不存在：%s" % e, file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print("JSON 解析失败：%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
