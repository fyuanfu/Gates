# Example — Upload Requirement Gap Discovery

This example shows the difference between generic edge-case brainstorming and
bounded, evidence-backed gap discovery.

## Input requirement

```text
REQ-12: When the user uploads a photo, the system uploads the file to cloud
storage and shows the photo in the user's gallery after upload succeeds.
```

Available project evidence:

```text
api/upload-contract.md:
- upload may return success
- upload may fail with a definite error
- upload may time out
- after timeout, the server may or may not have committed the object
- the contract does not provide exactly-once semantics
```

## Bad exploration

```text
Possible missing cases:
- network failure
- low battery
- airplane mode
- phone rotation
- process death
- server crash
- user logs out
- user switches language
- storage full
...
```

Why this is bad:

- most candidates are not derived from the requirement structure
- relevance is unknown
- reviewer load becomes unbounded
- it mixes product gaps with arbitrary engineering possibilities

## Bounded exploration

Selected perspective: `failure / recovery`

Concrete trigger:

```text
REQ-12 requires a remote upload followed by local visible completion.
The remote contract explicitly allows timeout with unknown remote commit state.
```

Derived candidate:

```text
If the client times out, the remote object may already exist while the client
has not observed success.
```

Search result:

```text
Current requirements: no post-timeout state defined
Acceptance criteria: no timeout behavior defined
Upload contract: unknown outcome is possible
Existing tests: only definite success and definite error are covered
```

## Reported candidate gap

```yaml
id: GAP-001
perspective: failure
status: open_question
materiality: HIGH
confidence: HIGH
requirement_refs:
  - REQ-12
trigger: >-
  Upload completion depends on a remote operation whose contract allows timeout
  with unknown commit outcome.
question: >-
  What user-visible state is required after timeout when the server may already
  have accepted the photo?
evidence_searched:
  - spec.md#REQ-12
  - acceptance.md#upload
  - api/upload-contract.md#timeouts
  - tests/upload/*
evidence_gap: >-
  No authoritative requirement defines post-timeout state, reconciliation, or
  retry behavior.
why_it_matters: >-
  Different answers can produce duplicate uploads, false failure UI, indefinite
  pending state, or inconsistent local/cloud state.
suggested_owner: product/domain owner
recommended_action: >-
  Define the post-timeout user-visible state and whether retry, reconciliation,
  or duplicate suppression is required.
```

## Why this candidate survives filtering

1. **Derivation:** it comes from a real remote-operation contract property.
2. **Evidence search:** requirement, acceptance, contract, and tests were checked.
3. **Materiality:** different answers affect visible state and data correctness.
4. **Unresolvedness:** no authoritative answer exists.
5. **Actionability:** the product/domain owner can define the expected behavior.

## What the skill must not do

It must not silently decide:

```text
"The correct answer is to retry three times and then show failed."
```

That would invent product behavior.

The correct output remains an `open_question` until an authorized source or
owner provides the decision.
