<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
and scope condition below is a machine's reading of the paper and needs your eyes.

What to check, in the order it pays:

1. Each claim's NUMBER and BASELINE. A magnitude attributed to the wrong baseline is
   the one error here that is worse than saying nothing, because it is quotable.
2. Each SCOPE. This is the field summarisers drop, so it is the field this file exists
   for. If a scope reads like a disclaimer, replace it with the condition that
   actually bounds the result.
3. The MISREADINGS. A drafted misreading is a guess about your readers; you know which
   one keeps happening.
4. `one_liner`: the sentence you will reuse verbatim in the README, the model card and
   the talk abstract. Make it yours.

Then promote it:  python scripts/draft_sidecars.py --accept efficient-multi-prompt-evaluation-of-llms
-->
---
coined: PromptEval
gloss: A method that estimates an LLM's whole distribution of scores across a given pool of
  prompt templates -- and its quantiles -- from a budget of evaluations comparable to testing
  a single template, by fitting an item-response model over (template, example) correctness
  and predicting the cells it never ran.
one_liner: 'Instead of picking one prompt template and reporting its score, estimate the distribution
  of scores over a whole pool of templates: an item-response model that borrows strength across
  templates and examples recovers the quantiles across 100 MMLU templates for the price of
  about two single-prompt evaluations.'
claims:
- id: estimate-the-distribution-not-one-prompt
  text: 'The paper reframes prompt sensitivity as an estimation problem rather than a search
    problem: given a fixed pool of prompt templates, estimate the full distribution of the
    model''s scores across that pool and report its quantiles, so a benchmark number stops
    depending on which template someone happened to pick.'
  scope: 'Quantiles are taken over the template pool, which makes them interpretable but pool-dependent:
    the 95th quantile is the 95th-percentile template among the ones you supplied, offered
    as a proxy for what an expert prompt engineer would reach, and the 5th as a proxy for
    a user who does no prompt engineering. Change the pool and the quantiles move. The paper
    is explicit that this shifts the burden from choosing one prompt to choosing the set,
    and lists that as a limitation.'
  evidence: Abstract, Section 1, Section 2, Appendix A
- id: borrow-strength-across-templates-and-examples
  text: The estimate works by modelling each correctness score as a Bernoulli draw whose logit
    is a template term minus an example term, fitting that model on the cells actually evaluated,
    and filling in every unevaluated (template, example) cell with its predicted probability
    -- so evaluations spent on one template inform every other template through the shared
    example difficulties.
  scope: 'Two assumptions matter. The scores are taken as independent given the template and
    example parameters, and the logit is additive, so a template shifts every example by the
    same amount: a template that helps some examples and hurts others is not representable,
    though observed cells still enter the estimate as raw averages. With one-hot template
    and example covariates the model is exactly the Rasch model from psychometrics, whose
    weakness is that its parameter count grows with the number of templates and examples;
    richer covariates exist to control that. Fitting is just logistic regression -- in these
    experiments under 2,000 rows and a few hundred to a few thousand columns, seconds on a
    laptop -- and cost is constant in the number of templates, growing linearly in the number
    of examples.'
  evidence: Section 3.1, Section 3.2, Equation 3.2, Equation 3.4, Appendix C
- id: budget-of-one-to-two-single-prompt-evaluations
  text: The cost is close to evaluating a single template. Two hundred evaluations -- about
    0.81% of the full template-by-example grid for an MMLU subject, 1.15% for a BIG-bench
    Hard task and 0.88% for an LMentry task -- already estimate the central quantiles accurately,
    which is more than a hundredfold saving over running every template on every example;
    the abstract's headline is a budget equivalent to two single-prompt evaluations on MMLU.
  scope: 'Budgets are per task and per model: the reported errors come from separate experiments
    for each task, each LLM and five sampling seeds, with the total budget ranging over 200,
    400, 800 and 1,600 evaluations. Those convert into single-prompt evaluations differently
    per benchmark, and the conversion is worth doing because it is what the abstract quotes.
    MMLU has exactly 100 templates, so one percent of the grid is one single-prompt evaluation
    and the four budgets are 0.81, 1.6, 3.2 and 6.5 of them -- the abstract''s "two" is the
    400 setting, and the smallest budget is less than one. BIG-bench Hard and LMentry have
    136-188 and 226-259 templates, so their 200-evaluation budgets are about 1.6-2.2 and 2.0-2.3
    single-prompt evaluations. That arithmetic is a derivation from the reported percentages,
    not printed in the paper. The hundredfold figure is exact for MMLU and LMentry (about
    123x and 114x) and short of it for BIG-bench Hard (about 87x), which is why the paper
    says "in most cases". Accuracy is not uniform across tasks: MMLU subjects with many more
    examples than the rest carry visibly higher error at a fixed budget, and there the paper
    recommends spending more.'
  evidence: Section 5, Figure 1, Section 8, Appendix E
- id: central-quantiles-are-easy-extremes-are-not
  text: The median of the score distribution is recoverable at the smallest budget tested,
    while the 5th and 95th quantiles need substantially more evaluations -- the estimation
    error at the extremes falls with budget long after the middle has converged.
  scope: This is the practical catch in the method. The tails are exactly what makes the distributional
    framing attractive -- the 95th quantile as achievable-by-an-expert, the 5th as worst-case-for-a-naive-user
    -- and they are the quantiles that cost the most to pin down. Reported as curves rather
    than numbers, averaged over tasks, models and seeds, with error bars over models.
  evidence: Section 5, Figure 3, Figure 1
- id: even-the-plain-rasch-model-beats-averaging
  text: The only alternative that does not require a model -- averaging the observed scores
    for each template and treating that as its performance -- is beaten by every version of
    the method, including the plainest one with no template features at all, on all three
    benchmarks and at every budget tested.
  scope: 'That baseline is the comparison, and it is the paper''s own: it states that no prior
    work targets efficient estimation of a performance distribution across prompts, so the
    comparisons are against averaging and against its own ablations, not against a competing
    method. To keep it fair, the baseline is given the same balanced sample. The margin also
    depends on having many templates -- see the pool-size result.'
  evidence: Section 5, Figure 2, Figure 3
- id: template-features-improve-the-estimate
  text: Describing templates by features rather than by identity improves estimates further.
    Sentence-transformer embeddings reduced to 25 dimensions are the most robust choice across
    benchmarks; hand-coded surface features (line breaks, colons, dashes and similar) work
    on BIG-bench Hard but fail on LMentry; and embeddings from a BERT model fine-tuned to
    predict correctness give the best results at extreme quantiles and small budgets.
  scope: 'The fine-tuned option is the most expensive and the paper does not recommend it:
    it needs full correctness data from a held-out set of other LLMs -- training inputs numbering
    209,280 for BIG-bench Hard, 175,776 for LMentry and 1,121,568 for MMLU -- and about 70
    hours of training on multiple NVIDIA A30 GPUs plus roughly 350 more searching hyperparameters,
    against 3-6 hours on a 32-core machine for a whole benchmark otherwise. The paper''s own
    recommendation is the pretrained embedder at a moderate budget. Example-side covariates
    were tried and dropped: sentence-transformer embeddings of examples gave no improvement
    in preliminary tests, so examples stay one-hot throughout.'
  evidence: Section 5, Figure 2, Figure 3, Appendix L, Appendix D, Appendix M
- id: consistency-guarantee
  text: 'The estimator is proved consistent: as both the number of templates and the number
    of examples grow, the estimated quantile function converges to the true one at every point,
    and the estimated distribution converges in Wasserstein-1 distance -- with a separate
    result that the per-template estimates are uniformly consistent across templates.'
  scope: 'Proved for linear or affine template and example functions, and resting on three
    conditions: bounded covariates, a number of unseen examples growing fast enough (the low-budget
    regime, in a form the paper chose to simplify the proof), and correct specification of
    the logistic model together with convergence of its maximum-likelihood estimate. It is
    an asymptotic statement, not a finite-sample error bound, and none of the reported error
    curves follow from it. Correct specification is the strong assumption, since the model
    it names has no template-by-example interaction.'
  evidence: Section 4, Theorem 4.4, Condition 4.1, Condition 4.2, Condition 4.3, Appendix
    I
- id: balanced-sampling-of-which-cells-to-run
  text: Which cells to evaluate matters as much as how to model them. Sampling template-example
    pairs uniformly leaves some templates with almost no evaluations by chance; the paper
    instead spends each unit of budget on a least-evaluated template paired with a least-evaluated
    example, which amounts to two-way stratified sampling and is used for the baseline as
    well.
  scope: 'A simple greedy procedure, given as the sampling algorithm rather than analyzed:
    the argument for it is stability, not optimality, and no adaptive or information-driven
    alternative is compared in the main experiments. The best-prompt-identification setting
    is where an adaptive scheme appears, via sequential elimination.'
  evidence: Section 3.2, Algorithm 2, Section 6.2
- id: mmlu-aggregate-scores-are-robust-to-format
  text: 'The paper runs the first large-scale prompt-sensitivity study of MMLU -- 15 open-source
    LLMs across 100 templates on all 57 subjects -- and finds that the whole-benchmark picture
    is stable: spreads averaged across subjects are small compared with what the literature
    reports elsewhere, and Llama-3-70B-Instruct comes out best regardless of template.'
  scope: 'Read this together with the subject-level result, not instead of it: the two coexist
    because per-subject fluctuations average out over 57 subjects. It is also specifically
    about format perturbation. The 100 MMLU templates were generated by traversing a template
    graph that swaps separators, spacing and operators, following Sclar et al., so they are
    punctuation-and-layout variants rather than the paraphrase-level rewrites used for the
    other two benchmarks. Nothing here says MMLU is insensitive to genuinely different instructions.
    The evaluation data is released.'
  evidence: Section 7, Figure 16, Appendix J, Appendix K, Section 1
- id: mmlu-subject-level-scores-are-not-robust
  text: 'Within individual MMLU subjects the same templates behave very differently: most
    of the 15 models show an average gap of roughly 10 accuracy points between their best
    and worst template on a subject, and the distribution of those gaps extends much further.'
  scope: This is the reason the method is assessed within tasks rather than on MMLU as a whole
    -- the paper says within-task analysis is the suitable setting because that is where the
    variability lives. The measure is a max-minus-min spread over 100 templates, which is
    by construction an extreme statistic and grows with the number of templates compared.
    Reported as a density plot over subjects per model rather than as a table. For calibration,
    the prior work this paper cites for much larger spreads is described in one place as 76
    accuracy points and in another as up to 80% on a different benchmark; neither figure is
    a result of this paper.
  evidence: Section 7, Figure 6, Section 1.1, Appendix K
- id: no-template-is-reliably-best
  text: There is no template that wins in general. Ranking templates within each MMLU subject
    and measuring how much those rankings agree gives a highest agreement of about 0.25 across
    subjects, and across models most agreement scores fall between 0.06 and 0.35 -- so a template
    that suits one model or one subject carries little information about another.
  scope: 'Two models sit above the rest: Gemma-7B-it at 0.45 and Mistral-7B-v0.1 at 0.35,
    against a floor of 0.056 for Flan-T5-XXL. The appendix text attributes the 0.45 to Gemma-7B,
    while its table gives Gemma-7B 0.18 and Gemma-7B-it 0.45, so it is the instruction-tuned
    model. Reading the table against the accuracy results adds something the paper does not
    draw out: Llama-3-70B-Instruct, the model that wins under every template, has one of the
    lowest agreements at 0.10, so being the strongest model is not the same as having stable
    template preferences -- a derived observation from two of the paper''s own tables. The
    paper also observes that the top-ranked templates for both of those models are heavy with
    commas -- the best-ranked one is literally "The, following, are, multiple, choice, questions,
    (with, answers), about, [topic]" and so on with every phrase comma-separated -- and suggests
    the separation may help the model parse the prompt''s parts. That is offered as a suggestion
    about tokenization, not a tested claim, and it rests on the two models out of fifteen
    whose rankings agree at all. Agreement is Kendall''s W, which measures concordance among
    rankings and ranges from 0 to 1; there is no significance test attached. A separate check
    finds no clear relation between how many format features two templates differ by and how
    far apart their accuracies fall.'
  evidence: Section 7, Table 1, Figure 17, Figure 18, Appendix K
- id: the-judges-prompt-changes-the-ranking
  text: The same sensitivity applies to LLM-as-a-judge. Varying only the prompt given to a
    GPT-4o-mini judge over 100 templates reverses the ranking of four similarly capable LLMs
    on 36% of those templates, and the method estimates the resulting distribution of win
    rates from about 2% of the possible evaluations -- cutting the distance to the true distribution
    to roughly a fifth of what per-template averaging achieves.
  scope: Four models chosen for similar capability (Cohere Command, Qwen1.5-7B-Chat, Mistral-7B-Instruct-v0.2,
    LLaMa-2-70B-Chat) on AlpacaEval 2.0, so a 36% flip rate is what happens to near-ties,
    not a general leaderboard instability rate. The prompts given to the evaluated models
    are held fixed; only the judge's prompt varies. The 100 judge templates were generated
    with ChatGPT (10,000 variations, undersampled by deleting near-duplicates). AlpacaEval's
    bounded scores are binarized at one half to fit the model but not at test time, and some
    templates are consistently generous or harsh across all four models.
  evidence: Section 6.1, Figure 4, Figure 12, Appendix G, Appendix B
- id: also-finds-the-best-prompt-with-less-regret
  text: 'The same correctness model can be pointed at picking a prompt rather than describing
    the pool: coupled with a sequential-elimination bandit, it reaches lower regret than the
    published best-arm-identification baseline at every budget from 500 to 1,500 evaluations,
    and does so for each of the three ways of representing templates.'
  scope: Regret here is the accuracy of the best template in the pool minus that of the chosen
    one, and the values are small in absolute terms -- a few percentage points at most --
    so the comparison is between two already-decent selectors. The baseline is run with a
    logistic-regression performance predictor in the main figure and additionally with a neural
    predictor in the appendix. This addresses selecting from a fixed pool; the paper notes
    that methods which generate new candidates as they go are outside what it does, and calls
    extending to an evolving pool future work.
  evidence: Section 6.2, Figure 5, Appendix H, Section 8
- id: the-advantage-grows-with-the-size-of-the-pool
  text: 'The method''s edge over per-template averaging depends on having many templates to
    borrow strength between: cutting the pool by a factor of five -- to 20 templates on MMLU
    -- keeps it ahead but narrows the gap.'
  scope: 'Which is the honest boundary of the contribution: the fewer templates you intend
    to evaluate, the closer plain averaging gets, and at a single template the question disappears.
    Reported qualitatively from a repeat of the main experiment, without a threshold at which
    the advantage stops being worth the modelling.'
  evidence: Appendix F, Figure 10
- id: what-it-does-not-do
  text: The method does not write, generate or improve prompts. It takes a pool of templates
    as given and either summarizes performance over it or picks the best member of it, and
    the paper names choosing that pool as the challenge its own framing creates.
  scope: For constructing pools it borrows from prior work rather than contributing a method,
    and it leaves open how to use the estimated distributions to compare models in a given
    context, having settled on quantiles as an established robust summary. Stochastic dominance
    is mentioned as an alternative comparison for risk-sensitive settings but not developed
    here.
  evidence: Appendix A, Section 8, Section 1
- id: how-it-was-run
  text: 'Three benchmarks with released per-template evaluation data: MMLU with 15 LLMs and
    100 templates over 57 subjects and about 14,000 examples, all newly collected for this
    paper; BIG-bench Hard with 11 LLMs and 136 to 188 templates over 15 tasks of 100 examples;
    and LMentry with 16 LLMs and 226 to 259 templates over 10 tasks of 26 to 100 examples,
    the latter two reusing Mizrahi et al.''s evaluations.'
  scope: 'Every reported number is an average over tasks, models and five sampling seeds,
    with error bars taken over models; the MMLU runs use the unitxt preprocessing library
    and the LM-Eval-Harness. Because MMLU''s data is collected here and the other two are
    reused, the format-perturbation versus paraphrase distinction between the benchmarks is
    also a distinction between data sources. The code and the MMLU evaluation data are released,
    and the method is integrated into PromptBench. One bookkeeping snag for anyone matching
    text to figures: Section 5 says five variations of the method are considered and then
    enumerates four (Rasch, discrete covariates, pretrained embeddings, fine-tuned embeddings),
    which are the four that appear in the figures.'
  evidence: Section 5, Appendix J, Section 1, footnote 2
qa:
- q:
  - How do I evaluate an LLM without picking one prompt?
  - How do I report a benchmark score that does not depend on the prompt template?
  - What is a prompt-robust way to compare LLMs?
  answers:
  - estimate-the-distribution-not-one-prompt
  - budget-of-one-to-two-single-prompt-evaluations
  - borrow-strength-across-templates-and-examples
- q:
  - How much does multi-prompt evaluation cost?
  - Is evaluating across 100 prompt templates affordable?
  - How many evaluations does PromptEval need?
  answers:
  - budget-of-one-to-two-single-prompt-evaluations
  - central-quantiles-are-easy-extremes-are-not
  - the-advantage-grows-with-the-size-of-the-pool
- q:
  - How does PromptEval work?
  - What model does PromptEval fit?
  - How can you estimate a template's score without running it on every example?
  - What does item response theory have to do with LLM evaluation?
  answers:
  - borrow-strength-across-templates-and-examples
  - template-features-improve-the-estimate
  - consistency-guarantee
- q:
  - Is MMLU sensitive to the prompt template?
  - Do MMLU rankings change if you change the prompt format?
  - How much does MMLU accuracy vary across prompts?
  answers:
  - mmlu-aggregate-scores-are-robust-to-format
  - mmlu-subject-level-scores-are-not-robust
  - no-template-is-reliably-best
- q:
  - Is there a best prompt template for MMLU?
  - Do good prompts transfer across models?
  - Does a template that works on one task work on another?
  answers:
  - no-template-is-reliably-best
  - mmlu-subject-level-scores-are-not-robust
  - also-finds-the-best-prompt-with-less-regret
- q:
  - Does the judge's prompt affect LLM-as-a-judge results?
  - How stable is AlpacaEval to the judge prompt?
  - Can prompt sensitivity flip a model ranking?
  answers:
  - the-judges-prompt-changes-the-ranking
  - no-template-is-reliably-best
  - estimate-the-distribution-not-one-prompt
- q:
  - How do I find the best prompt from a set of candidates?
  - Is PromptEval useful for prompt selection, not just evaluation?
  - How does this compare to bandit-based best-prompt identification?
  answers:
  - also-finds-the-best-prompt-with-less-regret
  - what-it-does-not-do
  - balanced-sampling-of-which-cells-to-run
- q:
  - Which evaluations should I run given a fixed budget?
  - How should I sample template-example pairs?
  - Is random sampling good enough for multi-prompt evaluation?
  answers:
  - balanced-sampling-of-which-cells-to-run
  - budget-of-one-to-two-single-prompt-evaluations
  - even-the-plain-rasch-model-beats-averaging
- q:
  - Do I need template embeddings, or is the simple version enough?
  - Which variant of PromptEval should I use?
  - Is fine-tuning an embedder worth it for prompt evaluation?
  answers:
  - template-features-improve-the-estimate
  - even-the-plain-rasch-model-beats-averaging
  - central-quantiles-are-easy-extremes-are-not
- q:
  - Why not just average the evaluations I ran per template?
  - What does the modelling buy over a plain average?
  - When is PromptEval not worth it?
  answers:
  - even-the-plain-rasch-model-beats-averaging
  - the-advantage-grows-with-the-size-of-the-pool
  - borrow-strength-across-templates-and-examples
- q:
  - Is there a theoretical guarantee for these estimates?
  - Is PromptEval consistent?
  - What assumptions does the consistency proof make?
  answers:
  - consistency-guarantee
  - borrow-strength-across-templates-and-examples
  - central-quantiles-are-easy-extremes-are-not
- q:
  - Can PromptEval write better prompts for me?
  - Does this solve prompt engineering?
  - Which prompts should go in the pool?
  answers:
  - what-it-does-not-do
  - estimate-the-distribution-not-one-prompt
  - also-finds-the-best-prompt-with-less-regret
- q:
  - What data and models were used?
  - Where can I get the 100-template MMLU evaluation data?
  - Which benchmarks was PromptEval tested on?
  answers:
  - how-it-was-run
  - mmlu-aggregate-scores-are-robust-to-format
  - template-features-improve-the-estimate
- q:
  - What should a leaderboard report instead of a single-prompt score?
  - How do I summarize performance across many prompts?
  - What does the 95th percentile prompt mean?
  answers:
  - estimate-the-distribution-not-one-prompt
  - central-quantiles-are-easy-extremes-are-not
  - budget-of-one-to-two-single-prompt-evaluations
misreadings:
- '"Two single-prompt evaluations" is a ratio per task and per model, not an absolute budget.
  Two hundred evaluations is about 0.8% of one MMLU subject''s full template-by-example grid;
  running the whole benchmark still means paying that for each of 57 subjects. The hundredfold
  saving is for central quantiles.'
- The 5th and 95th quantiles are not free. Those cost the most evaluations to estimate, and
  they are exactly the numbers the distributional framing is meant to supply -- the median
  is what converges at the smallest budget.
- PromptEval does not generate, rewrite or optimize prompts. It takes a pool as given, and
  the paper names choosing that pool as the new challenge its own framing creates.
- '"MMLU is not very prompt-sensitive" drops half the finding. Averaged over all 57 subjects
  the spreads are small and the best model is the best model under any template; within a
  single subject the best-to-worst gap averages about 10 accuracy points. Both are in the
  same section, and they are consistent -- subject-level noise averages out.'
- The 100 MMLU templates are format perturbations -- separators, spacing, operators -- generated
  by traversing a template graph. The BIG-bench Hard and LMentry templates are paraphrase-level
  rewrites from other authors' data. So the MMLU sensitivity result is about spurious formatting,
  and does not speak to genuinely different instructions.
- The large spreads the paper mentions in passing -- 76 accuracy points, or "up to 80%" --
  are prior work's findings on other benchmarks, cited two different ways in two different
  sections. Neither is a measurement made here.
- The consistency theorem is asymptotic in the number of templates and examples, and assumes
  the logistic model is correctly specified and its maximum-likelihood estimate converges.
  It is not a finite-sample bound and it does not certify any of the reported error curves.
- 'The correctness model has no template-by-example interaction: on the logit scale, a template
  shifts every example''s difficulty by the same amount. A template that helps some examples
  while hurting others sits outside the model, however well the estimator performs in aggregate.'
- The best-performing variant is not the recommended one. Fine-tuned template embeddings need
  full correctness data from a held-out set of other LLMs plus roughly 70 hours of training
  on multiple A30 GPUs and 350 more of hyperparameter search; the paper recommends the pretrained
  embedder at a moderate budget instead.
- 'Kendall''s W of 0.45 belongs to Gemma-7B-it, not Gemma-7B -- the appendix text and its
  own table disagree, and the table lists Gemma-7B at 0.18. Either way it is the outlier:
  most models fall between 0.06 and 0.35, which is the point.'
- '"Rankings flip on 36% of prompts" describes four LLMs picked for similar capability, judged
  by GPT-4o-mini on AlpacaEval 2.0, with the evaluated models'' own prompts held fixed. It
  is a statement about how fragile near-ties are under a varying judge prompt, not a general
  rate at which leaderboards reorder.'
- The comparison for distribution estimation is against averaging the cells you ran, plus
  the method's own ablations. The paper's claim is that no prior work targets this problem,
  so there is no competing efficient multi-prompt estimator in the tables.
- The advantage is not scale-free. Cutting the template pool fivefold narrows the gap to plain
  averaging, so the method earns its keep in proportion to how many templates you actually
  intend to compare.
- '"A budget equivalent to two single-prompt evaluations" is specific to MMLU, where the pool
  is exactly 100 templates so one percent of the grid is one single-prompt evaluation. The
  four budgets tested are 0.81, 1.6, 3.2 and 6.5 single-prompt evaluations on MMLU; the abstract''s
  number is the second of them, and the smallest budget tested is less than a single prompt''s
  worth.'
- The comma-heavy best template is an observation about two of fifteen models -- the only
  two whose template rankings agree across subjects at all (Kendall's W 0.45 and 0.35). It
  is a hypothesis about tokenization the paper offers in passing, not a prompt-design finding,
  and it says nothing about the thirteen models whose rankings do not agree.
terminology:
  PromptEval: 'The method: fit an item-response model to the (template, example) correctness
    scores you can afford to run, predict the rest, and read the distribution of per-template
    scores and its quantiles off the result.'
  performance distribution: Not a distribution over random draws but over the template pool
    -- the empirical distribution of one model's scores when each template in a fixed set
    is used. Its quantiles are the paper's proposed benchmark statistic.
  quantile as a benchmark metric: 'The paper''s suggested readings: the median as typical
    performance, the 95th quantile as what a skilled prompt engineer could reach, the 5th
    as what a user who does no prompt engineering gets. All relative to the supplied pool.'
  item response theory: A family of models from psychometrics for scoring test-takers on items
    of varying difficulty, where one latent ability parameter per subject and one difficulty
    parameter per item explain who answers what. Here the templates play the role of test-takers
    and the benchmark examples the role of items.
  Rasch model: 'The simplest such model: probability of a correct answer is a logistic function
    of ability minus difficulty. Recovered here when template and example covariates are one-hot,
    and used as the no-features variant of the method.'
  pIRT / X-pIRT: Performance-IRT, a prior estimator that combines the scores actually observed
    for a subject with model predictions for the rest; X-pIRT is this paper's extension allowing
    arbitrary template and example covariates rather than identities alone.
  borrowing strength: 'The reason the budget can be small: because example difficulties are
    shared across templates, an evaluation run under one template sharpens the estimate for
    every other template that never saw that example.'
  Wasserstein 1-distance: The error measure for a whole estimated distribution. Here it reduces
    to the mean absolute difference between the sorted true per-template scores and the sorted
    estimates, so it is the average quantile error.
  budget: The number of (template, example) pairs actually run through the model. It is the
    resource being economized, and all results are reported against it.
  two-way balanced sampling: 'The greedy rule for spending that budget: always evaluate a
    least-evaluated template on a least-evaluated example, so no template ends up with too
    few observations to estimate. Applied to the baseline too, so comparisons isolate the
    modelling.'
  performance spread: Best template's accuracy minus worst template's accuracy, the prompt-sensitivity
    measure inherited from prior work. An extreme statistic by construction, so it grows with
    the number of templates compared.
  Kendall's W: 'A concordance measure from 0 (no agreement) to 1 (perfect) for how much several
    rankers agree on an ordering. Used twice: subjects ranking templates, and models ranking
    templates -- both to ask whether any template is reliably good.'
  template graph: 'The structure used to generate the MMLU templates: nodes are templates
    characterized by a separator, a spacing choice and an operator, and neighbours differ
    by one such feature. Distance on this graph is how the paper quantifies "how different"
    two formats are.'
links_extra:
  code: https://github.com/felipemaiapolo/prompteval
  MMLU 100-template evaluation data: https://huggingface.co/PromptEval
  integration in PromptBench: https://github.com/microsoft/promptbench
---
