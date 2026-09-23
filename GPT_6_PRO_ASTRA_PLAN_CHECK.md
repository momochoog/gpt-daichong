---
title: "GPT-6 Pro 怎么开通？Astra、Plus / Pro 选择与到账核验"
description: "GPT-6 Pro 与 Astra 的关系，Plus、Pro 在 Chat、Work、Codex 的可用范围，以及付款前后如何核验套餐、模型入口和独立 API 账单。"
last_modified_at: 2026-09-23
---

# GPT-6 Pro 怎么开通？先分清 Astra、Plus / Pro 与使用入口

核验日期：2026-09-23，北京时间。本文由 AIXiamo 维护者整理，面向购买前选择和开通后核验；模型资格以 OpenAI 与本人账号实时显示为准。

**直接答案：**GPT-6 Pro 是 ChatGPT 中由 GPT-6 Astra 驱动的模型选项。它正向 Pro $100 / $200、Business 和 Enterprise 分批开放；Plus 用户在 Work / Codex 开放后有有限的 Astra 用量。OpenAI 于 2026-09-22 发布 GPT-6 Sol 和 Luna，面向 Plus、Pro 等计划在 ChatGPT Work 与 Codex 分批开放，普通 Chat 对话暂不能选择。希望在普通 Chat 中选择 GPT-6 Pro，应先核对支持的计划；主要用 Work / Codex 的用户，应在本人账号的对应入口查看模型和用量。依据：[OpenAI 模型与计划说明](https://help.openai.com/en/articles/20001354-gpt-56-and-gpt-6-pro-in-chatgpt)、[Sol / Luna 官方发布](https://openai.com/index/introducing-gpt-6-sol-and-luna/)、[Work / Codex 用量说明](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex)。

## 搜索“GPT-6 会员”时，你实际需要哪一种？

| 想完成的事 | 应核对的入口 | 付款前需要知道 |
| --- | --- | --- |
| 在 ChatGPT 里选择 GPT-6 Pro 问答 | Chat 的模型选择与计划 | Pro 两档均在开放范围；有独立模型用量限制 |
| 用 Astra、Sol 或 Luna 改代码、跑测试、处理仓库 | Codex 的模型选择与 Usage | Plus 的 Astra 用量有限；Sol / Luna 以本人账号分批开放的选项为准 |
| 用 Astra、Sol 或 Luna 研究资料、制作报告等交付物 | ChatGPT Work | Work 与普通 Chat 的模型资格和计量需要分别查看 |
| 把 GPT-6 模型接进自己的脚本或产品 | OpenAI API 项目 | `gpt-6-astra`、`gpt-6-sol`、`gpt-6-luna` 分别是 API 模型；API 独立计费，不由 ChatGPT 会员账单覆盖 |

GPT-6 Pro 的“Pro”是模型选项名称，ChatGPT Pro 是订阅计划名称。一次购买需要写清具体计划、周期和交付对象，不能仅凭“GPT-6 专用会员”几个字判断权益。API 模型和计量入口见 [GPT-6 Astra 官方模型页](https://developers.openai.com/api/docs/models/gpt-6-astra)。

## 购买前的三个确认

1. **确认本人账号和入口。** 先登录准备使用的账号，检查 Chat、Work 或 Codex 对应界面。企业工作区还要核对管理员的模型权限。
2. **确认要解决的是哪一种限制。** 模型尚未开放、已有模型但额度不足、支付不支持，是三种不同情况。官方明确购买 Credits 不会提前获得开放资格。
3. **确认订阅商品本身。** 核对计划、周期、续费方式、交付与退款条件。使用官方支持地区与真实付款资料；国内支付服务不会改变 OpenAI 的地区或模型访问规则。

本仓库原有的 [Plus 国内开通指南](README.md) 与 [Pro 5x / 20x 选择说明](GPT_PLUS_PRO_COMPARISON.md) 可用于进一步比较。模型入口与套餐关系的补充图文见 [AIXiamo：GPT-6 Astra 国内怎么用，Plus / Pro 与 API 如何区分](https://www.aixiamo.com/articles/gpt-6-astra-domestic-use-plus-pro-api-2026)。

## 开通后，怎样确认真的到账并能使用？

先在本人 ChatGPT 的套餐与账单页面核验订阅名称和状态，再到实际使用入口查看模型。保存核验时间即可，无需公开邮箱、付款凭据或账号信息。

| 账号里看到的情况 | 下一步 |
| --- | --- |
| 套餐仍未更新，订单显示处理中 | 查询原订单与交付状态，按原渠道核实 |
| 套餐已正确，但 Chat 中没有 GPT-6 Pro | 对照计划资格、分批开放和工作区权限 |
| Work / Codex 没有 Astra、Sol 或 Luna | 更新客户端，确认正确账号、入口与分批开放状态 |
| CLI 里没有 Astra | 先运行 `codex --version`；官方最低要求为 `0.153.0`，再检查登录方式和可用模型 |
| API 报无权限或无余额 | 核对 API 项目、密钥权限和独立账单；会员到账不能证明 API 已开通 |

“套餐已到账”和“新模型已向该入口开放”要分别验收。已付款问题继续使用 [付款与订单异常排障指南](CHATGPT_PAYMENT_ORDER_TROUBLESHOOTING.md)，避免因模型分批开放误判订单失败并重复付款。

## 常见问题

### Plus 能用 GPT-6 吗？

可以在已开放的 ChatGPT Work / Codex 中使用 GPT-6 Sol 和 Luna；Plus 的 Astra 用量仍有限。Sol / Luna 暂不能在普通 Chat 对话中选择，Plus 也不因此获得 Chat 中的 GPT-6 Pro。模型是否可见还取决于本人账号、工作区设置和分批开放状态；先检查对应入口的模型选择器，不要仅凭付款判断已开放。依据：[Sol / Luna 官方发布](https://openai.com/index/introducing-gpt-6-sol-and-luna/)、[OpenAI Work / Codex 说明](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex)。

### Pro 5x 和 20x 哪个能用 GPT-6 Pro？

两档都在 Chat 的开放范围内，但模型有独立限额，Work / Codex 另有用量结构。比较时查看实际工作量和账号显示的额度，而不是把 20x 理解为模型能力提升 20 倍。

### 买了会员就能调用 Astra API 吗？

不能。调用 Astra、Sol 或 Luna API 需要 API 项目的密钥、权限和独立账单；购买 Plus / Pro 会员不会附送 API 余额。先确认 API 可用，再按程序调用需求设置预算。模型 ID 见 [OpenAI API 模型目录](https://developers.openai.com/api/docs/models)，订阅与 API 的计费区别见 [OpenAI 账单说明](https://help.openai.com/en/articles/9039756-billing-settings-in-chatgpt-vs-platform)。
