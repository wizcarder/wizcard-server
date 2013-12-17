""" 
this is the place to define all message formats. 
Colander is the schema validator/generator used. Hopefully it'll work
"""

import colander
import limone

VALIDATOR = 0
HANDLER = 1

msgTypesValidatorsAndHandlers = {
    'signup'                      : (SignupSchema, Signup),
    'login'                       : (LoginSchema, Login),
    'phone_check_req'             : (PhoneCheckRequestSchema, PhoneCheckRequest),
    'phone_check_rsp'             : (PhoneCheckResponseSchema, PhoneCheckResponse),
    'register'                    : (RegisterSchema,Register),
    'current_location'            : (LocationUpdateSchema, LocationUpdate),
    'get_card'                    : (NotificationsGetSchema, NotificationsGet),
    'edit_card'                   : (WizcardEditSchema, WizcardEdit),
    'add_notification_card'       : (WizcardAcceptSchema, WizcardAccept),
    'delete_notification_card'    : (WizConnectionRequestDeclineSchema, WizConnectionRequestDecline),
    'delete_rolodex_card'         : (WizcardRolodexDeleteSchema, WizcardRolodexDelete),
    'card_flick'                  : (WizcardFlickSchema, WizcardFlick),
    'card_flick_accept'           : (WizcardFlickAcceptSchema, WizcardFlickAccept),
    'send_card_to_contacts'       : (WizcardSendToContactsSchema, WizcardSendToContacts),
    'send_card_to_user'           : (WizcardSendUnTrustedSchema, WizcardSendUnTrusted),
    'send_card_to_future_contacts': (WizcardSendToFutureContactsSchema, WizcardSendToFutureContacts),
    'find_users_by_location'      : (UserQueryByLocationSchema, UserQueryByLocation),
    'send_query_user'             : (UserQueryByNameSchema, UserQueryByName),
    'show_table_list'             : (TableQuerySchema, TableQuery),
    'table_details'               : (TableDetailsSchema, TableDetails),
    'create_table'                : (TableCreateSchema, TableCreate),
    'join_table'                  : (TableJoinSchema, TableJoin),
    'leave_table'                 : (TableLeaveSchema, TableLeave),
    'destroy_table'               : (TableDestroySchema, TableDestroy),
    'rename_table'                : (TableRenameSchema, TableRename)
}

class CommonHeaderSchema(colander.MappingSchema):
    msgType = colander.SchemaNode(colander.String(),
            validator=colander.OneOf(['signup', 'login', 'register', 'phone_check_req', 'phone_check_resp']))
    deviceID = colander.SchemaNode(colander.String())
    
class CommonSenderSchema(colander.MappingSchema):
    userID = colander.SchemaNode(colander.String())

class SenderSchema(CommonSender):
    deviceType = colander.SchemaNode(colander.String(),
              validator=colander.OneOf(['ios', 'android']))

class RegisterSchema(colander.MappingSchema):
    header = CommonHeader()
    sender = RegSender()
    
class SignupSchema(colander.MappingSchema):
class LoginSchema(colander.MappingSchema):
class RegisterSchema(colander.MappingSchema):
class LocationUpdateSchema(colander.MappingSchema):
class NotificationsGetSchema(colander.MappingSchema):
class WizcardEditSchema(colander.MappingSchema):
class WizConnectionRequestDeclineSchema(colander.MappingSchema):
class WizcardRolodexDeleteSchema(colander.MappingSchema):
class WizcardAcceptSchema(colander.MappingSchema):
class WizcardflickSchema(colander.MappingSchema):
class WizcardSendToContactsSchema(colander.MappingSchema):
class WizcardSendUnTrustedSchema(colander.MappingSchema):
class WizcardSendToFutureContactsSchema(colander.MappingSchema):
class UserQueryByNameSchema(colander.MappingSchema):
class UserQueryByLocationSchema(colander.MappingSchema):
class TableQuerySchema(colander.MappingSchema):
class TableDetailsSchema(colander.MappingSchema):
class TableCreateSchema(colander.MappingSchema):
class TableJoinSchema(colander.MappingSchema):
class TableLeaveSchema(colander.MappingSchema):
class TableDestroySchema(colander.MappingSchema):
class TableRenameSchema(colander.MappingSchema):
