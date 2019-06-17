#!/usr/bin/env python3
# Mandarin compiler
# Copyright (C) 2019  Alexander Korzun
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


from setuptools import setup


setup(
    name                = 'mandarin',
    version             = '0.0.0',
    description         = 'A mixedly-typed compiled programming language',
    author              = 'Alexander Korzun',
    author_email        = 'korzun.sas@mail.ru',
    license             = 'GPL',
    packages            = ['mandarin'],
    tests_require       = ['pytest'],
    setup_requires      = ['pytest-runner'],
    install_requires    = ['lark-parser', 'colorama'],
)
