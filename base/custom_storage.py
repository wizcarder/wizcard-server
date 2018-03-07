from queued_storage.backends import QueuedS3BotoStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class WizcardQueuedS3BotoStorage(QueuedS3BotoStorage):
    def __init__(self, *args, **kwargs):
        super(WizcardQueuedS3BotoStorage, self).__init__(*args, **kwargs)

    def generate_filename(self, filename):
        return self.get_storage(filename).generate_filename(filename)

    def save(self, name, content, max_length=None):
        return super(WizcardQueuedS3BotoStorage, self).save(name, content)

