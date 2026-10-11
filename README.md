# Loon 专属高质量全量分流规则集

自建维护的 Loon 高质量分流规则库。基于 v2fly 社区官方与 MetaCubeX 官方核心数据源交叉对齐，彻底替代第三方注水残缺的“两行空壳规则”。由自建服务器 Hermes Agent 每 6 小时自动巡检更新。

---

## 一览表与 Loon 订阅链接

### 1. 🤖 AI 专区（彻底解决风控与漏网）

| 规则名称 | 规则条数 | 说明 | Loon 远程规则订阅链接 |
| :--- | :--- | :--- | :--- |
| **`AI.list`** | 85 条 | **【强烈推荐】全家桶大合集**（Claude/OpenAI/Gemini/Perplexity/Cursor/Copilot） | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/AI.list` |
| **`Claude.list`** | 9 条 | Claude 专属（含认证跳转、所有子站、多模态沙箱与专用 CDN） | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Claude.list` |
| **`OpenAI.list`** | 27 条 | OpenAI 专属（补全 `chat.com`, `sora.com`, `oaistatsig.com`） | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/OpenAI.list` |
| **`Gemini.list`** | 46 条 | Google Gemini 专属（补齐 `aistudio.google.com` 等全部资产） | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Gemini.list` |

---

### 2. 🎬 流媒体与社交专区

| 规则名称 | 规则条数 | 策略建议 | Loon 远程规则订阅链接 |
| :--- | :--- | :--- | :--- |
| **`YouTube.list`** | 178 条 | 走 `YouTube` | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/YouTube.list` |
| **`Netflix.list`** | 28 条 | 走 `Netflix` | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Netflix.list` |
| **`Spotify.list`** | 31 条 | 走 `Spotify` | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Spotify.list` |
| **`Telegram.list`** | 21 条 | 走 `Telegram` | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Telegram.list` |
| **`Twitter.list`** | 24 条 | 走 `X` | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Twitter.list` |
| **`TikTok.list`** | 43 条 | 走 `TikTok` | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/TikTok.list` |
| **`Reddit.list`** | 12 条 | 走 `Reddit` | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Reddit.list` |
| **`WhatsApp.list`** | 11 条 | 走代理 | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/WhatsApp.list` |
| **`Bilibili.list`** | 53 条 | 走 `Bilibi` | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Bilibili.list` |

---

### 3. 🌐 科技大厂与基础服务

| 规则名称 | 规则条数 | 修复亮点 | Loon 远程规则订阅链接 |
| :--- | :--- | :--- | :--- |
| **`Google.list`** | 1181 条 | 包含全系 Google 核心、服务、API 与 CDN | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Google.list` |
| **`Microsoft.list`** | 798 条 | 彻底修复原版“缺微软主体”硬伤，覆盖 Windows 更新/Office 365/Xbox/Bing | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Microsoft.list` |
| **`Apple.list`** | 1953 条 | 一个完整苹果总库，告别原版被强行拆碎的 12 个“两行假分类” | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Apple.list` |
| **`GitHub.list`** | 65 条 | 覆盖主站、Raw 静态加速与 Releases 下载通道 | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/GitHub.list` |
| **`Cloudflare.list`** | 76 条 | 涵盖官方国际服务（已剥离国内 Nameserver 污染） | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Cloudflare.list` |
| **`Steam.list`** | 63 条 | 覆盖社区与商店（排除国内误判） | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Steam.list` |
| **`Pixiv.list`** | 11 条 | 包含高防插画 CDN 与 Fanbox | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Pixiv.list` |
| **`PayPal.list`** | 245 条 | 覆盖全球各区收单分站与反欺诈网关 | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/PayPal.list` |

---

### 4. 🛡️ 广告拦截与安全直连专区

| 规则名称 | 建议策略 | 核心价值 | Loon 远程规则订阅链接 |
| :--- | :--- | :--- | :--- |
| **`AdBlock.list`** | `REJECT` | **【强力推荐】全能去广告与反追踪盾（928 条）**：干掉 23 万条臃肿僵尸规则，精准拦截国内 App 开屏广告 SDK、遥测埋点及海外广告联盟 | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/AdBlock.list` |
| **`China.list`** | `国内网站` (DIRECT) | **纯净国内直连库（1713 条）**：已剔除误判的微软与海外 CDN，国内软件秒开不再转圈 | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/China.list` |
| **`ChinaASN.list`** | `国内网站` (DIRECT) | **中国自治系统直连库（1009 条）**：三大运营商及国内云厂商 BGP 自治系统号，零 DNS 负担（带 no-resolve） | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/ChinaASN.list` |
| **`WeChat.list`** | `国内网站` (DIRECT) | 微信专属直连（687 条）：覆盖微信小程序、图文与支付 | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/WeChat.list` |
| **`STUN.list`** | `REJECT` | **WebRTC 专用全局阻断集**：强杀 UDP 3478/5349 及 stun 探测域，防真实 IP 穿透暴露 | `https://raw.githubusercontent.com/J606y/loon-rules/main/rules/STUN.list` |

---

## 安全设计与运维

1. **防 WebRTC 侧漏**：
   所有海外规则文件顶部均前置注入 STUN 阻断：
   ```ini
   AND,((PROTOCOL,UDP),(DEST-PORT,3478)),REJECT
   AND,((PROTOCOL,UDP),(DEST-PORT,5349)),REJECT
   DOMAIN-KEYWORD,stun,REJECT
   ```
2. **全协议放行**：
   目标域名全协议放行走代理节点，支持满血代理加速。
3. **Hermes 自动巡检**：
   每 6 小时在本地服务器自动比对官方上游，有变动自动提交，绝不产生空白或假更新。
