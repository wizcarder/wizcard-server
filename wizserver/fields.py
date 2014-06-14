contact_container_template = {
    'fields': ['company', 'title', 'start', 'end', 'f_bizCardImage']
}

wizcard_related_objects_template = {
    'contact_container': contact_container_template
}

wizcard_template_brief_merged = {
    'fields': ['wizcard_id', 'user_id', 'first_name', 'last_name', 'phone', 'email', 'company', 'title'],
    'key_map' : {'wizcard_id':'id'},
    'merge': True
}

wizcard_template_brief = {
    'fields': ['wizcard_id', 'user_id', 'first_name', 'last_name', 'phone', 'email', 'company', 'title'],
    'key_map' : {'wizcard_id':'id'},
}

thumbnail_fields = wizcard_template_brief['fields'] + ['thumbnailImage']

wizcard_template_brief_with_thumbnail = {
    'fields': thumbnail_fields,
    'key_map' : wizcard_template_brief['key_map'],
}

extended_fields = wizcard_template_brief_with_thumbnail['fields'] + ['contact_container']
wizcard_template_extended = {
    'fields': extended_fields,
    'key_map' : wizcard_template_brief['key_map'],
    'related': wizcard_related_objects_template
}

flicked_wizcard_related_objects_template = {
    'wizcard': wizcard_template_brief,
}

flicked_wizcard_related_objects_merged_template = {
    'wizcard': wizcard_template_brief_merged
}

flick_pickers_template = {
    'fields': ['id'],
    'merge': True,
    'values_list': True
}

flicked_wizcard_template = {
    'fields': ['created', 'flick_id', 'wizcard'],
    'key_map': {'flick_id':'id'},
    'related': flicked_wizcard_related_objects_template
}

flicked_wizcard_merged_template = {
    'fields': ['created', 'flick_id', 'wizcard', 'tag'],
    'key_map': {'flick_id':'id', 'tag': 'get_tag'},
    'related': flicked_wizcard_related_objects_merged_template
}

flicked_wizcard_merged_template_own = {
    'fields': ['created', 'flick_id', 'wizcard', 'tag'],
    'key_map': {'flick_id':'id', 'tag': lambda: "own"},
    'related': flicked_wizcard_related_objects_merged_template
}

my_flicked_wizcard_template = {
    'fields': ['created', 'flick_id', 'lat', 'lng', 'lifetime', 'flick_pickers'],
    'key_map': {'flick_id':'id'},
    'related': {
        'flick_pickers': flick_pickers_template,
        'merge': True
    }
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

table_merged_template = {
    'fields': ['id', 'tablename', 'secureTable', 'numSitting', 'tag'],
    'key_map' : {'tag':'get_tag'}
}
