# Agent Architecture

```mermaid
flowchart TD
    U[User: item, quantity, location, fee limit] --> UI[Streamlit UI]
    UI --> RET[Recycler record retrieval tool]
    RET --> DB[(Mock recycler source records)]
    DB --> DEC[Decision engine: accepted material + fee]
    DEC -->|No accepting centre| REJ[Reject with reason]
    DEC -->|Fee over limit| HOLD[Approval required / no booking]
    DEC -->|Accepting centre within limit| DRAFT[Pickup draft]
    DRAFT --> HUMAN{Explicit human approval?}
    HUMAN -->|No| STOP[Stop; no action]
    HUMAN -->|Yes| ACT[Mock booking action]
    ACT --> VERIFY[Verify returned status/reference]
    VERIFY --> OUT[Status: requested, not collected]
    RET --> AUDIT[(Audit log)]
    DEC --> AUDIT
    ACT --> AUDIT
    VERIFY --> AUDIT
```

## Tools and boundaries
- **Retrieval tool:** loads recycler records and displays source IDs, URLs and retrieval timestamps.
- **Decision tool:** checks material acceptance and computes `base_fee + per_item_fee × quantity`.
- **Approval gate:** explicit user approval is required before mock booking.
- **Action tool:** creates a mock reference, not an external booking.
- **Verification:** checks the action result separately; `requested` is not equivalent to `collected`.
- **Audit log:** records inputs, plan and action outcomes for review.

## Current limitations
This starter prototype uses deterministic matching and synthetic data; it does not yet retrieve the organizer's live/mock website or call an LLM. For the hackathon submission, be transparent about this. If time permits, connect the supplied mock recycler site as the retrieval source and show its evidence in the UI.
