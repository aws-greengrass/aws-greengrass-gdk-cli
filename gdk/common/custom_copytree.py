import os
import shutil
import stat
import logging


class Error(OSError):
    pass


def copytree(src, dst, symlinks=False, excluded_pathnames=None, copy_function=shutil.copy2,  # noqa: C901
             ignore_dangling_symlinks=False, dirs_exist_ok=False):
    """
    Modified version of shutil's copytree implementation allowing us to ignore with a more complex list of glob
    patterns including directories. Instead of seeing if just file names match a globlike pattern, check if the whole
    path matches a pre-filtered list of unwanted paths. I've also added logging at the debug level to track paths
    being excluded during this copy.

    Functionality of this custom copytree is the same as shutil copytree, except how ignore works. This changes the
    parameters as well, now taking a set under excluded_pathnames instead of a callable under ignore.

    For original implementation reference: https://github.com/python/cpython/blob/3.8/Lib/shutil.py#L516

    This is intended for use in our zip build process so that we can copy the component folder to zip-build and
    handle exclusions based on whole glob notations, rather than just matching the filename against a glob-like
    pattern. Do not modify this function for other use cases unless you are certain it will fit the zip build use case,
    although breaking changes should be picked up by the included unit test.
    """
    with os.scandir(src) as itr:
        entries = list(itr)

    os.makedirs(dst, exist_ok=dirs_exist_ok)
    errors = []
    use_srcentry = copy_function is shutil.copy2 or copy_function is shutil.copy

    for srcentry in entries:
        if srcentry.path in excluded_pathnames:
            logging.debug("Found path to be excluded: " + srcentry.path)
            continue
        elif srcentry.is_dir and f"{srcentry.path}{os.path.sep}" in excluded_pathnames:
            # Edge case where we provide a glob ending in / so glob.glob returns a directory path ending in /.
            logging.debug("Found path to be excluded: " + srcentry.path)
            continue
        srcname = os.path.join(src, srcentry.name)
        dstname = os.path.join(dst, srcentry.name)
        srcobj = srcentry if use_srcentry else srcname
        try:
            is_symlink = srcentry.is_symlink()
            if is_symlink and os.name == 'nt':
                # Special check for directory junctions, which appear as
                # symlinks but we want to recurse.
                lstat = srcentry.stat(follow_symlinks=False)
                if lstat.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT:
                    is_symlink = False
            if is_symlink:
                linkto = os.readlink(srcname)
                if symlinks:
                    # We can't just leave it to `copy_function` because legacy
                    # code with a custom `copy_function` may rely on copytree
                    # doing the right thing.
                    os.symlink(linkto, dstname)
                    shutil.copystat(srcobj, dstname, follow_symlinks=not symlinks)
                else:
                    # ignore dangling symlink if the flag is on
                    if not os.path.exists(linkto) and ignore_dangling_symlinks:
                        continue
                    # otherwise let the copy occur. copy2 will raise an error
                    if srcentry.is_dir():
                        copytree(srcobj, dstname, symlinks, excluded_pathnames,
                                 copy_function, ignore_dangling_symlinks,
                                 dirs_exist_ok)
                    else:
                        copy_function(srcobj, dstname)
            elif srcentry.is_dir():
                copytree(srcobj, dstname, symlinks, excluded_pathnames, copy_function,
                         ignore_dangling_symlinks, dirs_exist_ok)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy_function(srcobj, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        # Copying file access times may fail on Windows
        if getattr(why, 'winerror', None) is None:
            errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)
    return dst
