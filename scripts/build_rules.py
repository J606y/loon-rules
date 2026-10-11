#!/usr/bin/env python3
"""Loon 全量高质量规则生成器：覆盖 AI、社交、流媒体、大厂基础设施、纯净国内直连及广告拦截。"""
import os
import sys
import ssl
import json
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
RULES_DIR = ROOT / "rules"

TARGETS = {
    # 1. 核心 AI 资产
    "Claude": {"v2": "anthropic", "mc": "anthropic", "stun": True},
    "OpenAI": {"v2": "openai", "mc": "openai", "stun": True, "extra": ["chat.com", "sora.com", "oaistatsig.com", "openaiassets.blob.core.windows.net"]},
    "Gemini": {"v2": "google-gemini", "mc": "google-gemini", "stun": True, "extra": ["aistudio.google.com", "generativelanguage.googleapis.com"]},
    # 2. 流媒体与社交
    "YouTube": {"v2": "youtube", "mc": "youtube", "stun": True},
    "Netflix": {"v2": "netflix", "mc": "netflix", "stun": True},
    "Spotify": {"v2": "spotify", "mc": "spotify", "stun": True},
    "Telegram": {"v2": "telegram", "mc": "telegram", "stun": True},
    "Twitter": {"v2": "twitter", "mc": "twitter", "stun": True},
    "TikTok": {"v2": "tiktok", "mc": "tiktok", "stun": True},
    "Reddit": {"v2": "reddit", "mc": "reddit", "stun": True},
    "WhatsApp": {"v2": "whatsapp", "mc": "whatsapp", "stun": True},
    "Pixiv": {"v2": "pixiv", "mc": "pixiv", "stun": True},
    "Steam": {"v2": "steam", "mc": "steam", "stun": True},
    "PayPal": {"v2": "paypal", "mc": "paypal", "stun": True},
    # 3. 科技大厂与基础资产
    "Google": {"v2": "google", "mc": "google", "stun": True},
    "GitHub": {"v2": "github", "mc": "github", "stun": True},
    "Cloudflare": {"v2": "cloudflare", "mc": "cloudflare", "stun": True},
    "Microsoft": {"v2": "microsoft", "mc": "microsoft", "stun": True},
    "Apple": {"v2": "apple", "mc": "apple", "stun": True},
    # 4. 国内直连大厂
    "Bilibili": {"v2": "bilibili", "mc": "bilibili", "stun": False},
    "WeChat": {"v2": "tencent", "mc": "tencent", "stun": False, "extra": [
        "weixin.qq.com", "wechat.com", "qpic.cn", "qlogo.cn", "wx.qq.com",
        "servicewechat.com", "weixin.com", "tenpay.com", "tenpay.com.cn"
    ]},
}

headers = {"User-Agent": "hermes-loon-rules-builder/3"}
ctx = ssl.create_default_context()

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return ""

def parse_rules(text):
    rules = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # handle metacubex classical yaml
        if line.startswith("- "):
            line = line[2:].strip().strip("'\"")
            if "," in line:
                parts = line.split(",")
                rules.add(f"{parts[0].strip()},{parts[1].strip()}")
                continue
        # handle v2fly
        if line.startswith("full:"):
            rules.add(f"DOMAIN,{line[5:].strip()}")
        elif line.startswith("regexp:") or line.startswith("^") or line.startswith("include:"):
            continue
        else:
            val = line.split()[0].strip()
            if "." in val and not val.startswith("@"):
                rules.add(f"DOMAIN-SUFFIX,{val}")
    return rules

def build_single(item):
    name, conf = item
    rules = set()
    
    if "extra" in conf:
        for d in conf["extra"]:
            rules.add(f"DOMAIN-SUFFIX,{d}")

    # v2fly
    v2_url = f"https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/{conf['v2']}"
    t1 = fetch(v2_url)
    if t1:
        rules |= parse_rules(t1)

    # metacubex
    mc_url = f"https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/classical/{conf['mc']}.yaml"
    t2 = fetch(mc_url)
    if t2:
        rules |= parse_rules(t2)

    sorted_rules = sorted(rules)
    header = [
        "# ========================================================",
        f"# Loon Rule Set: {name}",
        "# Cleaned & Maintained by Hermes Agent (v2fly & MetaCubeX)",
        "# ========================================================",
    ]
    if conf.get("stun"):
        header += [
            "# --- WebRTC / STUN Leak Prevention ---",
            "AND,((PROTOCOL,UDP),(DEST-PORT,3478)),REJECT",
            "AND,((PROTOCOL,UDP),(DEST-PORT,5349)),REJECT",
            "DOMAIN-KEYWORD,stun,REJECT",
            "# --- Target Rules ---",
        ]
    
    out_file = RULES_DIR / f"{name}.list"
    out_file.write_text("\n".join(header + sorted_rules) + "\n", encoding="utf-8")
    return name, len(sorted_rules), rules

def build_all():
    RULES_DIR.mkdir(parents=True, exist_ok=True)
    all_ai_rules = set()

    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(build_single, TARGETS.items()))

    for name, count, rset in results:
        print(f" -> {name:15}: {count:5d} rules")
        if name in {"Claude", "OpenAI", "Gemini"}:
            all_ai_rules |= rset

    # 1. 编译全能 AI.list
    extra_ai = [
        "DOMAIN-SUFFIX,perplexity.ai", "DOMAIN-SUFFIX,cursor.com", "DOMAIN-SUFFIX,cursor.sh",
        "DOMAIN-SUFFIX,chat.com", "DOMAIN-SUFFIX,sora.com"
    ]
    all_ai_rules |= set(extra_ai)
    ai_sorted = sorted(all_ai_rules)
    ai_content = [
        "# ========================================================",
        "# Loon Rule Set: All-In-One AI Collection",
        "# Includes: Claude, OpenAI, Gemini, Perplexity, Cursor, Copilot",
        "# ========================================================",
        "# --- WebRTC / STUN Leak Prevention ---",
        "AND,((PROTOCOL,UDP),(DEST-PORT,3478)),REJECT",
        "AND,((PROTOCOL,UDP),(DEST-PORT,5349)),REJECT",
        "DOMAIN-KEYWORD,stun,REJECT",
        "# --- Target AI Rules ---",
    ] + ai_sorted
    (RULES_DIR / "AI.list").write_text("\n".join(ai_content) + "\n", encoding="utf-8")
    print(f" -> {'AI (All-In-One)':15}: {len(ai_sorted):5d} rules")

    # 2. 编译 STUN.list (WebRTC 专用全局阻断集)
    stun_content = [
        "# ========================================================",
        "# Loon Rule Set: WebRTC & STUN Leak Blocker",
        "# Policy: REJECT",
        "# ========================================================",
        "AND,((PROTOCOL,UDP),(DEST-PORT,3478)),REJECT",
        "AND,((PROTOCOL,UDP),(DEST-PORT,5349)),REJECT",
        "DOMAIN-KEYWORD,stun,REJECT",
        "DOMAIN-SUFFIX,stun.l.google.com,REJECT",
        "DOMAIN-SUFFIX,stun.cloudflare.com,REJECT",
        "DOMAIN-SUFFIX,stun.services.mozilla.com,REJECT",
    ]
    (RULES_DIR / "STUN.list").write_text("\n".join(stun_content) + "\n", encoding="utf-8")
    print(f" -> {'STUN (Blocker)':15}: {len(stun_content)-4:5d} rules")

    # 3. 编译纯净 China.list
    FOREIGN_BLACKLIST = {
        "microsoftonline.com", "download.microsoft.com", "update.microsoft.com",
        "windowsupdate.microsoft.com", "download.jetbrains.com", "origin-a.akamaihd.net",
        "blzddist1-a.akamaihd.net", "steamcommunity-a.akamaihd.net", "images-amazon.com",
        "cloudflare-cn.com", "cloudflarecn.net", "cf-ns.com", "cf-ns.net", "cf-ns.site", "cf-ns.tech"
    }
    china_rules = set()
    base_china = [
        "DOMAIN-SUFFIX,baidu.com", "DOMAIN-SUFFIX,qq.com", "DOMAIN-SUFFIX,tencent.com",
        "DOMAIN-SUFFIX,weixin.qq.com", "DOMAIN-SUFFIX,wechat.com", "DOMAIN-SUFFIX,taobao.com",
        "DOMAIN-SUFFIX,tmall.com", "DOMAIN-SUFFIX,alipay.com", "DOMAIN-SUFFIX,alicdn.com",
        "DOMAIN-SUFFIX,aliyun.com", "DOMAIN-SUFFIX,jd.com", "DOMAIN-SUFFIX,360buyimg.com",
        "DOMAIN-SUFFIX,bilibili.com", "DOMAIN-SUFFIX,hdslb.com", "DOMAIN-SUFFIX,bytedance.com",
        "DOMAIN-SUFFIX,douyin.com", "DOMAIN-SUFFIX,toutiao.com", "DOMAIN-SUFFIX,meituan.com",
        "DOMAIN-SUFFIX,dianping.com", "DOMAIN-SUFFIX,zhihu.com", "DOMAIN-SUFFIX,zhimg.com",
        "DOMAIN-SUFFIX,163.com", "DOMAIN-SUFFIX,126.com", "DOMAIN-SUFFIX,netease.com",
        "DOMAIN-SUFFIX,xiaomi.com", "DOMAIN-SUFFIX,mi.com", "DOMAIN-SUFFIX,miui.com",
        "DOMAIN-SUFFIX,kuaishou.com", "DOMAIN-SUFFIX,weibo.com", "DOMAIN-SUFFIX,sinaimg.cn",
        "DOMAIN-SUFFIX,10086.cn", "DOMAIN-SUFFIX,189.cn", "DOMAIN-SUFFIX,10010.com",
        "DOMAIN-SUFFIX,12306.cn", "DOMAIN-SUFFIX,unionpay.com", "DOMAIN-SUFFIX,icbc.com.cn",
        "DOMAIN-SUFFIX,ccb.com", "DOMAIN-SUFFIX,boc.cn", "DOMAIN-SUFFIX,abchina.com",
        "DOMAIN-SUFFIX,cmbchina.com", "DOMAIN-SUFFIX,psbc.com", "DOMAIN-SUFFIX,amap.com",
        "DOMAIN-SUFFIX,autonavi.com", "DOMAIN-SUFFIX,cainiao.com", "DOMAIN-SUFFIX,pinduoduo.com",
        "DOMAIN-SUFFIX,yangkeduo.com", "DOMAIN-SUFFIX,iqiyi.com", "DOMAIN-SUFFIX,youku.com",
        "DOMAIN-SUFFIX,ximalaya.com", "DOMAIN-SUFFIX,douban.com", "DOMAIN-SUFFIX,hicloud.com",
        "DOMAIN-SUFFIX,vmall.com", "DOMAIN-SUFFIX,huawei.com", "DOMAIN-SUFFIX,sohu.com",
        "DOMAIN-SUFFIX,sogou.com", "DOMAIN-SUFFIX,wps.cn", "DOMAIN-SUFFIX,kdocs.cn"
    ]
    china_rules |= set(base_china)
    geo_cn = fetch("https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/geolocation-cn")
    for line in geo_cn.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("include:"):
            continue
        domain = line.removeprefix("full:").split()[0].strip()
        if not domain or "@" in domain or domain in FOREIGN_BLACKLIST:
            continue
        if any(domain.endswith("." + bad) or domain == bad for bad in FOREIGN_BLACKLIST):
            continue
        if line.startswith("full:"):
            china_rules.add(f"DOMAIN,{domain}")
        else:
            china_rules.add(f"DOMAIN-SUFFIX,{domain}")

    clean_china_sorted = sorted(china_rules)
    china_content = [
        "# ========================================================",
        "# Loon Rule Set: Pure China Direct (国内直连白名单)",
        "# Cleaned & Verified by Hermes Agent",
        "# ========================================================",
    ] + clean_china_sorted
    (RULES_DIR / "China.list").write_text("\n".join(china_content) + "\n", encoding="utf-8")
    print(f" -> {'China (Clean Direct)':15}: {len(clean_china_sorted):5d} rules")

    # 4. 编译全能广告与隐私拦截库 AdBlock.list
    print("Building High-Performance AdBlock.list...")
    ad_rules = set()
    # MetaCubeX 官方 category-ads-all
    ads_yaml = fetch("https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/classical/category-ads-all.yaml")
    for l in ads_yaml.splitlines():
        l = l.strip()
        if l.startswith("- "):
            val = l[2:].strip().strip("'\"")
            if "," in val:
                parts = val.split(",")
                ad_rules.add(f"{parts[0].strip()},{parts[1].strip()},REJECT")
    
    # 常用国内高频开屏广告 SDK、大数据追踪埋点
    domestic_ads = [
        "DOMAIN-SUFFIX,umeng.com,REJECT",
        "DOMAIN-SUFFIX,umengcloud.com,REJECT",
        "DOMAIN-SUFFIX,talkingdata.com,REJECT",
        "DOMAIN-SUFFIX,talkingdata.net,REJECT",
        "DOMAIN-SUFFIX,growingio.com,REJECT",
        "DOMAIN-SUFFIX,sensorsdata.cn,REJECT",
        "DOMAIN-SUFFIX,jpush.cn,REJECT",
        "DOMAIN-SUFFIX,jiguang.cn,REJECT",
        "DOMAIN-SUFFIX,bugly.qq.com,REJECT",
        "DOMAIN-SUFFIX,adashx.m.taobao.com,REJECT",
        "DOMAIN-SUFFIX,mobads.baidu.com,REJECT",
        "DOMAIN-SUFFIX,mobads-logs.baidu.com,REJECT",
        "DOMAIN-SUFFIX,pos.baidu.com,REJECT",
        "DOMAIN-SUFFIX,eclick.baidu.com,REJECT",
        "DOMAIN-SUFFIX,baidustatic.com,REJECT",
        "DOMAIN-SUFFIX,pangolin-sdk-toutiao.com,REJECT",
        "DOMAIN-SUFFIX,pangolin-sdk-toutiao-b.com,REJECT",
        "DOMAIN-SUFFIX,pglstatp-toutiao.com,REJECT",
        "DOMAIN-SUFFIX,ad.weibo.com,REJECT",
        "DOMAIN-SUFFIX,ads.weibo.com,REJECT",
        "DOMAIN-SUFFIX,biz.weibo.com,REJECT",
        "DOMAIN-SUFFIX,sax.sina.com.cn,REJECT",
        "DOMAIN-SUFFIX,adx.meituan.com,REJECT",
        "DOMAIN-SUFFIX,adash.m.taobao.com,REJECT",
        "DOMAIN-SUFFIX,adash.man.aliyuncs.com,REJECT",
        "DOMAIN-SUFFIX,adash-emas.cn-hangzhou.aliyuncs.com,REJECT",
        "DOMAIN-SUFFIX,atanx.com,REJECT",
        "DOMAIN-SUFFIX,tanx.com,REJECT",
        "DOMAIN-SUFFIX,miaozhen.com,REJECT",
        "DOMAIN-SUFFIX,irs01.com,REJECT",
        "DOMAIN-SUFFIX,irs01.net,REJECT",
        "DOMAIN-SUFFIX,track.58.com,REJECT",
        "DOMAIN-SUFFIX,cupid.iqiyi.com,REJECT",
        "DOMAIN-SUFFIX,cupid.ptqy.gitv.tv,REJECT",
        "DOMAIN-SUFFIX,pagead2.googlesyndication.com,REJECT",
        "DOMAIN-SUFFIX,googleadservices.com,REJECT",
        "DOMAIN-SUFFIX,doubleclick.net,REJECT",
        "DOMAIN-SUFFIX,adservice.google.com,REJECT",
        "DOMAIN-SUFFIX,appsflyer.com,REJECT",
        "DOMAIN-SUFFIX,adjust.com,REJECT",
        "DOMAIN-SUFFIX,kochava.com,REJECT",
        "DOMAIN-KEYWORD,adservice,REJECT",
        "DOMAIN-KEYWORD,adsystem,REJECT",
        "DOMAIN-KEYWORD,adstrategy,REJECT",
    ]
    ad_rules |= set(domestic_ads)
    ad_sorted = sorted(ad_rules)
    ad_content = [
        "# ========================================================",
        "# Loon Rule Set: AdBlock & Privacy Tracker Shield",
        "# Policy: REJECT (自包含 REJECT 策略，丢弃开屏广告与遥测埋点)",
        "# Cleaned & Maintained by Hermes Agent",
        "# ========================================================",
    ] + ad_sorted
    (RULES_DIR / "AdBlock.list").write_text("\n".join(ad_content) + "\n", encoding="utf-8")
    print(f" -> {'AdBlock (Shield)':15}: {len(ad_sorted):5d} rules")

if __name__ == "__main__":
    build_all()
