from __future__ import unicode_literals, division, print_function

import os.path
import collections
import numpy as np
import unittest
import pseudo_dojo.data as pdj_data

from copy import copy
from pseudo_dojo.core.testing import PseudoDojoTest
from pseudo_dojo.core.dojoreport import DojoReport

try:
    from matplotlib.figure import Figure as Fig
except ImportError:
    Fig = None


class DojoReportTest(PseudoDojoTest):

    def test_dojo_report_base_api(self):
        """Testing dojo report low-level API."""
        report = DojoReport.from_hints(10, "Si")
        #report = DojoReport.empty_from_pseudo(cls, pseudo, hints, devel=False)
        #print(report)
        assert report.symbol == "Si"
        assert report.element.symbol == "Si"
        assert report.ecuts
        assert not report.trials
        for trial in report.ALL_TRIALS:
            assert not report.has_trial(trial)
        assert report.check()

        #prev_ecuts = copy(report.ecuts)
        #report.add_ecuts(10000)
        #assert np.all(report.ecuts == prev_ecuts + [10000])

        report.add_hints([10, 20, 30])
        assert report.has_hints
        #assert report.hints.low.ecut == 10
        #assert report.hints.high.ecut == 30
        #assert not report.md5

        # Test add_entry
        with self.assertRaises(ValueError):
            report.add_entry("foobar", ecut=10, entry={})

        assert not report.has_trial("deltafactor", ecut=10)
        report.add_entry("deltafactor", ecut=10, entry={})
        str(report)
        assert report.has_trial("deltafactor", ecut=10)
        #assert not report.check(check_trials=["deltafactors"])

    def test_oncvpsp_dojo_report(self):
        """Testing pseudopotentials with dojo report"""
        h_wdr = pdj_data.pseudo("H-wdr.psp8")

        # Test DOJO REPORT and md5
        assert h_wdr.symbol == "H"
        assert h_wdr.xc == "PBE"

        ref_md5 = "8db4531eb441143fdda8032d237d0769"
        assert h_wdr.compute_md5() == ref_md5
        assert h_wdr.md5 == ref_md5
        assert "md5" in h_wdr.dojo_report and h_wdr.dojo_report["md5"] == ref_md5

        repr(h_wdr)
        assert isinstance(h_wdr.as_dict(), dict)

        # Test DojoReport
        #report = h_wdr.read_dojo_report()
        #report = h_wdr.read_dojo_report()
        assert h_wdr.has_dojo_report
        report = h_wdr.dojo_report
        #print(report)
        assert report.symbol == "H"
        assert report.element.symbol == "H"
        assert report["pseudo_type"] == "NC"
        assert report["version"] == "1.0"
        assert not report.has_hints

        # Basic consistency tests.
        missings = report.find_missing_entries()
        assert "ghosts" in missings
        assert not report.has_trial("foo")

        for trial in report.trials:
            assert report.has_trial(trial)
        assert report.has_trial("deltafactor", ecut=32)

        # Test deltafactor entry.
        self.assert_almost_equal(report["deltafactor"][32]["etotals"][1], -63.503524424394556)
        self.assert_almost_equal(report["deltafactor"][32]["volumes"][1],  66.80439150995784)

        assert not report.has_trial("deltafactor", ecut=-1)
        assert not report.has_trial("deafactor", ecut="32.00")

        # Test GBRV entries
        self.assert_almost_equal(report["gbrv_bcc"][32]["a0"], 1.8069170394120007)
        self.assert_almost_equal(report["gbrv_fcc"][34]["a0_rel_err"], 0.044806085362549146)

        # Test Phonon entry
        self.assert_almost_equal(report["phgamma"][36][-1], 528.9531110978663)

        # Test API to add ecuts and find missing entries.
        assert np.all(report.ecuts == [32.0,  34.0,  36.0, 38.0, 40.0, 42.0, 52.0])

        # TODO: reactivate these tests.
        #report.add_ecuts([30])
        #assert np.all(report.ecuts == [30.0, 32.0, 34.0, 36.0, 38.0, 40.0, 42.0, 52.0])
        #missing = report.find_missing_entries()
        #assert missing and all(v == [30] for v in missing.values())

        #report.add_ecuts([33, 53])
        #assert np.all(report.ecuts == [30.0, 32.0, 33.0, 34.0,  36.0, 38.0, 40.0, 42.0, 52.0, 53.0])
        #missing = report.find_missing_entries()
        #assert missing and all(v == [30, 33, 53] for v in missing.values())

    @unittest.skipIf(Fig is None, "This test requires matplotlib")
    def test_dojoreport_plots(self):
        """Testing dojoreport plotting methods"""
        if not self.has_matplotlib():
            raise unittest.SkipTest("Skipping matpltlib tests")

        h_wdr = pdj_data.pseudo("H-wdr.psp8")
        report = h_wdr.dojo_report
        assert isinstance(report.plot_deltafactor_convergence(xc=h_wdr.xc, show=False), Fig)
        assert report.plot_deltafactor_convergence(xc=h_wdr.xc, with_soc=True, show=False) is None
        assert isinstance(report.plot_deltafactor_eos(show=False), Fig)
        assert isinstance(report.plot_etotal_vs_ecut(show=False), Fig)
        assert isinstance(report.plot_gbrv_convergence(show=False), Fig)
        assert isinstance(report.plot_gbrv_eos('bcc', show=False), Fig)
        assert isinstance(report.plot_gbrv_eos('fcc', show=False), Fig)
        assert isinstance(report.plot_phonon_convergence(show=False), Fig)
