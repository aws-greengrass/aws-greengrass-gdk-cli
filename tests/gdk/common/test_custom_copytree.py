import os
import shutil
import tempfile
import unittest

import gdk.common.custom_copytree as custom_copytree


def write_file(path, content, binary=False):
    """Write *content* to a file located at *path*.

    If *path* is a tuple instead of a string, os.path.join will be used to
    make a path.  If *binary* is true, the file will be opened in binary
    mode.
    """
    if isinstance(path, tuple):
        path = os.path.join(*path)
    mode = 'wb' if binary else 'w'
    encoding = None if binary else "utf-8"
    with open(path, mode, encoding=encoding) as fp:
        fp.write(content)


class BaseTest:
    def mkdtemp(self, prefix=None):
        """Create a temporary directory that will be cleaned up.

        Returns the path of the directory.
        """
        d = tempfile.mkdtemp(prefix=prefix, dir=os.getcwd())
        return d


class TestCopyTree(BaseTest, unittest.TestCase):
    def test_copytree_with_exclude(self):
        """
        Despite copying the entirety of the copytree implementation and modifying the parts we need, the only case the project
        uses right now is passing a set of pathnames to exclude. Here we test this functionality by modifying the original
        shutil test for copytree with exclude.
        """
        # creating data
        join = os.path.join
        exists = os.path.exists
        src_dir = self.mkdtemp()
        try:
            dst_dir = join(self.mkdtemp(), 'destination')
            write_file((src_dir, 'test.txt'), '123')
            write_file((src_dir, 'test.tmp'), '123')
            os.mkdir(join(src_dir, 'test_dir'))
            write_file((src_dir, 'test_dir', 'test.txt'), '456')
            os.mkdir(join(src_dir, 'test_dir2'))
            write_file((src_dir, 'test_dir2', 'test.txt'), '456')
            os.mkdir(join(src_dir, 'test_dir2', 'subdir'))
            os.mkdir(join(src_dir, 'test_dir2', 'subdir2'))
            write_file((src_dir, 'test_dir2', 'subdir', 'test.txt'), '456')
            write_file((src_dir, 'test_dir2', 'subdir2', 'test.py'), '456')

            try:
                excluded = set([f"{src_dir}{os.path.sep}test.tmp", f"{src_dir}{os.path.sep}test_dir2{os.path.sep}"])
                custom_copytree.copytree(src_dir, dst_dir, excluded_pathnames=excluded)
                # checking the result: some elements should not be copied
                self.assertTrue(exists(join(dst_dir, 'test.txt')))
                self.assertFalse(exists(join(dst_dir, 'test.tmp')))
                self.assertFalse(exists(join(dst_dir, 'test_dir2')))
            finally:
                shutil.rmtree(dst_dir)
            try:
                excluded = set([f"{src_dir}{os.path.sep}test.tmp"])
                custom_copytree.copytree(src_dir, dst_dir, excluded_pathnames=excluded)
                # checking the result: some elements should not be copied
                self.assertFalse(exists(join(dst_dir, 'test.tmp')))
                self.assertTrue(exists(join(dst_dir, 'test_dir2', 'subdir2')))
                self.assertTrue(exists(join(dst_dir, 'test_dir2', 'subdir')))
            finally:
                shutil.rmtree(dst_dir)
        finally:
            shutil.rmtree(src_dir)
            shutil.rmtree(os.path.dirname(dst_dir))
