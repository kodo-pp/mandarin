# -*- coding: utf-8 -*-
# Mandarin compiler
# Copyright (C) 2018  Alexander Korzun
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

class MandarinError(RuntimeError):
    def __init__(self, text, posinfo):
        self.text = text
        self.posinfo = posinfo

    def __str__(self):
        return str(self.text) + ' ({})'.format(self.posinfo.fmt())


class MandarinSyntaxError(MandarinError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MandarinNotImplementedError(MandarinError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
