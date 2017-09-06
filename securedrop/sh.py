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
import logging
import subprocess

log = logging.getLogger(__name__)


def sh(command, input=None):
    """Run the *command* which must be a shell snippet. The stdin is
    either /dev/null or the *input* argument string.

    The stderr/stdout of the snippet are captured and logged via
    logging.debug(), one line at a time.
    """
    log.debug(":sh: " + command)
    if input is None:
        stdin = None
    else:
        stdin = subprocess.PIPE
    proc = subprocess.Popen(
        args=command,
        stdin=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        bufsize=1)
    if stdin is not None:
        proc.stdin.write(input)
        proc.stdin.close()
    lines_of_command_output = []
    with proc.stdout:
        for line in iter(proc.stdout.readline, b''):
            line = line.decode('utf-8')
            lines_of_command_output.append(line)
            log.debug(line.strip().encode('ascii', 'ignore'))
    if proc.wait() != 0:
        raise subprocess.CalledProcessError(
            returncode=proc.returncode,
            cmd=command
        )
    return "".join(lines_of_command_output)
