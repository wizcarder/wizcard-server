contact_container_fields = ['company', 'title', 'phone', 'start', 'end', 'f_bizCardUrl']
contact_container_keymap = {
        'f_bizCardUrl': 'get_fbizcard_url'
        }

contact_container_template = {
    'fields':  contact_container_fields,
    'key_map': contact_container_keymap
}

wizcard_fields_thumbnail_only = ['wizcard_id', 'user_id', 'thumbnailUrl']

wizcard_fields_mini = ['wizcard_id', 'user_id', 'thumbnailUrl', \
                       'first_name', 'last_name']

wizcard_fields_micro = ['wizcard_id']

wizcard_fields = ['wizcard_id', 'user_id', 'first_name', 'last_name', \
                  'phone', 'email', 'thumbnailUrl', 'contact_container', 'status']

wizcard_fields_keymap = {
        'wizcard_id': 'id',
        'thumbnailUrl': 'get_thumbnail_url',
        'status': 'connected_status_string'
        }

wizcard_fields_keymap_brief = {
        'wizcard_id': 'id',
        'thumbnailUrl': 'get_thumbnail_url',
        'contact_container': 'get_latest_contact_container',
        'status': 'followed_status_string'
        }

wizcard_related_objects_template = {
    'contact_container': contact_container_template
}

wizcard_template_thumbnail_only = {
    'fields': wizcard_fields_thumbnail_only,
    'key_map' : wizcard_fields_keymap
}

wizcard_template_mini = {
    'fields': wizcard_fields_mini,
    'key_map' : wizcard_fields_keymap
}
wizcard_template_micro = {
    'fields': wizcard_fields_micro,
    'merge' : True,
    'key_map' : wizcard_fields_keymap
}

wizcard_template_micro = {
    'fields': wizcard_fields_micro,
    'merge' : True,
    'key_map' : wizcard_fields_keymap
}

#use this for nearby
wizcard_template_brief = {
    'fields': wizcard_fields,
    'exclude': ['phone', 'email', 'status'],
    'key_map' : wizcard_fields_keymap_brief
}

#use these for rolodex (half/full)
wizcard_template_half = {
    'fields': wizcard_fields,
    'exclude': ['phone', 'email'],
    'key_map' : wizcard_fields_keymap_brief
}

wizcard_template_full = {
    'fields': wizcard_fields,
    'key_map' : wizcard_fields_keymap,
    'related': wizcard_related_objects_template
}

flick_pickers_template = {
    'fields': ['id']
}

related_wizcard_template_brief = {
    'wizcard': wizcard_template_brief
}


related_wizcard_template_full = {
    'wizcard': wizcard_template_full
}

flicked_wizcard_template = {
    'fields': ['created', 'timeRemaining', 'flick_id', 'wizcard'],
    'key_map': {
        'created':'a_created', 'timeRemaining':'time_remaining', 'flick_id':'id'
    },
    'related': related_wizcard_template_brief
}

my_flicked_wizcard_template = {
    'fields': ['created', 'flick_id', 'lat', 'lng',
               'timeout', 'flick_pickers'],
    'key_map': {
        'created':'a_created', 
        'flick_id':'id', 
        'timeout': 'time_remaining',
        'city': 'reverse_geo_name'},
    'related': {
        'flick_pickers': flick_pickers_template,
    }
}

user_query_brief_template = {
    'fields': ['user_id', 'wizcard'],
    'related': related_wizcard_template_brief,
    'key_map' : {'user_id':'id'}
}

user_query_full_template = {
    'fields': ['user_id', 'wizcard'],
    'related': related_wizcard_template_full,
    'key_map' : {'user_id':'id'}
}

nearby_table_template = {
    'fields': ['id', 'tablename', 'secureTable', 'numSitting', 'created',\
               'timeout', 'timeRemaining', 'wizcards', 'creator'],
    'key_map' : {'timeRemaining':'time_remaining', \
                 'created': 'a_created',\
                'wizcards': 'get_member_wizcards',\
                'creator': 'get_creator'}
}

table_template = {
    'fields': ['id', 'tablename', 'secureTable', 'numSitting', \
               'timeout', 'timeRemaining', 'wizcards', 'created', 'creator_id',
               'password'],
    'key_map' : {'created':'a_created',
                 'timeRemaining':'time_remaining',
                 'wizcards': 'get_member_wizcards'}
}

dead_cards_wizcard_template = {
    'fields': ['id', 'first_name', 'last_name', \
               'phone', 'email', 'contact_container'],
    'key_map': {'contact_container': 'get_deadcard_cc'}
}

cctx_wizcard_template = {
    'key_map' : {'wizcard' : 'asset_obj'},
    'related' : {'asset_obj' : wizcard_template_micro}
}
addressbook_template = {
	'fields' : ['id','phone', 'email','name'],
	'key_map' : {'phone' : 'get_all_phones',
		        'email' : 'get_all_emails',
                'name' : 'get_name'}
}
