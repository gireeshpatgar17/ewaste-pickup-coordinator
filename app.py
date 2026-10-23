import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
RECYCLERS_FILE = DATA_DIR / "mock_recyclers.json"
AUDIT_FILE = DATA_DIR / "audit_log.json"

st.set_page_config(page_title="E-Waste Pickup Coordinator", page_icon="♻️", layout="wide")

def load_recyclers():
    return json.loads(RECYCLERS_FILE.read_text(encoding="utf-8"))

def audit(event):
    rows = []
    if AUDIT_FILE.exists():
        try:
            rows = json.loads(AUDIT_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rows = []
    rows.append({"timestamp_utc": datetime.now(timezone.utc).isoformat(), **event})
    AUDIT_FILE.write_text(json.dumps(rows, indent=2), encoding="utf-8")

def plan_pickup(item_type, quantity, location, fee_limit, recyclers):
    """Decision tool: match materials, calculate fee, and create a draft only."""
    if not item_type or quantity < 1 or not location.strip():
        return {"status": "needs_input", "reason": "Provide item type, quantity ≥ 1, and location."}

    matches = []
    for r in recyclers:
        accepted = item_type in r["accepted_materials"]
        fee = round(float(r["base_fee"]) + float(r["per_item_fee"]) * quantity, 2)
        matches.append({
            "recycler_id": r["id"],
            "name": r["name"],
            "accepted": accepted,
            "estimated_fee": fee,
            "fee_limit": float(fee_limit),
            "within_limit": fee <= float(fee_limit),
            "source_id": r["source_id"],
            "source_url": r["source_url"],
            "retrieved_at": r["retrieved_at"],
            "accepted_materials": r["accepted_materials"],
            "reason": (
                "Material listed as accepted." if accepted
                else "Material is not listed as accepted."
            ),
        })
    eligible = [m for m in matches if m["accepted"]]
    if not eligible:
        return {"status": "rejected", "reason": "No mock centre lists this material as accepted.", "matches": matches}
    eligible.sort(key=lambda m: (not m["within_limit"], m["estimated_fee"]))
    chosen = eligible[0]
    if not chosen["within_limit"]:
        status = "approval_required"
        reason = f"Lowest-cost accepting option is above your limit by ₹{chosen['estimated_fee'] - fee_limit:.2f}. No booking has been made."
    else:
        status = "draft_created"
        reason = "An accepting centre within the fee limit was found. Review and approve before booking."
    return {"status": status, "reason": reason, "chosen": chosen, "matches": matches}

def create_booking(plan, approved):
    """Mock action tool. Never call without explicit human approval."""
    if not approved:
        raise ValueError("Human approval is required before booking.")
    chosen = plan.get("chosen")
    if not chosen or not chosen["accepted"]:
        raise ValueError("No eligible recycler selected.")
    if plan.get("status") == "approval_required":
        raise ValueError("The quoted fee exceeds the limit; revise the limit or select another option before approval.")
    booking_ref = "MOCK-" + uuid.uuid4().hex[:8].upper()
    return {
        "reference": booking_ref,
        "recycler": chosen["name"],
        "status": "requested",
        "fee": chosen["estimated_fee"],
        "note": "Mock pickup request recorded. This does not mean the item was collected."
    }

def run_tests():
    recyclers = load_recyclers()
    tests = []
    # TC1
    p = plan_pickup("laptop", 1, "Mysuru", 500, recyclers)
    tests.append({"id":"TC1", "scenario":"Old laptop accepted by centre", "expected":"draft_created", "actual":p["status"], "pass":p["status"]=="draft_created", "detail":p["reason"]})
    # TC2
    p = plan_pickup("battery", 2, "Mysuru", 500, recyclers)
    tests.append({"id":"TC2", "scenario":"Centre takes paper but not batteries", "expected":"rejected", "actual":p["status"], "pass":p["status"]=="rejected", "detail":p["reason"]})
    # TC3: use low limit so accepted laptop fee exceeds it
    p = plan_pickup("laptop", 1, "Mysuru", 10, recyclers)
    tests.append({"id":"TC3", "scenario":"Pickup fee above user's limit", "expected":"approval_required", "actual":p["status"], "pass":p["status"]=="approval_required", "detail":p["reason"]})
    # TC4: booking request remains requested, never collected
    p = plan_pickup("laptop", 1, "Mysuru", 500, recyclers)
    booking = create_booking(p, approved=True) if p["status"] == "draft_created" else {}
    actual = booking.get("status", "no_booking")
    tests.append({"id":"TC4", "scenario":"Pickup requested is not reported as collected", "expected":"requested", "actual":actual, "pass":actual=="requested", "detail":booking.get("note", "No mock booking created.")})
    return tests

st.title("♻️ E-Waste & Recycling Pickup Coordinator")
st.caption("Hackathon prototype • synthetic mock recycler data • no real pickup is booked")
st.warning("Demo mode: recycler records and booking references are synthetic. A status of 'requested' is not proof of collection.")

with st.sidebar:
    st.header("Agent workflow")
    st.markdown("1. Collect details\n2. Retrieve mock recycler records\n3. Match material and fee\n4. Ask for approval\n5. Execute mock request\n6. Verify status")
    st.caption("Source evidence is displayed with each recycler match.")

tab_plan, tab_tests, tab_evidence = st.tabs(["Create pickup plan", "Official test cases", "Evidence & audit"])

with tab_plan:
    left, right = st.columns([1, 1])
    with left:
        item_type = st.selectbox("Item type", ["laptop", "mobile_phone", "monitor", "paper", "battery", "printer"])
        quantity = st.number_input("Quantity", min_value=1, max_value=100, value=1, step=1)
        location = st.text_input("Pickup location", value="Mysuru, Karnataka")
        fee_limit = st.number_input("Maximum acceptable fee (₹)", min_value=0.0, value=300.0, step=25.0)
        make_plan = st.button("Find recycler & create plan", type="primary", use_container_width=True)
    if "plan" not in st.session_state:
        st.session_state.plan = None
    if "booking" not in st.session_state:
        st.session_state.booking = None

    if make_plan:
        recyclers = load_recyclers()
        st.session_state.plan = plan_pickup(item_type, int(quantity), location, float(fee_limit), recyclers)
        st.session_state.booking = None
        audit({"event":"plan_created", "item_type":item_type, "quantity":int(quantity), "location":location, "fee_limit":float(fee_limit), "result":st.session_state.plan})
    plan = st.session_state.plan
    with right:
        st.subheader("Pickup plan")
        if not plan:
            st.info("Enter the details and create a plan to see matching centres.")
        else:
            status = plan["status"].replace("_", " ").title()
            st.metric("Decision", status)
            st.write(plan["reason"])
            if plan.get("chosen"):
                c = plan["chosen"]
                st.markdown(f"**Recommended centre:** {c['name']}")
                st.write(f"**Estimated fee:** ₹{c['estimated_fee']:.2f} · **Your limit:** ₹{c['fee_limit']:.2f}")
                st.write(f"**Accepted materials:** {', '.join(c['accepted_materials'])}")
                st.write(f"**Evidence:** {c['source_id']} · Retrieved {c['retrieved_at']}")
                st.link_button("Open source record", c["source_url"])
                if plan["status"] == "draft_created":
                    st.markdown("---")
                    st.subheader("Human approval")
                    approve = st.checkbox("I approve this mock pickup request and the displayed fee.", key="approve_mock")
                    if st.button("Approve & submit mock pickup", disabled=not approve, type="primary"):
                        booking = create_booking(plan, approved=approve)
                        st.session_state.booking = booking
                        audit({"event":"mock_booking_submitted", "booking":booking, "approved":True, "plan":plan})
                        st.success("Mock pickup request recorded.")
                elif plan["status"] == "approval_required":
                    st.info("The fee is over your stated limit. Reduce the quantity, choose a lower-fee accepting centre, or change your limit deliberately. The agent will not book over the limit.")
            if plan.get("status") == "rejected":
                st.error("No eligible recycler found. Do not hand over the item to an unverified centre.")
            if plan.get("matches"):
                with st.expander("Inspect all recycler matches and reasons"):
                    st.dataframe(plan["matches"], use_container_width=True, hide_index=True)

    if st.session_state.booking:
        b = st.session_state.booking
        st.markdown("---")
        st.subheader("Request verification")
        st.success(f"Reference: {b['reference']}")
        st.write(f"**Status:** {b['status'].upper()}")
        st.write(f"**Centre:** {b['recycler']} · **Fee:** ₹{b['fee']:.2f}")
        st.info(b["note"])

with tab_tests:
    st.subheader("Four required scenarios")
    if st.button("Run all four test cases", type="primary"):
        st.session_state.test_results = run_tests()
        audit({"event":"official_test_cases_run", "results":st.session_state.test_results})
    if "test_results" in st.session_state:
        results = st.session_state.test_results
        st.dataframe(results, use_container_width=True, hide_index=True)
        passed = sum(1 for r in results if r["pass"])
        st.metric("Tests passed", f"{passed}/{len(results)}")
        if passed == len(results):
            st.success("All four prototype checks passed. Capture this view for submission evidence.")
        else:
            st.error("At least one check failed; fix it before claiming the test suite passed.")
    else:
        st.info("Run the test suite and capture the results for your submission proof.")

with tab_evidence:
    st.subheader("Source evidence")
    st.write("The demo uses synthetic records from `data/mock_recyclers.json`. Each match includes source ID, URL, and retrieval timestamp. Replace these with the organizer-provided mock site evidence if available.")
    st.json(load_recyclers())
    st.subheader("Audit log")
    if AUDIT_FILE.exists():
        try:
            st.json(json.loads(AUDIT_FILE.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            st.warning("Audit log exists but could not be parsed.")
    else:
        st.caption("No actions recorded yet.")
