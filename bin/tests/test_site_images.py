"""Tests for bin/site-images.  Run: python3 -m unittest discover bin/tests"""
import contextlib
import io
import os
import tempfile
import unittest
from importlib.machinery import SourceFileLoader

HERE = os.path.dirname(os.path.abspath(__file__))
si = SourceFileLoader("site_images",
                      os.path.join(HERE, "..", "site-images")).load_module()

PAGE = ("<head>\n<!-- background images -->\n</head><body>"
        "<footer>\n<!-- image credits -->\n</footer></body>")
MARK = si.MARK


class TestParse(unittest.TestCase):
    def test_rules_comments_blanks(self):
        text = "# page target image\n\n* body a.jpg\nx #sec-1 b.png\n"
        self.assertEqual(si.parse(text), [("*", "body", "a.jpg", ""),
                                          ("x", "#sec-1", "b.png", "")])

    def test_credit(self):
        self.assertEqual(si.parse("* body a.jpg  Doré, <em>Babel</em>.\n"),
                         [("*", "body", "a.jpg", "Doré, <em>Babel</em>.")])

    def test_bad_line(self):
        with self.assertRaisesRegex(ValueError, "line 2"):
            si.parse("* body a.jpg\n* body\n")


class TestImageUrl(unittest.TestCase):
    def test_local(self):
        self.assertEqual(si.image_url("a.jpg", "../"), "../images/a.jpg")

    def test_url(self):
        u = "https://example.org/a.jpg"
        self.assertEqual(si.image_url(u, "../"), u)


class TestSelector(unittest.TestCase):
    def test_body_is_fixed_layer(self):
        self.assertEqual(si.selector("body"), "body::before")

    def test_others_unchanged(self):
        self.assertEqual(si.selector("#sec-1"), "#sec-1")
        self.assertEqual(si.selector(".voice-sobor"), ".voice-sobor")


class TestCssFor(unittest.TestCase):
    rules = [("*", "body", "a.jpg", ""),
             ("01-*", ".voice-sobor", "b.jpg", ""),
             ("index", "body", "c.jpg", "")]

    def test_matching_rules_in_order(self):
        css = si.css_for("01-the-tower", self.rules, "../")
        self.assertEqual(css.splitlines(), [
            f'body::before {{ background-image: {si.VEIL}, '
            f'url("../images/a.jpg"); }}',
            f'.voice-sobor {{ background-image: {si.VEIL}, '
            f'url("../images/b.jpg"); }}'])

    def test_no_match(self):
        self.assertEqual(si.css_for("index", self.rules[1:2], ""), "")


class TestCreditsFor(unittest.TestCase):
    rules = [("*", "body", "a.jpg", "A."), ("01-*", "body", "b.jpg", ""),
             ("01-*", "#x", "c.jpg", "C."), ("index", "body", "d.jpg", "D.")]

    def test_matching_credits_only(self):
        self.assertEqual(si.credits_for("01-a", self.rules),
                         '<p class="credit">Background: A.</p>\n'
                         '<p class="credit">Background: C.</p>')

    def test_none(self):
        self.assertEqual(si.credits_for("02-b", self.rules[1:3]), "")


class TestInject(unittest.TestCase):
    def test_puts_in_block(self):
        out = si.inject(PAGE, MARK, "style", "body {}")
        self.assertIn(MARK + '\n<style class="bg">\nbody {}\n</style>', out)

    def test_rerun_replaces(self):
        out = si.inject(si.inject(PAGE, MARK, "style", "body {}"),
                        MARK, "style", "p {}")
        self.assertEqual(out.count("<style"), 1)
        self.assertIn("p {}", out)
        self.assertNotIn("body {}", out)

    def test_empty_removes_block(self):
        out = si.inject(PAGE, MARK, "style", "body {}")
        self.assertEqual(si.inject(out, MARK, "style", ""), PAGE)


class TestRender(unittest.TestCase):
    def test_style_and_credit(self):
        out = si.render("01-a", PAGE, [("*", "body", "a.jpg", "A.")], "../")
        self.assertIn('url("../images/a.jpg")', out)
        self.assertIn(si.CREDITS + '\n<div class="bg">\n'
                      '<p class="credit">Background: A.</p>\n</div>', out)


class SiteDir(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        os.makedirs(os.path.join(self.dir, "chapters"))
        os.makedirs(os.path.join(self.dir, "images"))
        for f in ("index.html", "chapters/01-a.html"):
            self.write(f, PAGE)
        self.write("chapters/notes.txt", "")
        self.write("images/a.jpg", "")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        with open(os.path.join(self.dir, name), "w") as f:
            f.write(text)

    def read(self, name):
        with open(os.path.join(self.dir, name)) as f:
            return f.read()


class TestMissing(SiteDir):
    def test_missing(self):
        rules = [("*", "body", "a.jpg", ""), ("*", "body", "gone.jpg", ""),
                 ("*", "body", "https://x.org/b.jpg", "")]
        self.assertEqual(si.missing(rules, self.dir),
                         [("*", "body", "gone.jpg", "")])


class TestUnmatched(unittest.TestCase):
    def test_unmatched(self):
        rules = [("06-the-dead-*", "body", "a.jpg", ""),
                 ("06-the-dead*", "body", "b.jpg", ""),
                 ("index", "body", "c.jpg", "")]
        self.assertEqual(si.unmatched(rules, ["index", "06-the-dead"]),
                         rules[:1])

    def test_all_match(self):
        self.assertEqual(si.unmatched([("*", "body", "a.jpg", "")], ["x"]),
                         [])


class TestPages(SiteDir):
    def test_pages(self):
        self.assertEqual(si.pages(self.dir), [
            ("index", os.path.join(self.dir, "index.html"), ""),
            ("01-a", os.path.join(self.dir, "chapters", "01-a.html"), "../")])


class TestMain(SiteDir):
    def test_usage(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(si.main(["site-images"]), 2)
        self.assertIn("usage:", err.getvalue())

    def test_run(self):
        self.write("images.txt", "01-a body a.jpg A.\n* body gone.jpg G.\n"
                   "01-a-* body a.jpg\n")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = si.main(["site-images",
                          os.path.join(self.dir, "images.txt"), self.dir])
        self.assertEqual(rc, 0)
        self.assertIn("no images/gone.jpg", err.getvalue())
        self.assertIn("01-a-* matches no page", err.getvalue())
        chap = self.read("chapters/01-a.html")
        self.assertIn('url("../images/a.jpg")', chap)
        self.assertIn("Background: A.", chap)
        self.assertNotIn("G.", chap)
        self.assertEqual(self.read("index.html"), PAGE)   # unchanged


if __name__ == "__main__":
    unittest.main()
