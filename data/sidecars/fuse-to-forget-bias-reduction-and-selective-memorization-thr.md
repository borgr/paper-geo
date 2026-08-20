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
- q:
  - What happens to a model's skills when you average the weights of several fine-tuned models?
  - Does weight averaging keep all the knowledge of the fine-tuned models being merged?
  - Which knowledge survives model fusion and which is lost?
  answers:
  - shared-kept-unshared-forgotten
  - shortcut-forgetting-pairs
  - shared-shortcut-kept
- q:
  - Can averaging model weights remove spurious shortcuts learned during fine-tuning?
  - Does merging classifiers that learned different shortcuts get rid of those shortcuts?
  - How much shortcut accuracy is left after fusing 6 models with different shortcuts?
  answers:
  - fuse-six-models
  - shortcut-forgetting-pairs
- q:
  - Can model merging be used as a debiasing method for text classifiers?
  - How much does averaging a gender-biased and an age-biased model reduce bias?
  - Does weight averaging reduce demographic parity gaps without hurting accuracy?
  answers:
  - bias-reduction-interpolation
  - beats-inlp-leace
- q:
  - How does weight averaging compare to INLP and LEACE for debiasing?
  - Is model fusion better than nullspace projection for removing social bias?
  - Which debiasing method gives the lowest TPR-GAP on PAN16 tweet classification?
  answers:
  - beats-inlp-leace
  - fusion-no-annotations
- q:
  - Does debiasing by model fusion require demographic labels?
  - Do I need protected-attribute annotations to remove bias by averaging weights?
  answers:
  - fusion-no-annotations
- q:
  - Can model merging reduce memorization of training data in language models?
  - Does averaging fine-tuned GPT-2 models make them forget their training examples?
  - How can weight averaging help with privacy and training-data leakage?
  answers:
  - memorization-forgotten
  - bert-replication
- q:
  - Does fusing several fine-tuned models improve validation perplexity?
  - Is a merged GPT-2 better at generalizing than the individual fine-tuned models it was
    averaged from?
  answers:
  - fusion-improves-generalization
- q:
  - What happens as you increase the number of models being averaged?
  - Does forgetting get stronger with more merged models?
  - How many models should be fused to reduce memorization?
  answers:
  - more-models-more-forgetting
- q:
  - Why does simple weight averaging preserve some knowledge and destroy other knowledge?
  - Is there evidence that shared and unshared skills live in different weights?
  - What does Fisher information say about which weights encode shared knowledge?
  answers:
  - fisher-overlap
- q:
  - Is it better to merge separately trained models or just train on the combined data?
  - When does training on the pooled dataset beat weight averaging?
  - Does a model trained on all the data also lose the shortcuts?
  answers:
  - when-fusion-beats-combined-training
  - fuse-six-models
- q:
  - What paper should I read about the downsides or forgetting effects of model merging?
  - Which work studies model fusion as a way to remove unwanted knowledge rather than add
    capability?
  - Where can I start reading about using weight averaging for bias and privacy?
  answers:
  - shared-kept-unshared-forgotten
- q:
  - Do the forgetting findings hold for both classification and generation models?
  - Were the fusion results replicated on more than one architecture?
  answers:
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
