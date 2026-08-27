# Gap Discovery Perspectives

This reference defines bounded exploration perspectives for `gap-discovery`.

These perspectives are an engineering search taxonomy, not a claim that one
industry standard mandates exactly these categories.

Use only perspectives that are structurally relevant to the current feature.

---

## 1. Scenario perspective

Purpose: discover missing behavior branches implied by an existing user goal or
scenario.

Derive from:

```text
actor + precondition + action + expected outcome
```

Useful operations:

- negate a material prerequisite
- repeat an action that is not obviously one-shot
- substitute a materially different valid actor or account state
- interrupt or cancel a multi-step scenario
- follow a branch already implied by a rule, state, or dependency

Keep only branches that can materially change observable behavior.

Example:

```text
Requirement: user can restore a note to its original folder
Known relation: note -> original folder
Derived branch: original folder no longer exists
Question: where must the restored note go?
```

---

## 2. State perspective

Purpose: discover incomplete state semantics.

For each state-changing operation model:

```text
source_state --event/guard--> target_state
```

Check whether the requirement defines, when relevant:

- valid source states
- valid target state
- transition guard
- invalid transition behavior
- intermediate state for non-atomic operations
- re-entry/retry semantics
- terminal or recovery state

Strong derivation pattern:

```text
non-atomic state transition
+
interruptible execution
->
missing intermediate/recovery-state question
```

---

## 3. Failure / recovery perspective

Purpose: discover missing failure semantics only where failure can alter an
externally meaningful outcome.

Derive from actual operations and dependencies, not a universal fault list.

Relevant triggers include:

- remote call with timeout/unknown outcome
- multi-step mutation where partial success can persist
- retryable operation without idempotency semantics
- local/remote commit boundary
- process/device interruption during durable mutation

Questions should focus on:

- externally valid state after failure
- rollback vs partial commit
- retry/re-entry behavior
- reconciliation/recovery
- authoritative success criterion

---

## 4. Boundary perspective

Purpose: discover requirement gaps at meaningful domain or system limits.

Apply only when the model contains a real boundary variable, such as:

- numeric range
- cardinality/count
- payload/file size
- time/age/expiry
- quota/capacity
- pagination/window
- lifecycle deadline
- version range

Do not enumerate arbitrary min/max values without a product or technical basis.

Derive questions by asking whether expected behavior changes at, below, or
above a meaningful threshold.

---

## 5. Rule / constraint perspective

Purpose: discover missing precedence, scope, or exception semantics.

Represent a rule minimally as:

```text
scope + condition -> required/prohibited outcome
```

Compare rules with overlapping scope.

Look for:

- same condition with different outcomes
- broad rule plus exception with undefined precedence
- multiple rules that can apply simultaneously
- rule conflicting with a state invariant
- undefined scope or actor applicability

Strong candidates cite both conflicting/overlapping rules.

---

## 6. Dependency perspective

Purpose: discover where the feature relies on an external contract whose
semantics are incomplete or not projected into product behavior.

For each dependency search for:

- success semantics
- error semantics
- ordering
- idempotency
- timeout behavior
- consistency guarantees
- version compatibility
- authentication/authorization expectations

Search for the contract before creating a gap.

Then project real contract uncertainty into externally meaningful behavior.

---

## 7. Non-functional perspective

Purpose: identify omitted quality requirements only when the feature structure
creates a credible NFR concern.

Relevant dimensions may include:

- performance / latency
- reliability / availability
- security / privacy
- compatibility
- resource use
- recoverability
- observability / operability

Do not ask every NFR for every feature.

Use triggers such as:

```text
large data path -> performance/capacity concern
sensitive data -> privacy/security concern
critical remote dependency -> reliability/recovery concern
cross-version protocol -> compatibility concern
```

---

## 8. Assumption perspective

Purpose: expose hidden premises that implementation would otherwise silently
choose.

Look for statements or model structures that only work if an unstated premise
is true.

Examples:

- original resource always exists
- operation executes exactly once
- only one actor can mutate the object
- clocks are synchronized
- remote state is immediately consistent
- permissions do not change mid-operation

A good assumption candidate has this shape:

```text
observed requirement/model behavior
+
required unstated premise
+
consequence if premise is false
```

Do not treat a common engineering possibility as an assumption unless the
current feature actually depends on it.

---

## 9. Cross-artifact coverage perspective

Purpose: discover structural gaps across already-existing engineering artifacts.

Examples:

```text
Goal -> Requirement -> Acceptance Criterion -> Test
Requirement -> Decision / Rule
Requirement -> Interface Contract
Requirement -> Risk / Constraint
```

Look for missing or contradictory relations such as:

- core requirement with no acceptance oracle
- acceptance scenario with no source requirement
- requirement relying on a dependency whose contract is absent
- requirement changed while linked test/decision still encodes old behavior

This perspective is often higher precision than open-ended model expansion
because it searches for concrete relation gaps.

---

# Cross-perspective interactions

High-value gaps often appear at the intersection of two model dimensions.

Prioritize combinations such as:

```text
scenario x state
scenario x dependency
state x failure
state x concurrency
rule x rule
rule x state
operation x data relationship
operation x invariant
acceptance x observable outcome
```

A candidate is stronger when both sides of the interaction are evidence-backed.

---

# Selection rule

Before applying a perspective ask:

1. Is there a concrete model element that makes this perspective relevant?
2. Could different answers materially change downstream behavior or acceptance?
3. Is the answer not already authoritative and explicit?

If the answer to (1) or (2) is no, skip the perspective.

This keeps the search bounded and reduces false-positive burden.
