# 数据样本

> 展示一条信号在我们的库里**实际**长什么样，以及**判定是怎么落到的**。
> 更新：2026-10-14
> **取证方式**：本页字段值与数字均来自云端库实测查询（2026-10-14 复现），不是凭记忆写的。复现语句见 [METRICS.md](METRICS.md) 第六节与 `data/metrics.json`。
> **隐私说明**：本页不含任何订户邮箱或个人数据。下面的原文链接与引语均为**公开报道/公开页面**的内容，不涉及个人隐私。

---

## ⚠️ 本文档自己的更正（2026-10-14）

**先说我们自己的错**：本页 v0.1 版曾把 id 54 的字段写成下面这样——

- **改前原值**：`"stamp": "warn"`、`"stamp_text": "待补录"`、`"src_reach": "direct"`、`"deep_srcs": 6`
- **实测真实值**：`"stamp": "ok"`、`"stamp_text": "海关验讫 ✓"`、`"src_reach": "proxy"`、`"deep_srcs"` 是 **jsonb 对象**（不是数字 6）
- **性质**：在一个宣称"字段结构如实公开"的文档里，把一条绿章写成黄章、把境外链写成境内直连、把数组写成数字。方向虽然是"把自己写得更保守"，但**失实就是失实**，且它同时违反了本包自己发布的 CTL schema。
- **发现方式**：交叉审计（逐字段比对 `STANDARD.md` 与 `information_schema` 真实列类型）+ 回库实测。
- **教训**：**"如实"不能靠印象，必须回源实测。** 这与更正 01（数错信源）是同一类错误——**没有核验就下断言**。

这一条同步记入了 [CORRECTIONS.md](CORRECTIONS.md) 更正 04。

---

## 一、一条信号的真实字段（id 54，实测）

```json
{
  "id": 54,
  "tag": "光器件产能售罄",
  "cat": "infra",
  "hook": "（信号标题：事件的客观陈述）",
  "src": "SIGNAL · 陆家嘴财经早餐 2026-10-10（引 Lumentum CEO 公开发言）",
  "src_url": "https://www.bloomberg.com/news/articles/2026-10-09/nvidia-backed-lumentum-sees-opto-parts-capacity-sold-out-to-2029",
  "src_quote": "Lumentum is unable to meet about 70% of demand for some products through next year, and won't be able to address 30% of demand for some other products through 2028",
  "src_reach": "proxy",
  "stamp": "ok",
  "stamp_text": "海关验讫 ✓",
  "deep_verified": true,
  "deep_verified_by": "行止",
  "deep_srcs": {
    "primary": { "name": "Bloomberg", "tier": "B", "desc": "CEO 东京受访口径 · 单一主源" },
    "cross": [
      { "name": "Quartz", "tier": "B" },
      { "name": "腾讯新闻", "tier": "B" },
      { "name": "证券时报", "tier": "B" },
      { "name": "财联社", "tier": "B" }
    ],
    "conflict": "口径一致无冲突。审计更正（10-10）：上述 4 家系同一 Bloomberg 采访之转载确认，非独立源；本条独立源 1/2，未达「≥2 独立来源」标准"
  },
  "deep_note": "信源层级：CEO 东京采访（Bloomberg）· 单一主源；…结论：核心口径一致、无冲突，但独立源 1/2 未达深核标准第 2 条，深核章存续由行止复核",
  "corrected": true,
  "foot": "〔jsonb 数组：页面脚注标签，如 AI 参与标识、核验结论、信源层级〕"
}
```

**注意两个细节**：

1. `src_reach` 是 **`proxy`**——原文是 Bloomberg（境外），我们不假装它境内直连。
2. `deep_srcs` 里那 4 家**仍列在 `cross` 中**，但 `conflict` 字段明确写了它们是转载、且独立源实为 1/2。**保留原始记录 + 披露修正**，而不是删掉历史——这是我们的处理方式。

---

## 二、字段与 CTL 的对照（我们自己做到了多少）

| CTL 字段 | 我们库里的对应 | 是否达标 |
|---|---|---|
| `claim`（陈述原文） | **无此字段**。`hook` 是标题式陈述，与"不转述的陈述原文"不完全等价 | ❌ 见 [KNOWN_GAPS.md](KNOWN_GAPS.md) G14 |
| `src_url` | ✅ 有 | ✅ |
| `src_quote` | ✅ 有（逐字摘录，见上） | ✅ |
| `src_count`（独立信源数） | **无此字段**，独立源数写在 `deep_note` 文本里 | ❌ 见 G2 |
| `src_reach` | ✅ 有 | ✅ |
| `stamp` | ✅ 有（ok / warn） | ✅ |
| `stamp_basis` | 用 `stamp_text`（"海关验讫 ✓"）近似，但它是**章位文案**而非"为什么盖这个章" | ⚠️ 部分 |
| `deep_check`（做过深核动作） | `deep_verified = true` | ✅ |
| `deep_qualified`（达到 L3） | 无法计算（依赖 `src_count`，缺字段）。id 54 实测未达 L3 | ❌ |
| `corrected` | ✅ 有，本条为 `true` | ✅ |
| `correction_note` | 无独立字段，更正说明写在 `deep_note` 与更正档案里 | ⚠️ 部分 |
| `ai_generated` | **无此字段**。AI 参与只存在于 `foot` 文本中，**不可机读** | ❌ 见 G13 |

**我们自己没有完全做到自己定的标准。** 这张表就是证据——它不是声明，是逐字段比对的结果。

---

## 三、三个真实判定样本（全部实测）

### 样本 A · id 54（Lumentum）—— 做过深核，**但未达 L3**，已更正

| 字段 | 实测值 |
|---|---|
| `stamp` | **ok**（绿章） |
| `deep_verified` | `true`（做过深核动作） |
| 独立源（审计后） | **1 / 2** —— 4 家均为同一 Bloomberg 采访之转载，引语逐字一致 |
| 是否达 L3 | ❌ **未达**（CTL L3 要求 `src_count ≥ 2`） |
| `corrected` | `true` |

**这条的价值**：它用真事证明了"数信源"有多容易错，也促成了 CTL 的 R1 规则。
**它同时暴露了我们的术语缺陷**：数据库里只有一个 `deep_verified` 布尔值，混用了"做过深核动作"和"达到深核资格"两种含义——这正是我们在 CTL v0.1 里把它拆成 `deep_check` / `deep_qualified` 的原因。

### 样本 B · id 15 / id 52 —— 曾被误伤，后自我撤回

| id | 实测 `stamp` | `corrected` | `src_reach` | 原文链 |
|---|---|---|---|---|
| 15（DeepSeek 昇腾开源） | **ok** | false | proxy | `github.com/deepseek-ai/DeepGEMM-Ascend` |
| 52（GPT-6.1 Sol Ultrafast） | **ok** | false | proxy | `platform.openai.com/docs/pricing` |

**实测说明**：两条当前均为绿章、`corrected = false`——即**误伤指控撤回后，我们没有给它们打上"曾被错误质疑"的标记**。
**这本身是一个缺口**：被审计误伤过的条目，在数据结构里不留痕迹。是否该留，我们目前没有结论，如实列出。

### 样本 C · id 57（阶跃 Step 5）—— 深核达标

| 字段 | 实测值 |
|---|---|
| `stamp` | **ok** |
| `deep_verified` | `true` |
| `deep_verified_by` | **`行止（AI 辅助核验 · 行止负责）`** |
| 独立源 | 2 家（官方参数页 + 登顶信息转述） |
| `corrected` | false |

**一个值得注意的对照**：id 57 的 `deep_verified_by` 已经写成了更正 03 后的新措辞，而**历史条目 id 54 的同一字段仍是旧值「行止」**——更正 03 没有回溯历史数据。这记入 [KNOWN_GAPS.md](KNOWN_GAPS.md) G15。

全库 `deep_verified = true` 的只有 **2 条**（id 54、id 57，实测）。样本量这么小，恰恰说明这套分级**尚未被充分验证**——我们不把它当成绩。

---

## 四、站点上渲染出来的样子

```
〔海关验讫 ✓〕  锐评: AI 辅助生成(零)  核验: ✓ 全称搜索通过  信源: 官方
```

AI 的参与在这里是**显式标注**的，不是藏起来的。
（但注意：它标注在 `foot` 文本里，**不可机读**——这是 CTL 要求我们尚未做到的部分，见 G13。）

---

## 五、审计范围

- **信号条目**：id 1–71，共 **70 条**（id 7 不存在，为跳号），截至 2026-10-13。
- **不含**：订户身份与邮箱（不入包）；`signal_events` 埋点明细（该表按设计只进不出、无 SELECT 策略，连我们自己也不读回）。
- **全量**：线上核验台账列出全部条目的章位、原文链、摘录、可达性。**如果你发现某条标注与实际不符——那就是我们要的错误**，请来挑错：[CONTRIBUTING.md](CONTRIBUTING.md)。
