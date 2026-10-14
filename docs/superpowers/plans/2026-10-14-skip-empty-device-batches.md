# Skip Empty GLP Device Batches Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Avoid empty GLP device POSTs and their rate-limit sleeps when adding more than five devices.

**Architecture:** Keep the change inside `Devices.add_devices`: pass the connection required by the existing helper, preserve category order, and dispatch only categories with devices. Add standard-library `unittest` coverage for a single populated category and mixed populated categories.

**Tech Stack:** Python 3.10+, `unittest`, `unittest.mock`.

## Global Constraints

- Pass `conn` to `__add_dev` to match its existing signature.
- Preserve the current behavior for every non-empty category.
- Preserve the existing per-request chunking, request ordering, and rate-limit behavior.
- Leave the `count <= INPUT_SIZE` request path unchanged.
- Do not add runtime dependencies.

---

### Task 1: Skip empty category requests

**Files:**
- Modify: `pycentral/glp/devices.py:153-156`
- Create: `tests/test_glp_devices.py`

**Interfaces:**
- Consumes: `Devices.add_devices(conn, network, compute, storage)` and its existing `__add_dev(conn, type, inputs)` helper.
- Produces: For `count > INPUT_SIZE`, calls to `__add_dev(conn, type, inputs)` for non-empty categories only, in network/compute/storage order; one result entry for each dispatched category.

- [x] **Step 1: Add failing tests for omitted empty categories**

```python
import unittest
from copy import deepcopy
from unittest.mock import Mock, patch

from pycentral.glp.devices import Devices


class AddDevicesTests(unittest.TestCase):
    def test_large_single_category_skips_empty_categories(self):
        conn = Mock()
        payloads = []

        def record_command(*args, **kwargs):
            payloads.append(deepcopy(kwargs["api_data"]))
            return {"code": 202, "msg": {}}

        conn.command.side_effect = record_command

        with patch("pycentral.glp.devices.time.sleep") as sleep:
            result = Devices().add_devices(
                conn,
                network=[{"serialNumber": str(i)} for i in range(6)],
            )

        self.assertEqual(len(payloads), 2)
        self.assertEqual(
            [len(payload["network"]) for payload in payloads], [5, 1]
        )
        self.assertTrue(all(not payload["compute"] for payload in payloads))
        self.assertTrue(all(not payload["storage"] for payload in payloads))
        self.assertEqual(len(result), 1)
        self.assertNotIn(15, [call.args[0] for call in sleep.call_args_list])

    def test_mixed_categories_keep_order_and_skip_empty_category(self):
        conn = Mock()
        payloads = []

        def record_command(*args, **kwargs):
            payloads.append(deepcopy(kwargs["api_data"]))
            return {"code": 202, "msg": {}}

        conn.command.side_effect = record_command

        with patch("pycentral.glp.devices.time.sleep") as sleep:
            Devices().add_devices(
                conn,
                network=[{"serialNumber": "n1"}] * 3,
                compute=[{"serialNumber": "c1"}] * 3,
            )

        self.assertEqual(len(payloads), 2)
        self.assertTrue(payloads[0]["network"])
        self.assertFalse(payloads[0]["compute"])
        self.assertTrue(payloads[1]["compute"])
        self.assertFalse(payloads[1]["network"])
        self.assertTrue(all(not payload["storage"] for payload in payloads))
        self.assertEqual(
            [call.args[0] for call in sleep.call_args_list], [15, 15]
        )


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run the tests and verify the current implementation fails**

Run: `python3 -m unittest discover -s tests -p 'test_glp_devices.py' -v`
Expected: both tests fail with `TypeError` because `add_devices` omits the required `conn` argument when calling `__add_dev`.

- [x] **Step 3: Dispatch only non-empty categories**

Replace the three unconditional helper calls in the `count > INPUT_SIZE` branch with:

```python
            for device_type, device_list in (
                ("network", network),
                ("compute", compute),
                ("storage", storage),
            ):
                if device_list:
                    resp_list.append(
                        self.__add_dev(conn, device_type, device_list)
                    )
```

- [x] **Step 4: Run the focused tests and verify the behavior**

Run: `python3 -m unittest discover -s tests -p 'test_glp_devices.py' -v`
Expected: both tests pass; only non-empty categories produce API calls, in the original order.

- [x] **Step 5: Run repository checks**

Run: `python3 -m compileall -q pycentral tests`
Expected: exit status 0.
