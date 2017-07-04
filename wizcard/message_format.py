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
class ContactsVerifySchema(colander.MappingSchema):
    pass
class ContactsUploadSchema(colander.MappingSchema):
    pass
class NotificationsGetSchema(colander.MappingSchema):
    pass
class WizcardEditSchema(colander.MappingSchema):
    pass
class RolodexEditSchema(colander.MappingSchema):
    pass
class WizcardAcceptSchema(colander.MappingSchema):
    pass
class WizConnectionRequestDeclineSchema(colander.MappingSchema):
    pass
class WizConnectionRequestWithdrawSchema(colander.MappingSchema):
    pass
class WizcardRolodexDeleteSchema(colander.MappingSchema):
    pass
class WizcardRolodexArchivedCardsSchema(colander.MappingSchema):
    pass
class WizcardFlickSchema(colander.MappingSchema):
    pass
class WizcardFlickPickSchema(colander.MappingSchema):
    pass
class WizcardFlickConnectSchema(colander.MappingSchema):
    pass
class WizcardMyFlickSchema(colander.MappingSchema):
    pass
class WizcardFlickWithdrawSchema(colander.MappingSchema):
    pass
class WizcardFlickEditSchema(colander.MappingSchema):
    pass
class WizcardFlickQuerySchema(colander.MappingSchema):
    pass
class WizcardFlickPickersSchema(colander.MappingSchema):
    pass
class TableMyTablesSchema(colander.MappingSchema):
    pass
class WizcardSendAssetToXYZSchema(colander.MappingSchema):
    pass
class WizcardSendToContactsSchema(colander.MappingSchema):
    pass
class WizcardSendUnTrustedSchema(colander.MappingSchema):
    pass
class WizcardSendToFutureContactsSchema(colander.MappingSchema):
    pass
class UserQuerySchema(colander.MappingSchema):
    pass
class WizcardGetDetailSchema(colander.MappingSchema):
    pass
class SettingsSchema(colander.MappingSchema):
    pass
class OcrRequestSelfSchema(colander.MappingSchema):
    pass
class OcrRequestDeadCardSchema(colander.MappingSchema):
    pass
class OcrDeadCardEditSchema(colander.MappingSchema):
    pass
class MeishiStartSchema(colander.MappingSchema):
    pass
class MeishiFindSchema(colander.MappingSchema):
    pass
class MeishiEndSchema(colander.MappingSchema):
    pass
class GetEmailTemplateSchema(colander.MappingSchema):
    pass
class GetRecommendationsSchema(colander.MappingSchema):
    pass
class SetRecoActionSchema(colander.MappingSchema):
    pass
class GetCommonConnectionsSchema(colander.MappingSchema):
    pass
class GetVideoThumbnailSchema(colander.MappingSchema):
    pass


class EntityCreateSchema(colander.MappingSchema):
    pass
class EntityDestroySchema(colander.MappingSchema):
    pass
class EntityEditSchema(colander.MappingSchema):
    pass
class EntityJoinSchema(colander.MappingSchema):
    pass
class TableJoinByInviteSchema(colander.MappingSchema):
    pass
class EntityLeaveSchema(colander.MappingSchema):
    pass
class EntityQuerySchema(colander.MappingSchema):
    pass
class MyEntitiesSchema(colander.MappingSchema):
    pass
class EntityDetailsSchema(colander.MappingSchema):
    pass
class EventsGetSchema(colander.MappingSchema):
    pass
class EntitiesEngageSchema(colander.MappingSchema):
    pass

