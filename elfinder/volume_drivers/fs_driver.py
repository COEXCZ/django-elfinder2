# -#- coding: utf-8 -*-
import hashlib
import os
import shutil
from datetime import datetime
import mimetypes as mimes

from django.conf import settings
from django.core.files import File
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils._os import safe_join

from elfinder.conf import settings as elfinder_settings
from elfinder.volume_drivers.base import BaseVolumeDriver


class FileExists(IOError):
    pass


class WrapperBase(object):
    def __init__(self, root):
        self.root = root

    def rename(self, new_name):
        parent_dir = os.path.dirname(self.path)
        new_abs_path = safe_join(self.root, parent_dir, new_name)
        if not os.path.exists(new_abs_path):
            os.rename(self.path, new_abs_path)
            self.path = new_abs_path
        else:
            raise FileExists()

    def is_dir(self):
        return False

    def is_file(self):
        return False

    def get_hash(self):
        return '%s_%s' % (self._real_hash(self.root)[0:2], self._real_hash(self.path))

    def get_parent_hash(self):
        if os.path.abspath(self.path) == os.path.abspath(self.root):
            return ''
        parent_path = os.path.dirname(self.path)
        return DirectoryWrapper(parent_path, self.root).get_hash()

    def _real_hash(self, path):
        path = '%s' % path
        enc_path = path.encode('utf8')
        m = hashlib.md5()
        m.update(enc_path)
        return str(m.hexdigest())


class FileWrapper(WrapperBase):
    def __init__(self, file_path, root):
        if not os.path.isfile(file_path):
            raise ValueError("'%s' is not a valid file path" % file_path)
        self._file = None
        self.path = file_path
        super(FileWrapper, self).__init__(root)

    def is_file(self):
        return True

    def get_path(self):
        return self._file_path

    def set_path(self, path):
        self._file_path = path
        if self._file is not None:
            self._file.close()
            self._file = None

    path = property(get_path, set_path)

    @property
    def name(self):
        return self._file.name

    def get_chunks(self):
        if self._file is None:
            self._file = File(open(self.path, 'rb'))
        return self._file.chunks()

    def get_contents(self):
        if self._file is None:
            self._file = File(open(self.path))
        self._file.seek(0)
        return self._file.read()

    def set_contents(self, data):
        if self._file is not None:
            self._file.close()
            self._file = None
        _file = File(open(self.path, "ab"))
        _file.write(data)
        _file.close()

    contents = property(get_contents, set_contents)

    def get_info(self):
        path = self.path
        info = {
            'name': os.path.basename(path),
            'hash': self.get_hash(),
            'date': datetime.fromtimestamp(os.stat(path).st_mtime).strftime("%d %b %Y %H:%M"),
            'size': self.get_size(),
            'read': os.access(path, os.R_OK),
            'write': os.access(path, os.W_OK),
            'rm': os.access(path, os.W_OK),
            'url': self.get_url(),
            'phash': self.get_parent_hash() or '',
        }
        if settings.DEBUG:
            info['abs_path'] = path

        # parent_hash = self.get_parent_hash()
        # if parent_hash:
        #     info['phash'] = parent_hash

        mime, is_image = self.get_mime(path)
        # if is_image and self.imglib and False:
        #     try:
        #         import Image
        #         l['tmb'] = self.get_thumb_url(f)
        #     except ImportError:
        #         pass
        #     except Exception:
        #         raise

        info['mime'] = mime

        return info

    def get_size(self):
        return os.lstat(self.path).st_size

    def get_url(self):
        rel_path = os.path.relpath(self.path, self.root).replace('\\', '/')
        user_path = '%s/' % (self.root.split('/')[-1],)
        return '%s%s%s' % (elfinder_settings.ELFINDER_FS_DRIVER_URL, user_path, rel_path)

    def get_mime(self, path):
        mime = mimes.guess_type(path)[0] or 'Unknown'
        if mime.startswith('image/'):
            return mime, True
        else:
            return mime, False

    def remove(self):
        os.remove(self.path)

    @classmethod
    def mkfile(cls, file_path, root):
        if not os.path.exists(file_path):
            f = open(file_path, "w")
            f.close()
            return cls(file_path, root)
        else:
            raise Exception("File '%s' already exists" % os.path.basename(file_path))


class DirectoryWrapper(WrapperBase):
    def __init__(self, dir_path, root):
        if not os.path.isdir(dir_path):
            raise ValueError("'%s' is not a valid dir path" % dir_path)
        self.path = dir_path
        super(DirectoryWrapper, self).__init__(root)

    def is_dir(self):
        return True

    def get_path(self):
        return self._dir_path

    def set_path(self, path):
        self._dir_path = path

    path = property(get_path, set_path)

    def get_info(self):
        path = self.path
        info = {
            'name': os.path.basename(path),
            'hash': self.get_hash(),
            'date': datetime.fromtimestamp(os.stat(path).st_mtime).strftime("%d %b %Y %H:%M"),
            'mime': 'directory',
            'size': self.get_size(),
            'read': os.access(path, os.R_OK),
            'write': os.access(path, os.W_OK),
            'rm': os.access(path, os.W_OK),
            'dirs': self.has_dirs(),
            'phash': self.get_parent_hash() or ''
        }
        if settings.DEBUG:
            info['abs_path'] = path

        # parent_hash = self.get_parent_hash()
        # if parent_hash:
        #     info['phash'] = parent_hash

        return info

    def get_size(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.path):
            for f in filenames:
                fp = safe_join(self.root, dirpath, f)
                if os.path.exists(fp):
                    total_size += os.stat(fp).st_size
        return total_size

    def has_dirs(self):
        for item in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, item)):
                return True
        return False

    def remove(self):
        shutil.rmtree(self.path)

    @classmethod
    def mkdir(cls, dir_path, root):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            return cls(dir_path, root)
        else:
            raise Exception("Directory '%s' already exists" % os.path.basename(dir_path))


class FileSystemVolumeDriver(BaseVolumeDriver):
    def __init__(self, fs_driver_root=elfinder_settings.ELFINDER_FS_DRIVER_ROOT,
                 *args, **kwargs):
        self.root = os.path.abspath(fs_driver_root)

    def get_volume_id(self):
        # return u"fsvolume"
        return DirectoryWrapper(self.root, self.root).get_hash().split("_")[0]

    def get_info(self, target):
        path = self._find_path(target)
        return self._get_path_info(path)

    def get_tree(self, target, ancestors=False, siblings=False):
        path = self._find_path(target)

        tree = [self._get_path_info(path)]
        tree.extend([self._get_path_info(safe_join(self.root, path, child)) for child in os.listdir(path)])

        if ancestors:
            proc_path = path
            while proc_path != self.root:
                tree.append(self._get_path_info(proc_path))
                proc_path, head = os.path.split(proc_path)
                for ancestor_sibling in os.listdir(proc_path):
                    ancestor_sibling_abs = safe_join(self.root, proc_path, ancestor_sibling)
                    if os.path.isdir(ancestor_sibling_abs):
                        tree.append(self._get_path_info(ancestor_sibling_abs))

        if siblings and not (path == self.root):
            parent_path, curr_dir = os.path.split(path)
            for sibling in os.listdir(parent_path):
                if sibling == curr_dir:
                    continue
                sibling_abs = safe_join(self.root, parent_path, sibling)
                tree.append(self._get_path_info(sibling_abs))
        # print
        # print "*******************************************"
        # print
        # for t in tree:
        #     print t
        # print
        return tree

    def read_file_view(self, request, hash):
        file_path = self._find_path(hash)
        from django.http import HttpResponse
        resp = HttpResponse(content_type='application/force-download')
        file = FileWrapper(file_path, self.root)
        for chunk in file.get_chunks():
            resp.write(chunk)

        return resp

    def mkdir(self, name, parent):
        parent_path = self._find_path(parent)
        new_abs_path = safe_join(self.root, parent_path, name)
        return DirectoryWrapper.mkdir(new_abs_path, self.root).get_info()

    def mkfile(self, name, parent):
        parent_path = self._find_path(parent)
        new_abs_path = safe_join(self.root, parent_path, name)
        return FileWrapper.mkfile(new_abs_path, self.root).get_info()

    def rename(self, name, target):
        obj = self._get_path_object(self._find_path(target))
        obj.rename(name)
        return {
            "added": [obj.get_info()],
            "removed": [target],
        }

    def list(self, target):
        dir_list = []
        for item in self.get_tree(target):
            dir_list.append(item['name'])
        return dir_list

    def paste(self, targets, source, dest, cut):
        """ Moves/copies target files/directories from source to dest. """
        # source_dir = self._get_path_object(source)
        dest_dir = self._get_path_object(self._find_path(dest))
        added = []
        removed = []
        if dest_dir.is_dir():
            for target in targets:
                orig_abs_path = self._find_path(target)
                orig_obj = self._get_path_object(orig_abs_path)
                new_abs_path = safe_join(self.root, dest_dir.get_path(), os.path.basename(orig_abs_path))
                if cut:
                    _fnc = shutil.move
                    removed.append(orig_obj.get_info()['hash'])
                else:
                    if orig_obj.is_dir():
                        _fnc = shutil.copytree
                    else:
                        _fnc = shutil.copy
                _fnc(orig_abs_path, new_abs_path)
                added.append(self._get_path_info(new_abs_path))

        return {"added": added,
                "removed": removed}

    def remove(self, target):
        obj = self._get_path_object(self._find_path(target))
        obj.remove()
        return target

    def upload(self, files, parent):
        added = []
        parent = self._get_path_object(self._find_path(parent))
        if parent.is_dir():
            for upload in files.getlist('upload[]'):
                new_abs_path = safe_join(self.root, parent.path, upload.name)
                try:
                    new_file = FileWrapper.mkfile(new_abs_path, self.root)
                    new_file.contents = upload.read()
                    added.append(new_file.get_info())
                except Exception:
                    pass
        return {"added": added}

    # private methods

    def _find_path(self, fhash, root=None, resolution=False):
        if root is None:
            root = '%s' % self.root
        final_path = None

        if not fhash:
            return root

        for dirpath, dirnames, filenames in os.walk(root):
            for f in filenames:
                f = safe_join(self.root, dirpath, f)
                f_obj = FileWrapper(f, self.root)
                # rf = f
                #f = f.encode('utf8')
                if fhash == f_obj.get_hash():
                    final_path = f
                    if resolution:
                        try:
                            final_path = str(final_path, 'utf8')
                        except:
                            pass
                    return final_path
            for d in dirnames:
                d = safe_join(self.root, dirpath, d)
                d_obj = DirectoryWrapper(d, self.root)
                # rd = d
                if fhash == d_obj.get_hash():
                    final_path = d
                    if resolution:
                        try:
                            final_path = str(final_path, 'utf8')
                        except:
                            pass
                    return final_path
            d = os.path.abspath(dirpath)
            d_obj = DirectoryWrapper(d, self.root)
            # rd = d
            if fhash == d_obj.get_hash():
                final_path = d
                if resolution:
                    try:
                        final_path = str(final_path, 'utf8')
                    except:
                        pass
                return final_path

        return final_path

    def _get_path_object(self, path):
        if os.path.isdir(path):
            return DirectoryWrapper(path, root=self.root)
        else:
            return FileWrapper(path, root=self.root)

    def _get_path_info(self, path):
        return self._get_path_object(path).get_info()
