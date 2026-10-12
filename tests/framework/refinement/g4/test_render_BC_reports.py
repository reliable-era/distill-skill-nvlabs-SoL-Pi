import unittest
from native import H
from render_BC_reports import render
class ReportGuards(unittest.TestCase):
 def test_partial_window_not_a_final_report(self):
  with self.assertRaises(AssertionError):render(H/'window-01-canonical.json',H/'window-01-descriptive-analysis.json',H/'window-01-independent-analysis.json')
if __name__=='__main__':unittest.main()
