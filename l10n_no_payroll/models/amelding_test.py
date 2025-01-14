import pyxb

from . import amelding_logic
from .amelding_testdata import testdata


pyxb.RequireValidWhenGenerating(True)


logic = amelding_logic.AmeldingLogikk(testdata["l10n_no_payroll.amelding"])
print(logic.melding_xml())
