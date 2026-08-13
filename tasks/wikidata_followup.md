# Wikidata follow-up — [Q140867203](https://www.wikidata.org/wiki/Q140867203)

Label **Leshem Choshen** · description *Israeli computer scientists and researcher*

Live diff against `config.yaml`. Re-run `python scripts/audit_identity.py`
after editing to confirm each line cleared.

## Worth adding while you are in the editor

Not identifiers — statements that help a disambiguator separate you from a
namesake, which is the whole job of this item.

| property | | value | why |
|---|---|---|---|
| given name | `P735` | Leshem | lets a query match the name parts separately from the label string |
| family name | `P734` | Choshen | same |
| educated at | `P69` | Hebrew University of Jerusalem (PhD) | the single strongest disambiguating fact about a researcher |
| employer | `P108` | with *start time* qualifiers | turns flat affiliations into a career an engine can order |

`educated at` is for degree-granting study only. A postdoc goes in `employer`
(`P108`), optionally qualified with *position held* (`P39`) = `Q1125292`
(postdoctoral researcher) — no degree was awarded, and the institution was
paying you. The test is just: was a degree awarded?

Skip date of birth, sex or gender, and image. None of them help retrieval
and all of them are personal data you would then be maintaining.

## Then: your papers

**Measured this run: 111 of 113 have a Wikidata item.**
(Matched on DOI and arXiv id across 111 papers that carry one
— exact keys, so this is coverage and not a name-search guess.)

- [Q141029633](https://www.wikidata.org/wiki/Q141029633) — TIES-Merging: Resolving Interference When Merging Models
- [Q141029634](https://www.wikidata.org/wiki/Q141029634) — tinyBenchmarks: evaluating LLMs with fewer examples
- [Q141029635](https://www.wikidata.org/wiki/Q141029635) — Active Learning for BERT: An Empirical Study
- [Q141029636](https://www.wikidata.org/wiki/Q141029636) — Findings of the BabyLM Challenge: Sample-Efficient Pretraining on Deve
- [Q141029638](https://www.wikidata.org/wiki/Q141029638) — Global MMLU: Understanding and Addressing Cultural and Linguistic Bias
- [Q106097217](https://www.wikidata.org/wiki/Q106097217) — An autonomous debating system
- [Q141029639](https://www.wikidata.org/wiki/Q141029639) — Q²: Evaluating Factual Consistency in Knowledge-Grounded Dialogues via
- [Q141029640](https://www.wikidata.org/wiki/Q141029640) — On the Weaknesses of Reinforcement Learning for Neural Machine Transla
- [Q141029641](https://www.wikidata.org/wiki/Q141029641) — Fusing finetuned models for better pretraining
- [Q141029642](https://www.wikidata.org/wiki/Q141029642) — DisentQA: Disentangling Parametric and Contextual Knowledge with Count
- [Q141029643](https://www.wikidata.org/wiki/Q141029643) — Model merging with SVD to tie the Knots
- [Q141029645](https://www.wikidata.org/wiki/Q141029645) — Beyond Binary Rewards: Training LMs to Reason About Their Uncertainty
- [Q141029646](https://www.wikidata.org/wiki/Q141029646) — Jump to Conclusions: Short-Cutting Transformers with Linear Transforma
- [Q141029647](https://www.wikidata.org/wiki/Q141029647) — Asymmetry in Low-Rank Adapters of Foundation Models
- [Q141029648](https://www.wikidata.org/wiki/Q141029648) — Efficient multi-prompt evaluation of LLMs
- [Q141029649](https://www.wikidata.org/wiki/Q141029649) — Call for Papers - The BabyLM Challenge: Sample-efficient pretraining o
- [Q141029650](https://www.wikidata.org/wiki/Q141029650) — Are You Convinced? Choosing the More Convincing Evidence with a Siames
- [Q141029651](https://www.wikidata.org/wiki/Q141029651) — Knowledge is a Region in Weight Space for Fine-tuned Language Models
- [Q141029652](https://www.wikidata.org/wiki/Q141029652) — Will it Blend? Blending Weak and Strong Labeled Data in a Neural Netwo
- [Q141029653](https://www.wikidata.org/wiki/Q141029653) — Corpus Wide Argument Mining - A Working Solution
- [Q141029654](https://www.wikidata.org/wiki/Q141029654) — DORA The Explorer: Directed Outreaching Reinforcement Action-Selection
- [Q141029655](https://www.wikidata.org/wiki/Q141029655) — Elements of World Knowledge (EWoK): A Cognition-Inspired Framework for
- [Q141029657](https://www.wikidata.org/wiki/Q141029657) — A Survey on Model MoErging: Recycling and Routing Among Specialized Ex
- [Q141029658](https://www.wikidata.org/wiki/Q141029658) — Efficient Benchmarking (of Language Models)
- [Q131458005](https://www.wikidata.org/wiki/Q131458005) — ColD Fusion: Collaborative Descent for Distributed Multitask Finetunin
- [Q141029659](https://www.wikidata.org/wiki/Q141029659) — Let's Agree to Agree: Neural Networks Share Classification Order on Re
- [Q141029660](https://www.wikidata.org/wiki/Q141029660) — Findings of the Second BabyLM Challenge: Sample-Efficient Pretraining 
- [Q141029661](https://www.wikidata.org/wiki/Q141029661) — NumeroLogic: Number Encoding for Enhanced LLMs' Numerical Reasoning
- [Q141029662](https://www.wikidata.org/wiki/Q141029662) — The Grammar-Learning Trajectories of Neural Language Models
- [Q141029663](https://www.wikidata.org/wiki/Q141029663) — [Call for Papers] The 2nd BabyLM Challenge: Sample-efficient pretraini
- [Q141029664](https://www.wikidata.org/wiki/Q141029664) — SemEval-2019 Task 1: Cross-lingual Semantic Parsing with UCCA
- [Q141029665](https://www.wikidata.org/wiki/Q141029665) — Inherent Biases in Reference-based Evaluation for Grammatical Error Co
- [Q141029666](https://www.wikidata.org/wiki/Q141029666) — Genie: Achieving Human Parity in Content-Grounded Datasets Generation
- [Q141029667](https://www.wikidata.org/wiki/Q141029667) — Reference-less Measure of Faithfulness for Grammatical Error Correctio
- [Q141029668](https://www.wikidata.org/wiki/Q141029668) — Automatic Metric Validation for Grammatical Error Correction
- [Q141029669](https://www.wikidata.org/wiki/Q141029669) — BabyLM Turns 3: Call for papers for the 2025 BabyLM workshop
- [Q141029670](https://www.wikidata.org/wiki/Q141029670) — Bigger is not always better: The importance of human-scale language mo
- [Q141029671](https://www.wikidata.org/wiki/Q141029671) — Learning to combine Grammatical Error Corrections
- [Q141029672](https://www.wikidata.org/wiki/Q141029672) — Where to start? Analyzing the potential value of intermediate models
- [Q141029673](https://www.wikidata.org/wiki/Q141029673) — Deductive Closure Training of Language Models for Coherence, Accuracy,
- [Q141029674](https://www.wikidata.org/wiki/Q141029674) — Compress then Serve: Serving Thousands of LoRA Adapters with Little Ov
- [Q131458863](https://www.wikidata.org/wiki/Q131458863) — Cluster & Tune: Boost Cold Start Performance in Text Classification
- [Q141029675](https://www.wikidata.org/wiki/Q141029675) — Sloth: scaling laws for LLM skills to predict multi-benchmark performa
- [Q141029676](https://www.wikidata.org/wiki/Q141029676) — The Language of Legal and Illegal Activity on the Darknet
- [Q141029677](https://www.wikidata.org/wiki/Q141029677) — Data Contamination Report from the 2024 CONDA Shared Task
- [Q141029678](https://www.wikidata.org/wiki/Q141029678) — Classifying Syntactic Errors in Learner Language
- [Q141029679](https://www.wikidata.org/wiki/Q141029679) — A Hitchhiker's Guide to Scaling Law Estimation
- [Q141029680](https://www.wikidata.org/wiki/Q141029680) — Unitxt: Flexible, Shareable and Reusable Data Preparation and Evaluati
- [Q141029682](https://www.wikidata.org/wiki/Q141029682) — ZipNN: Lossless Compression for AI Models
- [Q141029683](https://www.wikidata.org/wiki/Q141029683) — DOVE: A Large-Scale Multi-Dimensional Predictions Dataset Towards Mean
- [Q141029684](https://www.wikidata.org/wiki/Q141029684) — ComPEFT: Compression for Communicating Parameter Efficient Updates via
- [Q141029685](https://www.wikidata.org/wiki/Q141029685) — Benchmark Agreement Testing Done Right: A Guide for LLM Benchmark Eval
- [Q141029687](https://www.wikidata.org/wiki/Q141029687) — Label Sleuth: From Unlabeled Text to a Classifier in a Few Hours
- [Q141029688](https://www.wikidata.org/wiki/Q141029688) — When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation
- [Q141029689](https://www.wikidata.org/wiki/Q141029689) — Automatically Extracting Challenge Sets for Non-Local Phenomena in Neu
- [Q141029690](https://www.wikidata.org/wiki/Q141029690) — LiveXiv -- A Multi-Modal Live Benchmark Based on Arxiv Papers Content
- [Q141029691](https://www.wikidata.org/wiki/Q141029691) — Beneath the Surface of Consistency: Exploring Cross-lingual Knowledge 
- [Q141029692](https://www.wikidata.org/wiki/Q141029692) — The Future of Open Human Feedback
- [Q141029693](https://www.wikidata.org/wiki/Q141029693) — Label-Efficient Model Selection for Text Generation
- [Q141029694](https://www.wikidata.org/wiki/Q141029694) — Fuse to Forget: Bias Reduction and Selective Memorization through Mode
- [Q141029695](https://www.wikidata.org/wiki/Q141029695) — Human Learning by Model Feedback: The Dynamics of Iterative Prompting 
- [Q141029696](https://www.wikidata.org/wiki/Q141029696) — Mediators in Determining what Processing BERT Performs First
- [Q141029697](https://www.wikidata.org/wiki/Q141029697) — Lossless and Near-Lossless Compression for Foundation Models
- [Q141029698](https://www.wikidata.org/wiki/Q141029698) — Unsupervised Expressive Rules Provide Explainability and Assist Human 
- [Q141029699](https://www.wikidata.org/wiki/Q141029699) — Findings of the Third BabyLM Challenge: Accelerating Language Modeling
- [Q141029702](https://www.wikidata.org/wiki/Q141029702) — Naturally Occurring Feedback is Common, Extractable and Useful
- [Q141029708](https://www.wikidata.org/wiki/Q141029708) — The Mighty ToRR: A Benchmark for Table Reasoning and Robustness
- [Q141029715](https://www.wikidata.org/wiki/Q141029715) — Semantics-aware Attention Improves Neural Machine Translation
- [Q141029722](https://www.wikidata.org/wiki/Q141029722) — PreQuEL: Quality Estimation of Machine Translation Outputs in Advance
- [Q141029728](https://www.wikidata.org/wiki/Q141029728) — SERRANT: a syntactic classifier for English Grammatical Error Types
- [Q141029736](https://www.wikidata.org/wiki/Q141029736) — The ShareLM Collection and Plugin: Contributing Human-Model Chats for 
- [Q141029743](https://www.wikidata.org/wiki/Q141029743) — Global PIQA: Evaluating Commonsense Reasoning Across 100+ Languages an
- [Q141029751](https://www.wikidata.org/wiki/Q141029751) — General Agent Evaluation
- [Q141029757](https://www.wikidata.org/wiki/Q141029757) — NeurIPS 2023 LLM Efficiency Fine-tuning Competition
- [Q141029760](https://www.wikidata.org/wiki/Q141029760) — Navigating the Modern Evaluation Landscape: Considerations in Benchmar
- [Q141029761](https://www.wikidata.org/wiki/Q141029761) — Enhancing the Transformer Decoder with Transition-based Syntax
- [Q141029762](https://www.wikidata.org/wiki/Q141029762) — GrASP: A Library for Extracting and Exploring Human-Interpretable Text
- [Q141029763](https://www.wikidata.org/wiki/Q141029763) — Reinforcement Learning with Large Action Spaces for Neural Machine Tra
- [Q141029764](https://www.wikidata.org/wiki/Q141029764) — CommonLID: Re-evaluating State-of-the-Art Language Identification Perf
- [Q141029765](https://www.wikidata.org/wiki/Q141029765) — TextArena
- [Q141029766](https://www.wikidata.org/wiki/Q141029766) — Holmes: A Benchmark to Assess the Linguistic Competence of Language Mo
- [Q141029767](https://www.wikidata.org/wiki/Q141029767) — ComSum: Commit Messages Summarization and Meaning Preservation
- [Q141029769](https://www.wikidata.org/wiki/Q141029769) — Do LLMs Benefit From Their Own Words?
- [Q141029770](https://www.wikidata.org/wiki/Q141029770) — ErrorMap and ErrorAtlas: Charting the Failure Landscape of Large Langu
- [Q141029772](https://www.wikidata.org/wiki/Q141029772) — Pretraining Language Models for Diachronic Linguistic Change Discovery
- [Q141029773](https://www.wikidata.org/wiki/Q141029773) — BabyBabelLM: A Multilingual Benchmark of Developmentally Plausible Tra
- [Q141029774](https://www.wikidata.org/wiki/Q141029774) — Unforgettable Generalization in Language Models
- [Q141029775](https://www.wikidata.org/wiki/Q141029775) — CUBE: A Standard for Unifying Agent Benchmarks
- [Q141029776](https://www.wikidata.org/wiki/Q141029776) — Mediocrity is the key for LLM as a Judge Anchor Selection
- [Q141029777](https://www.wikidata.org/wiki/Q141029777) — MINDGAMES: A Live Arena for Evaluating Social and Strategic Reasoning 
- [Q141029778](https://www.wikidata.org/wiki/Q141029778) — Robustness as an Emergent Property of Task Performance
- [Q141029779](https://www.wikidata.org/wiki/Q141029779) — Will it Merge? On The Causes of Model Mergeability
- [Q141029780](https://www.wikidata.org/wiki/Q141029780) — LLM Hypnosis: Exploiting User Feedback for Unauthorized Knowledge Inje
- [Q141029781](https://www.wikidata.org/wiki/Q141029781) — On Neurons Invariant to Sentence Structural Changes in Neural Machine 
- [Q141029782](https://www.wikidata.org/wiki/Q141029782) — SemEval 2019 Shared Task: Cross-lingual Semantic Parsing with UCCA - C
- [Q141029783](https://www.wikidata.org/wiki/Q141029783) — Every Eval Ever: A Unifying Schema and Community Repository for AI Eva
- [Q141029784](https://www.wikidata.org/wiki/Q141029784) — BabyLM Turns 4 and Goes Multilingual: Call for Papers for the 2026 Bab
- [Q141029785](https://www.wikidata.org/wiki/Q141029785) — Automated Discovery Has No Universally Superior Harness
- [Q141029786](https://www.wikidata.org/wiki/Q141029786) — How Safe is Your Safety Metric? Automatic Concatenation Tests for Metr
- [Q141029787](https://www.wikidata.org/wiki/Q141029787) — A Latent Variable Framework for Scaling Laws in Large Language Models
- [Q141029788](https://www.wikidata.org/wiki/Q141029788) — Part of Speech and Universal Dependency effects on English Arabic Mach
- [Q141029789](https://www.wikidata.org/wiki/Q141029789) — Resolving Interference (RI): Disentangling Models for Improved Model M
- [Q141029791](https://www.wikidata.org/wiki/Q141029791) — Instructions Shape Production of Language, not Processing
- [Q141029792](https://www.wikidata.org/wiki/Q141029792) — Growing Pains: Extensible and Efficient LLM Benchmarking Via Fixed Par
- [Q141029793](https://www.wikidata.org/wiki/Q141029793) — Evaluation Cards: An Interpretive Layer for AI Evaluation Reporting
- [Q141029794](https://www.wikidata.org/wiki/Q141029794) — Stop Guessing When to Stop Testing: Efficient Model Evaluation with Ju
- [Q141029795](https://www.wikidata.org/wiki/Q141029795) — Cross-Lingual Exploration for Parametric Knowledge
- [Q141029796](https://www.wikidata.org/wiki/Q141029796) — CRISP: Complex Reasoning with Interpretable Step-based Plans
- [Q141029797](https://www.wikidata.org/wiki/Q141029797) — Can Gradient Descent Simulate Prompting?
- [Q141029798](https://www.wikidata.org/wiki/Q141029798) — MuLER: Detailed and Scalable Reference-based Evaluation
- [Q141029801](https://www.wikidata.org/wiki/Q141029801) — Some Grammatical Errors are Frequent, Others are Important

Two facts follow from that number, and both cut against the usual advice.

**Author Disambiguator is nearly empty for you.** Its job is to convert an
`author name string` (P2093) into `author` (P50) pointing at Q140867203. That only
works on items that already exist, so it can reach at most those listed
above. It is worth one pass — <https://author-disambiguator.toolforge.org>,
log in, paste `Q140867203` into *Author details*, tick rows whose **co-author list**
matches (the title is the weaker tell against a namesake), submit. Repeat per
name variant; it searches one string at a time. Do not press *create missing
author item* while your item exists — that is how duplicate author items
appear.

**It will not get you to 50 edits.** Worth saying because the autoconfirmed
threshold QuickStatements needs — 4 days old and 50 edits — looks like
something this step would pay for, and with a handful of linkable items it
cannot. Whether you still owe them is one command rather than an assumption:
`python scripts/wikidata_apply.py --check-account`. If you do, either make the
50 elsewhere or skip QuickStatements and edit by hand — the item's own
statements are a 15-minute job either way.

