# Changes made in revision

Reviewer point → change → location in `main.tex`. Every number traces to `RESULTS.md` / `revision_results.json`.

## Sampling, weighting, and composition

| Reviewer point | Change | Location in main.tex |
| --- | --- | --- |
| A1aw 1, fsGY 4: sample-mass rate is not an unbiased estimate of corpus composition; weights change English from 62.4% to 39.2% | Replaced all mass-weighted numbers with Horvitz–Thompson design-weighted estimates. English 39.2% doc / 41.4% token under any-15; tier means 30.8/9.8/11.4 doc, 27.6/8.7/11.2 token | §4, paragraph "Composition under consent filtering" |
| A1aw 1: weakening must be visible | Added explicit statement that under design weights the low tier overtakes the mid tier, that what remains is a high-tier step not a three-way gradient, that high-vs-low is p=0.016 on doc mass but p=0.10 on token mass (n.s.), while high-vs-rest holds on both (p=0.003, 0.015), and that ρ falls to 0.51 (p=0.069) doc and 0.22 (p=0.45) token | §4, "Composition under consent filtering" |
| A1aw 1: old numbers | Demoted 62.4% and 44.3/13.3/12.2 to a description of the head of the distribution; head-175 is a census, 63.9% of its mass is behind a block | §4, "Composition under consent filtering" |
| A1aw 1: explain why percentages apply beyond the sample | Full design description: 20,000-domain census cap (binding for all high-tier, four of five mid-tier, no low-tier language), two-stage draw (top 175 certainty + 175 uniform), tail weights 18.7 (Uyghur) to 113.3 (English), HT estimator, and the statement that estimates generalize to the top-20,000-domain web of a language; the inclusion probabilities and the HT formula itself sit in the Table 2 caption | §3, paragraph "Census cap and sample design"; Appendix A, Table 2 caption |
| A1aw 1 (framing) | Headline unit moved to domain-level opt-out and the naming/blocking decomposition, which carry no weights: 46.7% English, 28.8/11.2/9.8, means 28.1/11.1/10.0, p=0.008 / 0.002 | Abstract; §1 para 2; §4 "The consent gradient" |
| A1aw 1, fsGY 4 | Per-language design-weighted vs unweighted mass table | Appendix A, Table 2 (`tab:app-mass`) |

## Rebuild policy and crawler coverage

| Reviewer point | Change | Location in main.tex |
| --- | --- | --- |
| A1aw 3: blocking one crawler ≠ refusing Common Crawl; specify which restrictions the rebuild follows | Adopted CCBot as the rebuild policy because FineWeb and FineWeb-2 are Common Crawl derivatives; stated as such | §3, "Which restrictions a rebuild would follow" |
| A1aw 3: report results for that policy | CCBot-only leads the composition paragraph, with each number paired to its own statistic: design-weighted document mass 31.2% for English with tier means 26.5/8.9/10.7 (cluster p=0.032 high-vs-low, 0.005 high-vs-rest), and the CCBot *domain-level* rate 23.8/9.6/8.5 (p=0.032 and 0.007). Under CCBot, as under any-15, the low tier sits above the mid tier on design-weighted mass. Any-15 reported alongside as the "any AI agent" upper reading; all six policies in Table 3 | §4, "Composition under consent filtering"; Abstract |
| A1aw 3 | All six crawler policies per language | Appendix A, Table 3 (`tab:app-policy`) |
| fsGY 7, qs54 5: wildcard result belongs in Results, not Limitations | Moved out of Limitations into its own Results paragraph, with the consequence named: wildcard-only runs against the tier order (8.5/9.7/10.9, p=0.37); any-15-or-wildcard 32.9/13.1/14.7 (p=0.040) but inverts mid and low; CCBot-or-wildcard loses high-vs-low (p=0.064); high-vs-rest survives every variant (p≤0.008) | §4, paragraph "Wildcard blocks"; removed from Limitations |

## Retroactivity

| Reviewer point | Change | Location in main.tex |
| --- | --- | --- |
| fsGY 1: retroactivity qualifier must attach to composition claims in Section 4 and the abstract | "Under today's robots.txt applied retroactively to a corpus crawled earlier" now attaches directly to the composition numbers in both places, and §3 states that the composition numbers are what today's robots.txt would do to an earlier crawl, not a forecast of a future crawl | Abstract; §4 "Composition under consent filtering"; §3 "What the measure means" |
| fsGY 1 | Rebuild claim phrased as a counterfactual filter rather than a forecast | §4 "Composition under consent filtering"; §5 "What follows" |

## Mechanism

| Reviewer point | Change | Location in main.tex |
| --- | --- | --- |
| A1aw 2, qs54 1: blocking rates do not establish awareness or ability; limit conclusion to recorded policy | Removed "the ability to say no is therefore itself unequally distributed" (abstract), rewrote old lines 54–57, deleted "whether the AI opt-out conversation arrives at all" (old lines 229–231). Measured object named as recorded policy throughout | Abstract; §1 para 2; §4 "The gradient is naming, not blocking" |
| A1aw 2, qs54 2: maintenance-budget alternative | New paragraph: marginal conventional-bot naming has no significant gradient (35.7/19.0/24.6, p=0.190), but among files already naming a conventional crawler, AI naming is 64.0/44.5/19.0% (n=364/211/211, p=0.008) | §4, paragraph "Mechanism proxies" |
| qs54 2: CMS defaults | Stock defaults are 25.2% of low-tier bodies vs 9.0% high-tier; gradient survives on edited files (33.0/14.1/13.1, p=0.016) | §4, "Mechanism proxies" |
| qs54 2: hosting platforms | Platform-hosted subdomains are 12.0% of the low-tier sample and almost never opt out; removing them moves the pooled gap only 19.0 → 18.4 pp (low-tier non-platform 11.0% vs high-tier 29.4%) | §4, "Mechanism proxies" |
| A1aw 2: evidence for awareness | Allow-only AI naming ("aware and permitting"): 4.8/6.6/0.8%, p=0.008 | §4, "Mechanism proxies" |
| qs54 3: within-category comparison | Site-type controls with n's: ccTLD 31.7/12.2/13.3 (432/329/181) and gTLD 28.4/10.7/9.8 (510/707/590) in the body, org/edu/gov 15.2/10.5/2.3 (79/76/86) and no-keyword hostnames 31.9/12.4/10.9 (862/893/681) with the small-cell and weak-proxy caveats in the Table 4 caption | §4, site-type paragraph after "Mechanism proxies"; Appendix A, Table 4 caption |
| qs54 2: remaining alternatives | Stated that commercial incentive, legal exposure and publisher type remain unmeasured; low-tier conventional naming partly inherited SEO blocklists rather than curation | §4, "Mechanism proxies"; §5 "What the gradient means" |
| A1aw 2, qs54 4: name what would settle it | Named in the closing sentences of "What the gradient means": operator surveys and category-matched samples; our splits are the weakest version of that design | §5, "What the gradient means" |
| A1aw 2 | Awareness/infrastructure presented as the best-supported interpretation, tested rather than assumed; "silence equals neither refusal nor consent" retained as the binding constraint | §5, "What the gradient means" |
| A1aw 2, qs54 2 | Mechanism proxies per language | Appendix A, Table 4 (`tab:app-mech`) |

## Conditional blocking and the mid-tier dip

| Reviewer point | Change | Location in main.tex |
| --- | --- | --- |
| fsGY 2: conditional analyses underpowered; state as consistent-with | Restated as "no tier ordering we can detect"; reports cluster p=0.167, bootstrap 95% CI on the gap magnitude [0.6, 13.0] pp, four languages with n<20 named, the 100% cells as counts (Yoruba 17/17, Uyghur 15/15), low tier n=91 pooled | §4, "The gradient is naming, not blocking" |
| fsGY 3: mid-tier dip driven by Indonesian and Turkish; deserves more than a sentence | New paragraph describing both templates from the archived bodies: 28 of 31 Indonesian non-blocking namers are `tribunnews.com` regional subdomains placing Google-Extended and GPTBot in an `Allow: /` group with Googlebot; 20 of 25 Turkish share a news-CMS template stacking eight AI user-agent lines then a `User-agent: *` group of path-prefix disallows | §4, paragraph "The mid-tier dip is two templates" |
| fsGY 5: per-language conditional n's near Table 1 | Table 1 now has an *n* column (reachable domains naming ≥1 agent) and a Blk column, with a dagger on the four languages where n<20 | §4, Table 1 |
| fsGY 8: Figure 1 companion panel | Figure 1 is now two panels: (a) naming/blocking dumbbell, (b) blocking conditional on naming with bootstrap CIs and per-language n | §4, Figure 1 |

## Reachability and vantage point

| Reviewer point | Change | Location in main.tex |
| --- | --- | --- |
| fsGY 6, DJPp 1: single cloud vantage point; 403s may be artifacts | Paragraph rewritten around the failure-type breakdown: DNS failure rises 8.9 → 19.9 → 26.3% of fetches across tiers and is about half of mid- and low-tier failures, while 403 is flat at 4.6/4.6/4.5%, so the gradient is link rot rather than our vantage point | §4, "Reachability is part of the gradient" |
| DJPp 1: multi-region vantage points | States what multi-region probing would add: separating geographic IP blocking from server failure inside the flat 4.6%, and detecting robots.txt served conditionally on geography | §4, "Reachability is part of the gradient"; Limitations, "Vantage point and attribution" |
| fsGY 6 | Per-language failure types | Appendix A, Table 5 (`tab:app-fail`) |

## Size control

| Reviewer point | Change | Location in main.tex |
| --- | --- | --- |
| qs54 3: host-size analysis hard to follow and may leave size effects unresolved | Rewritten to state the design first, then head (40.4% vs 10.6%, n=559/538, p=0.008) and tail (14.7% vs 8.5%, n=462/319, p≥0.30, declined as independent confirmation) | §4, "Not a site-size artifact" |
| qs54 3: a large domain in one language is not comparable to one in another | Conceded directly: the top 175 hold 10.9% of retained English mass against 85.9% of retained Uyghur mass, so this is a within-language stratum control, not a matched comparison | §4, "Not a site-size artifact" |

## Definitions, corrections, and scope

| Reviewer point | Change | Location in main.tex |
| --- | --- | --- |
| fsGY 9: define "registered domain" once | Unit defined honestly as the URL hostname with a leading `www.` stripped, explicitly not eTLD+1, so subdomains count separately; consequences flagged for the mid-tier dip and platform analysis | §3, "Sampling frame"; Limitations, "Sampling and generalization" |
| A1aw comment: validation is 58/60, paper says 59 | Corrected to 58 of 60 (96.7%) and both disagreements described: `nli.ie` gives Bytespider `Disallow: *` rather than a literal slash; `pleinelune.niceboard.com` body truncated at 6,000 characters mid-blocklist | §3, "Fetching and parsing" |
| A1aw comment: FineWeb2 reference missing two authors | Entry now lists all ten authors including Amir Hossein Kargaran and Colin Raffel | `references.bib`, `penedo2025fineweb2` |
| qs54 6: English from FineWeb unjustified | Stated that FineWeb-2 contains no English subset, so the replication is impossible; both corpora are Common Crawl derivatives with near-identical pipelines; conceded English's census comes from a differently filtered corpus | §3, "Sampling frame"; Limitations, "Sampling and generalization" |
| fsGY 10 (typo): "stratify no result by the language served" | Now "report no results stratified by the language served" | Abstract, sentence 2 |
| fsGY 11: scope-bounding sentence | Abstract ends "What differs across these fourteen subsets is the recorded policy"; the introduction closes "What we report is a statement about these fourteen subsets"; Limitations adds that nothing extrapolates to the ~1,800 languages of FineWeb-2 | Abstract; §1 final paragraph; Limitations, "Scope of the claim" |
| fsGY 5 (Azerbaijani tier assignment) | Robustness sentence: excluding Azerbaijani leaves p=0.008 unchanged; moving it to the low tier gives p=0.005 | §4, paragraph "Robustness" |
| (self-check on unreachable domains) | 404 robustness: treating 404/410 as observed no-policy gives 25.9/10.3/8.0, p=0.008, ρ=0.76 | §4, "Robustness" |
| fsGY 12: crawler-block ranking tangential | Paragraph dropped for space; the ranking survives as one clause (CCBot 428 blocks, GPTBot 422, ClaudeBot 399, tier-to-tier rank correlations 0.89–0.94) | §4, "The gradient is naming, not blocking" |
| DJPp 2: alternative consent mechanisms | Two sentences on the TDM Reservation Protocol, `ai.txt`, `noai` in `robots` meta tags and `X-Robots-Tag`, terms of service, and CDN-managed blocking, with the argument that most demand the same infrastructure literacy while CDN defaults cut the other way; placed in Limitations so the five-page content budget holds | Limitations, paragraph "Consent beyond robots.txt" |
| qs54 Software 2 | Release now includes `analysis_revision.py`, which regenerates every number in the revision from the archived bodies | §3, "Fetching and parsing"; Ethics Statement |

## Structural changes not tied to one point

| Change | Location |
| --- | --- |
| Full per-language tables moved to an appendix and cited from the text | Appendix A, Tables 2–5 |
| Table 1's Mass column is now design-weighted document mass under the fifteen-agent policy; the unweighted comparison moved to Table 2 | §4, Table 1; Appendix A, Table 2 |
| Limitations reorganized: "Sampling and generalization", "Vantage point and attribution", "Agent roster and enforcement", "Scope of the claim"; wildcard material removed | Limitations |

## Trimming pass (content budget)

Sections 1–5 must end by the bottom of page 5. To get there without losing a reviewer-mandated element: the "Which crawlers get blocked" paragraph was dropped and its ranking kept as a clause; Related Work, the census/sample-design paragraph, the site-type paragraph, the mid-tier-dip paragraph and "Consent beyond robots.txt" were compressed; the Horvitz–Thompson formula, the org/edu/gov and no-keyword site-type splits and their caveats moved into the Appendix A table captions; Figure 1 was shrunk to 0.55 textwidth; "What would settle it" was folded into "What the gradient means"; and "Consent beyond robots.txt" moved into Limitations. Every number, CI, p-value and n that a reviewer asked for is still in the paper.
