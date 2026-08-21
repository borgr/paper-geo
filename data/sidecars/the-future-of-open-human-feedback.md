---
one_liner: A position paper by 20 interdisciplinary authors that defines open human feedback
  along 5 axes of openness, draws lessons from peer production and open source, and lays out
  7 challenges plus the platform, shared data pool and feedback loops needed for a sustainable
  open feedback ecosystem for language models.
key: donyehiya2025openfeedback
claims:
- id: openness-five-axes
  kind: result
  text: '"Open human feedback" is decomposed into 5 non-binary axes of openness: open methodology,
    open access, open model participation, open human participation and open timeline. Openness
    is treated as a gradient rather than a binary label, motivated by open-washing concerns
    in "open source AI".'
  scope: Definitional framework covering valenced human responses to model outputs; traditional
    labelled datasets and fully model-simulated feedback fall outside the definition.
  evidence: Section 1.1
- id: no-dataset-open-on-all-axes
  kind: result
  text: Of 16 human feedback datasets and model reports surveyed, only ShareLM and Chatbot
    Arena are marked open on all 5 axes of openness. Chatbot Arena's open access is flagged
    because the largest volume of its prompts and feedback remains unpublished.
  scope: The 16 rows span ShareLM, Chatbot Arena, WildChat, PRISM, HelpSteer2, DICES, AnthropicHH,
    WebGPT, LLaMa 2 and 3.1, InstructGPT, GPT4, Claude 2 and 3, and Gemini 1.0 and 1.5, as
    of the 2024 preprint.
  evidence: Table 1
- id: frontier-model-reports-closed
  kind: result
  text: The 5 frontier model families surveyed, GPT4, Claude 2, Claude 3, Gemini and Gemini
    1.5, are marked closed on all 5 openness axes. Their feedback collection methodology is
    not released, so it cannot be reproduced or studied externally.
  scope: Based on public model cards and technical reports available in 2024; LLaMa 2, LLaMa
    3.1 and InstructGPT are instead marked as having open methodology but closed data access.
  evidence: Table 1
- id: three-reasons-underdeveloped
  kind: result
  text: Sustainable sourcing of human feedback for language models is underdeveloped for 3
    stated reasons. High-quality preference datasets are proprietary, annotation and interface
    costs block new releases, and open datasets are static one-time collections rather than
    maintained living artifacts.
  scope: Diagnosis about chat-based human feedback for language models, not about supervised
    labelling datasets generally; stated with citations to proprietary dataset practice and
    annotation-cost studies.
  evidence: Section 1
- id: seven-themes
  kind: context
  text: The Future of Open Human Feedback organises the challenges of an open feedback ecosystem
    into 7 themes, each with existing approaches and recommendations. The themes are incentives,
    effort and involvement, expert contributions, linguistic and cultural diversity, dynamic
    feedback, privacy, and legal ownership.
  scope: A survey-and-recommendation structure produced by 20 interdisciplinary co-authors
    from academia, industry and open-source communities as of 2024; the themes are argued
    and cited, not experimentally ranked or weighted.
  evidence: Section 3
- id: peer-production-lessons
  kind: result
  text: Community-driven governance and vendor-neutral hosting are identified as the transferable
    ingredients from peer production and open source. Wikipedia's 290k edits per day are cited
    as evidence that volunteer ecosystems can sustain large-scale maintained artifacts.
  scope: Lessons drawn by analogy from Wikipedia, OpenStreetMap, Stack Overflow and open-source
    software projects; extrinsic motivators can displace existing intrinsic motivation, so
    the transfer is not automatic.
  evidence: Section 2.1
- id: expert-feedback-cost
  kind: result
  text: Expert feedback in specialised domains is priced out of open collection, with GPQA-style
    graduate-level expert contributions costing roughly $100 per hour. Companies such as OpenAI
    and DeepMind retain specialised AI trainers' feedback in-house.
  scope: Cost figure cited from GPQA's expert annotation; argued for technical domains such
    as healthcare, legal and finance where layperson feedback is insufficient, and it is a
    third-party figure rather than a new measurement.
  evidence: Section 3.3
- id: distillation-loophole
  kind: result
  text: Simulating feedback with powerful closed models is characterised as a popular loophole
    rather than a substitute for human feedback, carrying legal, reproducibility and transparency
    problems. It also adds a dependency on closed-model ecosystems.
  scope: Distilling one model's outputs to train another as a replacement for human annotation;
    aided or seeded feedback where humans still exercise judgement remains inside the paper's
    definition of human feedback.
  evidence: Section 1
- id: diversity-skew
  kind: result
  text: 'Existing open feedback collections skew toward English speakers from narrow communities,
    with a few annotators contributing the majority of data even in explicitly multilingual
    efforts. Only 4 of the 16 surveyed datasets are marked open on human participation: ShareLM,
    Chatbot Arena, WildChat and PRISM.'
  scope: Argued from cited analyses of WildChat, Chatbot Arena, OpenAssistant and the Aya
    Dataset; the skew toward bulk contributors is reported qualitatively, with no per-dataset
    contribution percentages given.
  evidence: Table 1
- id: naturally-occurring-feedback
  kind: result
  text: Prompted ratings and rankings should be supplemented with naturally occurring feedback
    cues already present in chats, such as a user thanking the model or editing their original
    prompt. Pairwise-comparison platforms attract short conversations with low topical, use-case
    and user diversity.
  scope: Recommendation about chat platforms collecting feedback from real users; argued from
    cited work on existing hosted platforms, with no measured accuracy gain from naturally
    occurring cues.
  evidence: Section 3.2
- id: ecosystem-three-components
  kind: result
  text: 'A sustainable open feedback ecosystem is specified as 3 components: an open-source
    feedback platform, a shared pool of chats and feedback, and participation from aligned
    individual and organisational contributors. Self-sustaining feedback loops join it to
    the model-training ecosystem.'
  scope: A proposed design, not a deployed system; current options are said to fall short,
    with Hugging Face Spaces lacking systematic feedback mechanisms and Argilla lacking support
    for discussing feedback, sharing incentives or collective governance.
  evidence: Section 4
- id: specialized-model-loop
  kind: result
  text: The proposed incentive mechanism for feedback contributors is a marketplace of models
    specialised by topic, culture or language. Feedback given by a community returns to that
    community as a better model for its own needs, not only as a public good.
  scope: A vision described through worked examples such as a law student needing exam-preparation
    accuracy, with personalisation by clustering similar users; no implementation or measured
    uptake is reported.
  evidence: Section 4
- id: human-owns-data
  kind: result
  text: Feedback data should be owned solely by the human contributor even though a model
    co-produced the exchange. Contributors are asked to give informed revocable consent to
    release under a permissive licence such as Creative Commons or an Open Data License.
  scope: A recommendation, and the underlying legal debate over AI-involved authorship remains
    unsettled; opt-out guarantees also face the unresolved problem of propagating removal
    into already-trained derivative models.
  evidence: Section 3.7
- id: actions-checklist
  kind: result
  text: The Future of Open Human Feedback closes with a checklist of concrete actions across
    its 7 themes, each labelled with 1 of 3 readiness levels. The levels are feasible with
    existing tools, partially feasible with some R&D, or requiring R&D.
  scope: Readiness labels are the 20 co-authors' collective assessment as of 2024, covering
    actions for incentives, contribution barriers, expert annotation, diversity, updated feedback,
    privacy and legal practice.
  evidence: Section 3
qa:
- ask:
    practitioner: What should I read about opening up human feedback data for language models?
    unsorted:
    - Is there a good overview paper on the human feedback data ecosystem for LLMs?
    - Where can I start reading about why RLHF preference data is closed and what to do about
      it?
  answered_by:
  - seven-themes
  - three-reasons-underdeveloped
  - ecosystem-three-components
- ask:
    unsorted:
    - What does it mean for a human feedback dataset to be open?
    - How can openness of preference data be measured beyond just a public download link?
    - Are there dimensions of openness for RLHF datasets other than access?
  answered_by:
  - openness-five-axes
- ask:
    unsorted:
    - Which human preference datasets are actually open?
    - Are any RLHF feedback datasets open on every dimension of openness?
    - How do WildChat, PRISM, Chatbot Arena and AnthropicHH compare on openness?
  answered_by:
  - no-dataset-open-on-all-axes
  - frontier-model-reports-closed
- ask:
    unsorted:
    - Why is there so little open human feedback data for language models?
    - What blocks researchers from releasing new preference datasets?
    - Why are open preference datasets static instead of continuously updated?
  answered_by:
  - three-reasons-underdeveloped
- ask:
    unsorted:
    - What can open human feedback collection learn from Wikipedia and open source?
    - Do peer production communities offer lessons for collecting AI training feedback?
    - How much do volunteer communities like Wikipedia actually produce?
  answered_by:
  - peer-production-lessons
- ask:
    unsorted:
    - How expensive is collecting expert feedback in domains like medicine or law?
    - Why can't open communities collect domain-expert annotations for LLMs?
    - What does graduate-level expert annotation cost per hour?
  answered_by:
  - expert-feedback-cost
- ask:
    unsorted:
    - Is generating preference data with GPT-4 a valid substitute for human feedback?
    - What is wrong with simulating human feedback using closed models?
    - Are synthetic preferences from strong models a problem for open AI research?
  answered_by:
  - distillation-loophole
- ask:
    unsorted:
    - Who actually contributes to open feedback datasets, and is the pool diverse?
    - Are open preference datasets representative across languages and cultures?
    - Do a few annotators dominate crowdsourced feedback for LLMs?
  answered_by:
  - diversity-skew
- ask:
    unsorted:
    - How can chat platforms collect feedback without asking users to rate responses?
    - What is naturally occurring feedback in a conversation with a language model?
    - Are thumbs-up ratings and pairwise comparisons enough for collecting feedback?
  answered_by:
  - naturally-occurring-feedback
- ask:
    unsorted:
    - What infrastructure would a sustainable open feedback ecosystem need?
    - What components are proposed for pooling chats and feedback across the community?
    - Do existing platforms like Hugging Face Spaces or Argilla already support open feedback
      collection?
  answered_by:
  - ecosystem-three-components
  - specialized-model-loop
- ask:
    unsorted:
    - Why would anyone donate their chat logs and feedback to a shared pool?
    - What incentives could sustain long-term contribution of preference data?
    - How can contributors of feedback benefit directly from what they give?
  answered_by:
  - specialized-model-loop
  - peer-production-lessons
- ask:
    unsorted:
    - Who legally owns feedback given on a language model's output?
    - What licensing and consent practices are recommended for sharing chat feedback?
    - Can users retract feedback they contributed to an open dataset?
  answered_by:
  - human-owns-data
- ask:
    unsorted:
    - What concrete steps can a project take today to open its feedback pipeline?
    - Which recommendations for open human feedback are already actionable versus needing
      research?
    - Is there a checklist for building an open human feedback project?
  answered_by:
  - actions-checklist
  - seven-themes
terminology:
  open human feedback: Human-generated, valenced responses to AI model outputs, characterised
    by open data accessibility and permissive terms of use with ongoing and inclusive participation
    by both humans and AI models.
  open model participation: 'An axis of feedback-dataset openness: whether feedback is collected
    only from one predetermined language model, or whether third parties can upload their
    own models to be included.'
  open timeline: 'An axis of feedback-dataset openness: whether feedback collection is dynamic
    and continues to cover new models, topics and capabilities, rather than being a one-time
    effort over a single short time frame.'
  self-sustaining feedback loop: An arrangement in which a community's chat feedback trains
    a model specialised to that community, so the contributors of feedback are also its direct
    beneficiaries.
  feedback: Human responses to model outputs carrying a positive or negative value judgement;
    annotations over human-written text are excluded because they contain no reaction to a
    model.
misreadings:
- 'The 5 axes of openness are not a binary open/closed test: a dataset can have open methodology
  while its data stays closed, as LLaMa 2, LLaMa 3.1 and InstructGPT are categorised in Table
  1.'
- The Future of Open Human Feedback is a position and survey paper with recommendations, not
  an empirical evaluation of feedback collection methods; no new dataset, platform or model
  is released or benchmarked.
- 'Openness of model weights is not openness of feedback data: open-weight model releases
  are categorised as closed on data access in the paper''s own survey table.'
- The vision of specialised models trained on community feedback is a proposal for an ecosystem,
  not a report of a deployed marketplace of models.
- 'The call for open participation is not a call for unrestricted crowdsourcing: participation
  can be exploitative, and diversity is not guaranteed by openness alone.'
---
