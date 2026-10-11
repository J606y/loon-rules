# Loon 专属高质量分流规则集

自用维护的 Loon 高质量分流规则库。拒绝个人打包二次转储的“两行虚假空壳”，基于 v2fly 社区官方与 MetaCubeX 官方核心数据源交叉对齐，由自建服务器 Hermes Agent 每 6 小时自动巡检更新。

---

## 规则集列表与 Loon 订阅链接

### 1. 🤖 AI 专区（彻底解决风控与漏网）

#### ① AI 全家桶大合集（推荐）
包含 Claude、OpenAI (ChatGPT/Sora)、Google Gemini、Perplexity、Cursor、Copilot 等所有主流 AI 资产。
```ini
https://raw.githubusercontent.com/J606y/loon-rules/main/rules/AI.list, policy=AI, tag=AI, enabled=true
```

#### ② Claude 专用（精确独立分流）
覆盖 Claude 专属认证、所有子站、多模态附件沙箱与专用 CDN。
```ini
https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Claude.list, policy=AI, tag=Claude, enabled=true
```

#### ③ OpenAI 专用（含 chat.com & sora.com）
补全了原版缺失的 `chat.com`、`sora.com`、`oaistatsig.com` 及微软云存储端点。
```ini
https://raw.githubusercontent.com/J606y/loon-rules/main/rules/OpenAI.list, policy=AI, tag=OpenAI, enabled=true
```

#### ④ Google Gemini 专用（含 aistudio 等 49 条完整资产）
补齐了 `aistudio.google.com`、`generativelanguage.googleapis.com` 等全部端点。
```ini
https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Gemini.list, policy=AI, tag=Gemini, enabled=true
```

---

### 2. 🪟 微软与苹果（告别碎片化残缺）

#### ⑤ Microsoft 完整微软系（800+ 条）
彻底修复可莉版“只分流网盘、缺微软主体”的致命伤，覆盖 Windows 更新、Office 365、Azure、Xbox、Bing、Copilot。
```ini
https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Microsoft.list, policy=Microsoft, tag=Microsoft, enabled=true
```

#### ⑥ Apple 苹果全家桶（1900+ 条）
一个完整苹果大库，替代原配置中被强行切碎的 12 个“两行空壳”文件（AppStore/AppleMail/AppleNews 等）。
```ini
https://raw.githubusercontent.com/J606y/loon-rules/main/rules/Apple.list, policy=Apple, tag=Apple, enabled=true
```

---

### 3. 🇨🇳 纯净国内直连专区（告别国内 App 转圈卡死）

#### ⑦ China 国内直连白名单（1700+ 条，纯净版）
基于 v2fly 官方源深度清洗编译。彻底剔除了原版中误把微软更新（`microsoftonline.com`）、JetBrains、以及各大国际 Akamai CDN 强行直连导致网页卡死的毒瘤条目；全面收拢国内大厂、政务、金融、生活服务主域名，秒级直连放行。
```ini
https://raw.githubusercontent.com/J606y/loon-rules/main/rules/China.list, policy=国内网站, tag=China, enabled=true
```

---

## 防侧漏安全设计

所有规则文件顶部均自动注入前置 **WebRTC / STUN 探测拦截**：
```ini
# --- WebRTC / STUN Leak Prevention ---
AND,((PROTOCOL,UDP),(DEST-PORT,3478)),REJECT
AND,((PROTOCOL,UDP),(DEST-PORT,5349)),REJECT
DOMAIN-KEYWORD,stun,REJECT
```
- **阻断 STUN 穿透**：阻断 UDP 3478/5349 及 stun 探测域，防止网页 JS 脚本探测出国内真实公网 IP；
- **全协议代理**：下方的目标业务域名放行全部 TCP 与 UDP/QUIC 流量，由用户的代理节点高速转发。

---

## 自动维护机制
- 服务器 Hermes 守护进程每 6 小时自动比对上游；
- 只有真实出现新域名且通过校验时才增量提交，无变动时完全静默；
- 失败时自动保留现有有效规则，绝不制造空白规则。
