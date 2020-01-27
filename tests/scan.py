# -*- python -*-
#
# gtk-doc - GTK DocBook documentation generator.
# Copyright (C) 2018  Stefan Sauer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

import argparse
import textwrap
import unittest

from parameterized import parameterized

from gtkdoc import scan


BASIC_TYPES = [
    "char",
    "signed char",
    "unsigned char",
    "short",
    "signed short",
    "unsigned short",
    "long",
    "signed long",
    "unsigned long",
    "int",
    "signed int",
    "unsigned int",
    "short int",
    "signed short int",
    "unsigned short int",
    "long int",
    "signed long int",
    "unsigned long int",
    "signed",
    "unsigned",
    "float",
    "double",
    "long double",
    "enum e",
    "struct s",
    "union u",
]

BASIC_TYPES_WITH_VOID = ['void'] + BASIC_TYPES

INLINE_MODIFIERS = [('g_inline', 'G_INLINE_FUNC'), ('static_inline', 'static inline')]


class ScanHeaderContentTestCase(unittest.TestCase):
    """Baseclass for the header scanner tests."""

    def setUp(self):
        self.decls = []
        self.types = []
        self.options = argparse.Namespace(
            deprecated_guards='GTKDOC_TESTER_DISABLE_DEPRECATED',
            ignore_decorators='',
            rebuild_types=False)
        scan.InitScanner(self.options)

    def scanHeaderContent(self, content):
        return scan.ScanHeaderContent(content, self.decls, self.types,
                                      self.options)

    def assertNoDeclFound(self, slist):
        self.assertEqual([], slist)
        self.assertEqual([], self.decls)
        self.assertEqual([], self.types)

    def assertNothingFound(self, slist, doc_comments):
        self.assertEqual({}, doc_comments)
        self.assertNoDeclFound(slist)


class ScanHeaderContent(ScanHeaderContentTestCase):
    """Test generic scanner behaviour."""

    def test_EmptyInput(self):
        slist, doc_comments = self.scanHeaderContent([])
        self.assertNothingFound(slist, doc_comments)

    def test_IgnoresOneLineComments(self):
        slist, doc_comments = self.scanHeaderContent(['/* test */'])
        self.assertNothingFound(slist, doc_comments)

    def test_IgnoresOneLineCommentsDoubleStar(self):
        slist, doc_comments = self.scanHeaderContent(['/** test */'])
        self.assertNothingFound(slist, doc_comments)

    def test_FindsDocComment(self):
        slist, doc_comments = self.scanHeaderContent("""\
            /**
             * Symbol:
             */""".splitlines(keepends=True))
        self.assertEqual(1, len(doc_comments))
        self.assertIn('symbol', doc_comments)

    def test_DocDoesNotChangeSlistDeclAndTypes(self):
        slist, doc_comments = self.scanHeaderContent("""\
            /**
             * Symbol:
             */""".splitlines(keepends=True))
        self.assertNoDeclFound(slist)

    def test_SkipInternalHeaders(self):
        header = textwrap.dedent("""\
            /* < private_header > */
            /**
             * symbol:
             */
            void symbols(void);""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertNothingFound(slist, doc_comments)

    def test_SkipSymbolWithPreprocessor(self):
        slist, doc_comments = self.scanHeaderContent("""\
            #ifndef __GTK_DOC_IGNORE__
            extern int bug_512565(void);
            #endif""".splitlines(keepends=True))
        self.assertNoDeclFound(slist)

    def test_AddDeprecatedFlagForSymbolsWithinDeprecationGuards(self):
        header = textwrap.dedent("""\
            #ifndef GTKDOC_TESTER_DISABLE_DEPRECATED
            /**
             * SYMBOL:
             *
             * Deprecated: 1.1. Use NEW_SYMBOL instead.
             */
            #define SYMBOL "value"
            #endif /* GTKDOC_TESTER_DISABLE_DEPRECATED */""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertEqual(1, len(self.decls))
        self.assertIn('<DEPRECATED/>', self.decls[0])

    def test_NoDeprecatedFlagForSymbolsOutsideDeprecationGuards(self):
        header = textwrap.dedent("""\
            #ifndef GTKDOC_TESTER_DISABLE_DEPRECATED
            /**
             * SYMBOL1:
             *
             * Deprecated: 1.1. Use NEW_SYMBOL1 instead.
             */
            #define SYMBOL1 "value"
            #endif /* GTKDOC_TESTER_DISABLE_DEPRECATED */
            /**
             * SYMBOL2:
             */
            #define SYMBOL2 "value"
            """)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertEqual(2, len(self.decls))
        self.assertNotIn('<DEPRECATED/>', self.decls[1])


class ScanHeaderContentEnum(ScanHeaderContentTestCase):
    """Test parsing of enum declarations."""

    def assertDecl(self, name, decl, slist):
        self.assertEqual([name], slist)
        d = '<ENUM>\n<NAME>%s</NAME>\n%s</ENUM>\n' % (name, decl)
        self.assertEqual([d], self.decls)
        self.assertEqual([], self.types)

    def test_FindsEnum(self):
        header = textwrap.dedent("""\
            enum data {
              TEST,
            };""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('data', header, slist)

    def test_FindsTypedefEnum(self):
        header = textwrap.dedent("""\
            typedef enum {
              ENUM
            } Data;""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('Data', header, slist)

    def test_HandleEnumWithDeprecatedMember(self):
        header = textwrap.dedent("""\
            enum data {
              TEST_A,
            #ifndef GTKDOC_TESTER_DISABLE_DEPRECATED
              TEST_B,
            #endif
              TEST_C
            };""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('data', header, slist)

    def test_HandleDeprecatedInMemberName(self):
        header = textwrap.dedent("""\
            typedef enum {
              VAL_DEFAULT,
              VAL_DEPRECATED,
            } Data;""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('Data', header, slist)

    def test_HandleDeprecatedMemberDecorator(self):
        header = textwrap.dedent("""\
            typedef enum {
              VAL_DEFAULT,
              OTHER_VAL MY_DEPRECATED_FOR(VAL_DEFAULT),
            } Data;""")
        expected = textwrap.dedent("""\
            typedef enum {
              VAL_DEFAULT,
              OTHER_VAL,
            } Data;""")
        self.options.ignore_decorators = 'MY_DEPRECATED_FOR()'
        scan.InitScanner(self.options)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('Data', expected, slist)

    def test_HandleDeprecatedDecorator(self):
        header = textwrap.dedent("""\
            typedef enum {
              VAL_DEFAULT,
              OTHER_VAL,
            } Data MY_DEPRECATED_FOR(OtherEnum);""")
        expected = textwrap.dedent("""\
            <DEPRECATED/>
            typedef enum {
              VAL_DEFAULT,
              OTHER_VAL,
            } Data;""")
        self.options.ignore_decorators = 'MY_DEPRECATED_FOR()'
        scan.InitScanner(self.options)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('Data', expected, slist)


class ScanHeaderContentFunctions(ScanHeaderContentTestCase):
    """Test parsing of function declarations."""

    def assertDecl(self, name, ret, params, slist):
        self.assertEqual([name], slist)
        d = '<FUNCTION>\n<NAME>%s</NAME>\n<RETURNS>%s</RETURNS>\n%s\n</FUNCTION>\n' % (name, ret, params)
        self.assertEqual([d], self.decls)
        self.assertEqual([], self.types)

    def test_FindsFunctionVoid(self):
        header = 'void func();'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', 'void', '', slist)

    def test_IgnoresInternalFunction(self):
        slist, doc_comments = self.scanHeaderContent([
            'void _internal(void);'
        ])
        self.assertNoDeclFound(slist)

    @parameterized.expand(INLINE_MODIFIERS)
    def test_IgnoresInternalInlineVoidFunction(self, _, modifier):
        header = textwrap.dedent("""\
            %s void _internal(void) {
            }""" % modifier)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertNoDeclFound(slist)

    @parameterized.expand(INLINE_MODIFIERS)
    def test_IgnoresInternalInlineFunction(self, _, modifier):
        header = textwrap.dedent("""\
            %s int _internal(int a) {
              return a + a; }""" % modifier)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertNoDeclFound(slist)

    @parameterized.expand([(t.replace(' ', '_'), t) for t in BASIC_TYPES_WITH_VOID])
    def test_HandlesReturnValue(self, _, ret_type):
        header = '%s func(void);' % ret_type
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', ret_type, 'void', slist)

    @parameterized.expand([(t.replace(' ', '_'), t) for t in BASIC_TYPES_WITH_VOID])
    def test_HandlesReturnValuePtr(self, _, ret_type):
        header = '%s* func(void);' % ret_type
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', ret_type + ' *', 'void', slist)

    @parameterized.expand([(t.replace(' ', '_'), t) for t in BASIC_TYPES_WITH_VOID])
    def test_HandlesReturnValueConstPtr(self, _, ret_type):
        header = 'const %s* func(void);' % ret_type
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', 'const ' + ret_type + ' *', 'void', slist)

    # TODO: also do parametrized?
    def test_FindsFunctionConstCharPtConstPtr_Void(self):
        header = 'const char* const * func(void);'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', 'const char * const *', 'void', slist)

    @parameterized.expand([(t.replace(' ', '_'), t) for t in BASIC_TYPES])
    def test_HandlesParameter(self, _, param_type):
        header = 'void func(%s);' % param_type
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', 'void', param_type, slist)

    @parameterized.expand([(t.replace(' ', '_'), t) for t in BASIC_TYPES])
    def test_HandlesNamedParameter(self, _, param_type):
        header = 'void func(%s a);' % param_type
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', 'void', param_type + ' a', slist)

    def test_HandlesMultipleParameterd(self):
        header = 'int func(char c, long l);'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', 'int', 'char c, long l', slist)

    def test_FindsFunctionStruct_Void_WithLinebreakAfterRetType(self):
        header = textwrap.dedent("""\
            struct ret *
            func (void);""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('func', 'struct ret *', 'void', slist)

    def test_FindsFunctionStruct_Void_WithLinebreakAfterFuncName(self):
        header = textwrap.dedent("""\
            struct ret * func
            (void);""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('func', 'struct ret *', 'void', slist)

    def test_FindsFunctionVoid_Int_WithLinebreakAfterParamType(self):
        header = textwrap.dedent("""\
            void func (int
              a);""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('func', 'void', 'int a', slist)

    @parameterized.expand(INLINE_MODIFIERS)
    def test_FindsInlineFunction(self, _, modifier):
        header = textwrap.dedent("""\
            %s void func (void)
            {
            }
            """ % modifier)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('func', 'void', 'void', slist)

    @parameterized.expand(INLINE_MODIFIERS)
    def test_FindsInlineFunctionWithNewlineAfterType(self, _, modifier):
        header = textwrap.dedent("""\
            %s void
            func (void)
            {
            }
            """ % modifier)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('func', 'void', 'void', slist)

    @parameterized.expand(INLINE_MODIFIERS)
    def test_FindsInlineFunctionWithConditionalBody(self, _, modifier):
        header = textwrap.dedent("""\
            %s int
            func (int a)
            {
            #if defined(__GNUC__) && (__GNUC__ >= 4) && defined(__OPTIMIZE__)
              return a;
            #else
              return 0;
            #endif
            }
            """ % modifier)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('func', 'int', 'int a', slist)

    @parameterized.expand(INLINE_MODIFIERS)
    def test_FindsInlineFunctionWithParenthesisName(self, _, modifier):
        header = textwrap.dedent("""\
            %s void
            (func) (void)
            {
            }
            """ % modifier)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('func', 'void', 'void', slist)


class ScanHeaderContentMacros(ScanHeaderContentTestCase):
    """Test parsing of macro declarations."""

    def assertDecl(self, name, decl, slist):
        self.assertEqual([name], slist)
        d = '<MACRO>\n<NAME>%s</NAME>\n%s</MACRO>\n' % (name, decl)
        self.assertEqual([d], self.decls)
        self.assertEqual([], self.types)

    def test_FindsMacroNumber(self):
        header = '#define FOO 1'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('FOO', header, slist)

    def test_FindsMacroExpression(self):
        header = '#define FOO (1 << 1)'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('FOO', header, slist)

    def test_FindsMacroFunction(self):
        header = '#define FOO(x) (x << 1)'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('FOO', header, slist)

    def test_IgnoresInternalMacro(self):
        slist, doc_comments = self.scanHeaderContent([
            '#define _INTERNAL (a) (a)'
        ])
        self.assertNoDeclFound(slist)

    def test_FindsDocCommentForDeprecationGuard(self):
        header = textwrap.dedent("""\
            /**
             * GTKDOC_TESTER_DISABLE_DEPRECATED:
             *
             * Documentation for a deprecation guard.
             */
            #define GTKDOC_TESTER_DISABLE_DEPRECATED 1""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertEqual(1, len(doc_comments))
        self.assertIn('gtkdoc_tester_disable_deprecated', doc_comments)
        self.assertDecl('GTKDOC_TESTER_DISABLE_DEPRECATED',
                        '#define GTKDOC_TESTER_DISABLE_DEPRECATED 1', slist)


class ScanHeaderContentStructs(ScanHeaderContentTestCase):
    """Test parsing of struct declarations."""

    def assertDecl(self, name, decl, slist):
        self.assertEqual([name], slist)
        d = '<STRUCT>\n<NAME>%s</NAME>\n%s</STRUCT>\n' % (name, decl)
        self.assertEqual([d], self.decls)
        self.assertEqual([], self.types)

    def test_FindsStruct(self):
        header = textwrap.dedent("""\
            struct data {
              int test;
            };""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('data', header, slist)

    def test_FindsTypedefStruct(self):
        header = textwrap.dedent("""\
            typedef struct {
              int test;
            } Data;""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('Data', header, slist)

    def test_HandleStructWithDeprecatedMember(self):
        header = textwrap.dedent("""\
            struct data {
              int test_a;
            #ifndef GTKDOC_TESTER_DISABLE_DEPRECATED
              int deprecated;
            #endif
              int test_b;
            };""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('data', header, slist)

    def test_IgnoresInternalStruct(self):
        header = 'struct _internal *x;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertNoDeclFound(slist)

    def test_IgnoresPrivateStruct(self):
        header = 'struct _x;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertNoDeclFound(slist)

    def test_OpaqueStructTypedefGeneratesEmptyDecl(self):
        header = 'typedef struct _data data;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('data', '', slist)

    def test_OpaqueStructGeneratesEmptyDecl(self):
        header = 'struct data;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('data', header, slist)

    def test_GetTitleFromGObjectClassStruct(self):
        header = textwrap.dedent("""\
            struct _GtkdocObjectClass {
              GObjectClass parent;
            };""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertIn('<TITLE>GtkdocObject</TITLE>', slist)

    def test_DeprecatedDecorator(self):
        header = textwrap.dedent("""\
            typedef struct {
              int x;
            } Data MY_DEPRECATED_FOR(OtherStruct);""")
        expected = textwrap.dedent("""\
            <DEPRECATED/>
            typedef struct {
              int x;
            } Data;""")
        self.options.ignore_decorators = 'MY_DEPRECATED_FOR()'
        scan.InitScanner(self.options)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('Data', expected, slist)

    def test_DeprecatedOpaqueStructTypedef(self):
        header = 'typedef struct _data data MY_DEPRECATED_FOR(OtherData);'
        expected = '<DEPRECATED/>\n'
        self.options.ignore_decorators = 'MY_DEPRECATED_FOR()'
        scan.InitScanner(self.options)
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('data', expected, slist)

    def test_HandleDeprecatedMemberDecorator(self):
        """Struct with deprecated members."""
        header = textwrap.dedent("""\
            struct data {
              int x1 G_GNUC_DEPRECATED;
              int x2 G_GNUC_DEPRECATED_FOR(replacement);
            };""")
        expected = textwrap.dedent("""\
            struct data {
              int x1;
              int x2;
            };""")
        scan.InitScanner(self.options)
        slist, doc_comments = self.scanHeaderContent(
                header.splitlines(keepends=True))
        self.assertDecl('data', expected, slist)


class ScanHeaderContentUnions(ScanHeaderContentTestCase):
    """Test parsing of union declarations."""

    def assertDecl(self, name, decl, slist):
        self.assertEqual([name], slist)
        d = '<UNION>\n<NAME>%s</NAME>\n%s</UNION>\n' % (name, decl)
        self.assertEqual([d], self.decls)
        self.assertEqual([], self.types)

    def test_FindsUnion(self):
        header = textwrap.dedent("""\
            union data {
              int i;
              float f;
            };""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('data', header, slist)

    def test_FindsTypedefUnion(self):
        header = textwrap.dedent("""\
            typedef union {
              int i;
              float f;
            } Data;""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('Data', header, slist)

    def test_IgnoresInternalUnion(self):
        header = 'union _internal *x;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertNoDeclFound(slist)

    def test_IgnoresPrivateUnion(self):
        header = 'union _x;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertNoDeclFound(slist)

    def test_OpaqueUnionTypedefGeneratesEmptyDecl(self):
        header = 'typedef union _data data;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('data', '', slist)

    def test_OpaqueUnionGeneratesEmptyDecl(self):
        header = 'union data;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('data', header, slist)


class ScanHeaderContentUserFunction(ScanHeaderContentTestCase):
    """Test parsing of function pointer declarations."""

    def assertDecl(self, name, ret, params, slist):
        self.assertEqual([name], slist)
        d = '<USER_FUNCTION>\n<NAME>%s</NAME>\n<RETURNS>%s</RETURNS>\n%s</USER_FUNCTION>\n' % (name, ret, params)
        self.assertEqual([d], self.decls)
        self.assertEqual([], self.types)

    def test_FindsFunctionVoid(self):
        header = 'typedef void (*func)();'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', 'void', '', slist)

    @parameterized.expand([(t.replace(' ', '_'), t) for t in BASIC_TYPES_WITH_VOID])
    def test_HandlesReturnValue(self, _, ret_type):
        header = 'typedef %s (*func)(void);' % ret_type
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', ret_type, 'void', slist)

    @parameterized.expand([(t.replace(' ', '_'), t) for t in BASIC_TYPES_WITH_VOID])
    def test_HandlesReturnValuePtr(self, _, ret_type):
        header = 'typedef %s* (*func)(void);' % ret_type
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', ret_type + ' *', 'void', slist)

    @parameterized.expand([(t.replace(' ', '_'), t) for t in BASIC_TYPES_WITH_VOID])
    def test_HandlesReturnValueConstPtr(self, _, ret_type):
        header = 'typedef const %s* (*func)(void);' % ret_type
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', 'const ' + ret_type + ' *', 'void', slist)

    def test_FindsFunctionVoid_Int_WithLinebreakAfterTypedef(self):
        header = textwrap.dedent("""\
            typedef
            void (*func) (int a);""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('func', 'void', 'int a', slist)

    def test_FindsFunctionStruct_Void_WithLinebreakAfterRetType(self):
        header = textwrap.dedent("""\
            typedef struct ret *
            (*func) (void);""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('func', 'struct ret *', 'void', slist)

    # TODO: not found
    # def test_FindsFunctionStruct_Void_WithLinebreakAfterFuncName(self):
    #     header = textwrap.dedent("""\
    #         typedef struct ret * (*func)
    #         (void);""")
    #     slist, doc_comments = self.scanHeaderContent(
    #         header.splitlines(keepends=True))
    #     self.assertDecl('func', 'struct ret *', 'void', slist)

    def test_FindsFunctionVoid_Int_WithLinebreakAfterParamType(self):
        header = textwrap.dedent("""\
            typedef void (*func) (int
              a);""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('func', 'void', 'int a', slist)

    @parameterized.expand([('void', 'void'), ('const_int', 'const int')])
    def test_FindsFunctionPointerVar(self, _, ret_type):
        header = '%s (*func)();' % ret_type
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('func', ret_type, '', slist)


class ScanHeaderContentVariabless(ScanHeaderContentTestCase):
    """Test parsing of variable declarations."""

    def assertDecl(self, name, decl, slist):
        self.assertEqual([name], slist)
        d = '<VARIABLE>\n<NAME>%s</NAME>\n%s</VARIABLE>\n' % (name, decl)
        self.assertEqual([d], self.decls)
        self.assertEqual([], self.types)

    @parameterized.expand([(t.replace(' ', '_'), t) for t in BASIC_TYPES])
    def test_FindsExternVar(self, _, var_type):
        header = 'extern %s var;' % var_type
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('var', header, slist)

    @parameterized.expand([(t.replace(' ', '_'), t) for t in BASIC_TYPES])
    def test_FindsExternPtrVar(self, _, var_type):
        header = 'extern %s* var;' % var_type
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('var', header, slist)

    def test_FindsConstInt(self):
        header = 'const int var = 42;'
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('var', header, slist)

    def test_FindConstCharPtr(self):
        header = 'const char* var = "foo";'
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('var', header, slist)


class ScanHeaderContentTypedefs(ScanHeaderContentTestCase):
    """Test parsing of typedef declarations."""

    def assertDecl(self, name, decl, slist):
        self.assertEqual([name], slist)
        d = '<TYPEDEF>\n<NAME>%s</NAME>\n%s</TYPEDEF>\n' % (name, decl)
        self.assertEqual([d], self.decls)
        self.assertEqual([], self.types)

    def test_FindsTypedefStructPointer(self):
        header = 'typedef struct data *dataptr;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('dataptr', header, slist)

    def test_FindsTypedefUnionPointer(self):
        header = 'typedef union data *dataptr;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('dataptr', header, slist)

    def test_FindsTypedef(self):
        header = 'typedef unsigned int uint;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertDecl('uint', header, slist)

    def test_SkipsEnumTypedefUnderscoreName(self):
        header = 'typedef enum _data data;'
        slist, doc_comments = self.scanHeaderContent([header])
        self.assertNoDeclFound(slist)


class SeparateSubSections(ScanHeaderContentTestCase):

    def test_NoSymbolsGiveEmptyResult(self):
        liststr = scan.SeparateSubSections([], {})
        self.assertEqual('\n', liststr)

    def test_CreatesStandardSectionFromIsObjectMacro(self):
        header = textwrap.dedent("""\
            #define GTKDOC_IS_OBJECT(obj) (G_TYPE_CHECK_INSTANCE_TYPE ((obj), GTKDOC_TYPE_OBJECT))
            void gtkdoc_object_function(void);
            """)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        liststr = scan.SeparateSubSections(slist, doc_comments)
        self.assertEqual(
            ['gtkdoc_object_function', '<SUBSECTION Standard>', 'GTKDOC_IS_OBJECT'],
            liststr.splitlines())

    def test_CreatesStandardSectionFromIsObjectClassMacro(self):
        header = textwrap.dedent("""\
            #define GTKDOC_IS_OBJECT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), GTKDOC_TYPE_OBJECT))
            void gtkdoc_object_function(void);
            """)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        liststr = scan.SeparateSubSections(slist, doc_comments)
        self.assertEqual(
            ['gtkdoc_object_function', '<SUBSECTION Standard>', 'GTKDOC_IS_OBJECT_CLASS'],
            liststr.splitlines())

    def test_CreatesStandardSectionFromGetTypeFunction(self):
        header = textwrap.dedent("""\
            GType gtkdoc_object_get_type(void) G_GNUC_CONST;
            void gtkdoc_object_function(void);
            """)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        liststr = scan.SeparateSubSections(slist, doc_comments)
        self.assertEqual(
            ['gtkdoc_object_function', '<SUBSECTION Standard>', 'gtkdoc_object_get_type'],
            liststr.splitlines())

    def test_CreatesStandardSectionAllMacros(self):
        header = textwrap.dedent("""\
            #define GTKDOC_TYPE_OBJECT            (gtkdoc_object_get_type())
            #define GTKDOC_OBJECT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), GTKDOC_TYPE_OBJECT, GtkdocObject))
            #define GTKDOC_OBJECT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass),  GTKDOC_TYPE_OBJECT, GtkdocObjectClass))
            #define GTKDOC_IS_OBJECT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), GTKDOC_TYPE_OBJECT))
            #define GTKDOC_IS_OBJECT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass),  GTKDOC_TYPE_OBJECT))
            #define GTKDOC_OBJECT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj),  GTKDOC_TYPE_OBJECT, GtkdocObjectClass))
            """)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        liststr = scan.SeparateSubSections(slist, doc_comments)
        self.assertEqual(
            ['<SUBSECTION Standard>', 'GTKDOC_IS_OBJECT', 'GTKDOC_IS_OBJECT_CLASS',
             'GTKDOC_OBJECT', 'GTKDOC_OBJECT_CLASS', 'GTKDOC_OBJECT_GET_CLASS',
             'GTKDOC_TYPE_OBJECT'],
            liststr.splitlines())

    def test_MovesSymbolIfUndocumented(self):
        header = textwrap.dedent("""\
            struct _GtkdocObject {
              GObject parent;
            };
            GType gtkdoc_object_get_type(void) G_GNUC_CONST;
            void gtkdoc_object_function(void);
            """)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        liststr = scan.SeparateSubSections(slist, doc_comments)
        self.assertEqual(
            ['gtkdoc_object_function', '<SUBSECTION Standard>', 'GtkdocObject', 'gtkdoc_object_get_type'],
            liststr.splitlines())

    def test_DoesNotMoveSymbolIfDocumented(self):
        header = textwrap.dedent("""\
            /**
             * GtkdocObject:
             *
             * instance data of gtk-doc unit test class
             */
            struct _GtkdocObject {
              GObject parent;
            };
            GType gtkdoc_object_get_type(void) G_GNUC_CONST;
            void gtkdoc_object_function(void);
            """)
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        liststr = scan.SeparateSubSections(slist, doc_comments)
        self.assertEqual(
            ['GtkdocObject', 'gtkdoc_object_function', '<SUBSECTION Standard>', 'gtkdoc_object_get_type'],
            liststr.splitlines())


class RemoveBracedContent(ScanHeaderContentTestCase):

    def test_OneLineFunctionBodyIsRemoved(self):
        decl = textwrap.dedent("""\
            static inline int function(int a) { return a + a; }""")
        (skip, decl) = scan.remove_braced_content(decl)
        self.assertEqual("static inline int function(int a);", decl)
        self.assertEqual(skip, False)

    def test_SimpleFunctionBodyIsRemoved(self):
        decl = textwrap.dedent("""\
            static inline int function(int a) {
              return a + a;
            }""")
        (skip, decl) = scan.remove_braced_content(decl)
        self.assertEqual("static inline int function(int a);", decl)
        self.assertEqual(skip, False)

    def test_SimpleFunctionWithNewlineBodyIsRemoved(self):
        decl = textwrap.dedent("""\
            static inline int function(int a)
            {
              return a + a;
            }""")
        (skip, decl) = scan.remove_braced_content(decl)
        self.assertEqual("static inline int function(int a);", decl)
        self.assertEqual(skip, False)

    def test_NestedFunctionBodyIsRemoved(self):
        decl = textwrap.dedent("""\
            static inline int function(int a) {
              if (a > 0) {
                return a + a;
              } else {
                return a - a;
              }
            }""")
        (skip, decl) = scan.remove_braced_content(decl)
        self.assertEqual("static inline int function(int a);", decl)
        self.assertEqual(skip, False)

    def test_NestedFunctionWithNewlinesBodyIsRemoved(self):
        decl = textwrap.dedent("""\
            static inline int function(int a)
            {
              if (a > 0)
              {
                return a + a;
              }
              else
              {
                return a - a;
              }
            }""")
        (skip, decl) = scan.remove_braced_content(decl)
        self.assertEqual("static inline int function(int a);", decl)
        self.assertEqual(skip, False)

    def test_SimpleFunctionWithParenthesisBodyIsRemoved(self):
        decl = textwrap.dedent("""\
            static inline int
            (function) (int a)
            {
              return a + a;
            }""")
        (skip, decl) = scan.remove_braced_content(decl)
        self.assertEqual("static inline int\n(function) (int a);", decl)
        self.assertEqual(skip, False)

    def test_FunctionWithMultilineParamsBodyIsRemoved(self):
        decl = textwrap.dedent("""\
            static inline int
            function (int a,
                      int b)
            {
              return a + b;
            }""")
        (skip, decl) = scan.remove_braced_content(decl)
        self.assertEqual(
            "static inline int\nfunction (int a,\n          int b);", decl)
        self.assertEqual(skip, False)


if __name__ == '__main__':
    from gtkdoc import common
    common.setup_logging()

    unittest.main()

    # t = RemoveBracedContent()
    # t.setUp()
    # t.test_NestedFunctionBodyIsRemoved()
