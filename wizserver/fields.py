contact_container_template = {
    'fields': ['company', 'title', 'start', 'end']
}

contact_container_template_with_bizcard = {
    'fields': ['company', 'title', 'start', 'end', 'f_bizCardImage']
}

wizcard_related_objects_template = {
    'contact_container': contact_container_template
}

wizcard_related_objects_template_with_bizcard = {
    'contact_container': contact_container_template_with_bizcard
}

wizcard_template_brief = {
    'fields': ['wizcard_id', 'user_id', 'first_name', 'last_name', 'phone', \
            'email', 'company', 'title'],
    'key_map' : {'wizcard_id':'id', 'company':'get_latest_company', 'title':\
            'get_latest_title'},
}

thumbnail_fields = wizcard_template_brief['fields'] + ['thumbnailImage']
wizcard_template_brief_with_thumbnail = {
    'fields': thumbnail_fields,
    'key_map' : wizcard_template_brief['key_map'],
}

extended_fields = wizcard_template_brief['fields'] + ['contact_container']
extended_fields_with_images = extended_fields + ['thumbnailImage']

wizcard_template_extended = {
    'fields': extended_fields,
    'key_map' : wizcard_template_brief['key_map'],
    'related': wizcard_related_objects_template
}

wizcard_template_full = {
    'fields': extended_fields_with_images,
    'key_map' : wizcard_template_brief['key_map'],
    'related': wizcard_related_objects_template_with_bizcard
}

wizcard_template_brief_merged = {
    'fields': wizcard_template_brief['fields'],
    'key_map' : wizcard_template_brief['key_map'],
    'merge' : True
}

wizcard_template_brief_with_thumbnail_merged = {
    'fields': thumbnail_fields,
    'key_map' : wizcard_template_brief['key_map'],
    'merge' : True
}

flicked_wizcard_related_objects_template= {
    'wizcard': wizcard_template_brief,
}

flicked_wizcard_related_objects_template_with_thumbnail= {
    'wizcard': wizcard_template_brief_with_thumbnail,
}

flicked_wizcard_related_objects_merged_template = {
    'wizcard': wizcard_template_brief_merged
}

flicked_wizcard_related_objects_merged_template_with_thumbnail = {
    'wizcard': wizcard_template_brief_with_thumbnail_merged
}

flick_pickers_template = {
    'fields': ['id'],
    'merge': True,
    'values_list': True
}

flicked_wizcard_template = {
    'fields': ['created', 'timeRemaining', 'flick_id', 'wizcard'],
    'key_map': {'created':'a_created', 'timeRemaining':'time_remaining', 'flick_id':'id'},
    'related': flicked_wizcard_related_objects_template
}

flicked_wizcard_template_with_thumbnail = {
    'fields': ['created', 'timeRemaining', 'flick_id', 'wizcard'],
    'key_map': {'created':'a_created', 'timeRemaining':'time_remaining', 'flick_id':'id'},
    'related': flicked_wizcard_related_objects_template_with_thumbnail
}

flicked_wizcard_merged_template = {
    'fields': ['created', 'timeout', 'flick_id', 'wizcard', 'tag'],
    'key_map': {'created': 'a_created', 'flick_id':'id', 'tag': 'get_tag' },
    'related': flicked_wizcard_related_objects_merged_template
}

flicked_wizcard_merged_template_with_thumbnail = {
    'fields': flicked_wizcard_merged_template['fields'],
    'key_map': {'created': 'a_created', 'flick_id':'id', 'tag': 'get_tag' },
    'related': flicked_wizcard_related_objects_merged_template_with_thumbnail
}
my_flicked_wizcard_template = {
    'fields': ['created', 'timeout', 'flick_id', 'lat', 'lng', 'timeout', \
            'flick_pickers'],
    'key_map': {'created':'a_created', 'flick_id':'id'},
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
    'fields': ['id', 'tablename', 'secureTable', 'password', 'numSitting', \
            'creator_id', 'created', 'timeRemaining'],
    'key_map' : {'created':'a_created', 'timeRemaining':'time_remaining'}
}

table_merged_template = {
    'fields': ['id', 'tablename', 'secureTable', 'password', 'numSitting', \
            'creator_id', 'created', 'timeRemaining', 'tag'],
    'key_map' : {'created':'a_created', 'timeRemaining':'time_remaining', 'tag':'get_tag'}
}

dead_cards_response_template = {
    'fields': ['id', 'company', 'email', 'first_name', 'last_name', \
            'title', 'web', 'company'],
}

