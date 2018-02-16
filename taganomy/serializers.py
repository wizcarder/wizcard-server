
from taganomy.models import Taganomy
from taggit_serializer.serializers import TagListSerializerField
from rest_framework.validators import ValidationError
import pdb

class TaganomySerializerField(TagListSerializerField):

    def to_internal_value(self, value):
        if not isinstance(value, dict):
            raise ValidationError({
                'expected dict, got {value}'.format(value=value.__class__.__name__)
            })

        taganomy_id = value.pop('taganomy_id', None)
        tags = value.pop('tags', None)

        # Perform the data validation.
        if taganomy_id is None:
            raise ValidationError({
                'id': 'This field is required.'
            })

        try:
            taganomy_inst = Taganomy.objects.get(id=taganomy_id)
        except:
            raise ValidationError({
                'id': 'Invalid Taganomy instance'
            })

        if tags is None:
            raise ValidationError({
                'tags': 'This field is required.'
            })

        tags = super(TaganomySerializerField, self).to_internal_value(tags)

        out = dict(taganomy=taganomy_inst, tags=tags)

        return out

