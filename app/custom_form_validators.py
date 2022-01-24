from enum import Enum

import humanfriendly
from wtforms import ValidationError


class MaxContentLength(object):

    def __init__(self, content_length, message=None):
        self.content_length = content_length
        self.message = message

    def __call__(self, form, field):
        if not self.message:
            self.message = '{} is too large. Limit the file size to {}'

        for upload in field.raw_data:
            if self.get_file_size(upload) > self.content_length:
                raise ValidationError(self.message.format(upload.filename, self.format_bytes(self.content_length)))

    @staticmethod
    def get_file_size(file):
        start = file.tell()
        file.seek(0, 2)
        size = file.tell()
        file.seek(start)
        return size

    @staticmethod
    def format_bytes(content_size):
        return humanfriendly.format_size(content_size, binary=True)
