# Discovery Module

Use this module to find concerns that the source artifact never mentioned. Its output is an Exploration Map of candidate facts, decisions, unknowns, and possible findings—not a verdict.

## 1. Establish anchors

Extract before expanding:

- user or system goal;
- actors and affected stakeholders;
- core objects and identities;
- entry and exit points;
- declared success and failure outcomes;
- system boundary and external dependencies;
- irreversible or safety-sensitive operations.

Mark absent anchors as candidates instead of inventing them.

## 2. Scan the problem spaces

Scan each relevant space and record both covered and missing branches.

| Space | Look for |
| --- | --- |
| Scenario | happy, alternative, failure, recovery, interruption, repeated operation, alternate entry, cross-device/account/platform/version |
| State | initial, intermediate, terminal, failed, retrying, expired; legal, illegal, missing, and unreachable transitions |
| Rule | condition, outcome, else behavior, precedence, conflict, default, timeout, retry, idempotency, termination |
| Data | identity, ownership, source of truth, lifecycle, consistency, duplication, deletion, migration, versioning, stale data |
| Dependency | OS, framework, backend, account, permission, network, database, external app, OEM, SDK, flag, configuration |
| Failure | timeout, partial failure, process death, reboot, duplicate or reordered execution, dependency loss, auth expiry, storage pressure |
| Environment | version, device form, locale, region, network, foreground/background, battery restriction, install and login state |
| Quality | security, privacy, performance, accessibility, observability, recoverability, compatibility, maintainability, verifiability |

Do not mechanically expand every Cartesian product. Expand a combination when at least one applies:

- it changes externally visible behavior;
- it crosses a trust, persistence, process, device, account, or ownership boundary;
- it can cause irreversible loss, corruption, disclosure, or long-lived inconsistency;
- historical failures or platform variability make it plausible;
- the design relies on an unstated guarantee;
- recovery differs from the happy path.

## 3. Generate missing branches

Use these transformations against each important flow or claim:

1. Interrupt it at every side effect.
2. Repeat it before and after completion.
3. Reverse the order of concurrent or remote events.
4. Remove or degrade each dependency.
5. Change identity, ownership, version, or environment mid-flow.
6. Resume after process death, reboot, timeout, or stale state.
7. Apply the operation from a second device, account, or entry point.
8. Ask what cleans up partial state and how success is observed.

Prefer concrete counter-scenarios such as “local delete completes, cloud propagation fails, later sync restores the item” over labels such as “network edge case.”

## 4. Separate completeness classes

Classify discovered branches:

- `REQUIRED`: omission plausibly causes incorrect, unsafe, inconsistent, unrecoverable, or unverifiable behavior in declared scope.
- `CONDITIONAL`: required only if a stated capability, environment, or dependency is in scope.
- `OPTIONAL`: product expansion or optimization that may be deferred without violating current behavior.
- `NOT_APPLICABLE`: excluded by evidence or an explicit scope decision.

Do not call a branch optional merely because the document omitted it.

## 5. Record the Exploration Map

For every material branch record:

```yaml
branch: "Offline deletion followed by later synchronization"
space: SCENARIO
class: REQUIRED
source_anchor: "Delete propagation flow"
coverage: EXPLICIT | IMPLICIT | MISSING | CONTRADICTED
why_relevant: "Can resurrect user-deleted content"
candidate_type: FACT | DECISION | UNKNOWN | FINDING
evidence_to_seek: "Deletion tombstone contract and sync behavior"
```

Convert a branch to a finding only after checking applicable scope and evidence. Convert it to a decision-tree node when an unresolved choice or fact gates downstream behavior.

## 6. Discovery completion check

Discovery is adequate when:

- every important actor, object, side effect, boundary, and dependency has been used as an expansion anchor;
- all high-risk flows have failure and recovery branches;
- core objects have lifecycle and state-transition coverage;
- cross-boundary data has identity, ownership, consistency, and deletion semantics;
- exclusions and deferred optional branches are explicit;
- remaining blind spots are recorded.

Discovery completeness is risk-bounded, never absolute. Report the bound and do not claim the entire theoretical space was exhausted.

