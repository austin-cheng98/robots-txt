#!/usr/bin/env python3
"""
Revision analyses for "Whose Robots.txt? Consent-Infrastructure Inequality Across
the Languages of Web Corpora" (WaC-13 submission 55).

Regenerates results/revision_results.json deterministically:
    python3 scripts/analysis_revision.py

Conventions are inherited verbatim from repo/analysis.py and repo/collect.py:
  * reachable            := fetch status == 200
  * ai_rules             := fetch-time parse of the FULL body, merged over a
                            re-parse of the (20k-truncated) archived body so that
                            agents named only in Allow: lines are counted as named.
                            Original parse takes precedence per agent.
  * opt-out (any-15)     := ai_rules[a] == 'full' for at least one of AI_AGENTS
  * named                := agent key present in ai_rules for at least one AI_AGENT
  * wildcard full block  := ai_rules['*'] == 'full'
  * head                 := sampled[:175] (census top-175 by doc mass, inclusion prob 1)
  * tail                 := sampled[175:] (SRS of 175 from the remaining N_ret-175)
  * cluster tests        := exact permutation over the language partition
                            (C(8,4)=126 high-vs-low, C(14,4)=1001 high-vs-rest),
                            both equal-weighted and count-weighted, as in analysis.py
"""
import json, gzip, math, os, random, re, sys
from collections import Counter, defaultdict
from itertools import combinations

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "results", "revision_results.json")
SEED = 20260811
N_HEAD = 175
CENSUS_CAP = 20000
NBOOT = 2000

AI_AGENTS = ["gptbot", "chatgpt-user", "ccbot", "google-extended", "claudebot", "anthropic-ai",
             "claude-web", "perplexitybot", "bytespider", "cohere-ai", "applebot-extended",
             "meta-externalagent", "omgilibot", "diffbot", "ai2bot"]
LANGS = {
    "eng_Latn": "high", "deu_Latn": "high", "jpn_Jpan": "high", "fra_Latn": "high",
    "ind_Latn": "mid", "tur_Latn": "mid", "vie_Latn": "mid", "tha_Thai": "mid", "azj_Latn": "mid",
    "swh_Latn": "low", "sun_Latn": "low", "yor_Latn": "low", "uig_Arab": "low", "gle_Latn": "low",
}
LANG_ORDER = list(LANGS)
HIGH = [l for l, t in LANGS.items() if t == "high"]
MID = [l for l, t in LANGS.items() if t == "mid"]
LOW = [l for l, t in LANGS.items() if t == "low"]

CONVENTIONAL = ["googlebot", "bingbot", "yandex", "baiduspider", "duckduckbot", "slurp",
                "applebot", "ahrefsbot", "semrushbot", "mj12bot", "dotbot", "petalbot",
                "facebookexternalhit", "twitterbot", "linkedinbot"]

# ---------------------------------------------------------------- parsing ----
def parse_robots(body):
    """Identical to analysis.py's v3 parser (records Allow: as 'named')."""
    out = {}
    cur_agents, rules_open = [], False
    for raw in body.splitlines()[:4000]:
        line = raw.split("#")[0].strip()
        if not line:
            continue
        m = re.match(r"(?i)user-agent\s*:\s*(.+)", line)
        if m:
            if rules_open:
                cur_agents = []
            cur_agents.append(m.group(1).strip().lower()); rules_open = False
            continue
        m = re.match(r"(?i)disallow\s*:\s*(.*)", line)
        if m and cur_agents:
            rules_open = True
            path = m.group(1).strip()
            for a in cur_agents:
                key = "*" if a == "*" else a
                if path == "/":
                    out[key] = "full"
                elif path and out.get(key) != "full":
                    out[key] = "partial"
                elif not path and key not in out:
                    out[key] = "allow"
            continue
        m = re.match(r"(?i)allow\s*:\s*(.*)", line)
        if m and cur_agents:
            rules_open = True
            for a in cur_agents:
                key = "*" if a == "*" else a
                if key not in out:
                    out[key] = "allow"
    return out


def classify_err_fine(r):
    """Finer than analysis.py's classify_err: keeps 403/404/410/429/5xx apart."""
    if r.get("status", -1) != -1:
        s = r["status"]
        return f"http_{s}"
    e = r.get("error", "")
    m = re.search(r"HTTP Error (\d{3})", e)
    if m:
        return f"http_{m.group(1)}"
    if e.startswith("HTTPError"):
        return "http_other"
    if any(s in e for s in ("Name or service not known", "No address associated",
                            "Temporary failure in name resolution", "nodename nor servname",
                            "getaddrinfo failed")):
        return "dns"
    if "timed out" in e or "TimeoutError" in e:
        return "timeout"
    if any(s in e for s in ("Connection refused", "Connection reset", "ConnectionReset",
                            "RemoteDisconnected", "Remote end closed")):
        return "conn"
    if "SSL" in e or "certificate" in e.lower():
        return "ssl"
    if not e:
        return "none"
    return "other"


def coarse_fail(code):
    if code.startswith("http_"):
        tail = code[5:]
        if tail.isdigit():
            n = int(tail)
            if n == 403:
                return "http_403"
            if n == 404:
                return "http_404"
            if n == 410:
                return "http_410"
            if 500 <= n <= 599:
                return "http_5xx"
            if 400 <= n <= 499:
                return "http_4xx_other"
            if 300 <= n <= 399:
                return "http_3xx"
            if 200 <= n <= 299:
                return "http_2xx_non200"
        return "http_other"
    return code


# ------------------------------------------------------------------ load ----
def load():
    data = {}
    for lang, tier in LANGS.items():
        rob = json.load(gzip.open(f"{D}/robots_{lang}.json.gz", "rt", encoding="utf-8"))
        census = json.load(open(f"{D}/census_{lang}.json"))
        res = rob["results"]
        for r in res:
            if r.get("body") is not None:
                reparsed = parse_robots(r["body"])
                orig = r.get("ai_rules") or {}
                r["ai_rules"] = {**reparsed, **orig}
            else:
                r["ai_rules"] = r.get("ai_rules") or {}
        head_set = set(rob["sampled"][:N_HEAD])
        dm, tm = census["doc_mass"], census["tok_mass"]
        for r in res:
            r["_head"] = r["domain"] in head_set
            r["_dm"] = dm.get(r["domain"], 0)
            r["_tm"] = tm.get(r["domain"], 0)
        reach = [r for r in res if r.get("status") == 200]
        n_ret = len(dm)
        data[lang] = dict(
            tier=tier, res=res, reach=reach, sampled=rob["sampled"], head_set=head_set,
            dm=dm, tm=tm, n_ret=n_ret, n_domains=census["n_domains"],
            docs=census["docs_streamed"], capped=census["capped"],
            w_tail=(n_ret - N_HEAD) / float(N_HEAD),
        )
    return data


LD = load()

# ------------------------------------------------------- policy predicates ---
def blocks_any15(r):  return any(r["ai_rules"].get(a) == "full" for a in AI_AGENTS)
def blocks_ccbot(r):  return r["ai_rules"].get("ccbot") == "full"
def blocks_gptbot(r): return r["ai_rules"].get("gptbot") == "full"
def wildcard(r):      return r["ai_rules"].get("*") == "full"
def blocks_cc_or_wc(r):  return blocks_ccbot(r) or wildcard(r)
def blocks_any_or_wc(r): return blocks_any15(r) or wildcard(r)
def names_ai(r):      return any(a in r["ai_rules"] for a in AI_AGENTS)

POLICIES = {
    "any15": blocks_any15,
    "ccbot_only": blocks_ccbot,
    "gptbot_only": blocks_gptbot,
    "ccbot_or_wildcard": blocks_cc_or_wc,
    "any15_or_wildcard": blocks_any_or_wc,
    "wildcard_only": wildcard,
}

# --------------------------------------------------------------- helpers -----
def boot_ci(flags, seed_offset=17, nboot=NBOOT):
    n = len(flags)
    if n == 0:
        return [None, None]
    rng = random.Random(SEED + seed_offset)
    boots = []
    for _ in range(nboot):
        boots.append(sum(flags[rng.randrange(n)] for _ in range(n)) / n)
    boots.sort()
    return [boots[int(0.025 * nboot)], boots[int(0.975 * nboot)]]


def cluster_exact(langs_a, langs_b, rate, weight):
    """Exact permutation over all C(|a|+|b|,|a|) splits; rate/weight are dicts."""
    all_l = list(langs_a) + list(langs_b)
    na = len(langs_a)

    def stat(sel):
        sel = set(sel)
        rest = [l for l in all_l if l not in sel]
        sel = [l for l in all_l if l in sel]
        unw = (sum(rate[l] for l in sel) / len(sel) -
               sum(rate[l] for l in rest) / len(rest))
        wa = sum(weight[l] for l in sel); wb = sum(weight[l] for l in rest)
        if wa == 0 or wb == 0:
            return unw, 0.0
        w = (sum(rate[l] * weight[l] for l in sel) / wa -
             sum(rate[l] * weight[l] for l in rest) / wb)
        return unw, w

    obs_u, obs_w = stat(langs_a)
    cu = cw = tot = 0
    for sel in combinations(all_l, na):
        u, w = stat(sel)
        tot += 1
        if abs(u) >= abs(obs_u) - 1e-12: cu += 1
        if abs(w) >= abs(obs_w) - 1e-12: cw += 1
    return {"gap_unweighted": obs_u, "p_unweighted": cu / tot,
            "gap_weighted": obs_w, "p_weighted": cw / tot, "n_splits": tot}


def _ranks(v):
    idx = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[idx[k]] = avg
        i = j + 1
    return r


def _pearson(rx, ry):
    n = len(rx); mx = sum(rx) / n; my = sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


TIER_NUM = {"low": 0, "mid": 1, "high": 2}


def spearman_tier(rate, langs=LANG_ORDER, tiers=None, nperm=20000):
    tiers = tiers or {l: LANGS[l] for l in langs}
    x = [TIER_NUM[tiers[l]] for l in langs]
    y = [rate[l] for l in langs]
    rx, ry = _ranks(x), _ranks(y)
    rho = _pearson(rx, ry)
    rng = random.Random(SEED)
    cnt = 0
    perm = rx[:]
    for _ in range(nperm):
        rng.shuffle(perm)
        if abs(_pearson(perm, ry)) >= abs(rho) - 1e-12:
            cnt += 1
    return {"rho": rho, "perm_p": cnt / nperm, "n_perm": nperm}


def tier_means(rate, tiers=None, langs=LANG_ORDER):
    tiers = tiers or {l: LANGS[l] for l in langs}
    acc = defaultdict(list)
    for l in langs:
        acc[tiers[l]].append(rate[l])
    return {t: sum(v) / len(v) for t, v in acc.items()}


# =============================================================================
# A. Design weights (Horvitz-Thompson)
# =============================================================================
def ht_mass_rate(lang, pred, masskey="_dm", denom="reachable"):
    """Design-weighted (HT) share of corpus mass under `pred`.

    denom='reachable' : blocked mass / reachable mass   (both HT-inflated)
    denom='sampled'   : blocked mass / all-sampled mass (unreachable counted as not blocked)
    denom='census'    : blocked mass / total retained census mass (known denominator)
    """
    ld = LD[lang]; w = ld["w_tail"]
    num = den = 0.0
    for r in ld["res"]:
        wt = 1.0 if r["_head"] else w
        m = r[masskey]
        reach = r.get("status") == 200
        if reach and pred(r):
            num += wt * m
        if denom == "reachable":
            if reach:
                den += wt * m
        elif denom == "sampled":
            den += wt * m
    if denom == "census":
        den = float(sum(ld["dm"].values()) if masskey == "_dm" else sum(ld["tm"].values()))
    return num / den if den else 0.0


def sample_mass_rate(lang, pred, masskey="_dm"):
    """The paper's estimator: unweighted mass sum over sampled reachable domains."""
    ld = LD[lang]
    num = sum(r[masskey] for r in ld["reach"] if pred(r))
    den = sum(r[masskey] for r in ld["reach"])
    return num / den if den else 0.0


def head_only_census_rate(lang, pred, masskey="_dm", denom="reachable"):
    """Census quantity: among the top-175 domains (all observed, prob 1)."""
    ld = LD[lang]
    head = [r for r in ld["res"] if r["_head"]]
    num = sum(r[masskey] for r in head if r.get("status") == 200 and pred(r))
    if denom == "reachable":
        den = sum(r[masskey] for r in head if r.get("status") == 200)
    else:
        den = sum(r[masskey] for r in head)
    return num / den if den else 0.0


design = {"per_lang": {}, "estimator_variants_english": {}, "notes": {}}
for lang in LANG_ORDER:
    ld = LD[lang]
    tot_ret_dm = sum(ld["dm"].values()); tot_ret_tm = sum(ld["tm"].values())
    head_dm = sum(ld["dm"][d] for d in ld["sampled"][:N_HEAD])
    head_tm = sum(ld["tm"][d] for d in ld["sampled"][:N_HEAD])
    design["per_lang"][lang] = {
        "tier": ld["tier"],
        "n_domains_census": ld["n_domains"],
        "N_retained": ld["n_ret"],
        "cap_bound": ld["n_domains"] > CENSUS_CAP,
        "domains_dropped_by_cap": max(0, ld["n_domains"] - CENSUS_CAP),
        "docs_streamed": ld["docs"],
        "docs_cap_bound": ld["capped"],
        "tail_weight": ld["w_tail"],
        "tail_inclusion_prob": N_HEAD / float(ld["n_ret"] - N_HEAD),
        "head175_share_of_retained_docmass": head_dm / tot_ret_dm,
        "head175_share_of_retained_tokmass": head_tm / tot_ret_tm,
        "retained_docmass_share_of_streamed_docs": tot_ret_dm / ld["docs"],
        "retained_docmass_total": tot_ret_dm,
        # unweighted (paper) vs design-weighted
        "sample_mass_doc_any15": sample_mass_rate(lang, blocks_any15, "_dm"),
        "sample_mass_tok_any15": sample_mass_rate(lang, blocks_any15, "_tm"),
        "design_wt_mass_doc_any15": ht_mass_rate(lang, blocks_any15, "_dm"),
        "design_wt_mass_tok_any15": ht_mass_rate(lang, blocks_any15, "_tm"),
        "design_wt_mass_doc_any15_denom_sampled": ht_mass_rate(lang, blocks_any15, "_dm", "sampled"),
        "design_wt_mass_doc_any15_denom_census": ht_mass_rate(lang, blocks_any15, "_dm", "census"),
        "head_only_census_mass_doc_any15": head_only_census_rate(lang, blocks_any15, "_dm"),
        "head_only_census_mass_doc_any15_denom_all_head": head_only_census_rate(
            lang, blocks_any15, "_dm", "all"),
        "head_only_census_mass_tok_any15": head_only_census_rate(lang, blocks_any15, "_tm"),
    }

# Reviewer A1aw reports English falling from 62.4% to 39.2% under design weights.
_eng_variants = {
    "HT_blocked_over_reachable_docmass": ht_mass_rate("eng_Latn", blocks_any15, "_dm", "reachable"),
    "HT_blocked_over_all_sampled_docmass": ht_mass_rate("eng_Latn", blocks_any15, "_dm", "sampled"),
    "HT_blocked_over_retained_census_docmass": ht_mass_rate("eng_Latn", blocks_any15, "_dm", "census"),
    "HT_blocked_over_reachable_tokmass": ht_mass_rate("eng_Latn", blocks_any15, "_tm", "reachable"),
    "HT_blocked_over_all_sampled_tokmass": ht_mass_rate("eng_Latn", blocks_any15, "_tm", "sampled"),
    "unweighted_sample_mass_docmass_paper": sample_mass_rate("eng_Latn", blocks_any15, "_dm"),
    "head_only_census_docmass": head_only_census_rate("eng_Latn", blocks_any15, "_dm"),
    "tail_only_sample_docmass": None,
    "domain_level_unweighted": None,
    "domain_level_design_weighted": None,
}
_ld = LD["eng_Latn"]
_tail_reach = [r for r in _ld["reach"] if not r["_head"]]
_eng_variants["tail_only_sample_docmass"] = (
    sum(r["_dm"] for r in _tail_reach if blocks_any15(r)) / max(1, sum(r["_dm"] for r in _tail_reach)))
_eng_variants["domain_level_unweighted"] = (
    sum(1 for r in _ld["reach"] if blocks_any15(r)) / len(_ld["reach"]))
_wnum = sum((1.0 if r["_head"] else _ld["w_tail"]) for r in _ld["reach"] if blocks_any15(r))
_wden = sum((1.0 if r["_head"] else _ld["w_tail"]) for r in _ld["reach"])
_eng_variants["domain_level_design_weighted"] = _wnum / _wden
_closest = min(((k, abs(v - 0.392)) for k, v in _eng_variants.items() if isinstance(v, float)),
               key=lambda kv: kv[1])
design["estimator_variants_english"] = dict(_eng_variants)
design["estimator_variants_english"]["reviewer_A1aw_target"] = 0.392
design["estimator_variants_english"]["closest_variant"] = _closest[0]
design["estimator_variants_english"]["closest_variant_abs_diff"] = _closest[1]

# design-weighted tier means + cluster tests
dw_doc = {l: design["per_lang"][l]["design_wt_mass_doc_any15"] for l in LANG_ORDER}
dw_tok = {l: design["per_lang"][l]["design_wt_mass_tok_any15"] for l in LANG_ORDER}
sm_doc = {l: design["per_lang"][l]["sample_mass_doc_any15"] for l in LANG_ORDER}
sm_tok = {l: design["per_lang"][l]["sample_mass_tok_any15"] for l in LANG_ORDER}
mass_w = {l: float(sum(r["_dm"] for r in LD[l]["reach"])) for l in LANG_ORDER}
n_reach_w = {l: float(len(LD[l]["reach"])) for l in LANG_ORDER}

design["tier_means"] = {
    "sample_mass_doc (paper)": tier_means(sm_doc),
    "sample_mass_tok (paper)": tier_means(sm_tok),
    "design_weighted_doc": tier_means(dw_doc),
    "design_weighted_tok": tier_means(dw_tok),
}
design["cluster_tests"] = {
    "sample_mass_doc_high_vs_low": cluster_exact(HIGH, LOW, sm_doc, n_reach_w),
    "sample_mass_doc_high_vs_rest": cluster_exact(HIGH, MID + LOW, sm_doc, n_reach_w),
    "design_weighted_doc_high_vs_low": cluster_exact(HIGH, LOW, dw_doc, n_reach_w),
    "design_weighted_doc_high_vs_rest": cluster_exact(HIGH, MID + LOW, dw_doc, n_reach_w),
    "design_weighted_tok_high_vs_low": cluster_exact(HIGH, LOW, dw_tok, n_reach_w),
    "design_weighted_tok_high_vs_rest": cluster_exact(HIGH, MID + LOW, dw_tok, n_reach_w),
}
design["spearman"] = {
    "sample_mass_doc": spearman_tier(sm_doc),
    "design_weighted_doc": spearman_tier(dw_doc),
    "design_weighted_tok": spearman_tier(dw_tok),
}
design["notes"] = {
    "retained_docmass_share_of_streamed_docs":
        "sum of retained doc_mass / docs_streamed. Below 1 both because the 20k cap drops "
        "tail domains and because some streamed docs have no parseable hostname.",
    "tail_weight": "(N_retained - 175)/175; N_retained = len(census doc_mass), capped at 20000.",
    "head_only_census": "not an estimate: all 175 head domains were fetched (inclusion prob 1).",
}

# =============================================================================
# B/C. Crawler-policy variants
# =============================================================================
policy_block = {}
for pname, pred in POLICIES.items():
    per_lang = {}
    dom_rate, smd, smt, dwd, dwt = {}, {}, {}, {}, {}
    for lang in LANG_ORDER:
        reach = LD[lang]["reach"]
        flags = [1 if pred(r) else 0 for r in reach]
        dom_rate[lang] = sum(flags) / len(flags)
        smd[lang] = sample_mass_rate(lang, pred, "_dm")
        smt[lang] = sample_mass_rate(lang, pred, "_tm")
        dwd[lang] = ht_mass_rate(lang, pred, "_dm")
        dwt[lang] = ht_mass_rate(lang, pred, "_tm")
        per_lang[lang] = {
            "tier": LANGS[lang], "n_reach": len(reach), "n_block": sum(flags),
            "domain_rate": dom_rate[lang], "domain_rate_ci95": boot_ci(flags),
            "sample_mass_doc": smd[lang], "sample_mass_tok": smt[lang],
            "design_wt_mass_doc": dwd[lang], "design_wt_mass_tok": dwt[lang],
        }
    pooled = {}
    for t, ls in (("high", HIGH), ("mid", MID), ("low", LOW)):
        num = sum(sum(1 for r in LD[l]["reach"] if pred(r)) for l in ls)
        den = sum(len(LD[l]["reach"]) for l in ls)
        pooled[t] = {"rate": num / den, "n": den, "n_block": num}
    policy_block[pname] = {
        "per_lang": per_lang,
        "tier_means_domain": tier_means(dom_rate),
        "tier_means_sample_mass_doc": tier_means(smd),
        "tier_means_design_wt_doc": tier_means(dwd),
        "tier_means_design_wt_tok": tier_means(dwt),
        "pooled_domain_rate": pooled,
        "cluster_domain_high_vs_low": cluster_exact(HIGH, LOW, dom_rate, n_reach_w),
        "cluster_domain_high_vs_rest": cluster_exact(HIGH, MID + LOW, dom_rate, n_reach_w),
        "cluster_design_wt_doc_high_vs_low": cluster_exact(HIGH, LOW, dwd, n_reach_w),
        "cluster_design_wt_doc_high_vs_rest": cluster_exact(HIGH, MID + LOW, dwd, n_reach_w),
        "cluster_sample_mass_doc_high_vs_low": cluster_exact(HIGH, LOW, smd, n_reach_w),
        "spearman_domain": spearman_tier(dom_rate),
        "spearman_design_wt_doc": spearman_tier(dwd),
    }

# =============================================================================
# D. Azerbaijani robustness
# =============================================================================
dom_any15 = {l: sum(1 for r in LD[l]["reach"] if blocks_any15(r)) / len(LD[l]["reach"])
             for l in LANG_ORDER}

azj = {}
# (a) exclude azj
langs_ex = [l for l in LANG_ORDER if l != "azj_Latn"]
mid_ex = [l for l in MID if l != "azj_Latn"]
azj["exclude"] = {
    "tier_means_domain": tier_means(dom_any15, langs=langs_ex),
    "tier_means_sample_mass_doc": tier_means(sm_doc, langs=langs_ex),
    "tier_means_design_wt_doc": tier_means(dw_doc, langs=langs_ex),
    "cluster_domain_high_vs_low": cluster_exact(HIGH, LOW, dom_any15, n_reach_w),
    "cluster_domain_high_vs_rest": cluster_exact(HIGH, mid_ex + LOW, dom_any15, n_reach_w),
    "cluster_design_wt_doc_high_vs_low": cluster_exact(HIGH, LOW, dw_doc, n_reach_w),
    "cluster_design_wt_doc_high_vs_rest": cluster_exact(HIGH, mid_ex + LOW, dw_doc, n_reach_w),
    "spearman_domain": spearman_tier(dom_any15, langs=langs_ex),
    "spearman_design_wt_doc": spearman_tier(dw_doc, langs=langs_ex),
    "note": "azj is mid tier, so high-vs-low is numerically unchanged; only high-vs-rest, "
            "the mid tier mean and the Spearman rank vector move.",
}
# (b) move azj to low
tiers_mv = {l: ("low" if l == "azj_Latn" else LANGS[l]) for l in LANG_ORDER}
LOW_MV = LOW + ["azj_Latn"]
MID_MV = [l for l in MID if l != "azj_Latn"]
azj["move_to_low"] = {
    "tier_means_domain": tier_means(dom_any15, tiers=tiers_mv),
    "tier_means_sample_mass_doc": tier_means(sm_doc, tiers=tiers_mv),
    "tier_means_design_wt_doc": tier_means(dw_doc, tiers=tiers_mv),
    "cluster_domain_high_vs_low": cluster_exact(HIGH, LOW_MV, dom_any15, n_reach_w),
    "cluster_domain_high_vs_rest": cluster_exact(HIGH, MID_MV + LOW_MV, dom_any15, n_reach_w),
    "cluster_design_wt_doc_high_vs_low": cluster_exact(HIGH, LOW_MV, dw_doc, n_reach_w),
    "cluster_design_wt_doc_high_vs_rest": cluster_exact(HIGH, MID_MV + LOW_MV, dw_doc, n_reach_w),
    "cluster_sample_mass_doc_high_vs_low": cluster_exact(HIGH, LOW_MV, sm_doc, n_reach_w),
    "spearman_domain": spearman_tier(dom_any15, tiers=tiers_mv),
    "spearman_design_wt_doc": spearman_tier(dw_doc, tiers=tiers_mv),
}
azj["baseline"] = {
    "tier_means_domain": tier_means(dom_any15),
    "cluster_domain_high_vs_low": cluster_exact(HIGH, LOW, dom_any15, n_reach_w),
    "cluster_domain_high_vs_rest": cluster_exact(HIGH, MID + LOW, dom_any15, n_reach_w),
}

# =============================================================================
# E. Conditional on naming
# =============================================================================
cond = {"per_lang": {}, "pooled": {}}
cond_rate, cond_w = {}, {}
for lang in LANG_ORDER:
    reach = LD[lang]["reach"]
    named = [r for r in reach if names_ai(r)]
    nb = sum(1 for r in named if blocks_any15(r))
    cond_rate[lang] = nb / max(1, len(named))
    cond_w[lang] = float(len(named))
    cond["per_lang"][lang] = {
        "tier": LANGS[lang], "n_reach": len(reach), "n_named": len(named),
        "n_blocked_given_named": nb,
        "cond_block_rate": cond_rate[lang],
        "cond_block_ci95": boot_ci([1 if blocks_any15(r) else 0 for r in named]),
        "named_rate": len(named) / len(reach),
    }
pool_named = defaultdict(list)
for lang in LANG_ORDER:
    for r in LD[lang]["reach"]:
        if names_ai(r):
            pool_named[LANGS[lang]].append(1 if blocks_any15(r) else 0)
for t, v in pool_named.items():
    cond["pooled"][t] = {"rate": sum(v) / len(v), "n": len(v), "n_block": sum(v)}

_rng = random.Random(SEED + 99)
_h, _l = pool_named["high"], pool_named["low"]
_gaps = []
for _ in range(NBOOT):
    a = sum(_h[_rng.randrange(len(_h))] for _ in range(len(_h))) / len(_h)
    b = sum(_l[_rng.randrange(len(_l))] for _ in range(len(_l))) / len(_l)
    _gaps.append(a - b)
_gaps.sort()
_abs = sorted(abs(g) for g in _gaps)
ph, nh = cond["pooled"]["high"]["rate"], cond["pooled"]["high"]["n"]
pl, nl = cond["pooled"]["low"]["rate"], cond["pooled"]["low"]["n"]
se = math.sqrt(ph * (1 - ph) / nh + pl * (1 - pl) / nl)
cond["pooled_gap_high_minus_low"] = {
    "gap": ph - pl,
    "boot_ci95_signed": [_gaps[int(0.025 * NBOOT)], _gaps[int(0.975 * NBOOT)]],
    "boot_ci95_abs": [_abs[int(0.025 * NBOOT)], _abs[int(0.975 * NBOOT)]],
    "wald_ci95_abs_paper": [abs(ph - pl) - 1.96 * se, abs(ph - pl) + 1.96 * se],
}
cond["cluster_high_vs_low"] = cluster_exact(HIGH, LOW, cond_rate, cond_w)
cond["cluster_high_vs_rest"] = cluster_exact(HIGH, MID + LOW, cond_rate, cond_w)
cond["tier_means_language_level"] = tier_means(cond_rate)
cond["spearman"] = spearman_tier(cond_rate)

# =============================================================================
# F. Mechanism proxies
# =============================================================================
def _conv_match(key, c):
    """applebot-extended is an AI agent, not a conventional crawler."""
    if c not in key:
        return False
    if c == "applebot" and key.strip() == "applebot-extended":
        return False
    return True


def conventional_hits(r):
    return {c for k in r["ai_rules"].keys() for c in CONVENTIONAL if _conv_match(k, c)}


def names_conventional(r):
    return bool(conventional_hits(r))


def n_directive_lines(body):
    n = 0
    for raw in body.splitlines():
        line = raw.split("#")[0].strip()
        if line and ":" in line:
            n += 1
    return n


def n_ua_groups(body):
    return sum(1 for raw in body.splitlines()
               if re.match(r"(?i)\s*user-agent\s*:", raw.split("#")[0]))


def norm_directives(body):
    out = []
    for raw in body.splitlines():
        line = raw.split("#")[0].strip().lower()
        if not line:
            continue
        line = re.sub(r"\s*:\s*", ": ", line)
        line = re.sub(r"\s+", " ", line)
        if line.startswith("sitemap:") or line.startswith("host:") or line.startswith("crawl-delay:"):
            continue
        out.append(line)
    return out


WP_DEFAULT = {"user-agent: *", "disallow: /wp-admin/", "allow: /wp-admin/admin-ajax.php"}
ALLOW_ALL = {"user-agent: *", "disallow:"}


def default_flags(r):
    body = r.get("body") or ""
    ct = (r.get("ct") or "").lower()
    low = body.lower()
    nd = set(norm_directives(body))
    is_html = ("text/html" in ct) or body.lstrip()[:1] == "<"
    return {
        "empty": body.strip() == "",
        "html": is_html,
        "allow_all_only": nd == ALLOW_ALL,
        "wordpress_default": nd == WP_DEFAULT,
        "blogger_default": ("mediapartners-google" in low and "disallow: /search" in low),
        "shopify": "# we use shopify" in low,
        "wix": "wix" in low,
        "squarespace": "squarespace" in low,
    }


STOCK_KEYS = ["wordpress_default", "blogger_default", "shopify", "wix", "squarespace"]
TRIVIAL_KEYS = ["empty", "html", "allow_all_only"]

GENERIC_CC = {"io", "co", "me", "tv", "cc", "ai", "ly", "fm", "to", "gg", "sh", "st", "am", "is", "ws"}
ORG_EDU_GOV_TLD = {"org", "edu", "gov", "mil", "int"}
SLD_PUBLIC = {"ac", "edu", "gov", "go", "gob", "gouv", "or", "org", "mil"}


def tld_class(dom):
    parts = dom.split(".")
    if len(parts) < 2:
        return "other"
    tld = parts[-1].lower()
    sld = parts[-2].lower() if len(parts) >= 2 else ""
    if tld in ORG_EDU_GOV_TLD:
        return "org_edu_gov"
    if len(parts) >= 3 and sld in SLD_PUBLIC:
        return "org_edu_gov"
    if len(tld) == 2 and tld not in GENERIC_CC:
        return "ccTLD"
    return "gTLD"


KEYWORD_CLASSES = {
    "news": r"news|berita|haber|tin|habar|nuacht|xewer",
    "blog": r"blog",
    "gov": r"gov|gob|go\.|gouv",
    "edu": r"edu|ac\.|univ",
    "shop": r"shop|store|toko",
    "wiki": r"wiki",
    "forum": r"forum",
}
PLATFORMS = ["blogspot.", "wordpress.com", "github.io", "wixsite", "medium.com",
             "substack", "tumblr", "weebly"]


def rate(rows, pred):
    if not rows:
        return {"rate": None, "n": 0, "k": 0}
    k = sum(1 for r in rows if pred(r))
    return {"rate": k / len(rows), "n": len(rows), "k": k}


mech = {}

# -- F1 conventional vs AI naming ---------------------------------------------
conv_rate, ai_name_rate = {}, {}
f1 = {"per_lang": {}, "pooled_tier": {}}
for lang in LANG_ORDER:
    reach = [r for r in LD[lang]["reach"] if r.get("body") is not None]
    conv = sum(1 for r in reach if names_conventional(r))
    ain = sum(1 for r in reach if names_ai(r))
    conv_rate[lang] = conv / len(reach)
    ai_name_rate[lang] = ain / len(reach)
    both = [r for r in reach if names_conventional(r)]
    f1["per_lang"][lang] = {
        "tier": LANGS[lang], "n_reach_with_body": len(reach),
        "share_names_conventional": conv / len(reach),
        "share_names_conventional_ci95": boot_ci([1 if names_conventional(r) else 0 for r in reach]),
        "share_names_ai": ain / len(reach),
        "ratio_ai_over_conventional": (ain / conv) if conv else None,
        "n_names_conventional": conv,
        "among_conventional_namers_share_names_ai": rate(both, names_ai),
        "among_conventional_namers_share_blocks_ai": rate(both, blocks_any15),
    }
for t, ls in (("high", HIGH), ("mid", MID), ("low", LOW)):
    rows = [r for l in ls for r in LD[l]["reach"] if r.get("body") is not None]
    conv_rows = [r for r in rows if names_conventional(r)]
    f1["pooled_tier"][t] = {
        "n": len(rows),
        "share_names_conventional": rate(rows, names_conventional),
        "share_names_ai": rate(rows, names_ai),
        "ratio_ai_over_conventional": (rate(rows, names_ai)["rate"] /
                                       rate(rows, names_conventional)["rate"]),
        "among_conventional_namers_share_names_ai": rate(conv_rows, names_ai),
        "among_conventional_namers_share_blocks_ai": rate(conv_rows, blocks_any15),
    }
f1["cluster_conventional_high_vs_low"] = cluster_exact(HIGH, LOW, conv_rate, n_reach_w)
f1["cluster_conventional_high_vs_rest"] = cluster_exact(HIGH, MID + LOW, conv_rate, n_reach_w)
f1["spearman_conventional"] = spearman_tier(conv_rate)
# AI naming conditional on conventional naming, as a language-level rate
cond_conv_rate, cond_conv_w = {}, {}
for lang in LANG_ORDER:
    rows = [r for r in LD[lang]["reach"] if r.get("body") is not None and names_conventional(r)]
    cond_conv_rate[lang] = (sum(1 for r in rows if names_ai(r)) / len(rows)) if rows else 0.0
    cond_conv_w[lang] = float(len(rows))
f1["cluster_ai_naming_given_conventional_high_vs_low"] = cluster_exact(
    HIGH, LOW, cond_conv_rate, cond_conv_w)
f1["per_conventional_bot_share_by_tier"] = {}
for t, ls in (("high", HIGH), ("mid", MID), ("low", LOW)):
    rows = [r for l in ls for r in LD[l]["reach"] if r.get("body") is not None]
    c = Counter()
    for r in rows:
        for h in conventional_hits(r):
            c[h] += 1
    f1["per_conventional_bot_share_by_tier"][t] = {
        b: {"n": c[b], "share": c[b] / len(rows)} for b in CONVENTIONAL}
mech["conventional_bot_naming"] = f1

# -- F2 stock defaults ---------------------------------------------------------
f2 = {"per_lang": {}, "pooled_tier": {}}
for lang in LANG_ORDER:
    reach = [r for r in LD[lang]["reach"] if r.get("body") is not None]
    fl = {r["domain"]: default_flags(r) for r in reach}
    d = {"tier": LANGS[lang], "n": len(reach)}
    for k in STOCK_KEYS + TRIVIAL_KEYS:
        d[k] = sum(1 for r in reach if fl[r["domain"]][k]) / len(reach)
    stock = [r for r in reach if any(fl[r["domain"]][k] for k in STOCK_KEYS)]
    trivial = [r for r in reach if any(fl[r["domain"]][k] for k in TRIVIAL_KEYS)]
    nondef = [r for r in reach
              if not any(fl[r["domain"]][k] for k in STOCK_KEYS + TRIVIAL_KEYS)]
    d["share_stock_cms_default"] = len(stock) / len(reach)
    d["share_trivial_or_nonpolicy"] = len(trivial) / len(reach)
    d["share_non_default"] = len(nondef) / len(reach)
    d["optout_within_non_default"] = rate(nondef, blocks_any15)
    d["optout_within_stock_default"] = rate(stock, blocks_any15)
    d["optout_overall"] = rate(reach, blocks_any15)
    f2["per_lang"][lang] = d
for t, ls in (("high", HIGH), ("mid", MID), ("low", LOW)):
    reach = [r for l in ls for r in LD[l]["reach"] if r.get("body") is not None]
    fl = [default_flags(r) for r in reach]
    d = {"n": len(reach)}
    for k in STOCK_KEYS + TRIVIAL_KEYS:
        d[k] = sum(1 for f in fl if f[k]) / len(reach)
    stock = [r for r, f in zip(reach, fl) if any(f[k] for k in STOCK_KEYS)]
    trivial = [r for r, f in zip(reach, fl) if any(f[k] for k in TRIVIAL_KEYS)]
    nondef = [r for r, f in zip(reach, fl)
              if not any(f[k] for k in STOCK_KEYS + TRIVIAL_KEYS)]
    d["share_stock_cms_default"] = len(stock) / len(reach)
    d["share_trivial_or_nonpolicy"] = len(trivial) / len(reach)
    d["share_non_default"] = len(nondef) / len(reach)
    d["optout_within_non_default"] = rate(nondef, blocks_any15)
    d["optout_within_stock_default"] = rate(stock, blocks_any15)
    d["naming_within_non_default"] = rate(nondef, names_ai)
    f2["pooled_tier"][t] = d
nondef_rate = {}
for lang in LANG_ORDER:
    reach = [r for r in LD[lang]["reach"] if r.get("body") is not None]
    nd = [r for r in reach if not any(default_flags(r)[k] for k in STOCK_KEYS + TRIVIAL_KEYS)]
    nondef_rate[lang] = (sum(1 for r in nd if blocks_any15(r)) / len(nd)) if nd else 0.0
f2["cluster_optout_within_non_default_high_vs_low"] = cluster_exact(
    HIGH, LOW, nondef_rate, n_reach_w)
mech["stock_defaults"] = f2

# -- F3 sophistication ---------------------------------------------------------
def med(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


f3 = {"per_lang": {}, "pooled_tier": {}}
for scope, items in (("per_lang", [(l, [l]) for l in LANG_ORDER]),
                     ("pooled_tier", [("high", HIGH), ("mid", MID), ("low", LOW)])):
    for key, ls in items:
        rows = [r for l in ls for r in LD[l]["reach"] if r.get("body") is not None]
        dl = [n_directive_lines(r["body"]) for r in rows]
        ug = [n_ua_groups(r["body"]) for r in rows]
        bl = [len(r["body"]) for r in rows]
        nag = [len(r["ai_rules"]) for r in rows]
        f3[scope][key] = {
            "n": len(rows),
            "median_directive_lines": med(dl), "mean_directive_lines": sum(dl) / len(dl),
            "median_ua_groups": med(ug), "mean_ua_groups": sum(ug) / len(ug),
            "median_body_len": med(bl), "mean_body_len": sum(bl) / len(bl),
            "median_named_agents": med(nag), "mean_named_agents": sum(nag) / len(nag),
            "share_body_truncated_20k": sum(1 for b in bl if b >= 20000) / len(bl),
        }
        if scope == "per_lang":
            f3[scope][key]["tier"] = LANGS[key]
mech["sophistication"] = f3

# -- F4 Allow-only AI naming ---------------------------------------------------
def allow_only_ai(r):
    return names_ai(r) and not blocks_any15(r)


f4 = {"per_lang": {}, "pooled_tier": {}}
for lang in LANG_ORDER:
    reach = LD[lang]["reach"]
    f4["per_lang"][lang] = {"tier": LANGS[lang], **rate(reach, allow_only_ai)}
for t, ls in (("high", HIGH), ("mid", MID), ("low", LOW)):
    rows = [r for l in ls for r in LD[l]["reach"]]
    f4["pooled_tier"][t] = rate(rows, allow_only_ai)
ao_rate = {l: f4["per_lang"][l]["rate"] for l in LANG_ORDER}
f4["cluster_high_vs_low"] = cluster_exact(HIGH, LOW, ao_rate, n_reach_w)
mech["allow_only_ai_naming"] = f4

# -- F5 site-type proxies ------------------------------------------------------
f5 = {"tld_class": {}, "keyword_class": {}, "platform_hosted": {}}
for t, ls in (("high", HIGH), ("mid", MID), ("low", LOW)):
    rows = [r for l in ls for r in LD[l]["reach"]]
    byc = defaultdict(list)
    for r in rows:
        byc[tld_class(r["domain"])].append(r)
    f5["tld_class"][t] = {c: {**rate(v, blocks_any15), "names_ai": rate(v, names_ai)["rate"],
                              "small_n": len(v) < 20}
                          for c, v in sorted(byc.items())}
    kc = {}
    for cname, pat in KEYWORD_CLASSES.items():
        rx = re.compile(pat)
        v = [r for r in rows if rx.search(r["domain"])]
        kc[cname] = {**rate(v, blocks_any15), "names_ai": rate(v, names_ai)["rate"],
                     "small_n": len(v) < 20}
    anyrx = re.compile("|".join(KEYWORD_CLASSES.values()))
    v = [r for r in rows if not anyrx.search(r["domain"])]
    kc["_none"] = {**rate(v, blocks_any15), "names_ai": rate(v, names_ai)["rate"],
                   "small_n": len(v) < 20}
    f5["keyword_class"][t] = kc
    pv = [r for r in rows if any(p in r["domain"] for p in PLATFORMS)]
    f5["platform_hosted"][t] = {
        **rate(pv, blocks_any15),
        "names_ai": rate(pv, names_ai)["rate"],
        "small_n": len(pv) < 20,
        "by_platform": {p: rate([r for r in rows if p in r["domain"]], blocks_any15)
                        for p in PLATFORMS},
        "non_platform_optout": rate([r for r in rows
                                     if not any(p in r["domain"] for p in PLATFORMS)],
                                    blocks_any15),
    }
f5["per_lang_tld_class"] = {}
for lang in LANG_ORDER:
    byc = defaultdict(list)
    for r in LD[lang]["reach"]:
        byc[tld_class(r["domain"])].append(r)
    f5["per_lang_tld_class"][lang] = {"tier": LANGS[lang],
                                      **{c: rate(v, blocks_any15) for c, v in sorted(byc.items())}}
f5["notes"] = ("Keyword classes are non-exclusive substring matches on the hostname; "
               "'tin' (Vietnamese 'tin tuc' = news) also matches 'bulletin', 'tintin', etc. "
               "TLD classes: org/edu/gov/mil/int or a public 2nd-level (ac./edu./gov./go./gob./"
               "gouv./or.) => org_edu_gov; 2-letter TLD not in the generic-use set "
               "(io,co,me,tv,cc,ai,ly,fm,to,gg,sh,st,am,is,ws) => ccTLD; else gTLD.")
mech["site_type"] = f5

# =============================================================================
# G. Validation recount
# =============================================================================
vl = json.load(open(os.path.join(D, "valid_labels.json")))
agree_field = sum(1 for x in vl if x.get("agree"))
agree_recomputed = sum(1 for x in vl if bool(x["manual_block"]) == bool(x["parser_block"]))
disagreements = [
    {"id": x["id"], "domain": x["domain"], "manual_block": x["manual_block"],
     "parser_block": x["parser_block"], "confidence": x.get("confidence"),
     "note": x.get("note"), "agree_field": x.get("agree")}
    for x in vl if bool(x["manual_block"]) != bool(x["parser_block"])
]
field_inconsistent = [
    {"id": x["id"], "domain": x["domain"], "agree_field": x.get("agree"),
     "manual_block": x["manual_block"], "parser_block": x["parser_block"]}
    for x in vl if bool(x.get("agree")) != (bool(x["manual_block"]) == bool(x["parser_block"]))
]
validation = {
    "n_labelled": len(vl),
    "agree_from_stored_field": agree_field,
    "agree_recomputed_from_labels": agree_recomputed,
    "n_disagreements": len(disagreements),
    "disagreements": disagreements,
    "stored_agree_field_inconsistent_rows": field_inconsistent,
    "accuracy": agree_recomputed / len(vl),
    "confidence_counts": dict(Counter(x.get("confidence") for x in vl)),
}

# =============================================================================
# H. Reachability failure breakdown
# =============================================================================
reach_fail = {"per_lang": {}, "pooled_tier": {}, "totals": {}}
for lang in LANG_ORDER:
    res = LD[lang]["res"]
    fails = [r for r in res if r.get("status") != 200]
    c = Counter(coarse_fail(classify_err_fine(r)) for r in fails)
    fine = Counter(classify_err_fine(r) for r in fails)
    reach_fail["per_lang"][lang] = {
        "tier": LANGS[lang], "n_sampled": len(res), "n_reach": len(LD[lang]["reach"]),
        "reach_rate": len(LD[lang]["reach"]) / len(res),
        "n_fail": len(fails),
        "counts": dict(c.most_common()),
        "shares_of_failures": {k: v / len(fails) for k, v in c.most_common()},
        "shares_of_sampled": {k: v / len(res) for k, v in c.most_common()},
        "fine_counts": dict(fine.most_common()),
        "http_404_count": c.get("http_404", 0),
        "http_403_count": c.get("http_403", 0),
        "dns_count": c.get("dns", 0),
        "reach_rate_counting_404_as_observed":
            (len(LD[lang]["reach"]) + c.get("http_404", 0) + c.get("http_410", 0)) / len(res),
    }
for t, ls in (("high", HIGH), ("mid", MID), ("low", LOW)):
    res = [r for l in ls for r in LD[l]["res"]]
    fails = [r for r in res if r.get("status") != 200]
    c = Counter(coarse_fail(classify_err_fine(r)) for r in fails)
    reach_fail["pooled_tier"][t] = {
        "n_sampled": len(res), "n_fail": len(fails),
        "counts": dict(c.most_common()),
        "shares_of_failures": {k: v / len(fails) for k, v in c.most_common()},
        "shares_of_sampled": {k: v / len(res) for k, v in c.most_common()},
        "http_404_share_of_failures": c.get("http_404", 0) / len(fails),
        "http_404_share_of_sampled": c.get("http_404", 0) / len(res),
    }
_allres = [r for l in LANG_ORDER for r in LD[l]["res"]]
_allfail = [r for r in _allres if r.get("status") != 200]
reach_fail["totals"] = {
    "n_sampled": len(_allres), "n_reach": len(_allres) - len(_allfail), "n_fail": len(_allfail),
    "counts": dict(Counter(coarse_fail(classify_err_fine(r)) for r in _allfail).most_common()),
    "fine_counts": dict(Counter(classify_err_fine(r) for r in _allfail).most_common()),
}
# does treating 404/410 as "observed, no policy" change the gradient?
reach_404 = {l: reach_fail["per_lang"][l]["reach_rate_counting_404_as_observed"]
             for l in LANG_ORDER}
optout_404 = {}
for lang in LANG_ORDER:
    res = LD[lang]["res"]
    denom = [r for r in res if r.get("status") == 200 or
             coarse_fail(classify_err_fine(r)) in ("http_404", "http_410")]
    optout_404[lang] = sum(1 for r in denom if r.get("status") == 200 and blocks_any15(r)) / len(denom)
reach_fail["optout_with_404_in_denominator"] = {
    "per_lang": optout_404,
    "tier_means": tier_means(optout_404),
    "cluster_high_vs_low": cluster_exact(HIGH, LOW, optout_404, n_reach_w),
    "cluster_high_vs_rest": cluster_exact(HIGH, MID + LOW, optout_404, n_reach_w),
    "spearman": spearman_tier(optout_404),
    "note": "analysis.py treats every non-200 as unreachable. A 404 is arguably an observed "
            "policy state (no robots.txt => no restrictions). This row puts 404/410 into the "
            "denominator as non-blocking.",
}
reach_fail["cluster_reach_rate_high_vs_low"] = cluster_exact(
    HIGH, LOW, {l: reach_fail["per_lang"][l]["reach_rate"] for l in LANG_ORDER}, n_reach_w)
reach_fail["cluster_dns_share_high_vs_low"] = cluster_exact(
    HIGH, LOW,
    {l: reach_fail["per_lang"][l]["dns_count"] / reach_fail["per_lang"][l]["n_sampled"]
     for l in LANG_ORDER}, n_reach_w)

# =============================================================================
# Baseline replication block (so the revision file is self-contained)
# =============================================================================
baseline = {"per_lang": {}, "pooled": {}, "tier_means_sample_mass_doc": tier_means(sm_doc)}
for lang in LANG_ORDER:
    reach = LD[lang]["reach"]
    baseline["per_lang"][lang] = {
        "tier": LANGS[lang], "n_sampled": len(LD[lang]["res"]), "n_reach": len(reach),
        "reach_rate": len(reach) / len(LD[lang]["res"]),
        "optout_domain": dom_any15[lang],
        "optout_domain_ci95": boot_ci([1 if blocks_any15(r) else 0 for r in reach]),
        "names_ai": ai_name_rate[lang],
        "cond_block": cond_rate[lang], "n_named": int(cond_w[lang]),
        "sample_mass_doc": sm_doc[lang],
        "wildcard": sum(1 for r in reach if wildcard(r)) / len(reach),
    }
for t, ls in (("high", HIGH), ("mid", MID), ("low", LOW)):
    rows = [r for l in ls for r in LD[l]["reach"]]
    baseline["pooled"][t] = {
        "n": len(rows),
        "optout": rate(rows, blocks_any15)["rate"],
        "names": rate(rows, names_ai)["rate"],
        "wildcard_inclusive": rate(rows, blocks_any_or_wc)["rate"],
    }
baseline["cluster_high_vs_low_optout_domain"] = cluster_exact(HIGH, LOW, dom_any15, n_reach_w)
baseline["cluster_high_vs_rest_optout_domain"] = cluster_exact(HIGH, MID + LOW, dom_any15, n_reach_w)
baseline["spearman_optout_domain"] = spearman_tier(dom_any15)

# =============================================================================
RESULTS = {
    "meta": {
        "seed": SEED, "n_boot": NBOOT, "n_head": N_HEAD, "census_cap": CENSUS_CAP,
        "langs": LANGS, "ai_agents": AI_AGENTS, "conventional_agents": CONVENTIONAL,
        "generated_by": "analysis_revision.py",
    },
    "baseline_replication": baseline,
    "A_design_weights": design,
    "BC_policy_variants": policy_block,
    "D_azerbaijani": azj,
    "E_conditional_on_naming": cond,
    "F_mechanism_proxies": mech,
    "G_validation": validation,
    "H_reachability_failures": reach_fail,
}
json.dump(RESULTS, open(OUT, "w"), indent=1, sort_keys=False)
print(f"wrote {OUT}")

# ------------------------------------------------------------- console -------
def pct(x): return "  n/a" if x is None else f"{100*x:5.1f}"


print("\n=== A. design-weighted doc-mass opt-out (any-15) ===")
print(f"{'lang':10s} {'tier':5s} {'N_ret':>6s} {'wtail':>7s} {'headshr':>7s} "
      f"{'sampmass':>8s} {'dwdoc':>7s} {'dwtok':>7s} {'headcensus':>10s}")
for l in LANG_ORDER:
    d = design["per_lang"][l]
    print(f"{l:10s} {d['tier']:5s} {d['N_retained']:6d} {d['tail_weight']:7.1f} "
          f"{pct(d['head175_share_of_retained_docmass'])} {pct(d['sample_mass_doc_any15'])} "
          f"{pct(d['design_wt_mass_doc_any15'])} {pct(d['design_wt_mass_tok_any15'])} "
          f"{pct(d['head_only_census_mass_doc_any15'])}")
print("tier means:", json.dumps(design["tier_means"], indent=1))
print("english estimator variants:", json.dumps(
    {k: (round(v, 4) if isinstance(v, float) else v)
     for k, v in design["estimator_variants_english"].items()}, indent=1))
for k, v in design["cluster_tests"].items():
    print(f"  {k}: gap {v['gap_unweighted']:.3f} p_unw {v['p_unweighted']:.4f} "
          f"| wgap {v['gap_weighted']:.3f} p_w {v['p_weighted']:.4f}")

print("\n=== B. policy variants: tier means (domain / design-wt doc) + cluster p ===")
for p, blk in policy_block.items():
    tm_d = blk["tier_means_domain"]; tm_w = blk["tier_means_design_wt_doc"]
    cl = blk["cluster_domain_high_vs_low"]; cr = blk["cluster_domain_high_vs_rest"]
    print(f"{p:20s} dom H/M/L {pct(tm_d['high'])}/{pct(tm_d['mid'])}/{pct(tm_d['low'])} "
          f"dw H/M/L {pct(tm_w['high'])}/{pct(tm_w['mid'])}/{pct(tm_w['low'])} "
          f"p_HL {cl['p_unweighted']:.4f} p_HR {cr['p_unweighted']:.4f} "
          f"rho {blk['spearman_domain']['rho']:.3f} (p {blk['spearman_domain']['perm_p']:.4f})")

print("\n=== D. Azerbaijani ===")
for k in ("baseline", "exclude", "move_to_low"):
    v = azj[k]
    tm_ = v["tier_means_domain"]
    print(f"{k:12s} dom H/M/L {pct(tm_.get('high'))}/{pct(tm_.get('mid'))}/{pct(tm_.get('low'))} "
          f"HL p {v['cluster_domain_high_vs_low']['p_unweighted']:.4f} "
          f"HR p {v['cluster_domain_high_vs_rest']['p_unweighted']:.4f}")

print("\n=== E. conditional on naming ===")
for l in LANG_ORDER:
    c = cond["per_lang"][l]
    print(f"{l:10s} {c['tier']:5s} named {c['n_named']:3d} blocked {c['n_blocked_given_named']:3d} "
          f"rate {pct(c['cond_block_rate'])}")
print("pooled:", {t: (round(v['rate'], 3), v['n']) for t, v in cond["pooled"].items()})
print("gap CI:", cond["pooled_gap_high_minus_low"])

print("\n=== F1. conventional vs AI naming ===")
for t in ("high", "mid", "low"):
    v = mech["conventional_bot_naming"]["pooled_tier"][t]
    print(f"{t:5s} n {v['n']:4d} conv {pct(v['share_names_conventional']['rate'])} "
          f"ai {pct(v['share_names_ai']['rate'])} ratio {v['ratio_ai_over_conventional']:.3f} "
          f"| among conv-namers: names AI {pct(v['among_conventional_namers_share_names_ai']['rate'])} "
          f"blocks AI {pct(v['among_conventional_namers_share_blocks_ai']['rate'])} "
          f"(n={v['among_conventional_namers_share_names_ai']['n']})")
print("cluster conv HL:", mech["conventional_bot_naming"]["cluster_conventional_high_vs_low"])

print("\n=== F2. defaults ===")
for t in ("high", "mid", "low"):
    v = mech["stock_defaults"]["pooled_tier"][t]
    print(f"{t:5s} stock {pct(v['share_stock_cms_default'])} trivial {pct(v['share_trivial_or_nonpolicy'])} "
          f"nondefault {pct(v['share_non_default'])} optout|nondef {pct(v['optout_within_non_default']['rate'])} "
          f"(n={v['optout_within_non_default']['n']})")

print("\n=== F3. sophistication ===")
for t in ("high", "mid", "low"):
    v = mech["sophistication"]["pooled_tier"][t]
    print(f"{t:5s} med lines {v['median_directive_lines']:.1f} med UA {v['median_ua_groups']:.1f} "
          f"med len {v['median_body_len']:.0f} med agents {v['median_named_agents']:.1f}")

print("\n=== F1b. conventional vs AI naming, per language ===")
for l in LANG_ORDER:
    v = mech["conventional_bot_naming"]["per_lang"][l]
    a = v["among_conventional_namers_share_names_ai"]
    print(f"{l:10s} {v['tier']:5s} n {v['n_reach_with_body']:3d} conv "
          f"{pct(v['share_names_conventional'])} ai {pct(v['share_names_ai'])} "
          f"| conv-namers n {a['n']:3d} names AI {pct(a['rate'])}")

print("\n=== F2b. defaults, per language ===")
for l in LANG_ORDER:
    v = mech["stock_defaults"]["per_lang"][l]
    print(f"{l:10s} {v['tier']:5s} stock {pct(v['share_stock_cms_default'])} "
          f"wp {pct(v['wordpress_default'])} blogger {pct(v['blogger_default'])} "
          f"html {pct(v['html'])} empty {pct(v['empty'])} "
          f"nondef {pct(v['share_non_default'])} optout|nondef "
          f"{pct(v['optout_within_non_default']['rate'])} (n={v['optout_within_non_default']['n']})")

print("\n=== F4. Allow-only AI naming (names, blocks none) ===")
for t in ("high", "mid", "low"):
    v = mech["allow_only_ai_naming"]["pooled_tier"][t]
    print(f"{t:5s} {pct(v['rate'])} (k={v['k']}/n={v['n']})")

print("\n=== F5. site type: opt-out by class x tier (n; * = n<20) ===")
for grp in ("tld_class", "keyword_class"):
    print(f"-- {grp}")
    keys = sorted({k for t in ("high", "mid", "low") for k in mech["site_type"][grp][t]})
    for k in keys:
        cells = []
        for t in ("high", "mid", "low"):
            v = mech["site_type"][grp][t].get(k)
            if not v or not v["n"]:
                cells.append(f"{t}: -")
            else:
                cells.append(f"{t}: {pct(v['rate'])} (n={v['n']}){'*' if v['small_n'] else ''}")
        print(f"   {k:14s} " + "  ".join(cells))
print("-- platform-hosted")
for t in ("high", "mid", "low"):
    v = mech["site_type"]["platform_hosted"][t]
    print(f"   {t:5s} n={v['n']} optout {pct(v['rate'])}{'*' if v['small_n'] else ''} "
          f"| non-platform {pct(v['non_platform_optout']['rate'])} (n={v['non_platform_optout']['n']})")

print("\n=== G. validation ===", json.dumps(
    {k: validation[k] for k in ("n_labelled", "agree_from_stored_field",
                                "agree_recomputed_from_labels", "n_disagreements")}))
for d in validation["disagreements"]:
    print("  DISAGREE", d["id"], d["domain"], "manual", d["manual_block"],
          "parser", d["parser_block"], "|", d["note"])

print("\n=== H. failures (share of sampled) ===")
for t in ("high", "mid", "low"):
    v = reach_fail["pooled_tier"][t]
    s = v["shares_of_sampled"]
    print(f"{t:5s} n {v['n_sampled']:4d} fail {v['n_fail']:4d} "
          + " ".join(f"{k} {100*val:.1f}" for k, val in sorted(s.items(), key=lambda kv: -kv[1])[:6]))
print("404-in-denominator tier means:",
      json.dumps(reach_fail["optout_with_404_in_denominator"]["tier_means"]))
