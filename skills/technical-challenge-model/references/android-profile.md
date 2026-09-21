# Android challenge profile

Load this profile only when the reviewed design actually contains the relevant Android mechanism. It is a routing aid, not a checklist.

| Mechanism | Candidate challenge lenses |
|---|---|
| WorkManager | retry, duplicate enqueue, constraints, process death, persistence, idempotency |
| Room / SQLite | transaction boundary, crash consistency, migration, schema compatibility, concurrent writers |
| Coroutine / Flow | cancellation, collector lifecycle, ordering, duplicate collection, shared-state concurrency |
| Connectivity callbacks | duplicate events, reorder, flapping, stale network state |
| Binder / remote service | remote death, reconnect, retry ambiguity, partial operation |
| background execution | OS restrictions, process death, Doze/App Standby, scheduling guarantees |
| persisted app state | upgrade/downgrade compatibility, stale state, account/identity binding |
| permission/storage dependency | revocation, unavailable storage, partial write, recovery |

Important boundaries:

- A platform behavior claim needs authoritative Android/platform evidence; do not infer guarantees from API naming.
- OEM differences are a challenge seed only when the design depends on behavior known to vary or the project carries an explicit compatibility constraint.
- Process death, lifecycle recreation, callback duplication, and retry are technical failure modes. The PRD should define the user-visible invariant; this profile challenges whether the mechanism preserves it.
