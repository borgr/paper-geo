---
one_liner: Reinforcement learning helps neural machine translation little because the action
  space is the whole vocabulary; shrinking it — by using a 1K target vocabulary, or by initializing
  the decoder's final layer with BERT embeddings and freezing it during RL — recovers 1.5
  BLEU on average over standard RL.
key: yehudai2022rl
claims:
- id: action-space-hypothesis
  kind: context
  text: Yehudai et al. (2022) identify the size of the action space, spanning all tens of
    thousands of vocabulary tokens, as a main obstacle to reinforcement learning's effectiveness
    in neural machine translation.
  scope: Four low-resource WMT pairs into English, MRT with BLEU as reward; prior work on
    large action spaces existed outside text generation.
- id: small-vocab-rl-gain
  kind: result
  text: Cutting the target BPE vocabulary from 17K-31K to 1K raises the BLEU gain that RL
    adds over MLE pretraining from 0.6/0.17/0.23/0.22 to 1.4/0.83/1.1/1.59 points on de-en,
    cs-en, ru-en and tr-en. That is about 1 BLEU point more improvement on average.
  evidence: Table 1
  scope: Low-resource WMT News Commentary v13 (SETIMES2 for tr-en), gated convolutional encoder-decoder,
    MRT mixed with token-level loss at alpha=0.3, smoothed BLEU as reward; the 1K models'
    absolute BLEU is lower.
- id: stv-low-ranks
  kind: result
  text: With a 1K target vocabulary, RL shifts probability mass upward from low-ranked tokens
    in neural machine translation. Within the first 100 ranks the small-vocabulary model reduces
    the probability of 83 ranks, against only 2 for the large-vocabulary model.
  evidence: Figure 1
  scope: Measured over 700K trials of gold-token rank under teacher-forced contexts, four
    language pairs into English, MRT training with smoothed BLEU as reward.
- id: bert-freeze-bleu
  kind: result
  text: Initializing the decoder's final fully connected layer with BERT embeddings and freezing
    it during RL reaches 24.71/17.37/18.30/14.55 BLEU on de-en/cs-en/ru-en/tr-en, 1.5 BLEU
    points above regular RL on average.
  evidence: Table 2
  scope: Four low-resource pairs into English, BERT target vocabulary of 30,526, MRT with
    BLEU reward, MLE pretraining with frozen BERT embeddings; on ru-en freezing does not help
    (18.30 vs 18.68).
- id: bert-init-alone
  kind: result
  text: BERT target-embedding initialization alone improves RL on all four language pairs
    into English, from 23.19/15.81/17.31/12.66 BLEU for plain RL to 24.44/17.04/18.68/14.37.
    Freezing MLE-learned target embeddings during RL instead gives only a slight gain.
  evidence: Table 2
  scope: Low-resource WMT setting, gated convolutional NMT, MRT objective; plain RL over MLE
    is itself near-flat (no change on cs-en and ru-en), which is the baseline the BERT gain
    is measured against.
- id: freeze-params
  kind: result
  text: Freezing the target embedding layer removes more than 60% of the network's trainable
    parameters, from 74.8M-77.2M down to 27.9M-30.2M across the four language pairs. BLEU
    improves rather than degrades under this reduction.
  evidence: Table 5
  scope: Gated convolutional encoder-decoder with hidden size 768 and BERT's 30,526-token
    target vocabulary, four low-resource pairs into English; the frozen embeddings must be
    informative rather than random.
- id: random-frozen-fails
  kind: result
  text: Freezing randomly initialized target embeddings during both MLE and RL degrades German-English
    translation by about 2 BLEU points. The benefit of freezing therefore depends on the quality
    of the embedding space rather than on parameter reduction.
  evidence: Table 2
  scope: Low-resource NMT setup with gated convolutional encoder-decoder, BERT's 30,526-token
    target vocabulary and the MRT objective, four pairs into English.
- id: simulation
  kind: result
  text: In a contextual bandit where 10 real actions are each duplicated 400 times into 4000
    policy-level actions, initializing the policy's last layer so duplicated actions share
    weights speeds up learning. Freezing that informative initialization speeds it up further.
  evidence: Figure 2
  scope: Synthetic 10-300-300-4000 feed-forward policy, 50 trials per agent, binary reward
    with Gaussian noise; the informative initialization encodes only which actions are duplicates
    and no information about which action is rewarding.
- id: human-eval
  kind: result
  text: Two professional translators rating 100 translations per language pair on a 0-100
    adequacy scale score the BERT-initialized, frozen-embedding RL model above baseline RL
    on all four language pairs. The Wilcoxon rank sum p-value is 8.5e-5.
  evidence: Figure 4
  scope: Both annotators native English speakers, judging how well each translation conveys
    the reference's information; significance is computed over the pooled score distributions
    of the two models, not per language pair.
- id: sim-scores
  kind: result
  text: On the SIM semantic-similarity metric the BERT-initialized frozen-embedding RL model
    scores 72.81/66.44/67.66/63.59 on de-en/cs-en/ru-en/tr-en against 71.17/63.29/66.17/59.99
    for plain RL, with the largest gains on cs-en and ru-en.
  evidence: Table 6
  scope: SIM as defined by Wieting et al. (2019), which gives partial credit to lexically
    different but semantically correct translations; BLEU, not SIM, was the reward optimized
    during RL.
- id: bert-vs-mle-embeddings
  kind: result
  text: MLE-learned target embeddings give nearly identical cosine-similarity distributions
    for inflection pairs, synonym pairs and random word pairs, whereas BERT embeddings separate
    inflections from random pairs. BERT still places synonyms close to random pairs.
  evidence: Figure 5
  scope: Word pair lists compiled from WordNet and spaCy; comparison is between the MLE model's
    learned target embeddings in this low-resource NMT setup and BERT's embedding layer.
- id: mle-bert-freeze
  kind: result
  text: 'During MLE pretraining, BERT target embeddings must be frozen to help: frozen BERT
    embeddings reach 23.46/16.59/18.14/14.15 BLEU versus 22.99/15.32/17.57/12.65 when trainable,
    a gain of 0.47 to 1.50 points.'
  evidence: Table 4
  scope: Four low-resource pairs into English with BERT's 30,526-token vocabulary; the paper
    attributes the difference to catastrophic forgetting of BERT parameters when the layer
    is trainable.
qa:
- ask:
    plain: why does reinforcement learning barely improve a translation model that was already
      trained normally?
    jargon: what limits the effectiveness of policy gradient fine-tuning in neural machine
      translation, and is the token-level action space the bottleneck?
    task: how do I get a meaningful gain out of RL fine-tuning on top of an MLE-trained translation
      model?
    practitioner: is RL fine-tuning worth running on my translation model, or will the gain
      be a fraction of a BLEU point?
  answered_by:
  - action-space-hypothesis
  - small-vocab-rl-gain
- ask:
    plain: which research first argued that having tens of thousands of word choices is what
      makes reinforcement learning weak for translation?
    jargon: where does the large-action-space explanation for the limited effect of RL in
      NMT originate?
    task: what should I read first about why the vocabulary-sized action space holds back
      RL for machine translation?
  answered_by:
  - action-space-hypothesis
- ask:
    plain: does a translation model with a much smaller set of output word pieces benefit
      more from reinforcement learning?
    jargon: how do RL gains over MLE pretraining change between a 1K and a 17K-31K target
      BPE vocabulary?
    task: how do I test whether the number of output tokens is what caps my RL fine-tuning
      gains in translation?
    practitioner: should I shrink my target subword vocabulary before RL fine-tuning a translation
      model?
  answered_by:
  - small-vocab-rl-gain
  - stv-low-ranks
- ask:
    plain: when reinforcement learning improves a translation model, does it lift word choices
      the model previously thought unlikely?
    jargon: does RL fine-tuning redistribute probability mass toward low-ranked target tokens,
      or only sharpen already high-probability ones?
    task: how do I tell which output tokens reinforcement learning actually promotes in my
      translation decoder?
  answered_by:
  - stv-low-ranks
  - bert-init-alone
- ask:
    plain: can pretrained language model word vectors in a translation decoder's output layer
      make reinforcement learning work better?
    jargon: how much BLEU does initializing the decoder's final fully connected layer with
      BERT target embeddings and freezing it add over standard RL fine-tuning?
    task: how do I shrink the effective action space of my translation decoder without cutting
      the vocabulary itself?
    practitioner: should I swap in BERT embeddings as my decoder output layer before RL fine-tuning?
  answered_by:
  - bert-freeze-bleu
  - bert-init-alone
- ask:
    plain: if the output word vectors of a translation model are left untouched during reinforcement
      learning, does quality suffer?
    jargon: what happens to BLEU and to the trainable parameter count when the target embedding
      layer is frozen during RL fine-tuning of a convolutional NMT model?
    task: how do I cut the number of parameters trained during RL fine-tuning of a translation
      model without losing quality?
    practitioner: can I freeze my decoder's output embedding layer during RL to save trainable
      parameters?
  answered_by:
  - freeze-params
  - random-frozen-fails
- ask:
    plain: is freezing a translation model's output word vectors helpful because there is
      less to learn, or because those vectors are already good?
    jargon: does the benefit of a frozen target embedding layer in RL come from parameter
      reduction or from the quality of the embedding space?
    task: how do I check whether freezing helps my policy for the right reason before I rely
      on it?
  answered_by:
  - random-frozen-fails
  - simulation
- ask:
    plain: is there a small controlled experiment showing that having many duplicate choices
      slows down reward-based learning?
    jargon: how does a contextual bandit with 10 real actions duplicated into 4000 motivate
      a shared-weight, frozen last layer for the policy?
    task: how do I demonstrate the cost of redundant actions in policy gradient learning outside
      of machine translation?
  answered_by:
  - simulation
- ask:
    plain: do people actually judge the improved translations as better, not just the automatic
      score?
    jargon: was the BLEU gain from the BERT-initialized frozen-embedding RL model confirmed
      by human adequacy judgments and by a semantic similarity metric?
    task: how do I verify that an RL fine-tuning gain in translation is real and not just
      reward gaming of BLEU?
    practitioner: should I trust the reported gains from frozen BERT target embeddings, or
      are they BLEU-only artifacts?
  answered_by:
  - human-eval
  - sim-scores
- ask:
    plain: do the gains from pretrained output word vectors show up on a meaning-based score
      and not only on the score being optimized?
    jargon: what semantic similarity scores does the BERT-initialized frozen-embedding RL
      model reach compared with plain RL on de-en, cs-en, ru-en and tr-en?
    task: how do I measure whether my RL-tuned translation model improved in meaning rather
      than only in the BLEU reward?
  answered_by:
  - sim-scores
- ask:
    plain: are pretrained word vectors better than ones a translation model learns itself
      at putting related words near each other?
    jargon: how do cosine-similarity distributions for inflection, synonym and random word
      pairs differ between BERT target embeddings and MLE-learned ones?
    task: how do I check whether my decoder's output embeddings generalize across similar
      target words?
    practitioner: if I want output embeddings that group related words, should I take BERT's
      or the ones my MLE training produced?
  answered_by:
  - bert-vs-mle-embeddings
- ask:
    plain: when pretrained word vectors are used as a translation model's output layer, should
      training be allowed to change them?
    jargon: during MLE pretraining of an NMT decoder, do BERT target embeddings have to be
      frozen to give a BLEU gain?
    practitioner: should I keep BERT target embeddings frozen or trainable while pretraining
      my translation model with cross-entropy?
  answered_by:
  - mle-bert-freeze
terminology:
  target embeddings: The rows of the final fully connected layer that maps a decoder's internal
    d-dimensional representation to the target vocabulary, viewed as embeddings of the output
    actions in inverse analogy to the input embedding layer.
  informative initialization: Initializing a policy network's last layer so that weight vectors
    projecting to similar or duplicated actions start out identical or close, encoding the
    structure of the action space without any information about which actions are rewarding.
  LTV / STV: Large target vocabulary (17K-31K BPE tokens) versus small target vocabulary (1K
    BPE tokens) on the target side of a translation model, with the source vocabulary unchanged.
  SIM: A semantic similarity metric for translation that assigns partial credit to translations
    that are semantically correct but lexically different from the reference, introduced by
    Wieting et al. (2019).
misreadings:
- 'The small-vocabulary result is not a recommendation to translate with a 1K target vocabulary:
  the 1K models have lower absolute BLEU than the large-vocabulary models, and the finding
  is that RL adds more on top of them.'
- Freezing the target embedding layer is not helpful by itself as a form of regularization
  or parameter reduction — freezing randomly initialized target embeddings costs about 2 BLEU
  on German-English.
- The 1.5 BLEU average improvement is measured against regular RL fine-tuning in the same
  BERT-vocabulary setup, not against the best system for these language pairs; the method
  surpasses the large-BPE-vocabulary RL baseline on all pairs except German.
- The gains are reported only in low-resource settings (roughly 200K-290K training sentence
  pairs) with a gated convolutional encoder-decoder and MRT; whether they carry to high-resource
  NMT or to Transformer-based large models is left to future work.
- 'BERT embeddings are not shown to capture synonymy well as target embeddings: their cosine-similarity
  distribution for synonyms that do not share a stem stays close to that of random word pairs.'
links_extra:
  code: https://github.com/AsafYehudai/Reinforcement-Learning-with-Large-Action-Spaces-for-Neural-Machine-Translation
---
