contact_container_template = {
    'fields': ['company', 'title', 'start', 'end']
}

wizcard_related_objects_template = {
    'contact_container': contact_container_template
}

wizcard_template_brief = {
    'fields': ['wizcard_id', 'user_id', 'first_name', 'last_name', 'phone', 'email'],
    'key_map' : {'wizcard_id':'id'},
    'related':wizcard_related_objects_template
}

thumbnail_fields = wizcard_template_brief['fields'] + ['thumbnailImage']

wizcard_template_brief_with_thumbnail = {
    'fields': thumbnail_fields,
    'key_map' : wizcard_template_brief['key_map'],
    'related': wizcard_template_brief['related']
}

extended_fields = thumbnail_fields + ['contact_container']
wizcard_template_extended = {
    'fields': extended_fields,
    'key_map' : wizcard_template_brief['key_map'],
    'related': wizcard_template_brief['related']
}

flicked_wizcard_related_objects_template = {
    'wizcard': wizcard_template_brief,
    'merge': True
}

flicked_wizcard_template = {
    'fields': ['created', 'flick_id', 'wizcard'],
    'key_map': {'flick_id':'id'},
    'related': flicked_wizcard_related_objects_template
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
        'wizcard': wizcard_template_brief,
        'merge':True
    },
    'key_map' : {'user_id':'id'}
}

table_template = {
    'fields': ['id', 'tablename', 'secureTable', 'numSitting', 'creator_id']
}
