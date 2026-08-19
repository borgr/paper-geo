<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 1 repair round. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept the-sharelm-collection-and-plugin-contributing-human-model-c

Stamp: spec=8f05813a4658 checks=pass body=7dd569e864c6
-->
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
- q:
  - Where can I find a large open dataset of real conversations between people and language
    models?
  - What dataset should I read about first for human-LLM chat logs?
  - Is there an openly licensed collection of human-chatbot conversations?
  answers:
  - collection-size
  - living-dataset-context
- q:
  - How many conversations are in the ShareLM collection and from how many models?
  - How large is the biggest unified open collection of human-model chat datasets?
  - What is the size of the ShareLM chat dataset?
  answers:
  - collection-size
- q:
  - How can users donate their own chatbot conversations for open research?
  - Is there a browser extension for sharing my LLM chats with the research community?
  - How do I contribute my ChatGPT or Gradio demo conversations to an open dataset?
  answers:
  - platform-coverage
  - open-license-release
- q:
  - What stops me from accidentally sharing a private conversation with a chat-donation plugin?
  - How does the ShareLM plugin let users delete a chat before it is uploaded?
  - What is delayed upload in conversation collection extensions?
  answers:
  - delayed-upload
  - study-popup-use
- q:
  - Which chat platforms does the ShareLM plugin support?
  - Can a chat-sharing extension record conversations from platforms other than ChatGPT?
  - Does the plugin work with Gradio and ChatUI demos?
  answers:
  - platform-coverage
- q:
  - How is human feedback collected on donated LLM conversations?
  - Can users rate individual model responses as well as whole conversations?
  - Does ShareLM collect thumbs-up/down preference signals?
  answers:
  - two-feedback-granularities
- q:
  - Was the ShareLM plugin evaluated with real users?
  - How usable did participants find the chat-donation extension?
  - What did the ShareLM user study find about installation and UI?
  answers:
  - user-study-install
  - study-popup-use
- q:
  - How is privacy handled when human-model chats are publicly released?
  - Are donated conversations anonymized before publication?
  - What metadata does the ShareLM plugin collect about me?
  answers:
  - anonymization
- q:
  - Why is a continuously growing chat dataset better than a one-time crowdsourced one?
  - What is the argument for living rather than static human-model conversation datasets?
  - How does ShareLM differ from ShareGPT and Chatbot Arena?
  answers:
  - living-dataset-context
  - platform-coverage
- q:
  - Who owns the data in a conversation-donation system?
  - What design principles guide user control in chat data collection tools?
  - Can I ask for my conversations to be removed from the ShareLM dataset?
  answers:
  - user-ownership-context
  - delayed-upload
- q:
  - Under what license are ShareLM plugin conversations published?
  - Where is the ShareLM data and plugin code available?
  - Is the collected chat data openly licensed?
  answers:
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
