import logging
import unittest

from tests.antivirus.common import GenericEicar
from modules.antivirus.mcafee.vscl import McAfeeVSCL


# ============
#  Test Cases
# ============

class McAfeeVSCLEicar(GenericEicar, unittest.TestCase):

    expected_results = {
        'eicar-passwd.zip': None,
        'eicar.arj': 'EICAR test file',
        'eicar.cab': 'EICAR test file',
        'eicar.com.pgp': None,
        'eicar.com.txt': 'EICAR test file',
        'eicar.lha': 'EICAR test file',
        'eicar.lzh': 'EICAR test file',
        'eicar.msc': 'EICAR test file',
        'eicar.plain': 'EICAR test file',
        'eicar.rar': None,
        'eicar.tar': 'EICAR test file',
        'eicar.uue': None,
        'eicar.zip': 'EICAR test file',
        'eicar_arj.bin': 'EICAR test file',
        'eicar_cab.bin': 'EICAR test file',
        'eicar_gz.bin': 'EICAR test file',
        'eicar_lha.bin': 'EICAR test file',
        'eicar_lzh.bin': 'EICAR test file',
        'eicar_msc.bin': 'EICAR test file',
        'eicar_niveau1.zip': 'EICAR test file',
        'eicar_niveau10.zip': 'EICAR test file',
        'eicar_niveau11.zip': 'EICAR test file',
        'eicar_niveau12.zip': 'EICAR test file',
        'eicar_niveau13.zip': 'EICAR test file',
        'eicar_niveau14.bin': 'Generic.dx',
        'eicar_niveau14.jpg': 'Generic.dx',
        'eicar_niveau2.zip': 'EICAR test file',
        'eicar_niveau3.zip': 'EICAR test file',
        'eicar_niveau30.bin': None,
        'eicar_niveau30.rar': None,
        'eicar_niveau4.zip': 'EICAR test file',
        'eicar_niveau5.zip': 'EICAR test file',
        'eicar_niveau6.zip': 'EICAR test file',
        'eicar_niveau7.zip': 'EICAR test file',
        'eicar_niveau8.zip': 'EICAR test file',
        'eicar_niveau9.zip': 'EICAR test file',
        'eicar_rar.bin': None,
        'eicar_tar.bin': 'EICAR test file',
        'eicar_uu.bin': None,
        'eicarhqx_binhex.bin': None,
    }

    antivirus_class = McAfeeVSCL


if __name__ == '__main__':
    unittest.main()
