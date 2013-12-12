""" 
this is the place to define all message formats. 
Colander is the schema validator/generator used. Hopefully it'll work
"""

import colander
import limone

class CommonHeader(colander.MappingSchema):
    msgType = colander.SchemaNode(colander.String(),
            validator=colander.OneOf(['signup', 'login', 'register', 'phone_check_req', 'phone_check_resp']))
    deviceID = colander.SchemaNode(colander.String())
    
class CommonSender(colander.MappingSchema):
    userID = colander.SchemaNode(colander.String())

class RegSender(CommonSender):
    deviceType = colander.SchemaNode(colander.String(),
              validator=colander.OneOf(['ios', 'android']))

class RegisterMsg(colander.MappingSchema):
    header = CommonHeader()
    sender = RegSender()
    
