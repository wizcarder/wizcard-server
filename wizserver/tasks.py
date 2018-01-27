from celery import task
from lib import wizlib
import logging
from userprofile.models import AB_Candidate_Phones, AB_Candidate_Emails, AB_Candidate_Names, AB_User, AddressBook

logger = logging.getLogger(__name__)


@task(ignore_result=True)
def contacts_upload_task(user, int_prefix, country_code, ab_list):
    emailEntryList = []
    phoneEntryList = []

    for ab_entry in ab_list:
        do_email = False
        do_phone = False

        if  'name' not in ab_entry:
            continue
        name = ab_entry.get('name')
        first_name, last_name = wizlib.split_name(name)

        if 'phone' in ab_entry:
            phone_list = list(set([wizlib.clean_phone_number(x, int_prefix, country_code)
                                   for x in ab_entry.get('phone') if wizlib.is_valid_phone(x, country_prefix=country_code)]))
            if len(phone_list):
                do_phone = True
            try:
                phoneEntryList = list(set([AB_Candidate_Phones.objects.get(phone=x)
                                           for x in phone_list if AB_Candidate_Phones.objects.filter(phone=x).exists()]))
            except:
                logger.error('duplicate phone already in db %s', x)
                continue
        if 'email' in ab_entry:
            email_list = list(set([x.lower() for x in ab_entry.get('email') if wizlib.is_valid_email(x)]))
            if len(email_list):
                do_email = True

            try:
                emailEntryList = [AB_Candidate_Emails.objects.get(email=x)
                                  for x in email_list if AB_Candidate_Emails.objects.filter(email=x).exists()]
            except:
                logger.error('duplicate email already in db %s', x)
                continue
        if not do_email and not do_phone:
            continue

        if not len(emailEntryList) and not len(phoneEntryList):
            # brand new. create AB model instance and mapping to user
            abEntry = AddressBook.objects.create(
                first_name=first_name,
                last_name=last_name
            )
            AB_Candidate_Names.objects.create(
                first_name=first_name,
                last_name=last_name,
                ab_entry=abEntry)

            if do_email:
                for email in email_list:
                    AB_Candidate_Emails.objects.create(email=email, ab_entry=abEntry)
            if do_phone:
                for phone in phone_list:
                    AB_Candidate_Phones.objects.create(phone=phone, ab_entry=abEntry)

            # join table
            AB_User.objects.get_or_create(user=user, ab_entry=abEntry)
        elif len(emailEntryList) and len(phoneEntryList):
            # ideally all should point to the same ABEntry
            l1 = set([x.ab_entry for x in emailEntryList])
            l2 = set([y.ab_entry for y in phoneEntryList])

            try:
                # if valid intersection
                abEntry = list(l1&l2)[0]
            except:
                continue

            AB_User.objects.get_or_create(user=user, ab_entry=abEntry)

            if not (abEntry.first_name_finalized or abEntry.last_name_finalized):
                # add to candidate list
                AB_Candidate_Names.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    ab_entry=abEntry
                )
        elif len(emailEntryList):
            abEntry = wizlib.most_common([x.ab_entry for x in emailEntryList])[0]
            if do_phone:
                for phone in phone_list:
                    AB_Candidate_Phones.objects.create(
                        phone=phone,
                        ab_entry=abEntry)

            if not (abEntry.first_name_finalized and abEntry.last_name_finalized):
                # add to candidate list
                AB_Candidate_Names.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    ab_entry=abEntry)

            AB_User.objects.get_or_create(user=user, ab_entry=abEntry)
        else:
            # found phone
            abEntry = wizlib.most_common([x.ab_entry for x in phoneEntryList])[0]
            if do_email:
                for email in email_list:
                    AB_Candidate_Emails.objects.create(
                        email=email,
                        ab_entry=abEntry)

            if not (abEntry.first_name_finalized and abEntry.last_name_finalized):
                # add to candidate list
                AB_Candidate_Names.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    ab_entry=abEntry)

            AB_User.objects.get_or_create(user=user, ab_entry=abEntry)

        # run a candidate selection for the ab_entry
        abEntry.run_finalize_decision()
