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
    'fields': ['user_id', 'first_name', 'last_name', 'email', 'address_street1', 'address_city', 'address_state', 'address_country', 'address_zip', 'contact_container'],
    'related':wizcard_related_objects_template
}

wizconnection_template = {
    'fields': ['id', 'wizCardId', 'first_name', 'last_name', 'email', 'address_street1', 'address_city', 'address_state', 'address_country', 'address_zip', 'contact_container'],
    'related':wizcard_related_objects_template,
    'allow_missing': True
}

query_template = { 
    'fields': ['user_id', 'first_name', 'last_name']
}

delete_wizcard_template = {
    'fields': ['id']
}

table_template = {
    'fields': ['id', 'tablename', 'secureTable', 'numSitting']
}
