#!/usr/bin/env python3
"""Loon 多规则生成与更新器：从 v2fly & MetaCubeX 权威源抓取，注入防 WebRTC 泄露前置规则。"""
import os
import sys
import ssl
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_DIR = ROOT / "rules"
DATA_DIR = ROOT / "data"

SOURCES = {
    "Claude": {
        "v2fly": "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/anthropic",
        "metacubex": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/classical/anthropic.yaml",
        "seed": [
            "DOMAIN-SUFFIX,anthropic.com", "DOMAIN-SUFFIX,clau.de", "DOMAIN-SUFFIX,claude.ai",
            "DOMAIN-SUFFIX,claude.com", "DOMAIN-SUFFIX,claude.dev", "DOMAIN-SUFFIX,claudemcpclient.com",
            "DOMAIN-SUFFIX,claudemcpcontent.com", "DOMAIN-SUFFIX,claudeusercontent.com",
            "DOMAIN,servd-anthropic-website.b-cdn.net"
        ]
    },
    "OpenAI": {
        "v2fly": "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/openai",
        "metacubex": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/classical/openai.yaml",
        "seed": [
            "DOMAIN-SUFFIX,chatgpt.com", "DOMAIN-SUFFIX,oaistatic.com", "DOMAIN-SUFFIX,oaiusercontent.com",
            "DOMAIN-SUFFIX,openai.com", "DOMAIN-SUFFIX,chat.com", "DOMAIN-SUFFIX,sora.com",
            "DOMAIN-SUFFIX,oaistatsig.com", "DOMAIN,openaiassets.blob.core.windows.net",
            "DOMAIN-SUFFIX,ai.com"
        ]
    },
    "Gemini": {
        "v2fly": "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/google-gemini",
        "metacubex": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/classical/google-gemini.yaml",
        "seed": [
            "DOMAIN,aistudio.google.com", "DOMAIN,generativelanguage.googleapis.com",
            "DOMAIN,alkalimakersuite-pa.clients6.google.com", "DOMAIN,makersuite.google.com",
            "DOMAIN,ai.google.dev", "DOMAIN-SUFFIX,gemini.google.com", "DOMAIN-SUFFIX,bard.google.com",
            "DOMAIN-SUFFIX,deepmind.com", "DOMAIN-SUFFIX,deepmind.google", "DOMAIN-SUFFIX,generativeai.google"
        ]
    },
    "Microsoft": {
        "v2fly": "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/microsoft",
        "metacubex": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/classical/microsoft.yaml",
        "seed": [
            "DOMAIN-SUFFIX,microsoft.com", "DOMAIN-SUFFIX,live.com", "DOMAIN-SUFFIX,office.com",
            "DOMAIN-SUFFIX,office365.com", "DOMAIN-SUFFIX,msn.com", "DOMAIN-SUFFIX,bing.com",
            "DOMAIN-SUFFIX,onedrive.com", "DOMAIN-SUFFIX,1drv.ms", "DOMAIN-SUFFIX,azure.com",
            "DOMAIN-SUFFIX,copilot.microsoft.com", "DOMAIN,sydney.bing.com"
        ]
    },
    "Apple": {
        "v2fly": "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/apple",
        "metacubex": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/classical/apple.yaml",
        "seed": [
            "DOMAIN-SUFFIX,apple.com", "DOMAIN-SUFFIX,icloud.com", "DOMAIN-SUFFIX,itunes.com",
            "DOMAIN-SUFFIX,mzstatic.com", "DOMAIN-SUFFIX,cdn-apple.com", "DOMAIN-SUFFIX,me.com"
        ]
    }
}

headers = {"User-Agent": "hermes-loon-rules-builder/1"}
ctx = ssl.create_default_context()

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"Fetch failed for {url}: {e}", file=sys.stderr)
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
        elif line.startswith("regexp:") or line.startswith("^"):
            continue # ignore regex in Loon basic lists
        else:
            # treat as suffix
            val = line.split()[0].strip()
            if "." in val and not val.startswith("@"):
                rules.add(f"DOMAIN-SUFFIX,{val}")
    return rules

def build_all():
    RULES_DIR.mkdir(parents=True, exist_ok=True)
    all_ai_rules = set()

    for name, meta in SOURCES.items():
        print(f"Building {name}...")
        cur_rules = set(meta.get("seed", []))
        
        # v2fly
        v2_text = fetch(meta["v2fly"])
        if v2_text:
            cur_rules |= parse_rules(v2_text)
            
        # metacubex
        mc_text = fetch(meta["metacubex"])
        if mc_text:
            cur_rules |= parse_rules(mc_text)

        # 过滤与排序
        sorted_rules = sorted(cur_rules)
        
        # 组装 Loon 规则文件（前置 WebRTC/STUN 阻断）
        content_lines = [
            "# ========================================================",
            f"# Loon Rule Set: {name}",
            "# Maintained by Hermes Agent from v2fly & MetaCubeX",
            "# ========================================================",
            "# --- WebRTC / STUN Leak Prevention ---",
            "AND,((PROTOCOL,UDP),(DEST-PORT,3478)),REJECT",
            "AND,((PROTOCOL,UDP),(DEST-PORT,5349)),REJECT",
            "DOMAIN-KEYWORD,stun,REJECT",
            "# --- Target Rules (Full TCP/UDP/QUIC Proxy) ---",
        ] + sorted_rules
        
        out_file = RULES_DIR / f"{name}.list"
        out_file.write_text("\n".join(content_lines) + "\n", encoding="utf-8")
        print(f" -> {name}.list generated ({len(sorted_rules)} rules)")

        if name in {"Claude", "OpenAI", "Gemini"}:
            all_ai_rules |= cur_rules

    # 额外生成一个合集：AI.list
    print("Building All-in-One AI.list...")
    # 增加额外的 Perplexity 与 Cursor 种子
    extra_ai_seeds = [
        "DOMAIN-SUFFIX,perplexity.ai", "DOMAIN-SUFFIX,cursor.com", "DOMAIN-SUFFIX,cursor.sh",
        "DOMAIN-SUFFIX,anthropic.com", "DOMAIN-SUFFIX,claude.ai", "DOMAIN-SUFFIX,openai.com",
        "DOMAIN-SUFFIX,chatgpt.com", "DOMAIN-SUFFIX,sora.com"
    ]
    all_ai_rules |= set(extra_ai_seeds)
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
        "# --- AI Proxy Rules ---",
    ] + ai_sorted
    (RULES_DIR / "AI.list").write_text("\n".join(ai_content) + "\n", encoding="utf-8")
    print(f" -> AI.list generated ({len(ai_sorted)} rules)")

if __name__ == "__main__":
    build_all()
