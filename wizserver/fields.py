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
    'fields': ['wizcard_id', 'user_id', 'first_name', 'last_name', 'phone', 'email', 'company', 'title'],
    'key_map' : {'wizcard_id':'id', 'company':'get_latest_company', 'title':'get_latest_title'},
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

wizcard_template_extended_with_images = {
    'fields': extended_fields_with_images,
    'key_map' : wizcard_template_brief['key_map'],
    'related': wizcard_related_objects_template_with_bizcard
}

wizcard_template_brief_with_thumbnail_merged = wizcard_template_brief_with_thumbnail.copy()
wizcard_template_brief_with_thumbnail_merged['merge'] = True

wizcard_template_extended_with_bizcard = {
    'fields': extended_fields,
    'key_map' : wizcard_template_brief['key_map'],
    'related': wizcard_related_objects_template_with_bizcard
}
flicked_wizcard_related_objects_template = {
    'wizcard': wizcard_template_brief_with_thumbnail,
}

flicked_wizcard_related_objects_merged_template = {
    'wizcard': wizcard_template_brief_with_thumbnail_merged
}

flick_pickers_template = {
    'fields': ['id'],
    'merge': True,
    'values_list': True
}

flicked_wizcard_template = {
    'fields': ['created', 'timeout', 'flick_id', 'wizcard'],
    'key_map': {'created':'a_created', 'flick_id':'id'},
    'related': flicked_wizcard_related_objects_template
}

flicked_wizcard_merged_template = {
    'fields': ['created', 'timeout', 'flick_id', 'wizcard', 'tag'],
    'key_map': {'created': 'a_created', 'flick_id':'id', 'tag': 'get_tag' },
    'related': flicked_wizcard_related_objects_merged_template
}

flicked_wizcard_merged_template_own = {
    'fields': ['created', 'timeout', 'flick_id', 'wizcard', 'tag'],
    'key_map': {'created':'a_created', 'flick_id':'id', 'tag': lambda: "own"},
    'related': flicked_wizcard_related_objects_merged_template
}

my_flicked_wizcard_template = {
    'fields': ['created', 'timeout', 'flick_id', 'lat', 'lng', 'timeout', 'flick_pickers'],
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
    'fields': ['id', 'tablename', 'secureTable', 'password', 'numSitting', 'creator_id', 'created', 'timeout'],
    'key_map' : {'created':'a_created'}
}

table_merged_template = {
    'fields': ['id', 'tablename', 'secureTable', 'password', 'numSitting', 'creator_id', 'created', 'timeout', 'tag'],
    'key_map' : {'created':'a_created', 'tag':'get_tag'}
}
