---
key: zaman2024fuse
coined: Fuse to Forget
gloss: averaging the weights of models with different biases so the biases they do not share
  get forgotten
one_liner: Fuse to Forget shows that averaging the weights of fine-tuned language models preserves
  knowledge the models share and erodes knowledge they do not, turning simple weight averaging
  into a debiasing and memorization-reduction tool.
claims:
- id: shared-kept-unshared-forgotten
  kind: context
  text: Fuse to Forget studies model fusion as a forgetting mechanism rather than an accumulation
    mechanism. Its claim is that weight averaging preserves knowledge shared across the fused
    models while unshared knowledge is degraded or lost.
  scope: Simple weighted averaging of parameters, on fine-tuned BERT-base and GPT-2 in sentiment
    classification, tweet classification and language modeling; task arithmetic and TIES were
    not tested.
- id: shortcut-forgetting-pairs
  kind: result
  text: Interpolating between two BERT-base sentiment classifiers that each learned a different
    synthetic shortcut drops shortcut accuracy on both synthetic validation sets midway along
    the path. Accuracy on the original SST2 task is preserved throughout.
  scope: SST2 with synthetic shortcuts injected into roughly 20% of the training data; shown
    for the Ordered Pair vs Token-in-Context and Ordered Pair vs Single Token pairs, both
    trained until shortcut accuracy exceeded 0.95.
  evidence: Figure 2(b) and 2(c)
- id: shared-shortcut-kept
  kind: result
  text: When two BERT-base models share the Token-in-Context shortcut but differ in learning
    OR versus Ordered Pair, interpolation forgets the unshared shortcuts. The shared shortcut
    survives with only a small accuracy drop.
  scope: SST2 with two shortcuts injected per instance in the synthetic split, one shared
    and one unshared; single model pair, BERT-base only.
  evidence: Figure 3
- id: fuse-six-models
  kind: result
  text: Averaging the weights of 6 BERT-base models, each trained with a different synthetic
    shortcut, drives shortcut accuracy on every shortcut validation set to around chance level.
    The fused model still beats the individual models on the original SST2 validation sets
    with statistical significance.
  scope: SST2, 6 shortcut types, uniform weight averaging; original-task numbers are averages
    over each model's corresponding validation set. The full model trained on the combined
    data instead learns all 6 shortcuts.
  evidence: Figure 4
- id: bias-reduction-interpolation
  kind: result
  text: Interpolating from a gender-biased to an age-biased BERT-base tweet classifier reduces
    Demographic Parity and TPR-GAP by approximately 60% while keeping accuracy high, with
    the introduction reporting reductions of up to 68%.
  scope: PAN16 tweet classification, each biased model trained on a subset skewed 80/20 on
    one protected attribute and balanced on the other; picking the interpolation coefficient
    uses demographic annotations at evaluation time.
  evidence: Figure 5
- id: beats-inlp-leace
  kind: result
  text: Fusing an age-biased and a gender-biased BERT-base classifier lowers Demographic Parity
    on the age-biased task from .185 to .063 and TPR-GAP from .088 to .028. That beats INLP
    (.076 DP, .041 TPR-GAP) and LEACE (.206 DP, .100 TPR-GAP) at comparable accuracy (.871
    versus .877).
  scope: PAN16, BERT-base fine-tuned 2 epochs, INLP with 200 logistic classifiers; fusion
    coefficients chosen as 0.3 for age and 0.4 for gender bias. On gender bias the full model
    trained on combined data reaches a lower DP (.033) than fusion (.047).
  evidence: Table 1
- id: fusion-no-annotations
  kind: result
  text: Weight-averaging two differently biased classifiers needs no demographic annotations
    during training and no series of trained probing classifiers, unlike INLP with its 200
    logistic classifiers. Annotations are needed only to evaluate or to pick which models
    to fuse.
  scope: PAN16 tweet classification with age and gender as protected attributes; the procedure
    does require access to two models whose biases differ, and it introduces a new mixed bias
    from combining them.
  evidence: Section 5.2
- id: memorization-forgotten
  kind: result
  text: Averaging 3 GPT-2 models fine-tuned on different 3K-article CNN-DM subsets raises
    the Average Likelihood Ratio on each model's own training data from 0.22 to about 0.66.
    The ALR on the 1K shared subset stays at 0.24, so only unshared memorized text is forgotten.
  scope: GPT-2 fine-tuned 10 epochs, batch size 16, learning rate 0.001, on CNN-DM subsets
    of 3K articles with 1K shared; higher ALR means less memorization. The full model trained
    on the combined data keeps a much lower ALR of 0.32 on all subsets.
  evidence: Table 2
- id: fusion-improves-generalization
  kind: result
  text: The fused GPT-2 model reaches 30.63 validation perplexity on CNN-DM, better than each
    of the 3 individual fine-tuned models at 35.25-35.81. It remains worse than the base GPT-2
    (23.50) and the full model trained on combined data (27.45).
  scope: GPT-2 fine-tuned 10 epochs on 3K-article CNN-DM subsets; all fine-tuned and fused
    models are overfitted relative to the un-fine-tuned base model.
  evidence: Table 2
- id: more-models-more-forgetting
  kind: result
  text: 'Fusing more GPT-2 models weakens memorization of unshared training data: ALR on a
    seed model''s own data rises from 0.485 for 2 fused models to 0.656 for 3 and 0.758 for
    4. Validation perplexity falls from 31.60 to 30.15 over the same range.'
  scope: GPT-2, CNN-DM subsets of 3K articles each with 1K shared, so total training data
    grows with the number of fused models; when total data is held fixed instead, perplexity
    worsens as more models are fused.
  evidence: Table 5
- id: fisher-overlap
  kind: result
  text: Weights carrying shared task knowledge overlap more across differently-shortcut BERT-base
    models than weights carrying unshared shortcut knowledge. Fisher overlap is .8077 versus
    .6877 for the TiC-OP pair and .7746 versus .6819 for the TiC-ST pair.
  scope: Empirical diagonal Fisher information computed over 200 SST2 validation examples,
    with label-reversed shortcut copies used to isolate shortcut knowledge; 2 model pairs
    chosen to minimize shortcut overlap.
  evidence: Table 4
- id: bert-replication
  kind: result
  text: 'The memorization pattern replicates on BERT-base: fusing 4 models raises ALR on unshared
    training data to 0.234 from 0.150 for the individual models, while the shared subset stays
    better memorized at 0.174.'
  scope: BERT-base fine-tuned 20 epochs, learning rate 3e-4, on CNN-DM subsets of 3000 articles
    with 1000 shared and no sequence packing; masked-language-model energy approximated over
    10 sampled masking subsets.
  evidence: Table 7
- id: when-fusion-beats-combined-training
  kind: result
  text: Training on the combined datasets is competitive with fusion for social biases, where
    pooling the data changes label-attribute ratios. It is not competitive for shortcuts or
    memorization, where the combined model learns every shortcut and memorizes every subset.
  scope: SST2 with injected shortcuts, PAN16 age/gender bias, and CNN-DM memorization with
    GPT-2; combined training helps only when pooling the data changes label-feature correlations,
    and it requires access to all the raw training data.
  evidence: Section 7
qa:
- ask:
    plain: if you average the weights of several fine-tuned models, does the combined model
      keep everything each one learned?
    jargon: under linear weight-space interpolation between fine-tuned checkpoints, which
      capabilities are retained and which degrade?
    task: how do I predict which abilities will survive when I merge two fine-tuned checkpoints
      of the same base model?
    practitioner: if I average my fine-tuned models, will I lose the behaviours only one of
      them learned?
  answered_by:
  - shared-kept-unshared-forgotten
  - shortcut-forgetting-pairs
  - shared-shortcut-kept
- ask:
    plain: can averaging model weights get rid of a cheat rule a classifier picked up during
      training?
    jargon: does weight averaging over classifiers fitted to distinct spurious features collapse
      shortcut accuracy to chance?
    task: how do I remove a spurious feature a sentiment classifier latched onto without retraining
      it from scratch?
    practitioner: my sentiment models each learned a different spurious cue -- should I average
      them to kill the cues?
  answered_by:
  - fuse-six-models
  - shortcut-forgetting-pairs
- ask:
    plain: can averaging two text classifiers make the result less biased about gender or
      age?
    jargon: does weight-space interpolation between differently biased classifiers reduce
      Demographic Parity and TPR-GAP at fixed accuracy?
    task: how do I cut the demographic gaps in my tweet classifier without losing task accuracy?
    practitioner: should I merge two of my classifiers as a debiasing step, or will accuracy
      drop too much?
  answered_by:
  - bias-reduction-interpolation
  - beats-inlp-leace
- ask:
    plain: how does merging two biased classifiers stack up against dedicated bias-removal
      techniques?
    jargon: how does weight averaging compare with iterative nullspace projection and concept
      erasure on Demographic Parity and TPR-GAP for PAN16?
    task: which debiasing route should I try first on a BERT tweet classifier -- weight averaging
      or a projection-based erasure method?
    practitioner: I already run nullspace projection for fairness -- is fusing two biased
      models worth switching to?
  answered_by:
  - beats-inlp-leace
  - fusion-no-annotations
- ask:
    plain: do you need to know people's gender or age to debias a classifier by averaging
      weights?
    jargon: does debiasing by weight averaging require protected-attribute annotations or
      trained probing classifiers?
    task: how do I reduce social bias in a classifier when I have no demographic labels for
      the training data?
    practitioner: I have no protected-attribute annotations -- can I still debias my model
      by fusing checkpoints?
  answered_by:
  - fusion-no-annotations
- ask:
    plain: can averaging language models make them stop reciting the text they were trained
      on?
    jargon: does weight averaging of separately fine-tuned GPT-2 checkpoints reduce memorization
      of their fine-tuning corpora?
    task: how do I reduce training-data leakage from a fine-tuned language model without retraining
      on scrubbed data?
    practitioner: my fine-tuned GPT-2 regurgitates its training articles -- would averaging
      several such models help?
  answered_by:
  - memorization-forgotten
  - bert-replication
- ask:
    plain: is a model made by averaging several fine-tuned models better on held-out text
      than any of them alone?
    jargon: how does the fused GPT-2 checkpoint's validation perplexity on CNN-DM compare
      to the individual fine-tuned models and to training on the pooled data?
    task: how do I get better held-out perplexity from several small fine-tuning runs on different
      data subsets?
    practitioner: I fine-tuned GPT-2 on 3 separate article subsets -- does averaging them
      generalize better than picking one?
  answered_by:
  - fusion-improves-generalization
- ask:
    plain: does adding more models to the average make the forgetting stronger?
    jargon: how does the number of fused checkpoints affect Average Likelihood Ratio on unshared
      fine-tuning data and validation perplexity?
    task: how many fine-tuned checkpoints do I need to average before memorized training text
      stops coming back?
    practitioner: is fusing 2 models enough to suppress memorization, or should I train more
      seeds to average?
  answered_by:
  - more-models-more-forgetting
- ask:
    plain: why does averaging weights wipe out some things a model learned but leave others
      intact?
    jargon: is there Fisher information evidence that shared task knowledge occupies more
      overlapping parameters than unshared shortcut knowledge?
    practitioner: before I trust weight averaging to erase a behaviour, is there parameter-level
      evidence for why it erases some and not others?
  answered_by:
  - fisher-overlap
- ask:
    plain: is averaging separately trained models better than just training one model on all
      the data together?
    jargon: when does joint training on pooled datasets match weight averaging for shortcut
      removal, bias mitigation and memorization?
    task: I can either pool my datasets and train once or train separately and average --
      which removes unwanted behaviour?
    practitioner: should I bother fusing checkpoints if I can just retrain on the union of
      my datasets?
  answered_by:
  - when-fusion-beats-combined-training
  - fuse-six-models
- ask:
    plain: what research treats combining models as a way to strip out unwanted behaviour
      rather than to add skills?
    jargon: which work frames weight averaging as a knowledge-forgetting mechanism for debiasing
      and memorization mitigation?
    task: where should I start reading if I want to use weight averaging for fairness and
      privacy rather than multi-task gains?
    practitioner: which paper should I read first before trying model fusion to remove bias
      or memorized data?
  answered_by:
  - shared-kept-unshared-forgotten
- ask:
    plain: does the finding that averaging erases unshared knowledge hold for both text classifiers
      and text generators?
    jargon: does the shared-versus-unshared forgetting pattern under weight averaging replicate
      across BERT-base and GPT-2?
    practitioner: I work with encoder classifiers, not GPT-style generators -- was fusion-driven
      forgetting shown on both?
  answered_by:
  - bert-replication
  - shared-kept-unshared-forgotten
misreadings:
- 'Fusion does not remove a bias that all the fused models share: forgetting only applies
  to knowledge the models do not have in common, so averaging models with the same bias leaves
  it intact.'
- The debiasing result does not mean fusion produces an unbiased model. Averaging a gender-biased
  and an age-biased classifier introduces a new mixed bias from the two sources.
- 'Reduced memorization does not mean the fused model forgets its training data entirely:
  fused models still assign training examples higher likelihood than held-out data, which
  is why the paper uses an Average Likelihood Ratio instead of a thresholded membership-inference
  recall.'
- The findings are demonstrated only for simple weighted averaging of parameters on fine-tuned
  BERT-base and GPT-2; whether they carry over to task arithmetic, TIES-Merging or other fusion
  strategies was not tested.
- 'Fusing models does not match training on the pooled data for generalization: the fused
  GPT-2 reaches 30.63 validation perplexity against 27.45 for the full model trained on the
  combined subsets.'
terminology:
  Average Likelihood Ratio (ALR): A memorization metric averaging, over a dataset, the exponentiated
    ratio between a reference (un-fine-tuned) model's likelihood of a sample and the fine-tuned
    model's likelihood; lower values mean stronger memorization, and it avoids the threshold
    needed by membership-inference recall.
  knowledge utilization function: A performance metric such as accuracy or BLEU evaluated
    on a dataset curated to probe one specific latent skill, used as a measurable proxy for
    knowledge that is embedded in model weights and not directly observable.
  shared versus unshared knowledge: Knowledge is shared when several models being fused score
    similarly on the dataset probing it, and unshared when their scores diverge, so that one
    model has the skill and another does not.
  Fisher overlap: One minus the squared Fréchet distance between two networks' empirical diagonal
    Fisher information matrices normalized to unit trace, where zero means the two networks
    use non-overlapping sets of weights for the probed knowledge.
  Token in Context (TiC) shortcut: A synthetic labelling rule in which the label is set by
    which of two special tokens co-occurs with a designated context token in the input.
  full model: A single model fine-tuned on the union of the datasets used by the individually
    fine-tuned models, serving as the combined-data baseline against which a weight-averaged
    fused model is compared.
links_extra:
  code: https://github.com/keremzaman/fusetoforget
  arxiv: https://arxiv.org/abs/2311.07682
---
