// vim: set syntax=antlr4:

grammar Mandarin;


//
// ******************
// ** PARSER RULES **
// ******************
//

code:                           toplevel_statement*;
toplevel_statement:             function_definition | native_function_declaration | NL;
native_function_declaration:    KW_DEF KW_NATIVE IDENTIFIER '(' typed_arglist ')' NL;
typed_arglist:                  '' | NL* typename? NL* IDENTIFIER NL* (',' NL* typename? NL* IDENTIFIER NL*)* ','? NL*;
typename:                       IDENTIFIER | array_typename;
array_typename:                 typename '[' ']';
function_definition:            KW_DEF IDENTIFIER '(' typed_arglist ')' NL code_block;
code_block:                     (code_statement | NL) NL+ KW_END NL;
code_statement:                 expression | var_declaration | var_assignment | if_statement | while_statement | for_statement;
var_declaration:                typename IDENTIFIER ('=' expression)?;
var_assignment:                 expression '=' expression;
if_statement:                   KW_IF expression NL if_code_block;
if_code_block:                  (code_statement | NL) NL+ if_code_block_continuation NL;
if_finalizing_code_block:       (code_statement | NL) NL+ KW_END NL;
if_code_block_continuation:     KW_END | KW_ELIF expression NL if_finalizing_code_block | KW_ELSE NL if_code_block;
while_statement:                KW_WHILE expression NL code_block;
for_statement:                  KW_FOR IDENTIFIER KW_IN expression NL code_block;
expression:                     atomic_expression | g__operator_toplevel | unary_operator atomic_expression;
atomic_expression:              '(' expression ')' | literal;
literal:                        num_integer | num_float | IDENTIFIER | string;
num_integer:                    SIGN? (INT_DEC | INT_BIN | INT_OCT | INT_HEX);
num_float:                      SIGN? (INT_DEC? '.' INT_DEC ('e' SIGN? INT_DEC)? | INT_DEC '.' INT_DEC? ('e' SIGN? INT_DEC)? | INT_DEC 'e' SIGN? INT_DEC);
string:                         QUOTE_SINGLE STRING_SIMPLE_CHAR_SINGLE* QUOTE_SINGLE | QUOTE_DOUBLE STRING_SIMPLE_CHAR_DOUBLE QUOTE_DOUBLE;

g__binop_500: g__less_priority '+' g__less_priority | g__less_priority '-' g__less_priority;
g__binop_1000: g__less_priority '*' g__less_priority | g__less_priority '/' g__less_priority;


//
// *****************
// ** LEXER RULES **
// *****************
//

fragment STRING_ESCAPE_CHAR:    '\\n'
                              | '\\r'
                              | '\\v'
                              | '\\t'
                              | '\\a'
                              | '\\b'
                              | '\\e'
                              | '\\x' HEXCHAR HEXCHAR
                              | '\\u' HEXCHAR HEXCHAR HEXCHAR HEXCHAR
                              | '\\U' HEXCHAR HEXCHAR HEXCHAR HEXCHAR HEXCHAR HEXCHAR HEXCHAR HEXCHAR;

fragment STRING_SIMPLE_CHAR_SINGLE:     ~('\\' | '\n' | '\r' | "'");
fragment STRING_SIMPLE_CHAR_DOUBLE:     ~('\\' | '\n' | '\r' | '"');

STRING_CHAR_SINGLE:     STRING_SIMPLE_CHAR_SINGLE | '\\\\' | "\\'" | STRING_ESCAPE_CHAR;
STRING_CHAR_DOUBLE:     STRING_SIMPLE_CHAR_DOUBLE | '\\\\' | '\\"' | STRING_ESCAPE_CHAR;

WHITESPACE:     [ \t] -> skip;
NL:             '\r\n' | '\n';

KW_IF: 'if';
KW_WHILE: 'while';
KW_FOR: 'for';
KW_END: 'end';
KW_DEF: 'def';
KW_NATIVE: 'native';

IDENTIFIER:     [a-zA-Z_][a-zA-Z0-9_]*;
SIGN:           [+-];
QUOTE_SINGLE:   "'";
QUOTE_DOUBLE:   '"';
INT_DEC:        [0-9]+;
INT_BIN:        '0b' [01]+;
INT_OCT:        '0o' [0-7]+;
INT_HEX:        '0x' HEXCHAR+;

fragment HEXCHAR:   [0-9a-zA-Z];

