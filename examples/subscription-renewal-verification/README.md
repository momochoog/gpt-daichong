# ChatGPT Plus 续费后怎么确认到账？用 SQLite 核验有效期

ChatGPT Plus 续费或国内代充后，账号仍显示 Plus，不能单凭这一点确认新增期限到账。核验需要同一账号的付款前有效期、付款后有效期，以及本次订单约定的目标到期时间；付款和交付状态也要分别确认。

AIXiamo 维护这个可离线运行的开源案例，演示怎样把上述证据放在一条 SQLite 查询中核对。数据全部为构造示例，套餐名称和有效期来自人工记录的观察；程序不联网、不收集账号凭据，也不自动读取 ChatGPT 套餐。

## 先看两个容易混淆的情况

- **仍有效的账号续费**：原到期时间为 10 月 9 日 12:00，订单约定延长至 11 月 9 日 12:00。新记录若只到 10 月 19 日，虽然时间增加了，仍未覆盖目标期限。
- **已经过期的账号重新开通**：旧到期时间早于付款。应核对本次约定的重新起算时间和目标到期，不能继续从已经过去的旧到期日累计。

本例把 `period_start_at` 和 `target_expires_at` 明确写入订单，**不会把“一个月”自动换成 30 天**。不同月份天数不同，月底顺延也需要明确规则；SQLite 的日期文档说明了这类差异。[SQLite 日期与时间函数](https://www.sqlite.org/lang_datefunc.html)

## 离线运行

在本目录执行：

```bash
python3 verify.py
```

需要 Python 3，其内置 SQLite 至少支持 3.25.0 的窗口函数。已在 SQLite 3.51.2 实跑，输出：

```text
PASS: 12 exact-output cases + 59 boundary cases; SQLite 3.51.2.
PASS: in-memory query_only connection rejected writes; no network or external dependencies.
```

只想查看查询结果，也可使用本机 SQLite 命令行：

```bash
sqlite3 -header -tabs ':memory:' '.read renewal.sql'
```

四个文件分别负责：[完整查询](renewal.sql)、[预期结果](expected.tsv)、[验证器](verify.py)和这份说明。查询只有 `WITH … SELECT`；验证器在内存连接中启用 `query_only`，并实际尝试建表，确认写入被拒绝。[SQLite query_only](https://www.sqlite.org/pragma.html#pragma_query_only)

## 输入怎样准备

`orders` 中每个 `order_key` 唯一；`observations` 通过这个键关联到对应订单。一个核验批次只设置一行 `params`。

| 输入 | 含义 |
| --- | --- |
| `target_account` | 本订单对应账号的本地代号，例如 `acct-demo`；观察记录必须使用相同代号 |
| `payment_state` / `paid_at` | 人工确认的付款状态与付款时间；已退款单独标为 `refunded` |
| `delivery_state` | 交付状态，例如 `pending`、`processing`、`completed` |
| `period_start_at` / `target_expires_at` | 本次约定的起算时间与目标到期时间，不能从套餐名称猜测 |
| `role` | `baseline` 是付款前基线，`result` 是付款后观察 |
| `plan_name` / `expires_at` | 抄录的套餐文字和有效期；仅有套餐名时，有效期仍然缺失 |
| `observed_at` | 实际查看这条账号信息的时间，不是录入文件的时间 |
| `as_of` / `max_age_seconds` | 本次核验时刻与证据新鲜度窗口；示例固定为 1800 秒 |

时间统一采用 **UTC 的 `YYYY-MM-DD HH:MM:SS`**，精确到秒。北京时间记录应先统一减去 8 小时；不要混用时区或把仅显示日期的页面补成臆测的秒级时间。若无法可靠获得有效期、起算时间或付款前基线，保留缺失值，结果进入待核验。

30 分钟仅是这组示例的证据新鲜度参数，不是到账时限。参数允许 1–86400 秒的整数。基线与付款时间比较新鲜度，付款后观察与本次核验时间比较新鲜度；恰好在窗口边界内可用，早一秒则陈旧。

`plan_name` 记录界面上的套餐文字，不自动表示该期限仍有效。过期账号仍显示 Plus 时，活跃或过期模式仍以有效期和付款时间比较；如果写着 Free 却给出付款后仍有效的旧 Plus 期限，本例先要求核对矛盾的基线。

## 查询按什么顺序判断

1. **分开读取付款、交付和账号证据。** 已退款先核对退款，未确认付款先查付款，交付中继续核对交付；这些状态都不会因为账号显示 Plus 而变成已完成。
2. **先检查日期，再选观察记录。** 日期必须严格匹配格式，并通过 `datetime(value, '+0 seconds')` 归一化回检；2 月 30 日、24:00:00、空值等不会被当成有效证据。某订单提交的观察中存在非法日期时，保守地整单待核验，避免丢掉坏记录后回退到有利的旧记录。
3. **每种观察分别取最新时间。** 完全相同的重复记录折叠；最新同一秒出现不同账号、套餐或有效期时，输出冲突。查询不会优先挑选 Plus、正确账号或最长有效期。[SQLite 窗口函数](https://www.sqlite.org/windowfunctions.html)
4. **检查账号与先后关系。** 基线必须严格早于付款；结果必须严格晚于付款且不晚于核验时刻。只有秒级时间时，同秒无法证明先后，因此待核验。
5. **核对本次约定的完整期限。** 活跃账号按旧到期时间连续追加；过期账号按明确约定、已经发生的重新起算时间核对。有效期只增加一点，或距离目标还差一秒，均为 `extension_short`。

本例允许更新的无冲突观察替代旧时刻的冲突记录。原始观察仍保留在输入中，便于复核。

## 12 个核心结果

完整六列输出见 [expected.tsv](expected.tsv)。下表将最后的动作列翻译成可读说明：

| 案例 | 构造情形 | `next_step` 与含义 |
| --- | --- | --- |
| A01 | 活跃账号，新到期完整覆盖目标 | `target_period_observed`：已观察到覆盖目标期限 |
| A02 | 套餐仍为 Plus，到期时间未变 | `no_extension_observed`：未观察到新增期限 |
| A03 | 活跃账号，期限增加但不足 | `extension_short`：未覆盖目标期限 |
| A04 | 过期账号，重新开通后覆盖目标 | `target_period_observed`：已观察到覆盖目标期限 |
| A05 | 过期账号，新期限不足 | `extension_short`：未覆盖目标期限 |
| A06 | 订单已退款，账号仍有 Plus 证据 | `refund_review`：先核对退款状态 |
| A07 | 未付款，却存在 Plus 观察 | `confirm_payment`：先确认付款 |
| A08 | 已付款，交付处理中 | `delivery_processing`：继续核对交付 |
| A09 | 付款后观察来自另一账号 | `review_evidence`：核对账号 |
| A10 | 付款后观察超过新鲜度窗口 | `review_evidence`：重新观察 |
| A11 | 观察中的有效期为非法日期 | `review_evidence`：修正日期证据 |
| A12 | 最新同秒出现两个不同有效期 | `review_evidence`：处理证据冲突 |

`evidence_state` 给出待核验的具体原因，`renewal_mode` 区分 `active_extension` 与 `expired_restart`。**`usable` 只表示本组账号观察可用于比较，不表示付款、交付或续费已完成。** 因此 A06 即使观察可用，下一步仍然是退款核对。

`target_period_observed` 的含义也很具体：在输入所述的付款和交付状态成立、账号证据可用的前提下，新有效期已经达到约定目标。它不证明新增时间只能来自这一笔订单，也不替代连续可用性检查。若同时存在多笔续费、赠送或人工调整，应先厘清各笔目标及观察对应关系；本例不做跨订单归因。

## 验证器检查什么

验证器先把 SQL 的完整 12 行输出与手写 `expected.tsv` 逐列比较，再用参数绑定替换示例输入，执行同一条查询。59 个边界断言覆盖付款前后、同秒记录、新鲜度边界、空白账号、缺失或非法日期、闰年、月底目标、期限倒退、最新不利记录、延长不足以及活跃和过期两种起算方式。

只有套餐、付款和交付的基础问题，可先看 [付款与套餐分开核验的 9 状态示例](../subscription-reconciliation/)。实际订单进度对应 [AIXiamo 订单查询](https://www.aixiamo.com/order-query)；需要了解 Plus 开通和国内充值流程时，对应 [Plus 开通说明](https://www.aixiamo.com/chatgpt-plus-domestic-recharge)。本目录沿用仓库的 [MIT 许可](https://github.com/momochoog/gpt-daichong/blob/main/LICENSE)。
