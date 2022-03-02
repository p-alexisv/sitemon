from app import *
import unittest
import os

class TestApp(unittest.TestCase):
    def test_getstat(self):
        self.assertEqual(getstat("https://httpstat.us/200")[0], 1)
        self.assertGreaterEqual(getstat("https://httpstat.us/200")[1], 1)
        self.assertEqual(getstat("https://httpstat.us/200")[2], 200)
        self.assertEqual(getstat("https://httpstat.us/503")[0], 0)
        self.assertGreaterEqual(getstat("https://httpstat.us/503")[1], 1)
        self.assertEqual(getstat("https://httpstat.us/503")[2], 503)
        self.assertEqual(getstat("https://httpstat.us/404")[0], 0)
        self.assertGreaterEqual(getstat("https://httpstat.us/404")[1], 1)
        self.assertEqual(getstat("https://httpstat.us/404")[2], 404)
        self.assertEqual(getstat("https://opsmgr-05.slot-59.pez.vmware.com")[0], 0)
        self.assertEqual(getstat("https://url")[0], 0)
        self.assertEqual(getstat("https://urlx")[0], 0)
        self.assertEqual(getstat("http://203.0.113.1")[0], 0)
        self.assertEqual(getstat("http://0.42.42.42")[0], 0)
        self.assertEqual(getstat("http://10.0.0.1")[0], 0)
        self.assertEqual(getstat("x://invalid.url")[0], 0)
        self.assertEqual(getstat("")[0], 0)
        self.assertEqual(getstat("a")[0], 0)
        self.assertEqual(getstat("1")[0], 0)
    def test_getsettings(self):
        os.environ["SITEMON_METRICSPORT"] = str(8000)
        os.environ["SITEMON_URLS"] = "https://httpstat.us/200,https://httpstat.us/503"
        os.environ["SITEMON_INTERVAL"] = str(60)
        self.assertEqual(getsettings()[0], 8000)
        self.assertEqual(getsettings()[1][0], "https://httpstat.us/200")
        self.assertEqual(getsettings()[1][1], "https://httpstat.us/503")
        self.assertEqual(getsettings()[2], 60)
        self.assertGreaterEqual(getsettings()[0], 1024)
        self.assertLessEqual(getsettings()[0], 65536)
        os.environ.pop("SITEMON_INTERVAL")
        self.assertEqual(getsettings()[2], 60)
        os.environ.pop("SITEMON_METRICSPORT")
        self.assertRaises(KeyError, getsettings)
        os.environ["SITEMON_METRICSPORT"] = str(8080)
        os.environ["SITEMON_URLS"] = ",https://httpstat.us/503"
        self.assertRaises(ValueError, getsettings)
        os.environ["SITEMON_METRICSPORT"] = str(80800)
        self.assertRaises(ValueError, getsettings)
        os.environ["SITEMON_METRICSPORT"] = str(80)
        self.assertRaises(ValueError, getsettings)
        os.environ["SITEMON_METRICSPORT"] = str("AAAAAA")
        self.assertRaises(ValueError, getsettings)

if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)
