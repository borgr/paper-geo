---
key: don-yehiya-etal-2025-sharelm
coined: ShareLM
gloss: a unified collection of human-with-LLM chat datasets plus a Chrome extension for donating
  your own chats
one_liner: ShareLM is a unified collection of human-model conversation datasets and a Chrome
  extension that lets any user donate their own chats from most chat platforms, with thumbs-up/down
  rating and a 24-hour delayed upload so unwanted conversations can be deleted before they
  leave local storage.
claims:
- id: collection-size
  kind: result
  text: The ShareLM collection unifies publicly released human-model conversation datasets
    into one format and contains over 2.3M conversations from over 40 different models. Its
    constituents include HH-RLHF, PRISM, WildChat and Chatbot Arena, plus conversations donated
    through the ShareLM plugin.
  scope: Size as reported at publication in 2025; the collection grows over time. WildChat
    and Chatbot Arena are gated datasets requiring the user to accept their own terms of use,
    and the constituent datasets keep their original licenses.
  evidence: Section 2
- id: delayed-upload
  kind: result
  text: The ShareLM plugin holds each recorded conversation in the browser's local database
    for 24 hours before posting it to the server. A user can review and delete a conversation
    in that window, before it ever leaves their own storage.
  scope: Chrome extension; deletion within the window is local, whereas removal after a dataset
    release is requested through a contact form and cannot undo copies already downloaded.
    A "Publish Now" button bypasses the delay.
  evidence: Section 3.2 and Section 4.3
- id: platform-coverage
  kind: result
  text: The ShareLM plugin records chats by matching elements in the web page XML rather than
    calling a model API, which makes it independent of any single model or serving platform.
    At publication it supported Gradio demos, ChatUI and ChatGPT.
  scope: Support is per web interface and needs a small code addition per new interface; unlike
    ShareGPT and Collective Cognition, which were ChatGPT-only.
  evidence: Section 3.2 and Section 7
- id: two-feedback-granularities
  kind: result
  text: 'The ShareLM plugin collects thumbs-up/down feedback at two granularities: for a whole
    conversation from the popup after the fact, and for each individual model response at
    the time of interaction.'
  scope: Per-response rating was available for the ChatUI interface only at publication; rating
    is voluntary, so many collected conversations carry no feedback.
  evidence: Section 5, Figure 1 and Figure 4
- id: user-study-install
  kind: result
  text: In a user study of 10 participants who installed and used the ShareLM plugin, 9 of
    10 rated the installation experience 5 out of 5, for an average of 4.8. Average scores
    were 4.7 for first-time use and 4.7 for the UI.
  scope: 10 participants, self-reported 1-5 ratings, no control condition; one participant
    complained that refresh time is long. Participants reported using open models only 2.7
    on average on a 1-5 frequency scale.
  evidence: Section 6
- id: study-popup-use
  kind: result
  text: Half of the 10 participants in the ShareLM user study reported using the plugin popup
    to rate or delete some of their conversations. The review-before-upload control is therefore
    exercised rather than ignored.
  scope: 10 participants in a short experimentation session, self-reported; no measurement
    of how many conversations were actually deleted in the wild.
  evidence: Section 6
- id: anonymization
  kind: result
  text: ShareLM runs a server-side anonymization script over donated conversation content
    to strip names, addresses and phone numbers. Alongside the text it collects only the URL,
    a GMT timestamp and a random user ID, with no IP address, local time or browser type.
  scope: The paper states explicitly that no shared text should be assumed fully anonymous,
    and asks users to avoid sending identifying content in the first place; demographic fields
    (age, country, gender) are optional and user-supplied.
  evidence: Section 3.2 and Appendix A
- id: living-dataset-context
  kind: context
  text: ShareLM argues that open human-model conversation datasets are usually treated as
    static one-time collections rather than living artifacts. It offers instead a continuously
    growing collection fed by an end-user browser plugin.
  scope: Positioning as of publication in 2025, relative to ShareGPT, Collective Cognition,
    Chatbot Arena and crowdsourced one-time datasets; the paper notes the plugin's user base
    is still not large.
  evidence: Section 1 and Section 7
- id: user-ownership-context
  kind: context
  text: ShareLM is a reference point for data-donation design in NLP, placing conversation
    collection on the user's side of the interaction. The user can pause recording, rate,
    delete and request removal of their own chats.
  scope: Design principles and a demo system as of publication in 2025; scaling depends on
    individual users installing an extension, and the paper notes that a model-serving entity
    collecting data would scale more easily.
  evidence: Section 3.1 and Limitations
- id: open-license-release
  kind: result
  text: Conversations donated through the ShareLM plugin are released on Hugging Face as part
    of the ShareLM collection, under the most permissive license allowed by the specific model.
    The code and Chrome extension are openly available.
  scope: Releases were validated manually before upload at publication, with full automation
    planned; per-model license terms bound what can be released.
  evidence: Section 3.2 and Section 8
qa:
- ask:
    plain: where should I start reading about openly available logs of people chatting with
      chatbots?
    jargon: which resource should be read first for open human-model dialogue corpora with
      permissive licensing?
    task: how do I find a growing, openly licensed corpus of real human-chatbot conversations
      to train or study on?
    practitioner: I need real human-chatbot dialogue data for my project, which public collection
      should I pick up first?
  answered_by:
  - collection-size
  - living-dataset-context
- ask:
    plain: how many real chatbot conversations are in the ShareLM collection, and from how
      many chatbots?
    jargon: what is the conversation count and model coverage of the ShareLM human-model dialogue
      collection?
    task: how do I tell whether a unified collection of human-chatbot chat logs is big enough
      for finetuning?
    practitioner: is the ShareLM conversation collection large enough to be worth downloading
      for my training run?
  answered_by:
  - collection-size
- ask:
    plain: how can ordinary people hand over their own chatbot conversations so researchers
      can use them?
    jargon: what mechanism lets end users donate human-model dialogues into an openly licensed
      corpus?
    task: how do I share the conversations I have with ChatGPT or a Gradio demo into a public
      dataset?
    practitioner: I want my own chatbot chats to end up in an open dataset, what do I install
      and where do they go?
  answered_by:
  - platform-coverage
  - open-license-release
- ask:
    plain: if a browser add-on records my chatbot conversations, can I take one back before
      it is sent anywhere?
    jargon: how does a conversation-donation extension implement a local retention window
      before server upload?
    task: how do I make sure a chat I regret never reaches the collection server?
    practitioner: do I get a chance to review and delete a recorded chat before it is uploaded,
      and do people actually use it?
  answered_by:
  - delayed-upload
  - study-popup-use
- ask:
    plain: which chatbot websites can a conversation-recording browser extension capture chats
      from?
    jargon: how does XML element matching in the page let a chat-collection extension stay
      model- and serving-platform agnostic?
    task: how do I collect conversations from a Gradio demo or a hosted chat UI without wiring
      up an API?
    practitioner: will a chat-donation extension work with the demo I host, or only with ChatGPT?
  answered_by:
  - platform-coverage
- ask:
    plain: can people mark whether a chatbot reply was good or bad while their conversations
      are being collected?
    jargon: at what granularities are thumbs-up/down preference signals gathered alongside
      donated human-model dialogues?
    task: how do I get per-response as well as per-conversation quality ratings out of real
      user chats?
    practitioner: if I use ShareLM data, do I get response-level human feedback or only whole-conversation
      ratings?
  answered_by:
  - two-feedback-granularities
- ask:
    plain: did real people try out the chat-donation browser extension, and how easy did they
      find it?
    jargon: what did the ShareLM usability study report on installation, first use and interface
      ratings?
    task: how do I know whether asking volunteers to install a chat-recording extension is
      realistic?
    practitioner: can I expect ordinary users to install and actually operate a conversation-donation
      plugin?
  answered_by:
  - user-study-install
  - study-popup-use
- ask:
    plain: what happens to personal details in chatbot conversations before they are published?
    jargon: what anonymization and metadata-minimization are applied to donated human-model
      dialogues prior to release?
    task: how do I release donated chat logs without exposing names, addresses or user identities?
    practitioner: if I donate my chats through ShareLM, what identifying information about
      me is kept?
  answered_by:
  - anonymization
- ask:
    plain: why keep collecting chatbot conversations continuously instead of running one crowdsourcing
      round?
    jargon: what is the case for treating human-model dialogue corpora as living artifacts
      rather than static one-time collections?
    task: how do I build a chat dataset that keeps growing as new models and platforms appear?
    practitioner: should I fund a one-off collection of human-chatbot chats or a continuous
      donation pipeline?
  answered_by:
  - living-dataset-context
  - platform-coverage
- ask:
    plain: who is in charge of a conversation once someone donates their chatbot chats?
    jargon: what user-ownership guarantees govern consent, pausing and removal in a data-donation
      pipeline for dialogue?
    task: how do I design chat data collection so the person who had the conversation keeps
      control of it?
    practitioner: if I donate conversations, can I later pause recording or get my chats taken
      out?
  answered_by:
  - user-ownership-context
  - delayed-upload
- ask:
    plain: can the donated chatbot conversations be used freely, and where do you download
      them?
    jargon: under what licensing terms are ShareLM plugin conversations released, and is the
      extension code open?
    task: how do I check the license and get hold of both the chat data and the recording
      extension?
    practitioner: am I allowed to train a commercial model on the donated conversations in
      the ShareLM collection?
  answered_by:
  - open-license-release
misreadings:
- 'ShareLM is not a single newly crowdsourced dataset: most of its 2.3M conversations come
  from previously released datasets such as HH-RLHF, PRISM, WildChat and Chatbot Arena, unified
  into one format, with the plugin''s own donations added on top.'
- 'The 24-hour delayed upload does not guarantee erasure after release: once a dataset version
  is public, a removal request cannot retract copies already downloaded.'
- The server-side anonymization script is an extra precaution, not a guarantee; the paper
  states explicitly that no shared text should be assumed fully anonymous.
- The user study with 10 participants measures usability of the extension, not the quality,
  diversity or representativeness of the conversations collected.
- Per-response thumbs-up/down rating was not available on every supported interface at publication,
  only on ChatUI; whole-conversation rating is what works everywhere.
- 'The plugin is not restricted to open-source models it hosts itself: it acts as a mediator
  on top of whatever chat web interface the user visits, and records nothing when the interface
  is unsupported or recording is paused.'
terminology:
  ShareLM collection: A set of publicly released human-with-LLM conversation datasets converted
    to a single schema (conversation_id, conversation, model_name, user_id, timestamp, source,
    user_metadata, conversation_metadata), together with conversations donated through the
    ShareLM Chrome extension.
  Delayed upload: Keeping recorded conversations in the browser's local database for 24 hours
    before sending them to a server, so the user can review, rate or delete them before they
    leave their own machine.
  Recording banner: A thin strip at the top of a supported chat page indicating that the current
    conversation is being recorded, with a button to pause sharing.
  Living artifact: A dataset designed to keep growing with new user contributions over time,
    as opposed to a one-time collected static dataset that ages as models and user preferences
    change.
links_extra:
  plugin: https://chromewebstore.google.com/detail/sharelm-share-your-chat-c/nldoebkdaiidhceaphmipeclmlcbljmh
  dataset: https://huggingface.co/datasets/shachardon/ShareLM
  paper: https://aclanthology.org/2025.acl-demo.17/
  project_page: https://sharelm.github.io/
---
