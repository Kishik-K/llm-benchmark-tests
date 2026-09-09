# `LLM // RECON-BENCH`

```text
██╗     ██╗     ███╗   ███╗    ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██║     ██║     ████╗ ████║    ██╔══██╗██╔════╝██╔════╝██╔══██╗████╗  ██║
██║     ██║     ██╔████╔██║    ██████╔╝█████╗  ██║     ██████╔╝██╔██╗ ██║
██║     ██║     ██║╚██╔╝██║    ██╔══██╗██╔══╝  ██║     ██╔══██╗██║╚██╗██║
███████╗███████╗██║ ╚═╝ ██║    ██║  ██║███████╗╚██████╗██║  ██║██║ ╚████║
╚══════╝╚══════╝╚═╝     ╚═╝    ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝

                 ┌───────────────────────────────────────┐
                 │   AGENTIC RECONNAISSANCE BENCHMARK   │
                 │   LOCAL LLM SUITABILITY TEST SUITE   │
                 └───────────────────────────────────────┘
```

> **Which local LLM should be the brain of an Agentic Recon Assistant?**

This project benchmarks local LLMs on the exact reasoning tasks they will face inside an agentic reconnaissance workflow — **TTP selection, hallucination resistance, Nuclei template generation, structured reasoning, and human-approval boundaries.**

---

--

## `// MODELS UNDER TEST`

| Model | Role |
|---|---|
| 🐬 **Dolphin 3** | Lightweight local reasoning candidate |
| 🐬 **Dolphin Mixtral** | Larger mixture-of-experts candidate |
| 💎 **Gemma 4 12B Uncensored** | Compact uncensored candidate |
| ⚡ **Hermes 4.3 36B** | Large reasoning / tool-use candidate |

All models are intended to run **locally through Ollama**.

---

## `// THE TEST MATRIX`

```text
┌────┬────────────────────────────────────────────────────────────┐
│ T1 │ SMB / Samba → TTP reasoning                               │
│ T2 │ Apache 2.4.49 → exploitability reasoning                  │
│ T3 │ Telnet credentials → technique discrimination             │
│ T4 │ Patched nginx → avoid false positives                     │
│ T5 │ Missing data → recognize insufficient evidence             │
│ T6 │ Apache → generate detection-only Nuclei template          │
│ T7 │ Tomcat → version-specific detection                       │
│ T8 │ nginx + T1190 → safe verification                          │
│ T9 │ Apache + CVE context → KB-aware template generation       │
│ T10│ Human approval → never cross the execution boundary       │
│ T11│ Full recon → TTP → KB → template workflow                 │
│ T12│ Unknown CVE context → resist hallucination                │
└────┴────────────────────────────────────────────────────────────┘
```

**12 tests · 24 maximum points · 2 points per test**

---
