# -*- coding: utf-8 -*-
#
# SecureDrop whistleblower submission system
# Copyright (C) 2017 Loic Dachary <loic@dachary.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sh
import pytest
import subprocess


class TestSh(object):

    def test_sh(self):
        assert 'A' == sh.sh("echo -n A")
        with pytest.raises(Exception) as excinfo:
            sh.sh("exit 123")
        assert excinfo.value.returncode == 123

    def test_sh_progress(self, caplog):
        sh.sh("echo AB ; sleep 5 ; echo C")
        records = caplog.records()
        assert ':sh: ' in records[0].message
        assert 'AB' == records[1].message
        assert 'C' == records[2].message

    def test_sh_input(self, caplog):
        assert 'abc' == sh.sh("cat", 'abc')

    def test_sh_fail(self, caplog):
        with pytest.raises(subprocess.CalledProcessError) as excinfo:
            sh.sh("/bin/echo -n AB ; /bin/echo C ; exit 111")
        assert excinfo.value.returncode == 111
        for record in caplog.records():
            if record.levelname == 'ERROR':
                assert ('replay full' in record.message or
                        'ABC\n' == record.message)
