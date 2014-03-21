""" 
this is the place to define all message formats. 
Colander is the schema validator/generator used. Hopefully it'll work
"""

import colander
import limone

VALIDATOR = 0
HANDLER = 1

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

class RegisterSchema(colander.MappingSchema):
    header = CommonHeaderSchema()
    sender = SenderSchema()
    
class SignupSchema(colander.MappingSchema):
    pass
class LoginSchema(colander.MappingSchema):
    pass
class PhoneCheckRequestSchema(colander.MappingSchema):
    pass
class PhoneCheckResponseSchema(colander.MappingSchema):
    pass
class RegisterSchema(colander.MappingSchema):
    pass
class LocationUpdateSchema(colander.MappingSchema):
    pass
class NotificationsGetSchema(colander.MappingSchema):
    pass
class WizcardEditSchema(colander.MappingSchema):
    pass
class WizcardAcceptSchema(colander.MappingSchema):
    pass
class WizConnectionRequestDeclineSchema(colander.MappingSchema):
    pass
class WizcardRolodexDeleteSchema(colander.MappingSchema):
    pass
class WizcardFlickSchema(colander.MappingSchema):
    pass
class WizcardFlickAcceptSchema(colander.MappingSchema):
    pass
class WizcardSendToContactsSchema(colander.MappingSchema):
    pass
class WizcardSendUnTrustedSchema(colander.MappingSchema):
    pass
class WizcardSendToFutureContactsSchema(colander.MappingSchema):
    pass
class UserQueryByLocationSchema(colander.MappingSchema):
    pass
class UserQueryByNameSchema(colander.MappingSchema):
    pass
class UserGetDetailSchema(colander.MappingSchema):
    pass
class TableQuerySchema(colander.MappingSchema):
    pass
class TableDetailsSchema(colander.MappingSchema):
    pass
class TableCreateSchema(colander.MappingSchema):
    pass
class TableJoinSchema(colander.MappingSchema):
    pass
class TableLeaveSchema(colander.MappingSchema):
    pass
class TableDestroySchema(colander.MappingSchema):
    pass
class TableRenameSchema(colander.MappingSchema):
    pass

