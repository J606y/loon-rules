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

headers = {"User-Agent": "Loon/919 CFNetwork/3860.500.111.2.2 Darwin/25.0.0"}
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

    # 4. 编译全能广告与隐私拦截库 AdBlock.list (涵盖国内开屏 + 海外全量广告联盟)
    print("Building High-Performance Global AdBlock.list...")
    ad_suffixes = set()
    ad_exacts = set()
    
    # MetaCubeX 官方 category-ads-all
    ads_yaml = fetch("https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/classical/category-ads-all.yaml")
    for l in ads_yaml.splitlines():
        l = l.strip()
        if l.startswith("- "):
            val = l[2:].strip().strip("'\"")
            if "," in val:
                k, v = val.split(",", 1)
                k, v = k.strip(), v.strip().lower()
                if k == "DOMAIN-SUFFIX":
                    ad_suffixes.add(v)
                elif k == "DOMAIN":
                    ad_exacts.add(v)

    # 海外顶级广告网络、移动端 SDK 与行为追踪
    foreign_major_ads = [
        # Google / Alphabet
        "2mdn.net", "admob.com", "adsense.com", "adservice.google.com", "adservices.google.com",
        "doubleclick.net", "googleadservices.com", "googleads.g.doubleclick.net", "googlesyndication.com",
        "googletagmanager.com", "googletagservices.com", "pagead2.googlesyndication.com",
        # Facebook / Meta
        "an.facebook.com", "pixel.facebook.com", "connect.facebook.net",
        # Amazon Ad
        "aax-us-east.amazon-adsystem.com", "amazon-adsystem.com", "assoc-amazon.com",
        # Global Ad Networks & Information Feed
        "criteo.com", "criteo.net", "taboola.com", "outbrain.com", "outbrainimg.com",
        "thetradedesk.com", "pubmatic.com", "openx.net", "rubiconproject.com", "magnite.com",
        "casalemedia.com", "sovrn.com", "yieldmo.com", "sharethrough.com", "smartadserver.com",
        "triplelift.com", "indexexchange.com", "adroll.com", "media.net", "zergnet.com",
        "revcontent.com", "mgid.com", "popads.net", "popcash.net", "propellerads.com",
        "exoclick.com", "trafficjunky.com", "juicyads.com", "adxprtz.com", "adtrue.com",
        # Mobile App SDKs
        "unityads.unity3d.com", "applvn.com", "applovin.com",
        "vungle.com", "ironsrc.com", "supersonicads.com", "inmobi.com", "chartboost.com",
        "mintegral.com", "adcolony.com", "liftoff.io", "fyber.com", "tapjoy.com",
        "startapp.com", "startappexchange.com", "flurry.com",
        # Foreign Analytics & Device Fingerprinting
        "appsflyer.com", "adjust.com", "adjust.net.in", "kochava.com", "branch.io",
        "singular.net", "mixpanel.com", "amplitude.com", "heap.io", "segment.io",
        "segment.com", "hotjar.com", "mouseflow.com", "fullstory.com", "smartlook.com",
        "crazyegg.com", "inspectlet.com", "qualaroo.com", "optimizely.com",
        # Streaming Audio/Video Ad Injection
        "adeventtracker.spotify.com", "ads.youtube.com", "innovid.com", "flashtalking.com",
        "spongecell.com", "sizmek.com", "moatads.com", "iasds01.com", "doubleverify.com"
    ]
    ad_suffixes |= set(foreign_major_ads)

    # 国内高频开屏广告 SDK、大数据追踪埋点
    domestic_ads = [
        "umeng.com", "umengcloud.com", "talkingdata.com", "talkingdata.net",
        "growingio.com", "sensorsdata.cn", "jpush.cn", "jiguang.cn",
        "bugly.qq.com", "adashx.m.taobao.com", "mobads.baidu.com",
        "mobads-logs.baidu.com", "pos.baidu.com", "eclick.baidu.com",
        "baidustatic.com", "pangolin-sdk-toutiao.com", "pangolin-sdk-toutiao-b.com",
        "pglstatp-toutiao.com", "ad.weibo.com", "ads.weibo.com", "biz.weibo.com",
        "sax.sina.com.cn", "adx.meituan.com", "adash.m.taobao.com",
        "adash.man.aliyuncs.com", "adash-emas.cn-hangzhou.aliyuncs.com",
        "atanx.com", "tanx.com", "miaozhen.com", "irs01.com", "irs01.net",
        "track.58.com", "cupid.iqiyi.com", "cupid.ptqy.gitv.tv"
    ]
    ad_suffixes |= set(domestic_ads)

    # 后缀剪枝
    pruned_suffixes = set()
    for s in ad_suffixes:
        parts = s.split(".")
        is_redundant = False
        for i in range(1, len(parts)):
            parent = ".".join(parts[i:])
            if parent in ad_suffixes:
                is_redundant = True
                break
        if not is_redundant:
            pruned_suffixes.add(s)

    final_ad_rules = []
    # 关键字
    for kw in ["adservice", "adsystem", "adstrategy", "adserver"]:
        final_ad_rules.append(f"DOMAIN-KEYWORD,{kw},REJECT")
    # 后缀
    for s in sorted(pruned_suffixes):
        final_ad_rules.append(f"DOMAIN-SUFFIX,{s},REJECT")
    # 精确单域
    for e in sorted(ad_exacts):
        # 如果已被后缀覆盖则不加
        parts = e.split(".")
        if not any(".".join(parts[i:]) in pruned_suffixes for i in range(len(parts))):
            final_ad_rules.append(f"DOMAIN,{e},REJECT")

    ad_content = [
        "# ========================================================",
        "# Loon Rule Set: Global AdBlock & Privacy Tracker Shield",
        "# Policy: REJECT (覆盖国内开屏广告 + 全球头部海外广告联盟/SDK)",
        "# Cleaned & Maintained by Hermes Agent",
        "# ========================================================",
    ] + final_ad_rules
    (RULES_DIR / "AdBlock.list").write_text("\n".join(ad_content) + "\n", encoding="utf-8")
    print(f" -> {'Global AdBlock':15}: {len(final_ad_rules):5d} rules")

    # 5. 编译 ChinaASN.list (中国大陆自治系统直连库，零 DNS 负担)
    print("Building ChinaASN.list...")
    asn_raw = fetch("https://rule.kelee.one/Loon/ChinaASN.lsr")
    asn_rules = set()
    for l in asn_raw.splitlines():
        l = l.strip()
        if l and not l.startswith("#"):
            parts = [p.strip() for p in l.split(",")]
            if len(parts) >= 2 and parts[0] == "IP-ASN":
                asn_rules.add(f"IP-ASN,{parts[1]},no-resolve")
    
    asn_sorted = sorted(asn_rules)
    asn_content = [
        "# ========================================================",
        "# Loon Rule Set: China ASN Direct (中国大陆自治系统 BGP 直连)",
        "# 覆盖中国电信、联通、移动、教育网及各大国内云厂商 (带 no-resolve)",
        "# Cleaned & Maintained by Hermes Agent",
        "# ========================================================",
    ] + asn_sorted
    (RULES_DIR / "ChinaASN.list").write_text("\n".join(asn_content) + "\n", encoding="utf-8")
    print(f" -> {'China ASN':15}: {len(asn_sorted):5d} rules")

if __name__ == "__main__":
    build_all()
