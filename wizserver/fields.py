

dead_cards_wizcard_template = {
    'fields': ['id', 'first_na'
                     'me', 'last_name',
               'phone', 'email', 'invited', 'contact_container', 'context'],
    'key_map': {
        'contact_container': 'get_deadcard_cc',
        'context': 'get_deadcard_context'
    },
}

addressbook_template = {
    'fields': ['id', 'phone', 'email', 'name'],
    'key_map': {
        'phone': 'get_all_phones',
        'email': 'get_all_emails',
        'name': 'get_name'
    }
}
