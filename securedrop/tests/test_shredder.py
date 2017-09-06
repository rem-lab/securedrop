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
import os
import shredder


class TestShredder(object):

    def test_already_exists(self, tmpdir, caplog):
        d = str(tmpdir)
        existing_path = os.path.join(d, 'existing')
        open(existing_path, 'w').close()
        assert os.path.exists(existing_path)
        s = shredder.Shredder(d)
        assert s.start()
        assert not s.start()
        while os.path.exists(existing_path):
            pass
        assert s.stop()
        assert not s.stop()
        assert 'error ignored' not in caplog.text()

    def test_move_file_or_directory(self, tmpdir, caplog):
        d = str(tmpdir.join('SHREDDER'))
        s = shredder.Shredder(d)
        s.start()
        while not os.path.exists(d):
            pass

        file_path = os.path.join(d, 'FILE_ONE')
        open(file_path, 'w').close()

        file_path = os.path.join(str(tmpdir), 'FILE_TWO')
        open(file_path, 'w').close()
        s.rm(file_path)

        directory_path = os.path.join(d, 'DIRECTORY_ONE')
        os.makedirs(directory_path)

        directory_path = os.path.join(str(tmpdir), 'DIRECTORY_TWO')
        os.makedirs(directory_path)
        s.rm(directory_path)

        s.stop()

        assert not os.listdir(d)
        assert 'error ignored' not in caplog.text()

    def test_ignore_srm_error(self, tmpdir, caplog):
        d = str(tmpdir)
        directory_path = os.path.join(d, 'DIRECTORY')
        os.makedirs(directory_path)
        file_path = os.path.join(directory_path, 'FILE')
        open(file_path, 'w').close()
        # no write permission, FILE cannot be removed
        os.chmod(directory_path, 0555)

        s = shredder.Shredder(d)
        s.start()
        s.stop()
        assert 'error ignored' in caplog.text()
