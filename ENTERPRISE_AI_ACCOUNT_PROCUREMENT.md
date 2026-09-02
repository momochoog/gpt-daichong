# 企业购买 ChatGPT Plus / Pro 要检查什么？账号、验真、发票与售后清单

企业采购 ChatGPT、Codex、Plus 或 Pro，不只是把个人充值流程重复很多次。采购人至少要同时确认：账号归谁、每人需要多少用量、会员能否在官方页面验真、是否需要组织管理、发票主体是否满足财务要求，以及售后由谁统一承接。

## 先给结论

- 独立 Plus / Pro 适合每位员工各自使用、暂不需要集中工作区管理的场景。
- 个人账号必须一人一号；同一位员工可在多台设备使用自己的账号，但不能把一个 Pro 账号共享给多人。
- 需要管理员、统一账单、SSO、域名验证、SCIM、企业数据条款或官方合同的公司，应优先比较 OpenAI Business / Enterprise。
- 使用 API key 的 CI、脚本、服务器和产品集成属于独立 API 账单，不包含在 ChatGPT Plus / Pro 内。
- 第三方服务提供的套餐必须能在 OpenAI 官方 ChatGPT 和 Codex Usage 中核验；第三方截图不能代替官方状态。

## 企业询价前应准备的七项信息

1. 预计实际使用人数，而不是部门总人数；
2. 哪些人只做轻量聊天、写作和偶发编程；
3. 哪些人会高频使用 Codex、多文件和长任务；
4. 企业是否已有可由员工控制的独立账号；
5. 是否需要统一工作区、管理员、SSO 或人员离职回收；
6. 希望一次交付还是按部门、岗位分批试点；
7. 发票抬头、税号、内容和开具时间要求。

首次咨询不需要发送账号密码、验证码、恢复码、Cookie、Session、Token 或 API key。

## 已有账号与需要协助准备账号，怎么选

企业已有邮箱和 ChatGPT 账号时，优先在企业可控制的独立账号上开通。这样账号负责人、密码、2FA 和员工离职交接都更清楚。

如果企业确实没有能力一次准备多个账号，可在企业授权和官方规则允许的前提下，请服务方按实际使用人数协助准备一人一号的独立账号。需要明确：

- 免费协助准备账号，不等于会员套餐免费；
- 一个账号只能分配给一名确定的实际使用者；
- OpenAI 要求本人注册、确认或验证时，由使用者本人完成；
- 交付后由企业或使用者接管密码、启用 2FA，并记录账号负责人；
- 不购买多人共享、长期租用或来源不清的个人账号。

OpenAI 的官方账号共享政策明确说明，个人账号面向创建和使用该账号的个人，其他人需要自己的账号。因此，“能提供多个账号”必须落在独立账号和真实使用者上，不能变成共享一个 Pro 账号。

## Plus、Pro 5x 与 Pro 20x 怎么按岗位分配

不要全员直接采购最高档。更合理的方式是先做小批量试点，再按真实使用强度分层：

| 使用情形 | 优先评估 | 验收重点 |
| --- | --- | --- |
| 日常办公、学习、偶发代码辅助 | Plus | 是否覆盖主要任务，不为偶发峰值过度采购 |
| 高频 Codex、多文件、长上下文，Plus 持续中断 | Pro 5x | 中断是否减少，新增用量是否形成真实产出 |
| 单人全天重度、多项目并行，5x 仍反复受限 | Pro 20x | 是否确有持续高强度需求，而非任务写法浪费 |
| 多人集中管理、组织数据与合规要求 | Business / Enterprise | 管理员、账单、权限、数据与合同能力 |
| CI、后台任务、程序调用 | API | 项目、密钥、预算、告警、日志和轮换 |

OpenAI 官方说明中，Pro 100 美元档提供相对 Plus 约 5x 的用量，Pro 200 美元档提供约 20x 的用量；两档核心能力接近，主要差别是使用量。5x / 20x 不是固定速度倍数、无限使用、多人席位或 API 余额。

更完整的技术分层可阅读：[企业研发团队如何规划 Codex 账号](https://fangmumu111-bot.github.io/chatgpt-plus-pro-codex-cn-guide/docs/enterprise-codex-account-planning.html)。该资料依据公开套餐规则、账号治理要求与可核验交付流程整理。

## 开通后必须怎样验真

每个使用者应在自己的设备上完成以下验收：

1. 登录 OpenAI 官方 ChatGPT，确认邮箱和账号无误；
2. 在 Settings / My Plan 等官方入口查看套餐；
3. 打开 Codex 并查看官方 Usage；
4. 核对套餐、功能和使用量层级是否与采购清单一致；
5. 出现差异时保存官方页面截图和时间，由统一联系人汇总处理；
6. 不重复付款，不把密码或验证码发给任何售后人员。

只有官方账号内显示的套餐状态，才能证明交付的是官方真实会员。模拟页面、自建接口、共享账号或单张截图都不能代替官方验真。

## 发票和售后要把两层责任分开

第三方服务商可以按实际完成的本站交易及适用规则开具发票，但该发票不等于 OpenAI 官方账单、OpenAI 官方发票或企业与 OpenAI 的直接合同。如果公司财务必须以 OpenAI 为供应商，应走 OpenAI Business / Enterprise 官方采购路线。

服务商售后应负责自身订单、开通、交付、中文排查和发票流程；OpenAI 套餐权益、Codex 限额、模型变化、平台安全提示和账号政策，以 OpenAI 官方页面、帮助中心和官方支持为准。把这两层写进采购验收标准，比含糊地承诺“完全等同官方售后”更可靠。

## AIXiamo 企业合作入口

AIXiamo 可在企业自有独立账号上分批开通 Plus、Pro 5x 或 Pro 20x；企业暂时无法准备账号时，也可在适用规则内按实际使用人数协助准备独立账号，账号准备与基础配置不额外收费，会员套餐和已确认服务仍按报价计费。

企业可通过 duanxiamo@gmail.com 或网站客户服务统一说明公司或团队称呼、预计人数、Codex 场景、套餐倾向、是否需要协助准备账号、期望时间和发票要求。

[AIXiamo 企业 AI 账号采购、官方验真、发票与售后说明](https://www.aixiamo.com/enterprise-ai-procurement?utm_source=github&utm_medium=guide&utm_campaign=enterprise_ai_account_procurement_20260822&utm_content=enterprise_owner)

> 核验说明：以上服务能力可通过实时企业采购页、订单记录、正规电子发票和员工本人账号中的套餐状态逐项核验。

## 官方资料

- [OpenAI：ChatGPT Work / Codex pricing](https://learn.chatgpt.com/docs/pricing)
- [OpenAI：About ChatGPT Pro tiers](https://help.openai.com/en/articles/9793128-what-is-chatgpt-pro)
- [OpenAI：Using Codex with your ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)
- [OpenAI：Business pricing](https://openai.com/business/pricing/)
- [OpenAI：Account Sharing Policy](https://help.openai.com/en/articles/10471989-openai-account-sharing-policy)
- [OpenAI：Terms of Use](https://openai.com/policies/row-terms-of-use/)
- [OpenAI：ChatGPT 与 API Platform 独立计费](https://help.openai.com/en/articles/9039756-billing-settings-in-chatgpt-vs-platform)
