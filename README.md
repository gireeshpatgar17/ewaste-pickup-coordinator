# E-Waste & Recycling Pickup Coordinator

A Streamlit hackathon prototype for finding a mock recycler, checking material acceptance and fees, preparing a pickup plan, requesting explicit human approval, and verifying the mock request status.

## Important demo limitations
- `data/mock_recyclers.json` contains synthetic sample records, not verified real recyclers.
- The `example.com` URLs are placeholders and must be replaced with the official mock recycler site/source URLs if the organizer supplied them.
- Booking references are generated locally and are mock references, not real service bookings.
- The system never reports an item as collected. The mock action ends at `requested`.
- Do not present synthetic source records as live retrieval evidence.

## Run locally (Windows PowerShell)
```powershell
cd ewaste_pickup_coordinator
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run automated tests
```powershell
pytest -q
```

## Four required scenarios
- TC1: accepted laptop → pickup draft.
- TC2: battery not accepted by any listed centre → rejected.
- TC3: fee exceeds the user's limit → approval_required, no booking.
- TC4: after explicit approval, mock request status is `requested`, never `collected`.

## Architecture
1. Streamlit UI collects item type, quantity, location, and fee limit.
2. Recycler retrieval tool reads source records from `data/mock_recyclers.json`.
3. Matching/decision tool checks accepted materials and calculates fee.
4. Approval gate blocks booking until the user explicitly checks the approval box.
5. Mock booking tool creates a reference only after approval.
6. Verification reports the observed status as `requested`.
7. JSON audit log stores plan and action events.

See `ARCHITECTURE.md` for the workflow diagram.

## Deployment URL:
https://ewaste-pickup-coordinator-by-gireeshpatgar.streamlit.app/
