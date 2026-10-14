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
