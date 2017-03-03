# -*- coding: utf-8 -*-
from django.conf import settings as user_settings
from django.utils.functional import LazyObject


class Settings(object):
    pass


class LazySettings(LazyObject):
    def _setup(self):
        self._wrapped = Settings()

        self.ELFINDER_VOLUME_DRIVER = getattr(
            user_settings, "ELFINDER_VOLUME_DRIVER",
            "elfinder.volume_drivers.model_driver.ModelVolumeDriver"
        )

        self.ELFINDER_FS_DRIVER_ROOT = getattr(
            user_settings, "ELFINDER_FS_DRIVER_ROOT",
            user_settings.MEDIA_ROOT
        )

        self.ELFINDER_FS_DRIVER_URL = getattr(
            user_settings, "ELFINDER_FS_DRIVER_URL",
            user_settings.MEDIA_URL
        )

        # special settings for TinyMCE connector
        self.ELFINDER_TINYMCE_PATH_TO_POPUP_JS = getattr(
            user_settings, "ELFINDER_TINYMCE_PATH_TO_POPUP_JS",
            None
        )


settings = LazySettings()


