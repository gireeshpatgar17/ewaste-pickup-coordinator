import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import plan_pickup, create_booking

RECYCLERS = json.loads((Path(__file__).resolve().parents[1] / "data/mock_recyclers.json").read_text())

def test_tc1_laptop_draft():
    result = plan_pickup("laptop", 1, "Mysuru", 500, RECYCLERS)
    assert result["status"] == "draft_created"

def test_tc2_battery_rejected():
    result = plan_pickup("battery", 1, "Mysuru", 500, RECYCLERS)
    assert result["status"] == "rejected"

def test_tc3_fee_over_limit():
    result = plan_pickup("laptop", 1, "Mysuru", 10, RECYCLERS)
    assert result["status"] == "approval_required"

def test_tc4_booking_not_collected():
    plan = plan_pickup("laptop", 1, "Mysuru", 500, RECYCLERS)
    booking = create_booking(plan, approved=True)
    assert booking["status"] == "requested"
    assert "not mean the item was collected" in booking["note"]

def test_no_booking_without_approval():
    plan = plan_pickup("laptop", 1, "Mysuru", 500, RECYCLERS)
    try:
        create_booking(plan, approved=False)
    except ValueError:
        return
    assert False, "Expected approval guard to reject booking"
