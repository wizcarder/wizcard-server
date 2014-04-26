from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from cards.models import WizConnectionRequest, Wizcard, UserBlocks
from cards.templatetags import friends_tags


class BaseTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        for i in range(1, 5):
            setattr(self, 'user%d' % i,
                                  User.objects.get(username='testuser%d' % i))


class BlocksFilterTestCase(BaseTestCase):
    def test_blocks_filter(self):
        result = friends_tags.blocks(self.user4)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('applied' in result)
        self.assertEqual(len(result['applied']), 2)
        self.assertTrue(self.user1 in result['applied'])
        self.assertTrue(self.user3 in result['applied'])
        self.assertTrue('received' in result)
        self.assertEqual(len(result['received']), 2)
        self.assertTrue(self.user1 in result['received'])
        self.assertTrue(self.user2 in result['received'])


class CardsFilterTestCase(BaseTestCase):
    def test_cards_filter(self):
        result = friends_tags.cards_(self.user1)
        self.assertEqual(len(result), 1)
        self.assertTrue(self.user2 in result)


class WizcardModelsTestCase(BaseTestCase):
    def test_wizconnection_request(self):
        are_wizconnections = Wizcard.objects.are_wizconnections
        for method, result in [('decline', False),
                               ('cancel', False),
                               ('accept', True)]:
            wizconnection_request = WizConnectionRequest.objects.create(
                                     from_user=self.user3, to_user=self.user4)
            self.assertEqual(are_wizconnections(self.user3, self.user4), False)
            getattr(wizconnection_request, method)()
            self.assertEqual(are_wizconnections(self.user3, self.user4), result)

    def test_wizconnection_manager_query_methods(self):
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user1,
                                                        self.user2), True)
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user1,
                                                        self.user3), False)
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user2,
                                                        self.user3), False)
        wizconnections_of = Wizcard.objects.wizconnections_of(self.user1)
        wizconnections_of = Wizcard.objects.wizconnections_of(self.user2)
        wizconnections_of = Wizcard.objects.wizconnections_of(self.user3)
        self.assertEqual(list(wizconnections_of), [self.user2])
        self.assertEqual(list(wizconnections_of), [self.user1])
        self.assertEqual(list(wizconnections_of), [])

    def test_wizconnection_manager_becard(self):
        Wizcard.objects.becard(self.user1, self.user4)
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user1,
                                                        self.user4), True)

    def test_wizconnection_manager_uncard(self):
        Wizcard.objects.uncard(self.user1, self.user2)
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user1,
                                                        self.user2), False)


class WizConnectionRequestsFilterTestCase(BaseTestCase):
    def test_wizconnection_requests_filter(self):
        WizConnectionRequest.objects.create(from_user=self.user1,
                                         to_user=self.user3)
        WizConnectionRequest.objects.create(from_user=self.user4,
                                         to_user=self.user1)
        result = friends_tags.wizconnection_requests(self.user1)
        # result['sent'] shouldn't contain user2 because they're already cards_
        # result = {
        #     'sent': [user3],
        #     'received': [user4],
        # }
        raise AssertionError


class WizcardViewsTestCase(BaseTestCase):
    urls = 'cards.urls'

    def test_wizconnection_request(self):
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('wizconnection_request', args=('testuser3',)))
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user1,
                                                        self.user3), False)
        self.assertEqual(WizConnectionRequest.objects.filter(from_user=self.user1,
                               to_user=self.user3, accepted=False).count(), 1)

    def test_wizconnection_accept(self):
        WizConnectionRequest.objects.create(from_user=self.user1,
                                         to_user=self.user3)
        self.client.login(username='testuser3', password='testuser3')
        self.client.get(reverse('wizconnection_accept', args=('testuser1',)))
        self.assertEqual(WizConnectionRequest.objects.filter(
                                                   accepted=True).count(), 2)
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user1,
                                                        self.user3), True)

    def test_wizconnection_cancel(self):
        WizConnectionRequest.objects.create(from_user=self.user1,
                                         to_user=self.user3)
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('wizconnection_cancel', args=('testuser3',)))
        self.assertEqual(WizConnectionRequest.objects.filter(
                                                   accepted=False).count(), 0)
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user1,
                                                        self.user3), False)

    def test_wizconnection_decline(self):
        WizConnectionRequest.objects.create(from_user=self.user1,
                                         to_user=self.user3)
        self.client.login(username='testuser3', password='testuser3')
        self.client.get(reverse('wizconnection_decline', args=('testuser1',)))
        self.assertEqual(WizConnectionRequest.objects.filter(
                                                   accepted=False).count(), 0)
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user1,
                                                        self.user3), False)

    def test_wizconnection_delete(self):
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('wizconnection_delete', args=('testuser2',)))
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user1,
                                                        self.user2), False)

    def test_wizconnection_mutual_request(self):
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('wizconnection_request', args=('testuser3',)))
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user1,
                                                        self.user3), False)
        self.client.login(username='testuser3', password='testuser3')
        self.client.get(reverse('wizconnection_request', args=('testuser1',)))
        self.assertEqual(WizConnectionRequest.objects.filter(from_user=self.user1,
                                to_user=self.user3, accepted=True).count(), 1)
        self.assertEqual(Wizcard.objects.are_wizconnections(self.user1,
                                                        self.user3), True)


class UserBlockTestCase(BaseTestCase):
    def test_blocking_info_methods(self):
        self.user1.user_blocks.blocks.add(self.user3, self.user4)
        self.assertEqual(self.user1.user_blocks.block_count(), 2)
        summary = UserBlocks.objects.get(user=self.user1).block_summary()
        self.assertEqual(self.user3.username in summary, True)
        self.assertEqual(self.user4.username in summary, True)


class UserBlocksViewsTestCase(BaseTestCase):
    urls = 'cards.urls'

    def test_block(self):
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('user_block', args=('testuser2',)))
        self.assertEqual(self.user2 in self.user1.user_blocks.blocks.all(),
                                                                         True)

    def test_unblock(self):
        self.user1.user_blocks.blocks.add(self.user2)
        self.client.login(username='testuser1', password='testuser1')
        self.client.get(reverse('user_unblock', args=('testuser2',)))
        self.assertEqual(self.user2 in self.user1.user_blocks.blocks.all(),
                                                                        False)
