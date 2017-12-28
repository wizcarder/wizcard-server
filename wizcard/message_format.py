"""
this is the place to define all message formats.
Colander is the schema validator/generator used. Hopefully it'll work
"""

import colander
import limone

msg_types = ['signup', 'register']
class CommonHeaderSchema(colander.MappingSchema):
    msgType = colander.SchemaNode(colander.String(),
            validator=colander.OneOf(msg_types))
    deviceID = colander.SchemaNode(colander.String())

class CommonSenderSchema(colander.MappingSchema):
    userID = colander.SchemaNode(colander.String())

class SenderSchema(CommonSenderSchema):
    deviceType = colander.SchemaNode(colander.String(),
              validator=colander.OneOf(['ios', 'android']))


