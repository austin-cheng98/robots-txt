# Number audit of `main.tex` (Phase 3)

Every numeric claim in `main.tex` was checked against `revision_results.json` (RJ), `RESULTS.md`, `repo/data/analysis_v3.json` (v3), or a direct re-parse of the archived bodies in `repo/data/`. Status is **pass** (already correct) or **fixed** (changed in this pass). Key paths are given as `top-level key > subkey`.

## Summary

Six problems were found. Five were in `main.tex` and are fixed; one is in `RESULTS.md` and is documented only.

| # | Claim | Problem | Status |
| --- | --- | --- | --- |
| 1 | CCBot composition (abstract and Results) | The design-weighted English mass 31.2% was paired with the CCBot **domain-level** tier means 23.8/9.6/8.5 and their p-values, which are a different statistic | fixed |
| 2 | "mid and low are not separable (p ≥ 0.34)" | 0.34 is the domain-pooled shuffle (`v3 > pooled.optout.mid_low.perm_p` = 0.33728), not the equal-weighted language-partition test the paper's convention requires (0.5159; count-weighted 0.4524) | fixed → p ≥ 0.45 |
| 3 | "63.9% of their mass is behind a block" | Denominator is the **reachable** head-175 mass; over all head-175 mass it is 56.0% | fixed (wording now says "of the mass of those that answered") |
| 4 | Table 5 pooled "404/410" cells 6.9 / 4.9 / 11.9% | Those are 404-only, while the per-language rows in the same column sum 404 + 410 | fixed → 7.3 / 5.3 / 12.2% |
| 5 | "an untouched WordPress, Blogger, Shopify, or Wix body" | Shopify's detected share is 0.0% in all three tiers | fixed (Shopify dropped from the body list; the appendix caption still names all five detectors) |
| 6 | `RESULTS.md` line 419: validation confidence "56 high, 4 medium" | `RJ > G_validation > confidence_counts` is 55 high, 1 medium, 4 low | documented only; not cited in `main.tex` |

## Abstract

| Claim | Source | Status |
| --- | --- | --- |
| 4,900 domains, fourteen languages, three tiers | `RJ > H_reachability_failures > totals.n_sampled` = 4900 | pass |
| 28.8 / 11.2 / 9.8% pooled | `RJ > BC_policy_variants > any15 > pooled_domain_rate` | pass |
| high–low p = 0.008 | `RJ > BC > any15 > cluster_domain_high_vs_low.p_unweighted` = 0.007937 | pass |
| naming 33.6% → 10.6% | `RJ > F_mechanism_proxies > ai_naming` | pass |
| conventional-list AI naming 64.0% → 19.0% | `RJ > F > among_conventional` | pass |
| CCBot design-weighted English mass 31.2% | `RJ > BC > ccbot_only > per_language.eng.design_wt_mass_doc` = 0.31203 | pass |
| CCBot tier means 26.5 / 8.9 / 10.7, low above mid | `RJ > BC > ccbot_only > tier_means_design_wt_doc` | fixed (was 23.8/9.6/8.5) |
| reachability 78% → 39% | Table 1 Reach column; `RJ > H` | pass |
| "more heavily" (was "far more heavily") | softening requested | fixed |

## Introduction and Related Work

| Claim | Source | Status |
| --- | --- | --- |
| Longpre 28% of most actively maintained sources; 14,000 domains | literature; not checkable against this repo | flagged, unchanged |
| Cui 610,681 Tranco domains, eighteen LLM bots | literature; not checkable against this repo | flagged, unchanged |

## Method

| Claim | Source | Status |
| --- | --- | --- |
| 200,000-document cap; binds except Sundanese, Yoruba, Uyghur | `v3 > capped` (true for all but sun/yor/uig) | pass |
| Census cap 20,000; 117,447 English and 82,783 Japanese domains discarded | `RJ > A_design_weights > per_lang.eng_Latn/jpn_Jpan` (`domains_dropped_by_cap` 117,447 and 82,783) | pass |
| Tail weight 18.7 (Uyghur) to 113.3 (English) | `RJ > A_design_weights > per_lang.uig/eng` tail weights 18.7314 and 113.2857 | pass |
| Two-stage draw: top 175 certainty + 175 uniform from N−175 | design, matches `analysis_revision.py` | pass |
| 60 labelled bodies, 58 agreements, 96.7% | `RJ > G_validation` (n_labelled 60, agree 58, accuracy 0.96667) | pass |
| `nli.ie` disagreement (manual block, parser no-block) | `RJ > G > disagreements[0]` | pass |
| `pleinelune.niceboard.com` truncated at 6,000 characters | re-verified directly: body length is exactly 6000, cut mid old-style scraper blocklist, no AI agent visible; label confidence "low" | pass |
| fifteen AI agents; five named plus "ten more" | `v3 > agent_counts` has 15 agents | pass |
| 126 high-versus-low splits | exact partition count | pass |
| "equal-weighted unless we say otherwise" | every bare `p = X` in the paper is `p_unweighted` | pass (verified claim by claim) |

## Results

### The consent gradient
| Claim | Source | Status |
| --- | --- | --- |
| English 46.7%, German 29.9% | Table 1; `RJ` per-language any15 | pass |
| 28.8 / 11.2 / 9.8% with n = 1,021 / 1,112 / 857 | `RJ > BC > any15 > pooled_domain_rate` and `n` | pass |
| 19.0-point gap, p = 0.008 equal-weighted, 0.032 count-weighted | `RJ > BC > any15 > cluster_domain_high_vs_low` (0.007937 / 0.031746) | pass |
| English CI [.408, .529] | `RJ` bootstrap CI for eng | pass |
| tier means 28.1 / 11.1 / 10.0 | `RJ > BC > any15 > tier_means_domain` | pass |
| 1,001 splits, p = 0.002 | `RJ > BC > any15 > cluster_domain_high_vs_rest.p_unweighted` = 0.001998 | pass |
| mid and low not separable | `v3 > cluster.mid_vs_low_optout` p_unweighted 0.5159, p_weighted 0.4524 | **fixed** (p ≥ 0.34 → p ≥ 0.45) |
| ρ = 0.69, p = 0.009 | `RJ > BC > any15 > spearman_domain` (0.6895, 0.0093) | pass |

### Naming, not blocking
| Claim | Source | Status |
| --- | --- | --- |
| naming 33.6 / 17.7 / 10.6, 23.0-point gap, p = 0.008 | `RJ > F > ai_naming`, `v3 > cluster.high_vs_low_names_all` | pass |
| p = 0.007 high-versus-rest, ρ = 0.77, p = 0.002 | `v3 > cluster.high_vs_rest_names_all` 0.006993; `v3 > spearman.names` 0.7664 / 0.00246 | pass |
| English naming 49.3% | Table 1 Names column | pass |
| CCBot 428, GPTBot 422, ClaudeBot 399 | `v3 > agent_counts` | pass |
| tier-to-tier rank correlations 0.89 to 0.94 | recomputed per-tier agent block counts: high–mid 0.939, high–low 0.886, mid–low 0.900 | pass |
| conditional 85.7 (343) / 62.9 (197) / 92.3 (91), p = 0.167 | `RJ > E_conditional_on_naming` (pooled, cluster p_unweighted 0.16667) | pass |
| bootstrap [0.6, 13.0] points | `RJ > E > boot_ci95_abs` [0.00583, 0.13030] | pass |
| Yoruba 17 of 17, Uyghur 15 of 15, four languages n < 20 | `RJ > E > per_language` | pass |

### Mid-tier dip
| Claim | Source | Status |
| --- | --- | --- |
| mid 62.9% → 79.8% without Indonesian and Turkish | `RJ > E` (67/84 = 79.76%) | pass |
| 28 of 31 Indonesian named-not-blocked are `tribunnews.com` subdomains, `Allow: /` group with Googlebot | re-parsed `repo/data/robots_ind_Latn.json.gz`: 225 reachable, 62 named, 31 named-not-blocked, 28 ending in `tribunnews.com`; sample body confirms Googlebot/bingbot/Google-Extended/GPTBot then `Allow: /` | pass |
| 20 of 25 Turkish share a news-CMS template, eight AI user-agent lines then a `User-agent: *` group of path-prefix disallows | re-parsed `repo/data/robots_tur_Latn.json.gz`: 238 reachable, 51 named, 25 named-not-blocked, exactly 20 sharing a body of 15 UA lines, length ~1495–1517; body confirms eight AI UA lines (GPTBot, Google-Extended, CCBot, ClaudeBot, Applebot-Extended, Omgilibot, Diffbot, FacebookBot) then `User-agent: *` with ~37 path-prefix disallows | pass |

### Mechanism proxies
| Claim | Source | Status |
| --- | --- | --- |
| conventional naming 35.7 / 19.0 / 24.6, gap 9.7 points, p = 0.190 | `RJ > F > conventional`, `cluster_conventional` | pass |
| among-conventional 64.0 (364) / 44.5 (211) / 19.0 (211), 39.7-point gap, p = 0.008 | `RJ > F > among_conventional`, `cluster_ai_naming_given_conventional` | pass |
| allow-only 4.8 / 6.6 / 0.8%, p = 0.008 | `RJ > F > allow_only` | pass |
| stock CMS defaults 25.2% low vs 9.0% high | `RJ > F > stock_defaults.share_stock_cms_default` | pass |
| Shopify listed as a stock default | detected share 0.0% in all tiers | **fixed** (removed from body list) |
| edited-file gradient 33.0 / 14.1 / 13.1, p = 0.016 | `RJ > F > stock_defaults.optout_within_non_default` and its cluster p (0.015873) | pass |

### Site type
| Claim | Source | Status |
| --- | --- | --- |
| ccTLD 31.7 (432) / 12.2 (329) / 13.3 (181) | `RJ > F > site_type.tld_class.ccTLD` | pass |
| gTLD 28.4 (510) / 10.7 (707) / 9.8 (590) | `RJ > F > site_type.tld_class.gTLD` | pass |
| org/edu/gov 15.2 / 10.5 / 2.3 (79/76/86) — now in the Table 4 caption | `RJ > F > site_type.tld_class.org_edu_gov` | pass |
| no-keyword hostnames 31.9 / 12.4 / 10.9 (862/893/681) — now in the Table 4 caption | `RJ > F > site_type.keyword._none` | pass |
| platform-hosted 12.0% of low-tier sample vs 2.1% of high-tier | `RJ > F > site_type.platform_hosted` (n 103/857 and 21/1021) | pass |
| pooled gap 19.0 → 18.4 points; low non-platform 11.0% vs high 29.4% | `RJ > F > site_type.non_platform_optout` | pass |

### Composition
| Claim | Source | Status |
| --- | --- | --- |
| CCBot design-weighted English 31.2%; tier means 26.5 / 8.9 / 10.7; p = 0.032 high–low, 0.005 high-versus-rest | `RJ > BC > ccbot_only > tier_means_design_wt_doc`, `cluster_design_wt_doc_high_vs_low` (0.031746), `..._high_vs_rest` (0.004995) | **fixed** |
| CCBot domain-level 23.8 / 9.6 / 8.5, p = 0.032 and 0.007, now labelled domain-level | `RJ > BC > ccbot_only > tier_means_domain`, `cluster_domain_high_vs_low` (0.031746), `cluster_domain_high_vs_rest` (0.006993) | **fixed** (label) |
| low tier above mid on design-weighted mass under CCBot as under any-15 | 10.7 > 8.9 (CCBot); 11.4 > 9.8 (any-15) | **added** |
| any-15 English 39.2% doc, 41.4% token | `RJ > A_design_weights > estimator_variants_english` (0.391678, 0.414151) | pass |
| any-15 tier means 30.8 / 9.8 / 11.4 doc and 27.6 / 8.7 / 11.2 token | `RJ > BC > any15 > tier_means_design_wt_doc` / `_tok` | pass |
| doc p = 0.016, token p = 0.10, high-versus-rest 0.003 and 0.015 | `RJ > BC > any15 > cluster_design_wt_doc_*` (0.015873, 0.002997); `RJ > A_design_weights > cluster_tests.design_weighted_tok` (0.10317, 0.014985) | pass |
| ρ = 0.51 (p = 0.069) doc, ρ = 0.22 (p = 0.45) token | `RJ > BC > any15 > spearman_design_wt_doc`; `RJ > A_design_weights > spearman.design_weighted_tok` | pass |
| unweighted 62.4%, tier means 44.3 / 13.3 / 12.2 | `RJ > A_design_weights > estimator_variants_english.unweighted_paper`; `RJ > A_design_weights > tier_means.sample_mass_doc` | pass |
| 63.9% of head-175 mass | `RJ > A_design_weights > estimator_variants_english.head_only_census_mass_doc_any15` = 0.63909, denominator = reachable head mass (the all-head figure is 0.5597) | **fixed** (wording) |

### Wildcard, robustness, size, reachability
| Claim | Source | Status |
| --- | --- | --- |
| wildcard-only 8.5 / 9.7 / 10.9 pooled, p = 0.37 | `RJ > BC > wildcard_only > pooled_domain_rate`, `cluster_domain_high_vs_low` (0.37302) | pass |
| any-15-or-wildcard 32.9 / 13.1 / 14.7, p = 0.040 | `RJ > BC > any15_or_wildcard` (pooled; cluster 0.039683) | pass |
| CCBot-or-wildcard high–low fails at p = 0.064 | `RJ > BC > ccbot_or_wildcard > cluster_domain_high_vs_low` = 0.063492 | pass |
| high-versus-rest survives every variant at p ≤ 0.008 | max over six policies = 0.007992 (excluding wildcard-only, which the sentence excludes by construction) | pass |
| Azerbaijani excluded p = 0.008, moved to low p = 0.005 | `RJ > D_azerbaijani` (0.007937; 0.0047619 over 210 splits) | pass |
| 404/410 as observed no-policy: 25.9 / 10.3 / 8.0, p = 0.008, ρ = 0.76 (p = 0.003) | `RJ > H > optout_with_404_in_denominator` | pass |
| head 40.4 (559) vs 10.6 (538), p = 0.008 | `v3 > pooled.head`, `v3 > cluster.high_vs_low_optout_head` | pass |
| tail 14.7 (462) vs 8.5 (319), p ≥ 0.30 | `v3 > pooled.tail`, `v3 > cluster.high_vs_low_optout_tail` = 0.301587 | pass |
| top 175 hold 10.9% of English retained mass vs 85.9% of Uyghur | `RJ > A_design_weights > per_lang.eng/uig` head-175 mass share | pass |
| reach 65–78% high, 39–58% low, p = 0.008, ρ = 0.92, p < 1e-4 | Table 1 Reach; `RJ > H > cluster_reach_rate`; `v3 > spearman.reach` (0.92249, 2e-05) | pass |
| DNS 8.9 / 19.9 / 26.3%, about half of mid- and low-tier failures | `RJ > H > pooled.shares_of_sampled.dns`; `shares_of_failures` 54.6 / 51.5% | pass |
| 403 flat at 4.6 / 4.6 / 4.5% | `RJ > H > pooled.shares_of_sampled.http_403` | pass |

## Tables

| Table | Check | Status |
| --- | --- | --- |
| Table 1 (`tab:main`) | all 14 rows × 7 columns (Reach, Names, Opt-out, CI, Mass, n, Blk) against `RJ` per-language any-15 | pass |
| Table 1 caption | Mass column now explicitly the fifteen-agent policy, since the body leads with CCBot | fixed |
| Table 2 (`tab:app-mass`) | census, N, dropped, w_tail, head % of mass, unweighted and design-weighted mass for all 14 languages, plus both tier-mean rows | pass |
| Table 3 (`tab:app-policy`) | all 14 × 6 policy rates, the tier-mean row, and both p rows | pass |
| Table 4 (`tab:app-mech`) | all 14 rows and 3 pooled rows and the p row | pass |
| Table 5 (`tab:app-fail`) | per-language rows: each row's six failure columns sum to that language's failure total; 404/410 and "other" reconcile | pass |
| Table 5 pooled rows | pooled 404/410 cells were 404-only | **fixed** → 7.3 / 5.3 / 12.2% |

## Cross-checks

- Every `p = X` in the body is the equal-weighted language-partition permutation. The two places where a count-weighted value appears (`0.032` count-weighted in "The consent gradient") are labelled as such. No domain-pooled shuffle is quoted as a `p` anywhere after fix #2.
- No sentence in Sections 1–5 contradicts Tables 2–5; each text figure was matched to its table cell.
- `python3 analysis_revision.py` was re-run after the edits: `revision_results.json` is byte-identical, confirming that no new computation was needed for the CCBot design-weighted cluster tests (they were already present under `BC_policy_variants > ccbot_only`).
