from queued_storage.backends import QueuedStorage, QueuedS3BotoStorage
from storages.backends.s3boto import S3BotoStorage
from django.utils.deconstruct import deconstructible
from django.core.cache import cache
import pdb

queued_s3_storage = QueuedS3BotoStorage(
    'django.core.files.storage.FileSystemStorage',
    'storages.backends.s3boto.S3BotoStorage')

@deconstructible
class WizcardQueuedS3BotoStorage(QueuedS3BotoStorage):
    def __init__(self, *args, **kwargs):
        super(WizcardQueuedS3BotoStorage, self).__init__(*args, **kwargs)

    def generate_filename(self, filename):
        return self.get_storage(filename).generate_filename(filename)

    def save(self, name, content, max_length=None):
        return super(WizcardQueuedS3BotoStorage, self).save(name, content)

