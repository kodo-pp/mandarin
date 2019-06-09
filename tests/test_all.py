import pytest
import lark

from mandarin.__main__ import run_parser
from mandarin.analyzer import Analyzer

# BEGIN import order is significant
import mandarin.generator
from mandarin.targets import targets
# END import order is significant


def _test_parses(filename, expect=True):
    def parses(code):
        ast = run_parser(code)
        an = Analyzer(ast)
        for target in targets:
            options = {'is_standalone': True}
            gen = target.GeneratorType(analyzer=an, options=options)
            code = gen.generate()
            # If it didn't raise, it probably works
        
    with open(filename) as f:
        code = f.read()
    if expect:
        parses(code)
    else:
        with pytest.raises(lark.exceptions.LarkError):
            parses(code)
            print('Something must be wrong')
            print('AST (dump): ' + repr(ast))
            print('AST (pretty):')
            print(ast.pretty())


def test_001():
    _test_parses('./test_files/001-hello-world.man')


def test_002():
    _test_parses('./test_files/002-function-declarations.man')


def test_003():
    _test_parses('./test_files/003-division.man')


def test_004():
    _test_parses('./test_files/004-more-complex-expressions.man')


def test_005():
    _test_parses('./test_files/005-factorial.man')


def test_006():
    _test_parses('./test_files/006-unary-operators.man')


def test_007():
    _test_parses('./test_files/007-while.man')


def test_008():
    _test_parses('./test_files/008-tricky-identifiers.man')


def test_009():
    _test_parses('./test_files/009-whitespace.man')


def test_010():
    _test_parses('./test_files/010-return.man')


def test_011():
    _test_parses('./test_files/011-methods.man')


def test_012():
    _test_parses('./test_files/012-classes.man')


def test_013():
    _test_parses('./test_files/013-many-operators.man')



def test_inv_001():
    _test_parses('./test_files/invalid/001-func-without-end.man', expect=False)


def test_inv_002():
    _test_parses('./test_files/invalid/002-if-without-end.man', expect=False)


def test_inv_003():
    _test_parses('./test_files/invalid/003-if-without-condition.man', expect=False)


def test_inv_004():
    _test_parses('./test_files/invalid/004-if-with-elif-without-condition.man', expect=False)


def test_inv_005():
    _test_parses('./test_files/invalid/005-if-with-two-elses.man', expect=False)


def test_inv_006():
    _test_parses('./test_files/invalid/006-if-with-two-conditions.man', expect=False)


def test_inv_007():
    _test_parses('./test_files/invalid/007-for-without-var.man', expect=False)


def test_inv_008():
    _test_parses('./test_files/invalid/008-for-without-range.man', expect=False)


def test_inv_009():
    _test_parses('./test_files/invalid/009-while-without-condition.man', expect=False)


def test_inv_010():
    _test_parses('./test_files/invalid/010-two-operands.man', expect=False)


def test_inv_011():
    _test_parses('./test_files/invalid/011-dangling-end.man', expect=False)


def test_inv_012():
    _test_parses('./test_files/invalid/012-dangling-else.man', expect=False)


def test_inv_013():
    _test_parses('./test_files/invalid/013-dangling-elif.man', expect=False)


def test_inv_014():
    _test_parses('./test_files/invalid/014-def-without-parens.man', expect=False)


def test_inv_015():
    _test_parses('./test_files/invalid/015-def-native-without-parens.man', expect=False)


def test_inv_016():
    _test_parses('./test_files/invalid/016-def-native-with-body.man', expect=False)


def test_inv_017():
    _test_parses('./test_files/invalid/017-def-without-body.man', expect=False)


def test_inv_018():
    _test_parses('./test_files/invalid/018-expression-at-toplevel.man', expect=False)


def test_inv_019():
    _test_parses('./test_files/invalid/019-extra-opening-paren.man', expect=False)


def test_inv_020():
    _test_parses('./test_files/invalid/020-extra-closing-paren.man', expect=False)


def test_inv_021():
    _test_parses('./test_files/invalid/021-keyword-as-identifier.man', expect=False)


def test_inv_022():
    _test_parses('./test_files/invalid/022-keyword-as-identifier-declaration.man', expect=False)
