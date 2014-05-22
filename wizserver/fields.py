user_template = {
    'fields': ['id', 'wizcard']
}

contact_container_template = {
    'fields': ['company', 'title']
}

wizcard_related_objects_template = {
    'contact_container': contact_container_template
}

wizcard_template = {
    'fields': ['wizcard_id', 'user_id', 'first_name', 'last_name', 'phone1', 'email', 'contact_container'],
    'key_map' : {'wizcard_id':'id'},
    'related':wizcard_related_objects_template
}

wizcard_template_thumbnail = {
    'fields': ['wizcard_id', 'user_id', 'first_name', 'last_name', 'phone1', 'email', 'thumbnailImage', 'contact_container'],
    'key_map' : {'wizcard_id':'id'},
    'related':wizcard_related_objects_template
}

flicked_wizcard_related_objects_template = {
    'wizcard': {'fields': ['wizcard_id'], 'key_map': {'wizcard_id':'id'}}
    
}

flicked_wizcard_related_objects_extended_template = {
    'wizcard': wizcard_template
}

flicked_wizcard_template = {
    'fields': ['created', 'wizcard_id', 'flick_id'],
    'key_map': {'flick_id':'id'}
}

flicked_wizcard_extended_template = {
    'fields': ['created', 'flick_id', 'wizcard'],
    'key_map': {'flick_id':'id'},
    'related': flicked_wizcard_related_objects_extended_template
}

user_query_template = { 
    'fields': ['user_id', 'first_name', 'last_name', 'wizcard'],
    'merge': True,
    'related':wizcard_related_objects_template,
    'key_map' : {'user_id':'id'}
}

user_query_extended_template = { 
    'fields': ['user_id', 'wizcard'],
    'related': {
        'wizcard': wizcard_template,
        'merge':True
    },
    'key_map' : {'user_id':'id'}
}

wizcard_user_query_template = { 
    'fields': ['user_id', 'first_name', 'last_name']
}

delete_wizcard_template = {
    'fields': ['id']
}

table_template = {
    'fields': ['id', 'tablename', 'secureTable', 'numSitting', 'creator_id']
}
