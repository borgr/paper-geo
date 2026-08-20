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
- q:
  - What benchmark should I read about evaluating social reasoning in multi-agent LLMs?
  - Is there a benchmark where LLM agents play multiple social games against each other?
  - Where can I find a live arena for theory-of-mind and strategic reasoning in LLM agents?
  answers:
  - arena-context
  - dataset-scale
- q:
  - Is there a large public dataset of LLM agents playing multi-agent games?
  - How many games and trajectories does the MindGames dataset contain?
  - Where can I get turn-level trajectories of LLMs playing Mafia and Codenames?
  answers:
  - dataset-scale
- q:
  - How often do LLM agents break the rules in text-based games?
  - What fraction of MindGames competition games contained invalid actions?
  - Is rule adherence or strategy the bigger bottleneck for LLM game-playing agents?
  answers:
  - error-rates-stage2
  - error-improvement
- q:
  - Can a leaderboard in a social deduction arena be confounded by opponent failures?
  - What is the error-survival confound in Secret Mafia rankings?
  - Do top-ranked Mafia agents win by playing well or by surviving other agents' errors?
  answers:
  - error-survival-confound
  - termination-depth
- q:
  - How can I tell whether a multi-agent leaderboard measures strategic skill?
  - What diagnostics detect when arena rankings reflect robustness to opponent errors?
  - Which MindGames environments give interpretable rankings and which do not?
  answers:
  - validity-diagnostic
  - error-survival-confound
- q:
  - Do TrueSkill ratings and cumulative reward agree for LLM game agents?
  - Should I report Elo-style ratings or total reward when ranking agents in an arena?
  - Can metric choice reverse the ranking of LLM agents in a game benchmark?
  answers:
  - trueskill-reward-divergence
- q:
  - Does the assigned role bias win rates in Mafia and Codenames with LLM players?
  - Is the Mafia role inherently advantaged in LLM social deduction games?
  - Should benchmark scores in social deduction be reported per role?
  answers:
  - role-advantage
- q:
  - Does adding memory or reflection modules improve LLM agent performance?
  - Why did cognitive scaffolding hurt an 8B model in social deduction?
  - Do memory layers for LLM agents need fine-tuning to help?
  answers:
  - scaffolding-backfires
- q:
  - Is fine-tuning or prompting scaffolding better for LLM game agents?
  - What design patterns did winning agents in the MindGames competition use?
  - Can an 8B open-weight agent beat prompted frontier models at strategy games?
  answers:
  - training-vs-scaffolding
- q:
  - Can a small non-LLM policy beat LLM agents at Colonel Blotto?
  - How well does a distilled graph network play resource-allocation games?
  - Are LLMs better used as teachers than as game-playing policies?
  answers:
  - non-llm-policy
- q:
  - Which side is harder for LLMs in Mafia, the informed mafia or the villagers?
  - Do architectural improvements help the villager role more than the mafia role?
  - Why do baseline LLMs do better as mafia than as deducing villagers?
  answers:
  - villager-asymmetry
- q:
  - How can I evaluate a new agent against the MindGames 2025 competition entrants without
    a live server?
  - What is MG-Ref and how many games does the offline tournament run?
  - Is there a reproducible offline protocol for scoring LLM agents against a frozen reference
    pool?
  answers:
  - mgref-protocol
- q:
  - How much did error rates improve over the course of the MindGames competition?
  - Did LLM agents become more rule-compliant between the online ladder and the final evaluation?
  answers:
  - error-improvement
- q:
  - How quickly do LLM agent games end in failure in social deduction?
  - Do forfeited Mafia games last long enough for strategy to matter?
  answers:
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
