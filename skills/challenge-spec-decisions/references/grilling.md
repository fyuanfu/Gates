# Grilling Module

Use this module to turn the Exploration Map into a dependency-ordered conversation that converges. The center is the unresolved decision tree, not a questionnaire.

## 1. Classify before asking

- `FACT`: one answer is discoverable from evidence. Search first.
- `DECISION`: multiple defensible options exist and an accountable owner must choose.
- `UNKNOWN`: information is currently insufficient; identify the evidence or authority needed, then reclassify.

Do not ask a human to recall a fact available in code, configuration, contracts, tests, logs, or source documents. Do not let the agent decide product semantics or high-impact trade-offs merely because a default seems reasonable.

## 2. Build dependencies

Create a directed edge `A -> B` when B cannot be answered or evaluated until A is resolved. Common prerequisite order:

```text
scope and semantics
→ identity and ownership
→ lifecycle and state
→ conflict and failure policy
→ architecture and mechanism
→ verification and rollout
```

Split compound nodes that contain independent choices. Merge duplicate nodes that would be answered by the same decision and evidence. Mark cycles; a cycle usually indicates entangled concepts or a missing higher-level policy.

## 3. Resolve facts autonomously

For each open fact:

1. name the exact proposition;
2. identify the strongest available source;
3. search for supporting and conflicting evidence;
4. record source, scope, freshness, and confidence;
5. resolve only within the evidence boundary.

If evidence conflicts, create a finding or an owner decision instead of choosing the convenient source.

## 4. Select the frontier

A frontier node has no unresolved prerequisite. Rank frontier nodes by:

```text
priority = unblock_value + consequence + irreversibility + uncertainty + cross_cutting_effect - retrieval_cost
```

Use qualitative scoring; do not fabricate precision. Prefer a node that unlocks many branches, can materially change the solution, or protects data/safety. Defer cosmetic and low-value implementation details.

## 5. Ask one decision question

Use this structure:

```markdown
**Question**
What must the owner decide?

**Why now**
Which downstream branches depend on it and what risk remains?

**Options**
- A — behavior and trade-off
- B — behavior and trade-off
- C — behavior and trade-off, when genuinely distinct

You may specify another policy.
```

Options must be mutually distinct at the decision level. Do not disguise a preferred answer as the only safe option. If the user cannot answer, capture the owner, evidence needed, and blocking consequence.

## 6. Process the answer

After every material response:

1. normalize the decision in testable language;
2. separate selected policy from supporting factual claims;
3. extract conditions, assumptions, exceptions, and implied branches;
4. check against existing evidence and prior decisions;
5. invoke Socratic challenge at the appropriate risk level;
6. update affected nodes and dependencies;
7. recompute the frontier.

Possible tree changes include resolve, split, merge, invalidate, reclassify, expose contradiction, and add branch. Never continue using the old order without recalculation.

## 7. Convergence and ownership

A node is resolved only when its answer is unambiguous enough to constrain downstream work and its critical claims are supported or explicitly accepted as risk.

Stop interactive grilling when no blocking frontier can be answered by the current participant. Then report rather than looping. Every unresolved material node must have:

- the missing decision or evidence;
- an accountable owner or owner role;
- affected downstream nodes;
- consequence of delay;
- blocking status;
- closure condition.

Conversation completeness does not prove problem-space completeness. Return to Discovery whenever an answer reveals a new actor, state, side effect, dependency, or failure mode.

