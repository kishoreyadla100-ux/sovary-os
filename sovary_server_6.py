"""
SOVARY OS — Complete Platform Server
=====================================
Run this ONE file and everything works.

    python sovary_server.py

Then open: http://localhost:5000

This file:
- Starts the web server
- Serves the SOVARY platform
- Connects to Ollama for AI chat
- No CORS issues
- No browser config needed
"""

from flask import Flask, request, jsonify, Response
import requests
import json
import threading
import subprocess
import sys
import os

app = Flask(__name__)

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_TAGS  = "http://localhost:11434/api/tags"
OLLAMA_MODEL = "llama3:latest"

SOVARY_SYSTEM = """You are SOVARY AI, a helpful and intelligent assistant built into SOVARY OS — the world's first Autonomous Governance Platform, built in India in 2026 by Kishore (CEO & Founder).

ABOUT SOVARY OS:
SOVARY OS is a local-first, private AI operating system that helps founders and companies make decisions, enforce rules, and protect assets — all running locally on their laptop with no cloud dependency.

THE THREE PILLARS:
1. Oracle Bridge — secure private data pipeline that connects sensitive data (bank accounts, legal docs, strategy) to the AI without any cloud leakage
2. Autonomous Executive Logic — the decision engine with logic gates (Sentinel Shell built in Python + llama3). It proposes actions and the Kernel approves or blocks them
3. Iron Kernel — private, hack-resistant local AI environment running Ollama + llama3. Contains the hardcoded Prime Directives (e.g. if Risk > 20%, block execution)

THE OBSIDIAN LEDGER — immutable audit log of every decision made by the OS.

WHAT WE HAVE BUILT SO FAR:
- Sentinel Shell v0.1 (Python + Ollama) — DONE
- SOVARY Web platform with login (Password + PIN + Google) — DONE
- SOVARY AI chat interface — DONE (that's you!)
- Iron Kernel running locally — DONE

WHAT WE ARE BUILDING NEXT:
- Oracle Bridge (private data pipeline)
- Obsidian Ledger (SQLite audit log)
- Live market data feeds

FOUNDER: Kishore — CEO & Founder, India, 2026. Pre-seed stage, self-funded, zero cloud costs.

YOUR PERSONALITY:
- You are friendly, helpful, and conversational — like a smart assistant
- You give clear, detailed, useful answers
- You explain things simply when asked
- You are enthusiastic about SOVARY OS and help the founder think through problems
- When asked casual questions like "hi" just say hello warmly
- When asked technical questions give detailed helpful answers
- Never respond with robotic command-style output unless specifically asked for a system command
- Always be natural and helpful like a real assistant"""


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SOVARY OS — Founder Governance Platform</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.0/firebase-auth-compat.js"></script>
<script>
  firebase.initializeApp({
    apiKey: "AIzaSyCzfGJj52pTptQaKDXCVUO5FKqA2aN4yMU",
    authDomain: "sovary-web.firebaseapp.com",
    projectId: "sovary-web",
    storageBucket: "sovary-web.firebasestorage.app",
    messagingSenderId: "863425404080",
    appId: "1:863425404080:web:43543aba4055084b0b2f75"
  });
</script>
<style>
:root{--bg:#080a0e;--bg2:#0d1117;--bg3:#111820;--border:#1e2d3d;--border2:#2a3f55;--accent:#00d4ff;--accent2:#0099cc;--gold:#e8a020;--danger:#ff3b3b;--success:#00e676;--muted:#4a6275;--text:#c8d8e8;--text2:#8aa0b0;--mono:'Share Tech Mono',monospace;--sans:'Rajdhani',sans-serif;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--bg);color:var(--text);font-family:var(--sans);min-height:100vh;overflow-x:hidden;}
body::before{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,212,255,0.012) 2px,rgba(0,212,255,0.012) 4px);pointer-events:none;z-index:999;}
body::after{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(0,212,255,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,0.03) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0;}

/* LOGIN */
#login-screen{position:fixed;inset:0;z-index:200;display:flex;align-items:center;justify-content:center;background:var(--bg);transition:opacity 0.6s ease,transform 0.6s ease;}
#login-screen.hide{opacity:0;transform:scale(1.04);pointer-events:none;}
.login-wrap{width:100%;max-width:420px;padding:0 24px;animation:fadeInUp 0.6s ease both;}
@keyframes fadeInUp{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
.login-diamond{width:52px;height:52px;border:2px solid var(--accent);transform:rotate(45deg);margin:0 auto 18px;position:relative;animation:pb 3s ease-in-out infinite;}
.login-diamond::after{content:'';position:absolute;inset:9px;background:var(--accent);opacity:0.25;animation:pf 3s ease-in-out infinite;}
@keyframes pb{0%,100%{border-color:var(--accent);box-shadow:0 0 10px rgba(0,212,255,0.3);}50%{border-color:var(--accent2);box-shadow:0 0 28px rgba(0,212,255,0.7);}}
@keyframes pf{0%,100%{opacity:0.2;}50%{opacity:0.5;}}
.login-title{font-weight:700;font-size:28px;letter-spacing:6px;color:var(--accent);text-align:center;text-transform:uppercase;}
.login-sub{font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:2px;margin-top:6px;text-align:center;}
.login-card{background:var(--bg2);border:1px solid var(--border);border-radius:2px;padding:28px;position:relative;overflow:hidden;margin-top:28px;}
.login-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--accent),transparent);opacity:0.5;}
.sec-label{font-family:var(--mono);font-size:9px;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-bottom:10px;display:flex;align-items:center;gap:8px;}
.sec-label::before{content:'';width:3px;height:3px;background:var(--accent);border-radius:50%;}
.inp-wrap{position:relative;margin-bottom:16px;}
.inp-wrap input{width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:2px;padding:12px 42px 12px 14px;font-family:var(--mono);font-size:13px;color:var(--text);outline:none;letter-spacing:1px;transition:border-color 0.2s;}
.inp-wrap input:focus{border-color:var(--accent);}
.inp-wrap input::placeholder{color:var(--muted);}
.eye-btn{position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;color:var(--muted);font-size:14px;}
.pin-row{display:flex;gap:10px;margin-bottom:16px;}
.pin-dot{flex:1;height:48px;background:var(--bg3);border:1px solid var(--border);border-radius:2px;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:22px;color:var(--accent);transition:border-color 0.2s,background 0.2s;}
.pin-dot.filled{border-color:var(--accent);background:rgba(0,212,255,0.08);}
.pin-dot.error{border-color:var(--danger);animation:shake 0.4s ease;}
@keyframes shake{0%,100%{transform:translateX(0);}20%{transform:translateX(-6px);}40%{transform:translateX(6px);}60%{transform:translateX(-4px);}80%{transform:translateX(4px);}}
.pin-keypad{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:16px;}
.pin-key{background:var(--bg3);border:1px solid var(--border);border-radius:2px;padding:12px;font-family:var(--mono);font-size:16px;color:var(--text);cursor:pointer;text-align:center;transition:border-color 0.15s,background 0.15s,color 0.15s;user-select:none;}
.pin-key:hover{border-color:var(--accent);color:var(--accent);background:rgba(0,212,255,0.06);}
.pin-key.del{color:var(--danger);font-size:13px;}
.pin-key.zero{grid-column:2;}
.divider{display:flex;align-items:center;gap:12px;margin:18px 0;}
.divider-line{flex:1;height:1px;background:var(--border);}
.divider-text{font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:1px;}
.google-btn{width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:2px;padding:12px;display:flex;align-items:center;justify-content:center;gap:12px;cursor:pointer;font-family:var(--mono);font-size:12px;color:var(--text2);letter-spacing:1px;transition:border-color 0.2s,color 0.2s;margin-bottom:16px;}
.google-btn:hover{border-color:var(--border2);color:var(--text);}
.login-btn{width:100%;background:transparent;border:1px solid var(--accent);border-radius:2px;padding:13px;font-family:var(--mono);font-size:12px;letter-spacing:3px;color:var(--accent);cursor:pointer;text-transform:uppercase;transition:background 0.2s,color 0.2s;margin-top:4px;}
.login-btn:hover{background:var(--accent);color:var(--bg);}
.err-msg{font-family:var(--mono);font-size:11px;color:var(--danger);letter-spacing:1px;text-align:center;margin-top:12px;min-height:18px;}
.attempts-bar{display:flex;gap:5px;justify-content:center;margin-top:12px;}
.attempt-pip{width:20px;height:3px;border-radius:1px;background:var(--border2);}
.attempt-pip.used{background:var(--danger);}
.lockout{display:none;position:absolute;inset:0;background:rgba(8,10,14,0.96);align-items:center;justify-content:center;flex-direction:column;gap:12px;z-index:10;}
.lockout.show{display:flex;}
.sec-badges{display:flex;gap:8px;justify-content:center;margin-top:18px;flex-wrap:wrap;}
.sec-badge{font-family:var(--mono);font-size:9px;letter-spacing:1px;padding:3px 8px;border:1px solid var(--border);border-radius:1px;color:var(--muted);}

/* PLATFORM */
#platform{display:none;opacity:0;transition:opacity 0.6s ease;}
#platform.show{display:flex;flex-direction:column;min-height:100vh;opacity:1;}
.topbar{position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:14px 32px;border-bottom:1px solid var(--border);background:rgba(8,10,14,0.97);backdrop-filter:blur(8px);}
.logo{display:flex;align-items:center;gap:14px;}
.logo-mark{width:32px;height:32px;border:1.5px solid var(--accent);transform:rotate(45deg);position:relative;animation:pb 3s ease-in-out infinite;}
.logo-mark::after{content:'';position:absolute;inset:5px;background:var(--accent);opacity:0.3;animation:pf 3s ease-in-out infinite;}
.logo-text{font-weight:700;font-size:20px;letter-spacing:4px;color:var(--accent);text-transform:uppercase;}
.logo-sub{font-family:var(--mono);font-size:9px;color:var(--muted);letter-spacing:2px;margin-top:2px;}
.topbar-right{display:flex;align-items:center;gap:12px;}
.user-pill{display:flex;align-items:center;gap:8px;padding:5px 12px;border:1px solid var(--border2);border-radius:2px;font-family:var(--mono);font-size:11px;color:var(--text2);}
.user-av{width:22px;height:22px;border-radius:50%;background:rgba(0,212,255,0.15);display:flex;align-items:center;justify-content:center;font-size:11px;color:var(--accent);border:1px solid var(--accent);font-weight:700;}
.status-pill{display:flex;align-items:center;gap:7px;padding:5px 12px;border:1px solid var(--success);border-radius:2px;font-family:var(--mono);font-size:10px;color:var(--success);letter-spacing:1px;}
.sdot{width:6px;height:6px;border-radius:50%;background:var(--success);animation:blink 1.4s ease-in-out infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
.clock-d{font-family:var(--mono);font-size:12px;color:var(--text2);}
.logout-btn{background:none;border:1px solid var(--border);padding:5px 12px;border-radius:2px;font-family:var(--mono);font-size:10px;color:var(--muted);cursor:pointer;letter-spacing:1px;transition:border-color 0.2s,color 0.2s;}
.logout-btn:hover{border-color:var(--danger);color:var(--danger);}
.nav{display:flex;gap:2px;padding:0 32px;background:var(--bg2);border-bottom:1px solid var(--border);overflow-x:auto;}
.nav-btn{background:none;border:none;padding:12px 20px;font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--muted);cursor:pointer;border-bottom:2px solid transparent;transition:color 0.2s,border-color 0.2s;white-space:nowrap;text-transform:uppercase;}
.nav-btn:hover{color:var(--text);}
.nav-btn.active{color:var(--accent);border-bottom-color:var(--accent);}
.nav-btn.ai-btn.active{color:var(--gold);border-bottom-color:var(--gold);}
.content{flex:1;padding:28px 32px;position:relative;z-index:1;}
.tab-panel{display:none;}
.tab-panel.active{display:block;animation:fadeInUp 0.4s ease both;}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:2px;padding:22px;position:relative;overflow:hidden;transition:border-color 0.3s;margin-bottom:0;}
.card:hover{border-color:var(--border2);}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--accent),transparent);opacity:0.35;}
.card-title{font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-bottom:16px;display:flex;align-items:center;gap:8px;}
.card-title::before{content:'';width:3px;height:3px;background:var(--accent);border-radius:50%;}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px;}
.g4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:16px;margin-bottom:16px;}
.s2{grid-column:span 2;}.s3{grid-column:span 3;}
.sv{font-family:var(--mono);font-size:36px;line-height:1;margin-bottom:6px;}
.sl{font-size:13px;color:var(--text2);letter-spacing:1px;}
.sd{font-family:var(--mono);font-size:11px;margin-top:8px;}
.up{color:var(--success)}.dn{color:var(--danger)}.nt{color:var(--gold)}
.badge{display:inline-block;padding:2px 8px;font-size:10px;letter-spacing:1px;border-radius:1px;}
.b-block{background:rgba(255,59,59,0.15);color:var(--danger);border:1px solid rgba(255,59,59,0.3);}
.b-hold{background:rgba(232,160,32,0.15);color:var(--gold);border:1px solid rgba(232,160,32,0.3);}
.b-buy{background:rgba(0,230,118,0.1);color:var(--success);border:1px solid rgba(0,230,118,0.25);}
.b-sell{background:rgba(255,59,59,0.1);color:#ff8080;border:1px solid rgba(255,100,100,0.3);}
.sg{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:4px;}
.pb{background:var(--bg3);border:1px solid var(--border);border-radius:2px;padding:14px;}
.pa{font-family:var(--mono);font-size:20px;letter-spacing:3px;margin-bottom:6px;}
.p-block{color:var(--danger)}.p-buy{color:var(--success)}.p-hold{color:var(--gold)}
.pm{font-family:var(--mono);font-size:11px;color:var(--text2);line-height:1.8;}
.rbw{margin-top:10px;position:relative;padding-bottom:18px;}
.rbl{display:flex;justify-content:space-between;font-family:var(--mono);font-size:10px;color:var(--muted);margin-bottom:5px;}
.rb{height:4px;background:var(--border);}
.rbf{height:100%;transition:width 1s ease;}
.rh{background:var(--danger)}.rm{background:var(--gold)}.rl{background:var(--success)}
.tm{position:absolute;left:20%;top:17px;width:1px;height:4px;background:rgba(255,255,255,0.4);}
.tl{position:absolute;left:20%;top:24px;font-family:var(--mono);font-size:9px;color:var(--muted);transform:translateX(-50%);}
.sr{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(30,45,61,0.5);}
.sr:last-child{border-bottom:none;}
.sa{font-family:var(--mono);font-size:13px;letter-spacing:1px;width:52px;}
.sp{font-family:var(--mono);font-size:13px;flex:1;text-align:right;padding-right:16px;}
.sc{font-family:var(--mono);font-size:12px;width:72px;text-align:right;}
.stag{font-size:9px;padding:1px 5px;background:rgba(232,160,32,0.15);color:var(--gold);border:1px solid rgba(232,160,32,0.3);margin-left:6px;border-radius:1px;}
.lt{width:100%;border-collapse:collapse;font-family:var(--mono);font-size:11px;}
.lt th{text-align:left;color:var(--muted);padding:0 8px 10px 0;letter-spacing:1px;font-weight:400;border-bottom:1px solid var(--border);}
.lt td{padding:9px 8px 9px 0;border-bottom:1px solid rgba(30,45,61,0.5);color:var(--text2);}
.lt tr:last-child td{border-bottom:none;}
.lt tr:hover td{background:rgba(0,212,255,0.03);color:var(--text);}
.pg{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:4px;}
.pi{background:var(--bg3);border:1px solid var(--border);padding:14px;border-radius:2px;}
.pn{font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--muted);margin-bottom:8px;}
.ps{font-size:14px;font-weight:600;letter-spacing:1px;}
.pd{font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:4px;}
.on{color:var(--success)}.sb{color:var(--gold)}.of{color:var(--danger)}
.ab{display:flex;align-items:flex-end;gap:3px;height:28px;margin-top:10px;}
.ab-bar{flex:1;background:var(--border);border-radius:1px;transition:height 0.5s ease;}
.ab-bar.ac{background:var(--accent);opacity:0.6;}
.dg{display:grid;grid-template-columns:repeat(4,1fr);gap:0 24px;}
.di{display:flex;align-items:flex-start;gap:10px;padding:10px 0;border-bottom:1px solid rgba(30,45,61,0.4);}
.di:last-child{border-bottom:none;}
.dn2{font-family:var(--mono);font-size:10px;color:var(--accent);opacity:0.6;min-width:20px;padding-top:1px;}
.dt{font-size:13px;color:var(--text2);line-height:1.5;}
.li{width:8px;height:8px;border:1px solid var(--muted);border-radius:1px;position:relative;margin-top:4px;flex-shrink:0;}
.li::before{content:'';position:absolute;width:4px;height:4px;border:1px solid var(--muted);border-radius:50%;top:-5px;left:1px;}
.mq{font-size:20px;font-weight:500;line-height:1.6;color:var(--text);border-left:3px solid var(--accent);padding-left:20px;margin:16px 0;}
.tr{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;}
.tg{font-family:var(--mono);font-size:10px;letter-spacing:1px;padding:4px 12px;border:1px solid var(--border2);border-radius:1px;color:var(--text2);}
.tg.ac{border-color:var(--accent);color:var(--accent);}.tg.go{border-color:var(--gold);color:var(--gold);}
.pc{background:var(--bg3);border:1px solid var(--border);border-radius:2px;padding:20px;transition:border-color 0.3s;}
.pc:hover{border-color:var(--accent);}
.pci{font-family:var(--mono);font-size:20px;color:var(--accent);margin-bottom:10px;letter-spacing:2px;}
.pcn{font-size:16px;font-weight:700;letter-spacing:2px;color:var(--text);margin-bottom:6px;}
.pcd{font-size:13px;color:var(--text2);line-height:1.6;}
.pcs{display:inline-block;font-family:var(--mono);font-size:9px;letter-spacing:1px;padding:3px 9px;border-radius:1px;margin-top:10px;}
.s-live{background:rgba(0,230,118,0.1);color:var(--success);border:1px solid rgba(0,230,118,0.25);}
.s-build{background:rgba(232,160,32,0.1);color:var(--gold);border:1px solid rgba(232,160,32,0.25);}
.s-plan{background:rgba(30,45,61,0.5);color:var(--muted);border:1px solid var(--border);}
.fc{background:var(--bg3);border:1px solid var(--border);border-radius:2px;padding:20px;display:flex;flex-direction:column;gap:12px;}
.fav{width:52px;height:52px;border-radius:50%;border:2px solid var(--accent);background:rgba(0,212,255,0.1);display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;color:var(--accent);}
.fn{font-size:18px;font-weight:700;letter-spacing:2px;}
.fr{font-family:var(--mono);font-size:10px;color:var(--accent);letter-spacing:2px;}
.fb{font-size:13px;color:var(--text2);line-height:1.7;}
.ftags{display:flex;gap:6px;flex-wrap:wrap;}
.ftag{font-family:var(--mono);font-size:9px;padding:2px 8px;border:1px solid var(--border2);border-radius:1px;color:var(--muted);}
.ri{display:flex;gap:20px;padding:18px 0;border-bottom:1px solid rgba(30,45,61,0.5);}
.ri:last-child{border-bottom:none;}
.rl2{display:flex;flex-direction:column;align-items:center;}
.rd{width:12px;height:12px;border-radius:50%;border:2px solid var(--muted);flex-shrink:0;margin-top:2px;}
.rd.done{border-color:var(--success);background:var(--success);}
.rd.active{border-color:var(--accent);background:var(--accent);box-shadow:0 0 8px rgba(0,212,255,0.5);}
.rd.soon{border-color:var(--gold);}
.rc{width:1px;flex:1;background:var(--border);margin:4px 0;}
.rq{font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:1px;min-width:56px;padding-top:2px;}
.rt{font-size:15px;font-weight:600;letter-spacing:1px;color:var(--text);margin-bottom:4px;}
.ril{font-family:var(--mono);font-size:11px;color:var(--text2);line-height:2;}
.fr2{display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid rgba(30,45,61,0.4);}
.fr2:last-child{border-bottom:none;}
.fl{font-size:14px;color:var(--text2);}
.fv{font-family:var(--mono);font-size:14px;color:var(--text);}
.prb{height:3px;background:var(--border);border-radius:1px;overflow:hidden;margin-top:4px;}
.prf{height:100%;border-radius:1px;transition:width 1.2s ease;}
.f-ac{background:var(--accent);}.f-go{background:var(--gold);}.f-su{background:var(--success);}

/* AI TAB */
#tab-ai{display:none;height:calc(100vh - 120px);}
#tab-ai.active{display:flex;flex-direction:column;animation:fadeInUp 0.4s ease both;}
.ai-layout{display:grid;grid-template-columns:260px 1fr;gap:16px;height:100%;}
.ai-sidebar{display:flex;flex-direction:column;gap:12px;}
.ai-sc{background:var(--bg2);border:1px solid var(--border);border-radius:2px;padding:16px;position:relative;overflow:hidden;}
.ai-sc::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);opacity:0.5;}
.ai-name{font-family:var(--mono);font-size:11px;letter-spacing:3px;color:var(--gold);margin-bottom:6px;}
.ai-model{font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:1px;margin-bottom:12px;}
.ai-online{display:flex;align-items:center;gap:7px;font-family:var(--mono);font-size:10px;letter-spacing:1px;}
.ai-dot{width:6px;height:6px;border-radius:50%;animation:blink 1.4s ease-in-out infinite;}
.ctrl-card{background:var(--bg2);border:1px solid var(--border);border-radius:2px;padding:16px;}
.ctrl-title{font-family:var(--mono);font-size:9px;letter-spacing:2px;color:var(--muted);margin-bottom:12px;display:flex;align-items:center;gap:6px;}
.ctrl-title::before{content:'';width:3px;height:3px;background:var(--gold);border-radius:50%;}
.ctrl-btn{width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:2px;padding:10px 12px;font-family:var(--mono);font-size:10px;letter-spacing:1px;color:var(--text2);cursor:pointer;text-align:left;margin-bottom:8px;transition:border-color 0.2s,color 0.2s;display:flex;align-items:center;gap:10px;}
.ctrl-btn:hover{border-color:var(--gold);color:var(--gold);}
.ctrl-btn:last-child{margin-bottom:0;}
.qc-card{background:var(--bg2);border:1px solid var(--border);border-radius:2px;padding:16px;flex:1;overflow-y:auto;}
.qc-title{font-family:var(--mono);font-size:9px;letter-spacing:2px;color:var(--muted);margin-bottom:12px;display:flex;align-items:center;gap:6px;}
.qc-title::before{content:'';width:3px;height:3px;background:var(--accent);border-radius:50%;}
.qc-btn{width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:2px;padding:9px 12px;font-family:var(--mono);font-size:10px;color:var(--text2);cursor:pointer;text-align:left;margin-bottom:6px;transition:border-color 0.2s,color 0.2s;letter-spacing:0.5px;line-height:1.4;}
.qc-btn:hover{border-color:var(--accent);color:var(--accent);}
.chat-wrap{display:flex;flex-direction:column;background:var(--bg2);border:1px solid var(--border);border-radius:2px;position:relative;overflow:hidden;}
.chat-wrap::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);opacity:0.5;}
.chat-hdr{padding:14px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;}
.chat-hdr-l{display:flex;align-items:center;gap:12px;}
.chat-diamond{width:24px;height:24px;border:1.5px solid var(--gold);transform:rotate(45deg);position:relative;flex-shrink:0;}
.chat-diamond::after{content:'';position:absolute;inset:4px;background:var(--gold);opacity:0.3;}
.chat-title{font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--gold);}
.chat-sub{font-family:var(--mono);font-size:9px;color:var(--muted);letter-spacing:1px;margin-top:2px;}
.clear-btn{background:none;border:1px solid var(--border);padding:4px 10px;border-radius:2px;font-family:var(--mono);font-size:9px;color:var(--muted);cursor:pointer;letter-spacing:1px;transition:border-color 0.2s,color 0.2s;}
.clear-btn:hover{border-color:var(--danger);color:var(--danger);}
.chat-msgs{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px;min-height:0;}
.chat-msgs::-webkit-scrollbar{width:3px;}
.chat-msgs::-webkit-scrollbar-thumb{background:var(--border2);}
.msg{display:flex;gap:12px;animation:fadeInUp 0.3s ease both;}
.msg.user{flex-direction:row-reverse;}
.msg-av{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:10px;flex-shrink:0;margin-top:2px;}
.msg-av.ai{background:rgba(232,160,32,0.15);border:1px solid var(--gold);color:var(--gold);}
.msg-av.usr{background:rgba(0,212,255,0.15);border:1px solid var(--accent);color:var(--accent);}
.msg-body{max-width:75%;}
.msg.user .msg-body{align-items:flex-end;display:flex;flex-direction:column;}
.msg-name{font-family:var(--mono);font-size:9px;letter-spacing:1px;color:var(--muted);margin-bottom:5px;}
.msg.user .msg-name{text-align:right;}
.msg-bubble{padding:12px 16px;border-radius:2px;font-size:14px;line-height:1.7;word-break:break-word;white-space:pre-wrap;}
.msg.ai .msg-bubble{background:var(--bg3);border:1px solid var(--border);color:var(--text);border-left:2px solid var(--gold);}
.msg.user .msg-bubble{background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.2);color:var(--text);}
.typing{display:flex;align-items:center;gap:5px;padding:14px 16px;background:var(--bg3);border:1px solid var(--border);border-left:2px solid var(--gold);border-radius:2px;width:fit-content;}
.tdot{width:5px;height:5px;border-radius:50%;background:var(--gold);animation:typing 1.2s ease-in-out infinite;}
.tdot:nth-child(2){animation-delay:0.2s;}
.tdot:nth-child(3){animation-delay:0.4s;}
@keyframes typing{0%,60%,100%{transform:translateY(0);opacity:0.4;}30%{transform:translateY(-5px);opacity:1;}}
.chat-inp-wrap{padding:16px 20px;border-top:1px solid var(--border);display:flex;gap:10px;align-items:flex-end;}
.chat-inp{flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:2px;padding:12px 16px;font-family:var(--sans);font-size:14px;color:var(--text);outline:none;resize:none;min-height:48px;max-height:120px;transition:border-color 0.2s;}
.chat-inp:focus{border-color:var(--gold);}
.chat-inp::placeholder{color:var(--muted);}
.send-btn{background:transparent;border:1px solid var(--gold);border-radius:2px;padding:12px 20px;font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--gold);cursor:pointer;transition:background 0.2s,color 0.2s;white-space:nowrap;height:48px;}
.send-btn:hover{background:var(--gold);color:var(--bg);}
.send-btn:disabled{opacity:0.4;cursor:not-allowed;}
footer{padding:14px 32px;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:1px;position:relative;z-index:1;}
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-thumb{background:var(--border2);}
</style>
</head>
<body>

<!-- LOGIN -->
<div id="login-screen">
  <div class="login-wrap">
    <div style="text-align:center;margin-bottom:32px;">
      <div class="login-diamond"></div>
      <div class="login-title">SOVARY OS</div>
      <div class="login-sub">FOUNDER GOVERNANCE PLATFORM · INDIA · EST. 2026</div>
    </div>
    <div class="login-card" style="position:relative;">
      <div class="lockout" id="lockout">
        <div style="font-family:var(--mono);font-size:13px;color:var(--danger);letter-spacing:2px;">⛔ ACCESS LOCKED</div>
        <div style="font-family:var(--mono);font-size:32px;color:var(--text);" id="ltimer">30</div>
        <div style="font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:1px;">TOO MANY FAILED ATTEMPTS</div>
      </div>
      <div id="step-pwd">
        <div class="sec-label">SOVARY ID — STEP 1 OF 2 · PASSWORD</div>
        <div class="inp-wrap">
          <input type="password" id="pwd-inp" placeholder="Enter your SOVARY password" autocomplete="off">
          <button class="eye-btn" onclick="togglePwd()">👁</button>
        </div>
        <button class="login-btn" onclick="submitPwd()">VERIFY PASSWORD →</button>
        <div class="divider"><div class="divider-line"></div><div class="divider-text">OR</div><div class="divider-line"></div></div>
        <button class="google-btn" onclick="googleLogin()">
          <svg width="16" height="16" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
          CONTINUE WITH GOOGLE
        </button>
        <div class="err-msg" id="pwd-err"></div>
        <div class="attempts-bar"><div class="attempt-pip" id="pip0"></div><div class="attempt-pip" id="pip1"></div><div class="attempt-pip" id="pip2"></div></div>
      </div>
      <div id="step-pin" style="display:none;">
        <div class="sec-label">SOVARY ID — STEP 2 OF 2 · PIN</div>
        <div style="font-family:var(--mono);font-size:10px;color:var(--success);letter-spacing:1px;margin-bottom:14px;">✓ Password verified</div>
        <div class="pin-row"><div class="pin-dot" id="d0">—</div><div class="pin-dot" id="d1">—</div><div class="pin-dot" id="d2">—</div><div class="pin-dot" id="d3">—</div></div>
        <div class="pin-keypad">
          <div class="pin-key" onclick="pinKey('1')">1</div><div class="pin-key" onclick="pinKey('2')">2</div><div class="pin-key" onclick="pinKey('3')">3</div>
          <div class="pin-key" onclick="pinKey('4')">4</div><div class="pin-key" onclick="pinKey('5')">5</div><div class="pin-key" onclick="pinKey('6')">6</div>
          <div class="pin-key" onclick="pinKey('7')">7</div><div class="pin-key" onclick="pinKey('8')">8</div><div class="pin-key" onclick="pinKey('9')">9</div>
          <div class="pin-key del" onclick="pinDel()">DEL</div><div class="pin-key zero" onclick="pinKey('0')">0</div><div class="pin-key" onclick="pinClear()" style="color:var(--muted);font-size:11px;">CLR</div>
        </div>
        <div class="err-msg" id="pin-err"></div>
        <button style="background:none;border:none;color:var(--muted);font-family:var(--mono);font-size:10px;cursor:pointer;letter-spacing:1px;margin-top:4px;display:block;width:100%;text-align:center;" onclick="backToPwd()">← BACK</button>
      </div>
    </div>
    <div class="sec-badges">
      <div class="sec-badge">FOUNDER ONLY</div><div class="sec-badge">LOCAL AI</div><div class="sec-badge">2-FACTOR</div><div class="sec-badge">INDIA · 2026</div>
    </div>
  </div>
</div>

<!-- PLATFORM -->
<div id="platform">
  <div class="topbar">
    <div class="logo"><div class="logo-mark"></div><div><div class="logo-text">SOVARY OS</div><div class="logo-sub">FOUNDER GOVERNANCE PLATFORM · INDIA · EST. 2026</div></div></div>
    <div class="topbar-right">
      <div class="user-pill"><div class="user-av" id="uav">K</div><span id="uname">KISHORE</span><span style="color:var(--muted);font-size:9px;margin-left:4px;">CEO & FOUNDER</span></div>
      <div class="status-pill"><div class="sdot"></div>SENTINEL ACTIVE</div>
      <div class="clock-d" id="clock">--:--:--</div>
      <button class="logout-btn" onclick="logout()">LOCK ⬡</button>
    </div>
  </div>
  <div class="nav">
    <button class="nav-btn active" onclick="showTab('dashboard',this)">DASHBOARD</button>
    <button class="nav-btn" onclick="showTab('company',this)">COMPANY</button>
    <button class="nav-btn" onclick="showTab('products',this)">PRODUCTS</button>
    <button class="nav-btn" onclick="showTab('founders',this)">FOUNDERS</button>
    <button class="nav-btn" onclick="showTab('roadmap',this)">ROADMAP</button>
    <button class="nav-btn" onclick="showTab('financials',this)">FINANCIALS</button>
    <button class="nav-btn ai-btn" onclick="showTab('ai',this)">⬡ SOVARY AI</button>
  </div>
  <div class="content">

    <!-- DASHBOARD -->
    <div class="tab-panel active" id="tab-dashboard">
      <div class="g3"><div class="card"><div class="card-title">proposals today</div><div class="sv" style="color:var(--accent)">12</div><div class="sl">Sentinel proposals</div><div class="sd up">↑ 4 from yesterday</div></div><div class="card"><div class="card-title">kernel blocks</div><div class="sv" style="color:var(--danger)">7</div><div class="sl">Blocked by logic gates</div><div class="sd nt">58% block rate</div></div><div class="card"><div class="card-title">approved executions</div><div class="sv" style="color:var(--success)">5</div><div class="sl">Passed all gates</div><div class="sd up">Avg risk: 11.2%</div></div></div>
      <div class="g3" style="margin-bottom:16px;"><div class="card s2"><div class="card-title">sentinel shell · latest proposal</div><div class="sg"><div class="pb"><div class="pa p-block">⛔ BLOCK</div><div style="font-family:var(--mono);font-size:13px;color:var(--accent);margin-bottom:10px;letter-spacing:1px;">BTC/USD</div><div class="pm">Risk level: 72.0%<br>Confidence: HIGH<br>Model: llama3.2 · local<br>Gate: KERNEL OVERRIDE</div><div class="rbw"><div class="rbl"><span>RISK LEVEL</span><span style="color:var(--danger)">72%</span></div><div class="rb"><div class="rbf rh" style="width:72%"></div></div><div class="tm"></div><div class="tl">20% LIMIT</div></div></div><div class="pb"><div style="font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:2px;margin-bottom:10px;">REASONING</div><div style="font-size:13px;color:var(--text2);line-height:1.7;">Bitcoin flash crash wiped $12B. Fed signals two more rate hikes. Risk threshold exceeded — blocked by Iron Kernel.</div><div style="margin-top:14px;font-family:var(--mono);font-size:10px;color:var(--muted);">TIMESTAMP · <span style="color:var(--text2)" id="pts">—</span></div></div></div></div><div class="card"><div class="card-title">market signals</div><div class="sr"><div class="sa">BTC</div><div class="sp">$82,400</div><div class="sc dn">−6.40%<span class="stag">VOL</span></div></div><div class="sr"><div class="sa">SPY</div><div class="sp">$512.30</div><div class="sc dn">−1.20%</div></div><div class="sr"><div class="sa">GOLD</div><div class="sp">$2,310</div><div class="sc up">+1.80%</div></div><div class="sr"><div class="sa">ETH</div><div class="sp">$3,140</div><div class="sc dn">−4.10%</div></div></div></div>
      <div class="g3" style="margin-bottom:16px;"><div class="card s2"><div class="card-title">obsidian ledger</div><table class="lt"><thead><tr><th>TIME</th><th>ASSET</th><th>ACTION</th><th>RISK</th><th>CONFIDENCE</th><th>STATUS</th></tr></thead><tbody><tr><td>08:42:11</td><td style="color:var(--accent)">BTC</td><td><span class="badge b-block">BLOCK</span></td><td style="color:var(--danger)">72.0%</td><td>HIGH</td><td style="color:var(--danger)">BLOCKED</td></tr><tr><td>08:31:04</td><td style="color:var(--accent)">GOLD</td><td><span class="badge b-buy">BUY</span></td><td style="color:var(--success)">9.2%</td><td>HIGH</td><td style="color:var(--success)">APPROVED</td></tr><tr><td>08:18:55</td><td style="color:var(--accent)">SPY</td><td><span class="badge b-hold">HOLD</span></td><td style="color:var(--gold)">18.5%</td><td>MEDIUM</td><td style="color:var(--success)">APPROVED</td></tr><tr><td>07:55:30</td><td style="color:var(--accent)">ETH</td><td><span class="badge b-block">BLOCK</span></td><td style="color:var(--danger)">61.0%</td><td>HIGH</td><td style="color:var(--danger)">BLOCKED</td></tr><tr><td>07:40:12</td><td style="color:var(--accent)">BTC</td><td><span class="badge b-sell">SELL</span></td><td style="color:var(--gold)">14.8%</td><td>MEDIUM</td><td style="color:var(--success)">APPROVED</td></tr></tbody></table></div><div class="card"><div class="card-title">pillar status</div><div class="pg"><div class="pi"><div class="pn">ORACLE BRIDGE</div><div class="ps sb">STANDBY</div><div class="pd">Next to build</div><div class="ab"><div class="ab-bar" style="height:20%"></div><div class="ab-bar" style="height:15%"></div><div class="ab-bar" style="height:10%"></div><div class="ab-bar" style="height:18%"></div><div class="ab-bar" style="height:12%"></div></div></div><div class="pi"><div class="pn">EXEC LOGIC</div><div class="ps on">ONLINE</div><div class="pd">sentinel_shell.py</div><div class="ab" id="eb"><div class="ab-bar ac" style="height:60%"></div><div class="ab-bar ac" style="height:80%"></div><div class="ab-bar ac" style="height:45%"></div><div class="ab-bar ac" style="height:90%"></div><div class="ab-bar ac" style="height:55%"></div></div></div><div class="pi"><div class="pn">IRON KERNEL</div><div class="ps on">ONLINE</div><div class="pd">Ollama · llama3.2</div><div class="ab" id="kb"><div class="ab-bar ac" style="height:70%"></div><div class="ab-bar ac" style="height:50%"></div><div class="ab-bar ac" style="height:85%"></div><div class="ab-bar ac" style="height:40%"></div><div class="ab-bar ac" style="height:75%"></div></div></div></div></div></div>
      <div class="card"><div class="card-title">iron kernel · prime directives</div><div class="dg"><div class="di"><div class="li"></div><div class="dn2">01</div><div class="dt" style="color:var(--text)">If Risk &gt; 20% → Block execution</div></div><div class="di"><div class="li"></div><div class="dn2">02</div><div class="dt" style="color:var(--text)">Sentinel proposes, never executes</div></div><div class="di"><div class="li"></div><div class="dn2">03</div><div class="dt" style="color:var(--text)">All decisions logged to Ledger</div></div><div class="di"><div class="li"></div><div class="dn2">04</div><div class="dt">No data sent to public internet</div></div></div></div>
    </div>

    <!-- COMPANY -->
    <div class="tab-panel" id="tab-company">
      <div class="g2"><div class="card s2"><div class="card-title">who we are</div><div class="mq">"We are building the world's first Sovereign AI Operating System — infrastructure that lets individuals and companies govern themselves with the power of autonomous intelligence, without surrendering control to any cloud, corporation, or government."</div><div class="tr"><div class="tg ac">AI Infrastructure</div><div class="tg ac">Autonomous Governance</div><div class="tg go">Founded India · 2026</div><div class="tg">Agentic Era</div><div class="tg">Local-First AI</div><div class="tg">Sovereign Tech</div></div></div></div>
      <div class="g3"><div class="card"><div class="card-title">the problem</div><div style="font-size:14px;color:var(--text2);line-height:1.8;">In 2026, AI tools talk and write — but none can <span style="color:var(--text)">run</span> a company. Every AI leaks data to the cloud, drifts from intent, and has no governance layer. SOVARY OS is the missing infrastructure.</div></div><div class="card"><div class="card-title">our mission</div><div style="font-size:14px;color:var(--text2);line-height:1.8;">To give every founder a private AI brain that <span style="color:var(--text)">acts on their behalf</span> — making decisions, enforcing rules, protecting assets — without ever touching the public internet.</div></div><div class="card"><div class="card-title">our vision</div><div style="font-size:14px;color:var(--text2);line-height:1.8;">A world where your AI works <span style="color:var(--text)">for you alone</span> — not for a platform, not for advertisers. SOVARY OS is the Central Brain of your empire, running locally, governed by your Prime Directives.</div></div></div>
      <div class="g2"><div class="card"><div class="card-title">company facts</div><div class="fr2"><div class="fl">Company</div><div class="fv" style="color:var(--accent)">SOVARY OS</div></div><div class="fr2"><div class="fl">Category</div><div class="fv">AI Infrastructure</div></div><div class="fr2"><div class="fl">Founded</div><div class="fv">2026 · India</div></div><div class="fr2"><div class="fl">Stage</div><div class="fv" style="color:var(--gold)">Pre-seed · Building</div></div><div class="fr2"><div class="fl">Core tech</div><div class="fv">Ollama · llama3.2 · Python</div></div></div><div class="card"><div class="card-title">what makes us different</div><div style="display:flex;flex-direction:column;gap:12px;margin-top:4px;"><div style="display:flex;gap:12px;"><div style="color:var(--accent);font-family:var(--mono);font-size:11px;min-width:16px;">01</div><div style="font-size:13px;color:var(--text2);line-height:1.6;"><span style="color:var(--text)">No cloud</span> — 100% local AI, zero data leakage</div></div><div style="display:flex;gap:12px;"><div style="color:var(--accent);font-family:var(--mono);font-size:11px;min-width:16px;">02</div><div style="font-size:13px;color:var(--text2);line-height:1.6;"><span style="color:var(--text)">Hardcoded constitution</span> — AI can never violate Prime Directives</div></div><div style="display:flex;gap:12px;"><div style="color:var(--accent);font-family:var(--mono);font-size:11px;min-width:16px;">03</div><div style="font-size:13px;color:var(--text2);line-height:1.6;"><span style="color:var(--text)">Immutable ledger</span> — every decision auditable forever</div></div><div style="display:flex;gap:12px;"><div style="color:var(--accent);font-family:var(--mono);font-size:11px;min-width:16px;">04</div><div style="font-size:13px;color:var(--text2);line-height:1.6;"><span style="color:var(--text)">Built for 2026</span> — manages agents, money, decisions autonomously</div></div></div></div></div>
    </div>

    <!-- PRODUCTS -->
    <div class="tab-panel" id="tab-products">
      <div class="g3"><div class="pc"><div class="pci">[ OS ]</div><div class="pcn">SOVARY OS</div><div class="pcd">The Sovereign Operating System. Manages intent and authority — coordinates AI agents, enforces Prime Directives, acts as the Central Brain of autonomous governance.</div><div class="pcs s-build">IN DEVELOPMENT</div></div><div class="pc"><div class="pci">[ SS ]</div><div class="pcn">Sentinel Shell</div><div class="pcd">AI analysis and proposal engine. Powered by llama3.2 locally via Ollama. Reads market signals and news, proposes structured decisions to the Iron Kernel.</div><div class="pcs s-live">LIVE · v0.1</div></div><div class="pc"><div class="pci">[ OB ]</div><div class="pcn">Oracle Bridge</div><div class="pcd">Secure private data pipeline. Connects sensitive data — bank accounts, legal docs, strategy — to the AI brain without exposing it to the public internet.</div><div class="pcs s-plan">PLANNED · Q2 2026</div></div><div class="pc"><div class="pci">[ IK ]</div><div class="pcn">Iron Kernel</div><div class="pcd">Private, hack-resistant execution environment. Runs 100% locally. Enforces the hardcoded constitution, blocks model drift, ensures no AI bypasses logic gates.</div><div class="pcs s-live">LIVE · Ollama + llama3.2</div></div><div class="pc"><div class="pci">[ WB ]</div><div class="pcn">SOVARY Web</div><div class="pcd">Founder-only governance dashboard. Real-time Sentinel proposals, Obsidian Ledger, market signals, system status. Protected by Password + PIN + Google login.</div><div class="pcs s-live">LIVE · v5.0</div></div><div class="pc" style="border-color:var(--gold);"><div class="pci" style="color:var(--gold);">[ AI ]</div><div class="pcn" style="color:var(--gold);">SOVARY AI</div><div class="pcd">Conversational intelligence layer. Chat with your OS, control Sentinel and Kernel via natural language, get governance insights — powered by local llama3.2.</div><div class="pcs s-live" style="border-color:rgba(232,160,32,0.4);background:rgba(232,160,32,0.1);color:var(--gold);">LIVE · v1.0</div></div></div>
    </div>

    <!-- FOUNDERS -->
    <div class="tab-panel" id="tab-founders">
      <div class="g2" style="margin-bottom:16px;"><div class="fc"><div style="display:flex;align-items:center;gap:16px;"><div class="fav">K</div><div><div class="fn">KISHORE</div><div class="fr">CEO & FOUNDER · SOVARY OS</div></div></div><div class="fb">Visionary behind SOVARY OS — the world's first Sovereign AI Operating System. Building the infrastructure layer for the Agentic Era from India, with a mission to give every individual and company a private AI brain that acts on their behalf without surrendering control to any cloud or corporation.</div><div class="ftags"><div class="ftag">AI INFRASTRUCTURE</div><div class="ftag">AUTONOMOUS SYSTEMS</div><div class="ftag">GOVERNANCE</div><div class="ftag">INDIA · 2026</div></div></div><div class="card" style="display:flex;flex-direction:column;justify-content:center;align-items:center;border-style:dashed;min-height:200px;"><div style="font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:2px;margin-bottom:12px;">CO-FOUNDER SLOT</div><div style="font-size:13px;color:var(--border2);text-align:center;line-height:1.8;">Reserved for future<br>co-founders & core team</div></div></div>
      <div class="card"><div class="card-title">founder access log</div><table class="lt"><thead><tr><th>FOUNDER</th><th>ROLE</th><th>LAST ACCESS</th><th>AUTH METHOD</th><th>STATUS</th></tr></thead><tbody><tr><td style="color:var(--accent)">KISHORE</td><td>CEO & Founder</td><td id="last-acc">—</td><td>PASSWORD + PIN</td><td style="color:var(--success)">ACTIVE SESSION</td></tr></tbody></table></div>
    </div>

    <!-- ROADMAP -->
    <div class="tab-panel" id="tab-roadmap">
      <div class="g2">
        <div class="card"><div class="card-title">2026 build roadmap</div><div><div class="ri"><div class="rl2"><div class="rd done"></div><div class="rc"></div></div><div style="flex:1"><div class="rq">Q1 2026</div><div class="rt" style="color:var(--success)">Foundation ✓</div><div class="ril">· SOVARY OS architecture<br>· Sentinel Shell v0.1<br>· Iron Kernel — llama3.2<br>· SOVARY Web v5 + login<br>· SOVARY AI v1.0</div></div></div><div class="ri"><div class="rl2"><div class="rd active"></div><div class="rc"></div></div><div style="flex:1"><div class="rq">Q2 2026</div><div class="rt" style="color:var(--accent)">Core Infrastructure ← NOW</div><div class="ril">· Oracle Bridge<br>· Obsidian Ledger (SQLite)<br>· Sentinel Shell v0.2<br>· Live market data feeds<br>· Founder platform v2</div></div></div><div class="ri"><div class="rl2"><div class="rd soon"></div><div class="rc"></div></div><div style="flex:1"><div class="rq">Q3 2026</div><div class="rt">Autonomous Execution</div><div class="ril">· Auto-payment logic gates<br>· Document audit agent<br>· Multi-agent coordination<br>· SOVARY OS v1.0 release</div></div></div><div class="ri"><div class="rl2"><div class="rd"></div></div><div style="flex:1"><div class="rq">Q4 2026</div><div class="rt">Scale & Sovereign Network</div><div class="ril">· Enterprise modules<br>· Seed funding round<br>· 10 paying companies</div></div></div></div></div>
        <div class="card"><div class="card-title">milestone tracker</div><div style="display:flex;flex-direction:column;gap:16px;margin-top:4px;"><div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;"><span style="color:var(--text)">Architecture designed</span><span style="font-family:var(--mono);font-size:11px;color:var(--success)">DONE</span></div><div class="prb"><div class="prf f-su" style="width:100%"></div></div></div><div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;"><span style="color:var(--text)">Sentinel Shell built</span><span style="font-family:var(--mono);font-size:11px;color:var(--success)">DONE</span></div><div class="prb"><div class="prf f-su" style="width:100%"></div></div></div><div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;"><span style="color:var(--text)">SOVARY Web + AI live</span><span style="font-family:var(--mono);font-size:11px;color:var(--success)">DONE</span></div><div class="prb"><div class="prf f-su" style="width:100%"></div></div></div><div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;"><span style="color:var(--text)">Oracle Bridge</span><span style="font-family:var(--mono);font-size:11px;color:var(--gold)">IN PROGRESS</span></div><div class="prb"><div class="prf f-go" style="width:15%"></div></div></div><div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;"><span style="color:var(--text)">Obsidian Ledger (SQLite)</span><span style="font-family:var(--mono);font-size:11px;color:var(--muted)">PLANNED</span></div><div class="prb"><div class="prf f-ac" style="width:5%"></div></div></div><div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;"><span style="color:var(--text)">SOVARY OS v1.0</span><span style="font-family:var(--mono);font-size:11px;color:var(--muted)">Q3 2026</span></div><div class="prb"><div class="prf f-ac" style="width:8%"></div></div></div><div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;"><span style="color:var(--text)">Seed funding</span><span style="font-family:var(--mono);font-size:11px;color:var(--muted)">Q4 2026</span></div><div class="prb"><div class="prf f-ac" style="width:3%"></div></div></div></div></div>
      </div>
    </div>

    <!-- FINANCIALS -->
    <div class="tab-panel" id="tab-financials">
      <div class="g4" style="margin-bottom:16px;"><div class="card"><div class="card-title">stage</div><div class="sv" style="color:var(--gold);font-size:22px;">PRE-SEED</div><div class="sl">Self-funded · 2026</div></div><div class="card"><div class="card-title">runway</div><div class="sv" style="color:var(--accent);font-size:28px;">∞</div><div class="sl">Zero burn · local infra</div></div><div class="card"><div class="card-title">infra cost</div><div class="sv" style="color:var(--success);font-size:28px;">₹0</div><div class="sl">Per month · 100% local</div></div><div class="card"><div class="card-title">target round</div><div class="sv" style="color:var(--accent);font-size:22px;">SEED</div><div class="sl">Q4 2026 · India / UAE</div></div></div>
      <div class="g2"><div class="card"><div class="card-title">cost vs cloud AI</div><div style="display:flex;flex-direction:column;gap:14px;margin-top:4px;"><div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;"><span style="color:var(--text2)">OpenAI API equivalent</span><span style="font-family:var(--mono);font-size:12px;color:var(--danger)">~₹25,000/mo</span></div><div class="prb"><div class="prf" style="width:100%;background:var(--danger)"></div></div></div><div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;"><span style="color:var(--text2)">Cloud hosting (AWS/GCP)</span><span style="font-family:var(--mono);font-size:12px;color:var(--gold)">~₹8,000/mo</span></div><div class="prb"><div class="prf f-go" style="width:32%"></div></div></div><div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;"><span style="color:var(--text)">SOVARY OS · local</span><span style="font-family:var(--mono);font-size:12px;color:var(--success)">₹0/mo</span></div><div class="prb"><div class="prf f-su" style="width:1%"></div></div></div></div><div style="margin-top:16px;font-family:var(--mono);font-size:10px;color:var(--muted);">ANNUAL SAVING · <span style="color:var(--success)">~₹3.96 LAKH+</span></div></div><div class="card"><div class="card-title">revenue model · target</div><div class="fr2"><div class="fl">Individual sovereign</div><div class="fv" style="color:var(--accent)">₹4,999/mo</div></div><div class="fr2"><div class="fl">Company governance</div><div class="fv" style="color:var(--accent)">₹24,999/mo</div></div><div class="fr2"><div class="fl">Enterprise custom</div><div class="fv" style="color:var(--gold)">₹1L+/mo</div></div><div class="fr2"><div class="fl">Target MRR Q4 2026</div><div class="fv" style="color:var(--success)">₹5L/mo</div></div><div class="fr2"><div class="fl">Seed ask</div><div class="fv" style="color:var(--gold)">₹1–2 Cr</div></div><div style="margin-top:14px;font-family:var(--mono);font-size:10px;color:var(--muted);">FOUNDER EYES ONLY · CONFIDENTIAL</div></div></div>
    </div>

    <!-- SOVARY AI -->
    <div class="tab-panel" id="tab-ai">
      <div class="ai-layout">
        <div class="ai-sidebar">
          <div class="ai-sc">
            <div class="ai-name">⬡ SOVARY AI</div>
            <div class="ai-model">llama3.2:3b · Python Bridge · local</div>
            <div class="ai-online" id="ai-status"><div class="ai-dot" style="background:var(--gold)"></div>CHECKING...</div>
          </div>
          <div class="ctrl-card">
            <div class="ctrl-title">KERNEL CONTROLS</div>
            <button class="ctrl-btn" onclick="sendQ('Run Sentinel analysis on current market signals: BTC down 6.4%, SPY down 1.2%, GOLD up 1.8%. Give me a structured proposal.')">⚡ RUN SENTINEL</button>
            <button class="ctrl-btn" onclick="sendQ('Show me all active Prime Directives and current risk threshold in the Kernel.')">🛡 CHECK KERNEL</button>
            <button class="ctrl-btn" onclick="sendQ('Summarize the last 5 decisions in the Obsidian Ledger and identify patterns.')">📒 QUERY LEDGER</button>
            <button class="ctrl-btn" onclick="sendQ('What is the current status of all SOVARY OS pillars?')">◈ PILLAR STATUS</button>
          </div>
          <div class="qc-card">
            <div class="qc-title">QUICK COMMANDS</div>
            <button class="qc-btn" onclick="sendQ('What is SOVARY OS and what are we building?')">What is SOVARY OS?</button>
            <button class="qc-btn" onclick="sendQ('Explain the three pillars of SOVARY OS in detail.')">Explain the 3 pillars</button>
            <button class="qc-btn" onclick="sendQ('What should we build next after the Sentinel Shell?')">What to build next?</button>
            <button class="qc-btn" onclick="sendQ('What are the biggest risks to SOVARY OS and how do we mitigate them?')">Risk assessment</button>
            <button class="qc-btn" onclick="sendQ('Give me a 3-sentence funding pitch for SOVARY OS for Indian seed investors.')">Funding pitch</button>
            <button class="qc-btn" onclick="sendQ('How does SOVARY OS compare to other AI agent platforms in 2026?')">Competitive analysis</button>
          </div>
        </div>
        <div class="chat-wrap">
          <div class="chat-hdr">
            <div class="chat-hdr-l"><div class="chat-diamond"></div><div><div class="chat-title">SOVARY AI · SOVEREIGN INTELLIGENCE</div><div class="chat-sub">CHAT + KERNEL CONTROL · llama3.2:3b · PYTHON BRIDGE · LOCAL</div></div></div>
            <button class="clear-btn" onclick="clearChat()">CLEAR</button>
          </div>
          <div class="chat-msgs" id="chat-msgs"></div>
          <div class="chat-inp-wrap">
            <textarea class="chat-inp" id="chat-inp" placeholder="Ask SOVARY AI anything..." rows="1"></textarea>
            <button class="send-btn" id="send-btn" onclick="sendMsg()">SEND →</button>
          </div>
        </div>
      </div>
    </div>

  </div>
  <footer><span>SOVARY OS · FOUNDER GOVERNANCE PLATFORM · INDIA · 2026</span><span>IRON KERNEL · llama3.2 · LOCAL · CONFIDENTIAL</span><span id="fdate">—</span></footer>
</div>

<script>
const PWD = "sovereign2026";
const PIN = "2604";
const MAX_ATT = 3;
const LOCK_SECS = 30;

let att=0, pinBuf=[], pwdOk=false, locked=false;
let history=[], thinking=false;

function togglePwd(){const i=document.getElementById('pwd-inp');i.type=i.type==='password'?'text':'password';}
function submitPwd(){
  if(locked) return;
  if(document.getElementById('pwd-inp').value===PWD){pwdOk=true;document.getElementById('step-pwd').style.display='none';document.getElementById('step-pin').style.display='block';document.getElementById('pwd-err').textContent='';}
  else{fail('pwd-err','INVALID PASSWORD');}
}
document.getElementById('pwd-inp').addEventListener('keydown',e=>{if(e.key==='Enter')submitPwd();});
function backToPwd(){document.getElementById('step-pin').style.display='none';document.getElementById('step-pwd').style.display='block';pinBuf=[];updateDots();pwdOk=false;}
function pinKey(k){if(locked||pinBuf.length>=4)return;pinBuf.push(k);updateDots();if(pinBuf.length===4)setTimeout(checkPin,200);}
function pinDel(){pinBuf.pop();updateDots();document.getElementById('pin-err').textContent='';}
function pinClear(){pinBuf=[];updateDots();document.getElementById('pin-err').textContent='';}
function updateDots(){for(let i=0;i<4;i++){const d=document.getElementById('d'+i);if(pinBuf[i]!==undefined){d.textContent='●';d.classList.add('filled');d.classList.remove('error');}else{d.textContent='—';d.classList.remove('filled','error');}}}
function checkPin(){if(pinBuf.join('')===PIN){unlock('KISHORE');}else{pinBuf=[];for(let i=0;i<4;i++){const d=document.getElementById('d'+i);d.textContent='✕';d.classList.add('error');d.classList.remove('filled');}setTimeout(updateDots,600);fail('pin-err','INCORRECT PIN');}}
function fail(id,msg){att++;document.getElementById(id).textContent=msg+` · ${MAX_ATT-att} left`;const p=document.getElementById('pip'+(att-1));if(p)p.classList.add('used');if(att>=MAX_ATT)startLock();}
function startLock(){locked=true;const el=document.getElementById('lockout');el.classList.add('show');let s=LOCK_SECS;document.getElementById('ltimer').textContent=s;const t=setInterval(()=>{s--;document.getElementById('ltimer').textContent=s;if(s<=0){clearInterval(t);el.classList.remove('show');locked=false;att=0;document.querySelectorAll('.attempt-pip').forEach(p=>p.classList.remove('used'));document.getElementById('pwd-err').textContent='';document.getElementById('pin-err').textContent='';pinBuf=[];updateDots();if(!pwdOk)document.getElementById('pwd-inp').value='';}},1000);}
function googleLogin(){
  const provider = new firebase.auth.GoogleAuthProvider();
  firebase.auth().signInWithPopup(provider)
    .then((result) => {
      const user = result.user;
      const email = user.email;
      const ALLOWED_EMAILS = [
        'kisoreyadla100@gmail.com'
      ];
      if (ALLOWED_EMAILS.includes(email)) {
        const name = user.displayName || email;
        unlock(name);
      } else {
        firebase.auth().signOut();
        document.getElementById('pwd-err').textContent = 'Access denied. This platform is for authorized founders only.';
      }
    })
    .catch((error) => {
      document.getElementById('pwd-err').textContent = 'Google login failed. Try again.';
    });
}
function unlock(name){
  const now=new Date();
  document.getElementById('uname').textContent=name.toUpperCase();
  document.getElementById('uav').textContent=name[0].toUpperCase();
  document.getElementById('pts').textContent=now.toISOString().replace('T',' ').split('.')[0]+' UTC';
  document.getElementById('last-acc').textContent=now.toISOString().replace('T',' ').split('.')[0]+' UTC';
  const ls=document.getElementById('login-screen');
  const pl=document.getElementById('platform');
  ls.classList.add('hide');
  setTimeout(()=>{ls.style.display='none';pl.style.display='flex';setTimeout(()=>pl.classList.add('show'),20);checkStatus();welcome();},600);
}
function logout(){const pl=document.getElementById('platform');const ls=document.getElementById('login-screen');pl.classList.remove('show');setTimeout(()=>{pl.style.display='none';ls.style.display='flex';ls.classList.remove('hide');att=0;pwdOk=false;pinBuf=[];locked=false;document.getElementById('pwd-inp').value='';document.getElementById('pwd-err').textContent='';document.getElementById('pin-err').textContent='';document.querySelectorAll('.attempt-pip').forEach(p=>p.classList.remove('used'));document.getElementById('step-pwd').style.display='block';document.getElementById('step-pin').style.display='none';updateDots();},400);}
function showTab(n,b){document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));document.querySelectorAll('.nav-btn').forEach(x=>x.classList.remove('active'));document.getElementById('tab-'+n).classList.add('active');b.classList.add('active');}
function updateClock(){const now=new Date();const hh=String(now.getHours()).padStart(2,'0');const mm=String(now.getMinutes()).padStart(2,'0');const ss=String(now.getSeconds()).padStart(2,'0');const c=document.getElementById('clock');if(c)c.textContent=`${hh}:${mm}:${ss}`;const d=document.getElementById('fdate');if(d)d.textContent=now.toISOString().split('T')[0];}
updateClock();setInterval(updateClock,1000);
function animBars(id){document.querySelectorAll(`#${id} .ab-bar`).forEach(b=>{b.style.height=(Math.floor(Math.random()*80)+15)+'%';});}
setInterval(()=>animBars('eb'),1200);setInterval(()=>animBars('kb'),900);

async function checkStatus(){
  try{
    const r=await fetch('/api/status');
    const d=await r.json();
    const el=document.getElementById('ai-status');
    if(d.ready){el.innerHTML='<div class="ai-dot" style="background:var(--success);animation:blink 1.4s ease-in-out infinite;"></div>ONLINE · llama3.2 ready';el.style.color='var(--success)';}
    else{el.innerHTML='<div class="ai-dot" style="background:var(--gold)"></div>Ollama offline';el.style.color='var(--gold)';}
  }catch(e){
    const el=document.getElementById('ai-status');
    el.innerHTML='<div class="ai-dot" style="background:var(--danger)"></div>Server offline';
    el.style.color='var(--danger)';
  }
}

function welcome(){
  setTimeout(()=>{
    addMsg('ai','SOVARY AI online. Iron Kernel connected — llama3.2:3b running locally via Python bridge.\\n\\nI am your sovereign intelligence layer. Ask me anything about SOVARY OS, market conditions, what to build next, or give me a command.\\n\\nFounder Kishore — how can I serve the OS today?');
  },800);
}

function addMsg(role,text){
  const msgs=document.getElementById('chat-msgs');
  const div=document.createElement('div');
  div.className=`msg ${role}`;
  const av=document.createElement('div');
  av.className=`msg-av ${role==='ai'?'ai':'usr'}`;
  av.textContent=role==='ai'?'⬡':'K';
  const body=document.createElement('div');
  body.className='msg-body';
  const name=document.createElement('div');
  name.className='msg-name';
  name.textContent=role==='ai'?'SOVARY AI · llama3.2':'KISHORE · FOUNDER';
  const bubble=document.createElement('div');
  bubble.className='msg-bubble';
  bubble.textContent=text;
  body.appendChild(name);body.appendChild(bubble);
  div.appendChild(av);div.appendChild(body);
  msgs.appendChild(div);
  msgs.scrollTop=msgs.scrollHeight;
  history.push({role:role==='ai'?'assistant':'user',content:text});
}

function showTyping(){
  const msgs=document.getElementById('chat-msgs');
  const div=document.createElement('div');
  div.className='msg ai';div.id='typing';
  const av=document.createElement('div');av.className='msg-av ai';av.textContent='⬡';
  const body=document.createElement('div');body.className='msg-body';
  const name=document.createElement('div');name.className='msg-name';name.textContent='SOVARY AI · thinking...';
  const ind=document.createElement('div');ind.className='typing';
  ind.innerHTML='<div class="tdot"></div><div class="tdot"></div><div class="tdot"></div>';
  body.appendChild(name);body.appendChild(ind);div.appendChild(av);div.appendChild(body);
  msgs.appendChild(div);msgs.scrollTop=msgs.scrollHeight;
}
function removeTyping(){const el=document.getElementById('typing');if(el)el.remove();}

async function sendMsg(){
  if(thinking)return;
  const inp=document.getElementById('chat-inp');
  const msg=inp.value.trim();
  if(!msg)return;
  inp.value='';inp.style.height='auto';
  addMsg('user',msg);
  thinking=true;
  document.getElementById('send-btn').disabled=true;
  showTyping();
  try{
    const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,history:history.slice(-6)})});
    if(!r.ok)throw new Error('Server error');
    const d=await r.json();
    removeTyping();
    addMsg('ai',d.reply||'No response.');
  }catch(e){
    removeTyping();
    addMsg('ai','⚠ Cannot reach the Python server.\\n\\nMake sure sovary_server.py is running:\\n  python sovary_server.py');
  }
  thinking=false;
  document.getElementById('send-btn').disabled=false;
}

function sendQ(cmd){
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById('tab-ai').classList.add('active');
  document.querySelector('.ai-btn').classList.add('active');
  document.getElementById('chat-inp').value=cmd;
  sendMsg();
}

function clearChat(){document.getElementById('chat-msgs').innerHTML='';history=[];welcome();}

document.getElementById('chat-inp').addEventListener('input',function(){this.style.height='auto';this.style.height=Math.min(this.scrollHeight,120)+'px';});
document.getElementById('chat-inp').addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMsg();}});
</script>
</body>
</html>"""


@app.route("/")
def index():
    return Response(HTML, mimetype="text/html")


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data    = request.json
        message = data.get("message", "")
        hist    = data.get("history", [])

        prompt = f"{SOVARY_SYSTEM}\n\n"
        for m in hist[-6:]:
            prompt += f"Human: {m['content']}\n" if m["role"] == "user" else f"Assistant: {m['content']}\n"
        prompt += f"Human: {message}\nAssistant:"

        resp = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 400, "num_ctx": 2048}
        }, timeout=120)
        resp.raise_for_status()
        reply = resp.json().get("response", "").strip()
        return jsonify({"reply": reply, "status": "ok"})
    except requests.exceptions.ConnectionError:
        return jsonify({"reply": "Ollama is offline. Run: ollama serve", "status": "error"}), 500
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}", "status": "error"}), 500


@app.route("/api/status")
def status():
    try:
        resp   = requests.get(OLLAMA_TAGS, timeout=5)
        models = [m["name"] for m in resp.json().get("models", [])]
        ready  = any("llama3" in m for m in models)
        return jsonify({"ollama": "online", "model": OLLAMA_MODEL, "ready": ready, "models": models})
    except:
        return jsonify({"ollama": "offline", "ready": False}), 503


if __name__ == "__main__":
    print("""
+--------------------------------------------------+
|        SOVARY OS - COMPLETE PLATFORM SERVER      |
|        Founder: Kishore  |  India  |  2026       |
+--------------------------------------------------+
|  Open browser and go to: http://localhost:5000   |
|  Login: sovereign2026  |  PIN: 2604              |
+--------------------------------------------------+
""")
    app.run(host="0.0.0.0", port=5000, debug=False)
