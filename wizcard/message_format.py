""" 
this is the place to define all message formats. 
Colander is the schema validator/generator used. Hopefully it'll work
"""

import colander
import limone

class CommonHeader(colander.MappingSchema):
    msgType = colander.String(),
              validator=colander.OneOf(['signup', 'login', 'phone_check_req', 'phone_check_resp'])
    deviceType = colander.String(),
              validator=colander.OneOf(['ios', 'android'])
    
class BaseMessage(colander.MappingSchema):
    
