from strip_rtf import sanitize_links

RTF_IN = r'''
\uldb Mouse,Mickey,1928\plain\fs20 {\v Mouse_Mickey_1928>main}
\uldb Reference\plain\fs20 {\v 2GNTK0>main@Reference.HLP}
'''
RTF_OUT = r'''
\uldb [[Mouse,Mickey,1928\plain\fs20 ]]
\uldb [[documents/Reference.md]]
'''

import unittest


class Test(unittest.TestCase):

    def testName(self):
        self.assertEqual(sanitize_links(RTF_IN), RTF_OUT)


if __name__ == "__main__":
    unittest.main()
