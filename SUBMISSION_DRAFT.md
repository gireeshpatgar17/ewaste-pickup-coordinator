# Submission form draft

**Project name:** E-Waste Pickup Coordinator

**Tools used:** Python, Streamlit, JSON-based mock data, pytest, GitHub; update this list to reflect the tools actually used.

**Solution & agent workflow:**
The E-Waste & Recycling Pickup Coordinator collects the item type, quantity, pickup location, and maximum acceptable fee. It retrieves recycler records, checks whether the material is accepted, calculates the estimated fee, and explains its recommendation using source IDs and timestamps. If the material is unsupported, it rejects the request. If the fee exceeds the user's limit, it asks for a decision and does not book. For eligible plans, it requires explicit human approval before executing a mock pickup request. It then verifies the returned reference and status, which remains “requested” rather than “collected.” The prototype records audit evidence and includes automated checks for all four official scenarios.

**Agent architecture:** Streamlit UI → recycler retrieval tool → material/fee decision engine → approval gate → mock booking action → independent status verification → audit log.

**Test cases / proof:** Attach screenshots of TC1–TC4 results, the approval gate, the generated mock reference, and the status verification. Clearly label synthetic data and mock actions. Replace placeholders with actual organizer mock-site evidence if provided.

**Demo video outline (2–3 minutes):**
1. 0:00–0:20 — Problem and goal.
2. 0:20–0:55 — Laptop accepted; show source evidence and draft.
3. 0:55–1:20 — Battery rejected.
4. 1:20–1:45 — Fee above limit; show no booking.
5. 1:45–2:10 — Approve a valid mock pickup; show reference and “requested” status.
6. 2:10–2:30 — Run test suite and explain limitations.
