# Response to reviewers — "Whose Robots.txt? Consent-Infrastructure Inequality Across the Languages of Web Corpora" (Submission 55)

We are grateful for four careful reviews. Every checkable point the reviewers raised was correct, including A1aw's recomputed 39.2% figure and the validation count. We have rebuilt the paper around that: the headline unit is now the domain-level opt-out rate and the naming/blocking decomposition, which the sampling critique does not touch; every mass-weighted number is now a design-weighted (Horvitz–Thompson) estimate, and where design weighting weakens the result we say so in Results rather than in a footnote. We also added a Results paragraph of mechanism proxies that tests, rather than assumes, the awareness reading, and we replaced the causal language about "the ability to say no" with language about recorded policy throughout.

All numbers below are reproducible from the released code (`analysis_revision.py`, seed 20260811).

---

## Reviewer A1aw (Soundness 2, Excitement 3, Overall 2.5)

**1. "The corpus-loss estimate depends strongly on how sites are selected… Adding these sampling weights changes the English estimate from 62.4% to 39.2% within the retained data. The authors need to explain why their reported percentages can be applied beyond the selected sample."**

You are right, and we reproduce your figure exactly (0.3917 against your 0.392). Our "mass-weighted" rate added the document mass of sampled domains, which gives each of the 175 certainty-selected head domains the same weight as each of the 175 tail domains drawn with probability 175/(N−175). It described the sampled head, not the language. Three changes follow.

*Method, "Census cap and sample design"* now states the design in full: the census keeps only the top 20,000 domains by document mass (binding for all four high-tier languages, four of five mid-tier, and no low-tier language, discarding 117,447 English and 82,783 Japanese domains), the two-stage draw, the inclusion probabilities, the tail weight (N−175)/175 ranging from 18.7 for Uyghur to 113.3 for English, and the Horvitz–Thompson estimator we now use. It also says explicitly that every estimate generalizes to the top-20,000-domain web of a language, a population systematically narrower for the high tier.

*Results, "Composition under consent filtering"* now reports design-weighted estimates: English 39.2% of document mass and 41.4% of token mass under the fifteen-agent policy, tier means 30.8/9.8/11.4 (document) and 27.6/8.7/11.2 (token). It states the weakening plainly: the low tier overtakes the mid tier under design weights, so what survives is a high-tier step and not a three-way gradient; high-versus-low is p = 0.016 on document mass but p = 0.10 on token mass, not significant, while high-versus-rest survives both (p = 0.003 and 0.015); the rank correlation falls to ρ = 0.51 (p = 0.069) on document mass and ρ = 0.22 (p = 0.45) on token mass. The old 62.4% and 44.3/13.3/12.2 are demoted in the same paragraph to a description of the sampled head: the top 175 English domains by document mass were fetched with certainty, and 63.9% of the mass of those that answered a request sits behind a block.

*Framing.* Because the domain-level rates carry no weights and are unaffected by any of this, they now carry the headline claim in the abstract, introduction, and Results: English 46.7%, pooled tier rates 28.8/11.2/9.8, language-level means 28.1/11.1/10.0, cluster p = 0.008 high-versus-low and 0.002 high-versus-rest. Table 2 (Appendix A) gives design-weighted and unweighted mass per language side by side, and its caption carries the inclusion probabilities and the Horvitz–Thompson formula.

**2. "Different blocking rates do not establish a difference in awareness or ability to refuse… Without such evidence, the conclusion should be limited to differences in recorded website policies."**

Agreed on the standard, and we have done both things: limited the default claim to recorded policy, and added the evidence that we do have.

*Language.* The abstract's "the ability to say no is therefore itself unequally distributed" is gone; the introduction's "removes the text of communities that know how to refuse and keeps the text of communities that were never part of the conversation" (old lines 54–57) is now "it filters by a signal written far more often in some languages' web than in others, so what it removes tracks the distribution of recorded refusals rather than of preferences"; and the Results claim "what differs across languages is whether the AI opt-out conversation arrives at all" (old lines 229–231) has been deleted.

*New evidence.* A new Results paragraph, "Mechanism proxies," tests the competing accounts. Marginal conventional-crawler naming shows no significant tier gradient (35.7/19.0/24.6%, not monotone, cluster p = 0.190), so low-tier operators are not simply failing to maintain the file. Restricting to robots.txt that already curate a conventional-crawler list, the share that also names an AI agent is 64.0% (n = 364), 44.5% (n = 211), and 19.0% (n = 211), cluster p = 0.008. A maintenance-budget account predicts both rates fall together; they do not. Files that name an AI agent and block none — the observable "aware and permitting" signal — are 4.8/6.6/0.8% (p = 0.008), essentially absent in the low tier. Stock CMS defaults are 25.2% of low-tier bodies against 9.0% of high-tier ones, but the gradient survives restricting to edited files (33.0/14.1/13.1, p = 0.016). Platform-hosted subdomains are 12.0% of the low-tier sample and almost never opt out, yet removing them moves the pooled gap only from 19.0 to 18.4 points.

*Hedging.* The Discussion now presents awareness and infrastructure as the interpretation the evidence best supports rather than as a finding, names what the proxies cannot exclude (commercial incentive, legal exposure, publisher type), and closes by naming what would settle it (operator surveys, category-matched samples).

**3. "Blocking one crawler does not necessarily mean refusing collection by Common Crawl… The authors should specify which restrictions their proposed rebuild would follow and report results for that policy."**

Correct, and we have adopted CCBot as the rebuild policy, since both FineWeb and FineWeb-2 are Common Crawl derivatives. *Method, "Which restrictions a rebuild would follow"* states this. *Results, "Composition under consent filtering"* now leads with CCBot, and an earlier draft of this revision paired the CCBot design-weighted English mass with the CCBot *domain-level* tier means, which was wrong. Each number is now paired with its own statistic.

- CCBot, design-weighted document mass: English 31.2%; tier means 26.5 / 8.9 / 10.7%; cluster p = 0.032 high-versus-low, 0.005 high-versus-rest; ρ = 0.37 (p = 0.19).
- CCBot, domain level (no weights): tier means 23.8 / 9.6 / 8.5%; pooled 24.5 / 9.6 / 8.3%; cluster p = 0.032 high-versus-low, 0.007 high-versus-rest; ρ = 0.54 (p = 0.054).

Under CCBot, as under the fifteen-agent policy, the low tier sits above the mid tier on design-weighted mass, and the paper now says so. The fifteen-agent union is reported alongside as the "any AI agent" upper reading and GPTBot-only in one clause (22.7/10.2/8.4). Table 3 (Appendix A) gives all six policies per language.

**Comment: "The validation file records 58 agreements out of 60, while the paper reports 59."**

You are right and the paper was wrong. *Method, "Fetching and parsing"* now reports 58 of 60 (96.7%) and describes both disagreements, which run in opposite directions: `nli.ie` gives Bytespider `Disallow: *` rather than a literal slash, which our rule excludes and the manual label counts as a block, and `pleinelune.niceboard.com` has a body truncated at 6,000 characters partway through an old-style scraper blocklist, so the parser records a block the visible text cannot support. The second was not described at all in the submitted version.

**Comment: "The FineWeb2 reference is missing Amir Hossein Kargaran and Colin Raffel."**

Fixed in `references.bib`; the entry now lists all ten authors.

---

## Reviewer fsGY (Soundness 4, Excitement 4, Overall 3.5)

**"Attach the retroactivity qualifier directly to the composition claims (Section 4 and abstract), not only Method/Limitations."**

Done. The abstract now reads "Under today's robots.txt applied retroactively to a corpus crawled earlier, design-weighted document mass behind a Common Crawl opt-out is 31.2% for English…", and the same clause opens the Results paragraph "Composition under consent filtering." The Method paragraph "What the measure means" states the frame once more: every composition number is what today's robots.txt would do to an earlier crawl, not a forecast of a future crawl.

**"Conditional (naming→blocking) analyses are underpowered… State as consistent-with rather than established."**

Agreed. *Results, "The gradient is naming, not blocking"* now says the conditional rates show "no tier ordering we can detect," reports cluster p = 0.167 and the bootstrap 95% interval on the magnitude of the pooled gap ([0.6, 13.0] points), and then prints the reason: four languages have fewer than twenty naming domains, the 100.0% cells for Yoruba (17 of 17) and Uyghur (15 of 15) are counts rather than rates, and the low-tier 92.3% rests on 91 domains in all. The sentence "That is consistent with no ordering in blocking rather than evidence of its absence" replaces the earlier claim.

**"Report per-language conditional-on-naming n's in or near Table 1."**

Done. Table 1 now carries an *n* column (reachable domains naming at least one agent) and a Blk column (share of those n that block), with a dagger on the four languages where n < 20. Panel (b) of the new Figure 1 plots the same quantity with bootstrap CIs and prints n per language.

**"Mid-tier conditional dip is driven by Indonesian and Turkish… deserves more than a sentence."**

It now has its own Results paragraph, "The mid-tier dip is two templates," with what those sites' rules actually look like. Of the 31 Indonesian domains that name an agent without blocking it, 28 are regional subdomains of `tribunnews.com`, whose shared robots.txt places Google-Extended and GPTBot in the same `Allow: /` group as Googlebot and bingbot (the paper's sentence names Googlebot only, for space). Of the 25 Turkish ones, 20 share a news-CMS template that stacks eight AI user-agent lines with Turkish comments naming the vendors and then opens a `User-agent: *` group whose directives are path-prefix disallows, so the named agents receive partial rules rather than `Disallow: /`. We note this is exactly where recorded policy and underlying preference come apart, and that our hostname unit counts a publisher network many times.

**"Extrapolation from a stratified sample to full-corpus composition: a justification or a check on the full per-language census head would close the gap."**

You and A1aw identified the same problem, and the answer is that the sample-mass rate is *not* unbiased for the census rate. See the response to A1aw point 1: Horvitz–Thompson estimates replace it throughout, and the head-175 census quantity (63.9% for English) is reported separately as the head check you suggest, since the head was enumerated with certainty.

**"Single cloud vantage point: some 403s may be artifacts; could interact with the tier gradient."**

*Results, "Reachability is part of the gradient"* is rewritten around the failure-type breakdown, which is the direct test. DNS resolution failure rises monotonically across tiers, from 8.9% of high-tier fetches to 19.9% and 26.3%, and accounts for roughly half of mid- and low-tier failures. A 403, the failure mode a datacenter vantage point would produce, is flat at 4.6/4.6/4.5%. So the reachability gradient is link rot, not our vantage point. It then says what multi-region vantage points would still add: separating geographic IP blocking from server failure within that flat 4.6%, and detecting robots.txt served conditionally on geography. Table 5 (Appendix A) gives per-language failure types.

**"Tier assignment is coarse; Azerbaijani is Joshi class 1 but placed in mid; add a robustness note."**

Added to *Results, "Robustness"*: excluding Azerbaijani leaves high-versus-low unchanged at p = 0.008; moving it to the low tier strengthens it to p = 0.005. The rank correlation rises under both.

**"Causal/awareness interpretation remains partly inferential."**

See A1aw point 2. The Discussion now enumerates five candidate mechanisms, says which the evidence excludes and which it does not, and keeps "silence equals neither refusal nor consent" as the binding constraint on our reading.

**"Scope: add a sentence in abstract/intro bounding the claim."**

The abstract now ends "What differs across these fourteen subsets is the recorded policy," and the introduction closes with "What we report is a statement about these fourteen subsets." The Limitations paragraph "Scope of the claim" adds that nothing here licenses extrapolation to the roughly 1,800 languages FineWeb-2 covers.

**"Abstract 'stratify no result by the language served' is awkward."**

Fixed: "report no results stratified by the language served."

**"Wildcard-block sensitivity (32.9/13.1/14.7%) is buried in Limitations and belongs in Results."**

Moved to a Results paragraph, "Wildcard blocks," and it now names its own consequence rather than presenting the variant as reassuring. Wildcard-only blocking runs slightly *against* the tier order (8.5/9.7/10.9% pooled, p = 0.37). Any-15-or-wildcard gives 32.9/13.1/14.7%, which still separates high from low (p = 0.040) but inverts mid and low. CCBot-or-wildcard is the one variant where the high-versus-low test fails, at p = 0.064. High-versus-rest survives every variant at p ≤ 0.008. The Limitations section no longer carries this material.

**"Figure 1: consider adding conditional-blocking dots or a companion panel."**

Done: Figure 1 is now two panels, (a) the naming/blocking dumbbell as before and (b) blocking conditional on naming with bootstrap CIs and the naming count n per language.

**"Define 'registered domain' (eTLD+1?) once."**

We were using the term incorrectly. *Method, "Sampling frame"* now says the unit is the URL hostname with a leading `www.` stripped, explicitly not the registered domain or eTLD+1, so a publisher network spread over regional subdomains contributes several units. This matters for the mid-tier dip and for the platform-subdomain analysis, and it is flagged again in Limitations.

**"The crawler-block ranking is slightly tangential and could be trimmed for space."**

The paragraph is gone. The ranking survives as one clause inside *Results, "The gradient is naming, not blocking"*: CCBot (428 blocks), GPTBot (422), and ClaudeBot (399) lead, and the tier-to-tier rank correlations run 0.89 to 0.94.

---

## Reviewer DJPp (Soundness 4, Excitement 4, Overall 4)

**"Briefly discuss how multi-region vantage points might affect fetch success rates (distinguishing geographic IP blocks from server failures)."**

Added to *Results, "Reachability is part of the gradient"*. The failure-type breakdown separates what we can already distinguish: DNS failure rises 8.9 → 19.9 → 26.3% across tiers while 403 stays flat near 4.6%, so the gradient is link rot rather than IP blocking. The paragraph then states what multi-region probing would add that we cannot supply, namely separating geographic IP blocking from server failure inside that flat 4.6%, and detecting robots.txt served conditionally on geography.

**"Consider expanding on alternative consent mechanisms beyond robots.txt."**

Added as a two-sentence paragraph, "Consent beyond robots.txt," placed in Limitations so that Sections 1–5 fit the content budget. It covers the TDM Reservation Protocol, `ai.txt` proposals, `noai` values in `robots` meta tags and `X-Robots-Tag` headers, and terms of service. We note these demand the same infrastructure literacy and vendor-token vocabulary, so we expect them to track rather than offset the gradient, and that CDN-managed AI blocking plausibly cuts the other way by writing restrictions on behalf of operators who never edited a file.

**"Sample restricted to 14 languages and 350 domains each."**

Acknowledged and now bounded explicitly in the abstract, introduction, and Limitations, as described under fsGY's scope comment.

---

## Reviewer qs54 (Soundness 2, Excitement 2, Overall 2)

**"The paper frames its central claim around unequal ability or opportunity to consent, but the method measures differences in robots.txt naming and blocking rates… The prose closes this gap rhetorically: lines 54–57 and lines 229–231."**

This was a fair reading of the prose and both sentences are gone. Lines 54–57 now read: "it filters by a signal written far more often in some languages' web than in others, so what it removes tracks the distribution of recorded refusals rather than of preferences." Lines 229–231 ("what differs across languages is whether the AI opt-out conversation arrives at all") have been deleted; the paragraph now ends on the denominators instead. The abstract's causal claim is replaced by "What differs across these fourteen subsets is the recorded policy." Throughout, the measured object is named as recorded policy.

**"Other mechanisms could produce the same ordering: different incentives to block AI crawlers, maintenance budgets, legal exposure/risk management, hosting platforms, CMS defaults, publisher types."**

We took this as the main task of the revision and tested the mechanisms that are observable in the data. The new Results paragraph "Mechanism proxies" reports, for maintenance budget, that marginal conventional-crawler naming has no significant tier gradient (35.7/19.0/24.6%, p = 0.190) while AI naming among the files that already curate a conventional list falls 64.0 → 44.5 → 19.0% (p = 0.008), which a maintenance-budget account does not predict; for CMS defaults, that stock bodies are 25.2% of the low tier against 9.0% of the high tier but the gradient survives on edited files (33.0/14.1/13.1, p = 0.016); for hosting platforms, that platform-hosted subdomains are 12.0% of the low-tier sample and almost never opt out, yet removing them moves the pooled gap only from 19.0 to 18.4 points, because the low tier's non-platform rate of 11.0% is still far below the high tier's 29.4%. We also report the "aware and permitting" rate (4.8/6.6/0.8%, p = 0.008). We state in the site-type paragraph that commercial incentive, legal exposure, and publisher type remain live alternatives our data cannot separate, and the Discussion names operator surveys and category-matched samples as what would settle it. We also flag against ourselves that low-tier conventional-bot naming is partly inherited SEO blocklists rather than curation.

**"The host-size analysis (lines 232–247) may leave size effects unresolved, since a large domain in one language may not be comparable to a large domain in another; the analysis is also hard to follow."**

Both points are correct. *Results, "Not a site-size artifact"* is rewritten to state the design first (each sample splits into a head of the 175 largest domains by document mass and a uniform tail), then the numbers (head: 40.4% high, n = 559, against 10.6% low, n = 538, p = 0.008; tail: 14.7%, n = 462, against 8.5%, n = 319, p ≥ 0.30, which we decline to count as independent confirmation), then the limit you identified: a head domain is large only relative to its own language, and the top 175 domains hold 10.9% of retained English document mass against 85.9% of retained Uyghur mass, so this is a within-language stratum control and not a matched comparison of comparable objects. That concession is new.

**"Language is not the only axis; a within-category comparison (e.g., English news vs Vietnamese news) would be more informative."**

Agreed that this is the right design, and we could not run it properly. What we can report is the site-type paragraph after "Mechanism proxies": the gradient holds within ccTLDs (31.7/12.2/13.3%, n = 432/329/181) and within gTLDs (28.4/10.7/9.8%, n = 510/707/590) in the body, with `.org`/`.edu`/`.gov` (15.2/10.5/2.3%, n = 79/76/86) and hostnames carrying no recognizable keyword (31.9/12.4/10.9%, n = 862/893/681) in the caption of Table 4. The caption also records that several cells hold fewer than twenty domains and that a hostname keyword is a weak proxy for what a site publishes, and the Discussion says a category-matched sample is what would actually settle it and that our splits are "the weakest possible version of that design."

**"Two routes: narrow the claim to a descriptive audit… or add evidence for the mechanism."**

We have taken both. The claim is narrowed to recorded policy, and the mechanism proxies above are the added evidence, presented as narrowing the space of explanations rather than closing it.

**"The wildcard-block result (lines 324–333) materially qualifies the main analysis and belongs in Results/Discussion, not Limitations."**

Agreed and moved, with its consequence stated rather than softened; see the response to fsGY on wildcards. The previous framing ("compresses the gradient slightly while leaving it above twofold") understated it: wildcard-only blocking runs against the tier order, and CCBot-or-wildcard loses high-versus-low significance at p = 0.064.

**"English from FineWeb while others from FineWeb-2 is stated without justification; ideally replicated with English from FineWeb-2."**

The justification is that FineWeb-2 contains no English subset, so the replication you ask for is not possible. *Method, "Sampling frame"* now states this directly, adds that both corpora derive from Common Crawl and are processed by near-identical pipelines, and concedes that English's census is nonetheless drawn from a differently filtered corpus. Limitations repeats that we cannot rule out that this contributes to English's position.

**Software 2.**

The release now also contains `analysis_revision.py`, which regenerates every number in this revision, including all six crawler policies, the design weights, the mechanism proxies, the Azerbaijani and 404 variants, and the failure-type breakdown, from the archived bodies in about ten seconds.

---

## Summary of what got weaker

We want this visible rather than buried. Design weighting cuts the English mass figure from 62.4% to 39.2% (31.2% under CCBot) and removes the monotone three-way ordering on mass, leaving a high-tier step; the design-weighted token-mass gap is not significant (p = 0.10); folding blanket wildcard blocks into the CCBot policy removes high-versus-low significance (p = 0.064); marginal conventional-bot naming shows no significant gradient, so the maintenance-budget alternative is excluded by the conditional statistic and not the marginal one; stock CMS defaults account for a real part of the raw gap; and the validation count was 58 of 60, not 59. What is unchanged is the domain-level result the paper now leads with: English 46.7%, tier rates 28.8/11.2/9.8, naming 33.6/17.7/10.6, cluster p = 0.008 and 0.002, which carry no weights and are unaffected by the sampling critique.

---

## Note on layout

Sections 1–5 end on page 5 and the paper is 9 pages in the `review` style (Limitations and Ethics on page 6, References through page 6–7, Appendix A after). To reach the content budget we dropped the crawler-ranking paragraph (keeping the ranking as a clause), moved the Horvitz–Thompson formula and two site-type splits into the Appendix A table captions, moved "Consent beyond robots.txt" into Limitations, folded "What would settle it" into "What the gradient means," and compressed Related Work, the sampling paragraph, and the mid-tier-dip, site-type, and composition paragraphs. No reviewer-requested number, CI, p-value, or n was removed.
