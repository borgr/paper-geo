---
one_liner: MindGames is a live multi-game arena (Colonel Blotto, Iterated Prisoner's Dilemma,
  Codenames, Secret Mafia) on TextArena that rated 944 LLM agents from 76 teams, released
  29,571 logged multi-agent games, and audits when leaderboard position reflects strategic
  skill rather than surviving opponents' rule violations.
key: mindgames2026
coined: MG-Ref
gloss: 'MindGames Reference Set: a frozen pool of top low-error competition agents plus a
  deterministic offline tournament schedule for scoring a new agent'
claims:
- id: arena-context
  kind: context
  text: 'MindGames is a live, multi-game arena for LLM agents built on TextArena, pairing
    TrueSkill rating with full trajectory logging across four games. Its four environments
    were chosen for complementary social-reasoning demands: belief attribution, opponent modeling,
    cooperative inference under knowledge asymmetry, and sustained deception.'
  scope: 'Text-only games with structured action formats: Colonel Blotto, 3-player Iterated
    Prisoner''s Dilemma, Codenames, Secret Mafia; as of the 2026 report on the NeurIPS 2025
    cycle.'
- id: dataset-scale
  text: The MindGames NeurIPS 2025 cycle released 29,571 multi-agent games spanning 94,132
    player trajectories and 243M tokens across four game environments, with turn-level observations,
    actions, rewards and metadata.
  scope: 944 submitted agents from 76 teams plus organizer baselines; Stage I ladder contributes
    25,307 games and Stage II 4,264; tokens counted with the Qwen3-4B tokenizer.
  evidence: Table 2
- id: error-rates-stage2
  text: Rule-following, not strategy, was the dominant bottleneck in Stage II of the MindGames
    competition. 50.3% of Secret Mafia games and 38.6% of Codenames games contained at least
    one invalid action, versus 8.5% for Colonel Blotto and 0% for Iterated Prisoner's Dilemma.
  scope: Stage II games only (882 Secret Mafia, 879 Codenames, 1,491 Colonel Blotto, 1,012
    IPD); counts games with at least one fatal or non-fatal error by any player. IPD's 0%
    is partly an artifact of auto-replacing invalid actions with a default cooperate move.
  evidence: Table 4
- id: error-improvement
  text: Error rates in the MindGames arena fell substantially between the open ladder and
    the final evaluation. Codenames dropped from 85.4% to 38.6% of games containing an error,
    Secret Mafia from 77.9% to 50.3%, and Colonel Blotto from 16.5% to 8.5%, while IPD stayed
    at 0%.
  scope: Stage I (July–October 2025, open ladder, 232/177/171/399 participating models per
    environment) versus Stage II (October–November 2025, frozen submissions, 41–55 models);
    improvement conflates agent iteration with the smaller, qualified Stage II model pool.
  evidence: Figure 3
- id: error-survival-confound
  text: Secret Mafia leaderboard position in the MindGames Stage II cycle reflects robustness
    to opponent failure as much as social-deduction skill. The top-ranked efficient agent
    caused errors in only 4 of 130 games but witnessed opponent errors in 129.
  scope: Stage II Efficient Agent division, top-3 ranked Secret Mafia models; fewer than 1%
    of their games were fully error-free, and most Secret Mafia errors are non-fatal, so only
    61 of 129 witnessed-error games ended in an opponent forfeit.
  evidence: Table 5
- id: termination-depth
  text: Terminated Secret Mafia games in the MindGames Stage II cycle ended after fewer than
    3 turns on average, against an expected game length of 8–12 turns. Most forfeits therefore
    happened before meaningful strategic interaction.
  scope: Stage II games with premature termination; IPD excluded because it recorded zero
    failures. Colonel Blotto and Codenames also fail early (3–4 turns) but that is a larger
    fraction of their expected length.
  evidence: Figure 4
- id: validity-diagnostic
  text: 'MindGames proposes two environment-level validity diagnostics for live arenas: game-level
    error rate, and median termination depth as a fraction of expected game length. Once error
    rate exceeds roughly 30% and termination depth falls below half of expected length, leaderboard
    position should be read as robustness to opponent failure rather than strategic skill.'
  scope: Thresholds are proposed from the four MindGames environments in the 2025 cycle rather
    than validated on outside arenas; they classify IPD and Colonel Blotto as interpretable,
    Codenames as mixed, and Secret Mafia as error-survival dominated.
  evidence: Section 5.1
- id: trueskill-reward-divergence
  text: TrueSkill and cumulative reward measure different things in the MindGames arena. Generalization
    Track models spanned roughly -120 to +170 in total reward yet compressed into a TrueSkill
    band of about 0 to +50.
  scope: Stage II top models under calibrated matchmaking pairing similarly rated agents;
    the reversal appears in Secret Mafia between the efficient and unlimited divisions.
  evidence: Figure 5
- id: role-advantage
  text: Role assignment is a substantive confound in social deduction but not in Codenames.
    Across the MindGames competition the Mafia role consistently yields above-average win
    rates while detective, doctor and villager underperform, whereas Codenames role advantages
    stay centered on zero in both stages.
  scope: Role advantage measured as a model's per-role win rate minus its own average win
    rate, across models with at least 8 (Stage I) or 30 (Stage II) games; villager frequency
    is slightly understated because players eliminated before acting are absent from the released
    trajectories.
  evidence: Figure 8
- id: scaffolding-backfires
  text: 'Adding memory and deduction scaffolding to an LLM not trained to use it hurt Secret
    Mafia performance: win rate fell from 25.0% with refined prompting to 16.7%. Supervised
    fine-tuning the same architecture on stronger-model traces then raised it to 45.0%.'
  scope: Qwen3-8B agent, single team's self-reported ablation in the Social Deduction Efficient
    division; a second team independently found an XML cross-turn memory variant underperformed
    its simpler thinking-only agent on an 8B model without fine-tuning.
  evidence: Appendix A.2.1
- id: training-vs-scaffolding
  text: In the MindGames competition, 4 of 6 top Efficient-division (≤9B open-weight) entries
    fine-tuned on game trajectories, whereas 5 of 6 top Unlimited-division entries used no
    task-specific training. Training-time adaptation dominated under parameter constraints
    and inference-time structure dominated at frontier scale.
  scope: Stage II top-3 teams per track and division; the exception is In2AI, whose RL-trained
    Qwen3-8B ranked first in the Unlimited Generalization track ahead of prompted GPT-5. Division
    pools experienced different matchmaking dynamics, so cross-division comparison is qualitative.
  evidence: Table 3
- id: non-llm-policy
  text: A 6.8M-parameter graph attention policy reached a 78.40% win rate (95% CI 77.36–79.44)
    over 1,000 Colonel Blotto games, up from 58.4% for PPO alone. It was trained by LLM-guided
    preference generation and distillation rather than by playing as an LLM.
  scope: Single team's self-reported evaluation on Colonel Blotto and Codenames against their
    own opponent pool, not competition leaderboard games; Qwen 2.5-Instruct and Llama 3-Instruct
    served only as preference teachers.
  evidence: Appendix A.1.5
- id: villager-asymmetry
  text: Architectural improvements in Secret Mafia disproportionately help the information-poor
    Villager side. One MindGames team reports a 9x Village-side improvement (8.3% to 75.0%
    win rate) versus Mafia improving from 25% to 62.5%.
  scope: Two teams' self-reported Social Deduction results with differing baselines, so the
    multipliers are not comparable; a second team lifted Villager win rate from 16% to 60%
    with Mafia at 88–96%.
  evidence: Appendix A.2.4
- id: mgref-protocol
  kind: context
  text: MG-Ref lets a new agent be scored offline against the MindGames 2025 cohort by playing
    198 games against a frozen pool of top-ranked, low-error Stage II submissions. Each run
    reports TrueSkill, cumulative reward, role-conditioned win rates and error-attribution
    columns under a deterministic factorial schedule.
  scope: '198 games per participant: 30 Colonel Blotto, 36 IPD, 36 Codenames, 96 Secret Mafia.
    Reference ratings are frozen and only the new agent''s posterior updates. Secret Mafia
    runs with only 5 active identities, so its offline TrueSkill is a local estimate.'
  evidence: Table 17
qa:
- ask:
    plain: where can I find a benchmark where language model agents play social games against
      each other?
    jargon: is there a live multi-environment arena for evaluating theory-of-mind and strategic
      reasoning in LLM agents?
    task: how do I evaluate an LLM agent on social reasoning against other agents rather than
      on a static test set?
    practitioner: which arena should I put my agent in if I want to measure its deception
      and opponent-modeling ability?
  answered_by:
  - arena-context
  - dataset-scale
- ask:
    plain: is there a big public collection of recorded games played by language model agents?
    jargon: what scale of multi-agent trajectory data with turn-level observations, actions
      and rewards is publicly released for LLM game play?
    task: where do I get game trajectories to fine-tune an agent on social deduction and negotiation
      play?
    practitioner: is there enough released game data to train on, or do I have to generate
      my own self-play?
  answered_by:
  - dataset-scale
- ask:
    plain: how often do language model agents break the rules of a text game instead of losing
      on strategy?
    jargon: what share of LLM agent games contain invalid actions, and is format compliance
      or strategic play the binding constraint?
    task: how do I tell whether my agent is losing because of bad strategy or malformed actions?
    practitioner: should I spend my effort on action-format reliability or on smarter play
      for my game-playing agent?
  answered_by:
  - error-rates-stage2
  - error-improvement
- ask:
    plain: can a ranking in a social deduction game be decided by other players making mistakes
      rather than by skill?
    jargon: to what extent does Secret Mafia leaderboard position reflect robustness to opponent
      forfeits rather than social-deduction ability?
    task: how do I check whether my agent's rank in a Mafia-style arena came from opponents
      crashing out?
    practitioner: can I trust a top spot on a social deduction leaderboard as evidence my
      agent actually plays well?
  answered_by:
  - error-survival-confound
  - termination-depth
- ask:
    plain: how can you tell whether a game leaderboard is measuring skill or just measuring
      who avoids mistakes?
    jargon: which environment-level validity diagnostics flag when arena rankings are dominated
      by opponent error rather than strategic skill?
    task: what should I measure about my own agent arena to know its rankings are interpretable?
    practitioner: which of the social-reasoning game environments can I actually report rankings
      from?
  answered_by:
  - validity-diagnostic
  - error-survival-confound
- ask:
    plain: do skill ratings and total points agree when ranking game-playing language models?
    jargon: how far do TrueSkill ratings and cumulative reward diverge as ranking metrics
      for LLM agents in a multi-game arena?
    task: which metric should I rank my agents by after running a round-robin of games?
    practitioner: if I report TrueSkill instead of total reward for my agent, does the ordering
      change?
  answered_by:
  - trueskill-reward-divergence
- ask:
    plain: do language model players win more just because of which role they were dealt in
      Mafia or Codenames?
    jargon: is role assignment a confound in win rates for LLM social deduction, and does
      the same hold for cooperative word games?
    task: how should I report win rates for a social deduction agent so the role draw does
      not distort the number?
    practitioner: do I need to break my agent's scores out per role, or is an overall win
      rate fine?
  answered_by:
  - role-advantage
- ask:
    plain: does bolting memory and reasoning modules onto a language model agent actually
      make it play better?
    jargon: can cognitive scaffolding degrade an LLM agent's social deduction win rate without
      fine-tuning to use it?
    task: how do I get an 8B agent to actually use a memory and deduction module instead of
      being hurt by it?
    practitioner: should I add a memory and reflection layer to my small open-weight agent,
      or fine-tune it on game traces first?
  answered_by:
  - scaffolding-backfires
- ask:
    plain: for a language model playing strategy games, is training on past games better than
      clever prompting?
    jargon: how does the balance between training-time adaptation and inference-time scaffolding
      shift with parameter budget for LLM game agents?
    task: I have a 9B open-weight model and a frontier API model to enter in a game competition,
      which one do I fine-tune?
    practitioner: under a small parameter budget, should I fine-tune on trajectories or invest
      in prompting structure for my agent?
  answered_by:
  - training-vs-scaffolding
- ask:
    plain: can a tiny specialised network beat language models at a resource-allocation game?
    jargon: how well does a distilled graph attention policy perform against LLM opponents
      in Colonel Blotto compared with plain PPO?
    task: how do I use a language model to train a small game policy instead of deploying
      the language model as the player?
    practitioner: should I deploy an LLM as my Blotto player or distill it into a small policy
      network?
  answered_by:
  - non-llm-policy
- ask:
    plain: in Mafia, which side is harder for language models, the ones who know the secret
      or the ones who must deduce it?
    jargon: do architectural improvements to LLM agents raise Village-side win rates more
      than Mafia-side win rates in social deduction?
    task: which side should I measure to see whether my Mafia agent's deduction actually improved?
    practitioner: if I improve my agent's architecture, where should I expect the gain to
      show up in a hidden-role game?
  answered_by:
  - villager-asymmetry
- ask:
    plain: is there a repeatable way to score a new game-playing agent against last year's
      competitors without rerunning the competition?
    jargon: what offline protocol scores a new agent against a frozen pool of prior top-ranked,
      low-error submissions with role-conditioned and error-attribution reporting?
    task: how do I compare my new agent to a published cohort of agents on the same games
      without a live ladder?
    practitioner: can I benchmark my agent against the 2025 competition entrants after the
      competition has closed?
  answered_by:
  - mgref-protocol
- ask:
    plain: did language model agents get better at following game rules as a competition went
      on?
    jargon: how did game-level invalid-action rates change between the open ladder and the
      final evaluation stage of an LLM agent competition?
    task: how much of an agent's invalid-action rate can I expect to remove with iteration
      on prompting and parsing?
    practitioner: is rule-following in text game agents a solved problem yet, or should I
      budget engineering for it?
  answered_by:
  - error-improvement
- ask:
    plain: when a language model agent forfeits a social deduction game, does the game get
      far enough for strategy to matter?
    jargon: how does median termination depth in forfeited Secret Mafia games compare with
      expected game length?
    task: how do I check whether my agent's losses happened before any real strategic interaction
      took place?
    practitioner: should I discard forfeited games from my agent's evaluation, or do they
      still say something about play?
  answered_by:
  - termination-depth
misreadings:
- 'MindGames Secret Mafia leaderboard position is not a clean measure of social deduction
  ability: in the 2025 cycle it is better read as robustness to a failure-heavy interaction
  regime, because nearly every game contained an opponent error.'
- The 0% error rate for Iterated Prisoner's Dilemma does not show that LLM agents follow IPD
  rules perfectly; the environment silently replaces invalid actions with a default cooperate
  move, so violations cannot be recorded.
- The finding that memory and deduction layers reduced win rate does not mean scaffolding
  is useless — the same architecture reached 45.0% win rate after supervised fine-tuning taught
  the model to use it.
- MindGames results do not support claims that LLM agents possess general theory of mind;
  the paper states that high error rates and metric confounds preclude such claims and that
  strategic signals appear only locally and unevenly.
- 'Cross-division comparisons in the MindGames rankings are not like-for-like: the Efficient
  and Unlimited pools experienced different matchmaking dynamics, and the paper treats them
  as qualitative indicators.'
terminology:
  error-survival confound: A measurement failure in live multi-agent arenas where an agent's
    rating rises because opponents commit rule violations and forfeit, so leaderboard position
    reflects robustness to opponent failure rather than strategic ability.
  Caused / Witnessed: 'Per-model error-attribution counts over games: Caused is games in which
    the focal model committed at least one invalid action (fatal or non-fatal), Witnessed
    is games in which some opponent did; the categories are not mutually exclusive.'
  fatal versus non-fatal error: An invalid agent action that terminates the game or eliminates
    the player (fatal) versus one that is retried or silently auto-corrected while play continues
    (non-fatal).
  Efficient Agent division: A competition division restricting submitted agents to open-weight
    models under 9B parameters, contrasted with an Unlimited division that permits any size
    and closed-source models.
  role advantage: A model's win rate when assigned a particular game role minus that same
    model's average win rate across all roles it played, so positive values indicate the role
    helps relative to the model's own baseline.
  termination-depth diagnostic: The median number of turns before a game ends in failure,
    expressed as a fraction of the environment's expected game length, used to judge whether
    forfeits occur before meaningful strategic interaction.
links_extra:
  project page: https://www.mindgamesarena.com/
  dataset: https://huggingface.co/datasets/mindgameschallenge/MGC2025
  code: https://github.com/mind-games-challenge/mindgames-starter-kit
---
