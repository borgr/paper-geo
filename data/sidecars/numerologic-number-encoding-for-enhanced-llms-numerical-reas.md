---
key: schwartz2024numerologic
coined: NumeroLogic
gloss: prefixing every number in text with its digit count, e.g. "42" becomes "2:42"
one_liner: NumeroLogic reformats numbers in text by prefixing each one with its digit count
  (so "42" becomes "<sn>2<mn>42<en>"), giving a causal language model the place value of a
  digit before it reads it and forcing it to reason about magnitude before generating one.
claims:
- id: nanogpt-add-sub
  kind: result
  text: With NumeroLogic digit-count prefixes, a from-scratch NanoGPT reaches 99.96% accuracy
    on 3-digit integer addition and 97.20% on subtraction, against 88.37% and 73.76% with
    plain number formatting.
  scope: NanoGPT trained from scratch with character-level tokenization, jointly on 5 arithmetic
    tasks with 10K samples per task (3K for multiplication); addition and subtraction operands
    up to 3 digits.
  evidence: Table 1
- id: nanogpt-mult-float
  kind: result
  text: NumeroLogic more than doubles NanoGPT's 2-digit integer multiplication accuracy, from
    13.81% to 28.94%, and adds about 4 points on 4-decimal sine (30.59% to 34.59%) and square
    root (22.13% to 26.66%).
  scope: Single NanoGPT trained from scratch on all 5 tasks at once; sine operands in [-pi/2,
    pi/2], square root operands in [0, 10], 4 decimal places.
  evidence: Table 1
- id: llama-float-tasks
  kind: result
  text: Fine-tuning Llama2-7B with NumeroLogic raises 3-digit floating-point multiplication
    accuracy from 24.73% to 31.03% and 5-digit floating-point addition from 91.40% to 94.43%,
    with gains of 1-6 points on every non-saturated task.
  scope: One LoRA-finetuned Llama2-7B (rank 8) per task, with the embedding and final linear
    layers trained in full rank; 300K training equations for add/sub/mul, 30K for sine and
    sqrt.
  evidence: Table 2
- id: llama-saturated
  kind: result
  text: 'On tasks Llama2-7B already nearly solves, NumeroLogic still helps: 5-digit integer
    addition goes from 99.86% to 100.0% and subtraction from 99.60% to 99.93%, removing over
    80% of the remaining subtraction errors.'
  scope: LoRA fine-tuning of pretrained Llama2-7B on 5-digit integer addition and subtraction,
    300K training equations per task; the headroom here is under 0.5 points, so the absolute
    gain is small.
  evidence: Table 2
- id: mmlu-pretraining
  kind: result
  text: Continuing self-supervised pretraining of Llama2-7B on RefinedWeb text with numbers
    rewritten in NumeroLogic format improves 0-shot MMLU accuracy by a statistically significant
    0.5%. Continued pretraining on the same tokens with plain numbers does not improve over
    the pretrained model.
  scope: Continued causal-LM pretraining with LoRA on RefinedWeb, plain and NumeroLogic runs
    matched on token count; 0-shot MMLU evaluation; English text only.
  evidence: Figure 2
- id: mmlu-numeric-subsets
  kind: result
  text: 'The MMLU gain from NumeroLogic concentrates where numbers appear: +1.16% on tasks
    containing numbers versus +0.14% on tasks without, and +0.79% on STEM versus +0.1% on
    social sciences.'
  scope: Per-category breakdown of the 0-shot MMLU evaluation of Llama2-7B after continued
    pretraining with LoRA on RefinedWeb; the "Others" category gains most at +1.19%.
  evidence: Tables 3 and 4
- id: operands-vs-results
  kind: result
  text: Encoding only the addition result with a digit-count prefix lifts NanoGPT accuracy
    from 88.37% to 98.05%, while encoding only the operands reaches 89.34%. Encoding both
    operands and result is best at 99.78%.
  scope: 3-digit addition with NanoGPT trained from scratch, same protocol as the joint 5-task
    arithmetic setup with character-level tokenization.
  evidence: Table 5
- id: not-extra-tokens
  kind: result
  text: Replacing NumeroLogic's prefix tokens with the same number of filler white-space tokens
    gives 24.37% on 3-digit float multiplication, close to the 24.73% plain-format baseline.
    NumeroLogic itself reaches 31.03%, so the benefit is not merely the extra tokens.
  scope: Llama2-7B finetuned on 3-digit floating-point multiplication; the random white-space
    placement of Shen et al. (2023), with a matched token budget, reaches 27.76%, better than
    plain but below NumeroLogic.
  evidence: Table 7
- id: encoding-variants
  kind: result
  text: On 3-digit integer multiplication the full "<sn>3<mn>100<en>" format scores 35.33%
    and dropping the end-of-number token gives 34.93%. One dedicated special token per digit
    count gives 33.56%, below the 34.20% plain baseline.
  scope: Llama2-7B finetuned on 3-digit integer multiplication; the paper attributes the failure
    of per-digit-count special tokens to the rarity of short numbers in the training distribution.
  evidence: Table 6
- id: no-arch-change
  kind: context
  text: NumeroLogic is a regex-based text pre- and post-processing step that requires no change
    to model architecture, so digit-count prefixes can be added around an existing tokenizer
    and stripped from generations.
  scope: Adding 3 special tokens (<sn>, <mn>, <en>) to the vocabulary and expanding embedding
    and output layers for pretrained models; increases tokens per number and inference latency.
  evidence: Section 3
- id: general-lm-not-arithmetic-trick
  kind: context
  text: NumeroLogic is positioned as a number-representation change for general self-supervised
    language modeling rather than a task-specific arithmetic fix. Arithmetic tasks only measure
    the effect, and MMLU shows transfer to language understanding.
  scope: As of 2024; contemporaneous arithmetic work such as digit reversal, algorithmic chain-of-thought
    and random white-space insertion targets specific arithmetic tasks. The general-LM evidence
    is one Llama2-7B run on English RefinedWeb text.
  evidence: Section 2
- id: place-value-hypothesis
  kind: context
  text: NumeroLogic starts from the hypothesis that left-to-right causal reading is a real
    handicap for numbers. A decoder-only model cannot know whether a digit means units or
    millions until it has read the whole number.
  scope: A motivating hypothesis supported indirectly by the arithmetic and MMLU gains rather
    than by a direct probe of place-value representations.
  evidence: Section 1
qa:
- q:
  - How can I make a language model better at arithmetic without changing its architecture?
  - Is there a simple text formatting trick that improves LLM number handling?
  - What does prefixing numbers with their digit count do for a language model?
  answers:
  - no-arch-change
  - nanogpt-add-sub
  - llama-float-tasks
- q:
  - Why do LLMs struggle to read numbers left to right?
  - What is the place-value problem for decoder-only language models reading digits?
  - Why does a causal model not know if a digit means thousands or hundreds?
  answers:
  - place-value-hypothesis
- q:
  - Does the digit-count prefix help a 7B model or only tiny models?
  - Do NumeroLogic gains hold when finetuning Llama2-7B?
  - How much does number reformatting improve floating-point multiplication for Llama2-7B?
  answers:
  - llama-float-tasks
  - llama-saturated
- q:
  - Does changing number formatting help general language understanding, not just arithmetic?
  - What happens to MMLU when a model is pretrained with digit-count-prefixed numbers?
  - Can number encoding improve benchmark accuracy outside of math tasks?
  answers:
  - mmlu-pretraining
  - mmlu-numeric-subsets
- q:
  - Are the gains from extra tokens rather than from the digit-count information?
  - Would inserting filler whitespace tokens give the same benefit as NumeroLogic?
  - How does random whitespace insertion compare with digit-count prefixes on multiplication?
  answers:
  - not-extra-tokens
- q:
  - Is digit-count encoding more useful on the operands or on the result of an arithmetic
    equation?
  - Does the benefit of digit-count prefixes come from input comprehension or from a chain-of-thought
    effect on the answer?
  - Should digit-count prefixes be applied to operands, results, or both?
  answers:
  - operands-vs-results
- q:
  - Which digit-count number format works best?
  - Is an end-of-number token needed, or is a digit-count prefix enough?
  - Do dedicated special tokens per digit count work better than a digit-count prefix?
  answers:
  - encoding-variants
- q:
  - What should I read about number tokenization and numerical reasoning in LLMs?
  - Which papers propose changing how numbers are represented for language models?
  - Where does work on number formatting for language models sit relative to arithmetic chain-of-thought
    methods?
  answers:
  - general-lm-not-arithmetic-trick
  - place-value-hypothesis
- q:
  - What are the costs or downsides of adding digit-count prefixes to numbers?
  - Does NumeroLogic increase token count and inference latency?
  answers:
  - no-arch-change
- q:
  - How much does digit-count encoding help small models trained from scratch on arithmetic?
  - Does the format help on sine and square root, not just addition?
  - What are NanoGPT accuracies with and without digit-count prefixes on multiplication?
  answers:
  - nanogpt-mult-float
  - nanogpt-add-sub
misreadings:
- 'NumeroLogic does not make the model output digit counts to the user: the digit-count prefix
  is stripped in post-processing and only the number itself is kept.'
- The MMLU improvement from NumeroLogic is 0.5% overall, concentrated in number-containing
  and STEM tasks; it is not a large across-the-board language-understanding gain.
- 'NumeroLogic was not validated as a from-scratch pretraining recipe for large models: the
  7B experiments continue pretraining or finetune an existing Llama2-7B with LoRA, and no
  model above 7B parameters was tested.'
- 'The gain is not explained by giving the model more tokens to compute with: matched-budget
  filler white-space tokens perform like the plain format.'
- 'Multiplication is improved but not solved: 3-digit multiplication accuracy with Llama2-7B
  remains around 31-35%.'
terminology:
  NumeroLogic: A number format for text fed to language models in which each number is prefixed
    by its digit count, e.g. "42" written as "<sn>2<mn>42<en>" and "3.14" as "<sn>1.2<mn>3.14<en>",
    with the prefix stripped after generation.
  <sn> / <mn> / <en>: Special start-number, mid-number and end-number tokens that delimit
    the digit-count prefix and the number itself; replaced by the characters "{", ":" and
    "}" in character-level small-model experiments.
  Only prefix encoding: A variant digit-count format that keeps the leading digit count but
    omits the end-of-number token, e.g. "<sn>3<mn>100".
  Random white-spaces baseline: A control format from Shen et al. (2023) that inserts filler
    white-space tokens at random positions between digits, used with a token budget matched
    to digit-count prefixing.
---
