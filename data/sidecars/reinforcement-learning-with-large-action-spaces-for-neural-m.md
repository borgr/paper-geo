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
    unsorted:
    - Why does reinforcement learning give such small gains for neural machine translation?
    - What limits the effectiveness of RL fine-tuning in machine translation?
    - Is the vocabulary size a problem for policy gradient training of translation models?
  answered_by:
  - action-space-hypothesis
  - small-vocab-rl-gain
- ask:
    practitioner: What should I read about reinforcement learning and large action spaces
      in text generation?
    unsorted:
    - Which paper argues that the action space is what holds back RL for translation?
    - Where does the idea of treating the NMT vocabulary as a too-large action space come
      from?
  answered_by:
  - action-space-hypothesis
- ask:
    unsorted:
    - Does shrinking the target vocabulary make RL fine-tuning of a translation model work
      better?
    - How much BLEU does RL add when the target BPE vocabulary is only 1K tokens?
    - What happens to RL gains with a small versus large target vocabulary in NMT?
  answered_by:
  - small-vocab-rl-gain
  - stv-low-ranks
- ask:
    unsorted:
    - Can RL improve translation on tokens the pretrained model ranked low?
    - Does RL only promote tokens that already had high probability after MLE pretraining?
    - Which tokens are responsible for the gains when RL is applied with a small action space?
  answered_by:
  - stv-low-ranks
  - bert-init-alone
- ask:
    unsorted:
    - How do you reduce the effective action space of a translation model without changing
      its vocabulary?
    - Can BERT embeddings be used as the decoder's output layer to help RL fine-tuning?
    - How much BLEU does initializing and freezing the output embedding layer with BERT gain
      over standard RL?
  answered_by:
  - bert-freeze-bleu
  - bert-init-alone
- ask:
    unsorted:
    - Should the output embedding layer be frozen during RL fine-tuning of an NMT model?
    - Does freezing the decoder's final fully connected layer hurt translation quality?
    - How many trainable parameters does freezing target embeddings remove in a convolutional
      NMT model?
  answered_by:
  - freeze-params
  - random-frozen-fails
- ask:
    unsorted:
    - Does freezing help because there are fewer parameters to learn, or because the embeddings
      are good?
    - What happens if you freeze randomly initialized output embeddings during RL?
  answered_by:
  - random-frozen-fails
  - simulation
- ask:
    unsorted:
    - Is there a synthetic experiment showing that duplicated actions slow down policy gradient
      learning?
    - How does a contextual bandit with duplicated actions motivate freezing the policy's
      last layer?
    - Does an informative last-layer initialization help even when it carries no reward information?
  answered_by:
  - simulation
- ask:
    unsorted:
    - Do human annotators prefer translations from the BERT-initialized frozen-embedding RL
      model?
    - Was the BLEU improvement from reducing the action space confirmed by human evaluation?
    - How was adequacy judged when comparing baseline RL against the improved RL model for
      translation?
  answered_by:
  - human-eval
  - sim-scores
- ask:
    unsorted:
    - Do the gains from BERT target embeddings show up on metrics other than the optimized
      BLEU reward?
    - What are the SIM semantic similarity scores for RL with frozen BERT target embeddings?
  answered_by:
  - sim-scores
- ask:
    unsorted:
    - Are BERT embeddings better than MLE-learned output embeddings at grouping related words?
    - Why do BERT target embeddings generalize over similar actions better than embeddings
      learned by MLE?
    - Do BERT embeddings put synonyms close together?
  answered_by:
  - bert-vs-mle-embeddings
- ask:
    unsorted:
    - Should BERT embeddings be trainable or frozen during MLE pretraining of a translation
      model?
    - What is the BLEU difference between frozen and trainable BERT embeddings in MLE training?
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
