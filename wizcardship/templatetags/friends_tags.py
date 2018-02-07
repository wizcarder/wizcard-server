from django import template
from django.contrib.auth.models import User
from wizcardship.models import WizConnectionRequest, Wizcard, UserBlocks


register = template.Library()


class AddToWizConnectionsNode(template.Node):
    def __init__(self, target_user, current_user='user',
                       template_name='wizconnections/_add_to.html'):
        self.target_user = template.Variable(target_user)
        self.current_user = template.Variable(current_user)
        self.template_name = template_name

    def render(self, context):
        target_user = self.target_user.resolve(context)
        current_user = self.current_user.resolve(context)
        if current_user.is_authenticated():
            ctx = {'target_user': target_user,
                   'current_user': current_user}
            if not target_user is current_user:
                ctx['are_wizconnections'] = Wizcard.objects.are_wizconnections(
                                                    target_user, current_user)
                ctx['is_invited'] = bool(WizConnectionRequest.objects.filter(
                                                    from_user=current_user,
                                                    to_user=target_user,
                                                    accepted=False).count())
            return template.loader.render_to_string(self.template_name,
                                                    ctx,
                                                    context)
        else:
            return u''


class BlockUserLinkNode(template.Node):
    def __init__(self, target_user, current_user='user',
                       template_name='wizconnections/_block.html'):
        self.target_user = template.Variable(target_user)
        self.current_user = template.Variable(current_user)
        self.template_name = template_name

    def render(self, context):
        target_user = self.target_user.resolve(context)
        current_user = self.current_user.resolve(context)
        if current_user.is_authenticated():
            ctx = {'target_user': target_user,
                   'current_user': current_user}
            if not target_user is current_user:
                ctx['is_blocked'] = bool(UserBlocks.objects.filter(
                         user=current_user, blocks__pk=target_user.pk).count())
            return template.loader.render_to_string(self.template_name,
                                                    ctx,
                                                    context)
        else:
            return u''


def add_to_wizconnections(parser, token):
    bits = token.split_contents()
    tag_name, bits = bits[0], bits[1:]
    if not bits:
        raise template.TemplateSyntaxError(
                           '%s tag requires at least one argument' % tag_name)
    elif len(bits) > 3:
        raise template.TemplateSyntaxError(
                            '%s tag takes at most three arguments' % tag_name)
    if len(bits) == 3:
        if bits[2].startswith('"') and bits[2].endswith('"'):
            bits[2] = bits[2][1:-1]
        else:
            raise template.TemplateSyntaxError(
                      'Third argument for %s tag must be a string' % tag_name)
    return AddToWizConnectionsNode(*bits)


def blocks(value):
    user = _get_user_from_value('wizconnections', value)
    return {
        'applied': User.objects.filter(blocked_by_set__user=user),
        'received': User.objects.filter(user_blocks__blocks=user),
    }


def block_user(parser, token):
    bits = token.split_contents()
    tag_name, bits = bits[0], bits[1:]
    if not bits:
        raise template.TemplateSyntaxError(
                           '%s tag requires at least one argument' % tag_name)
    elif len(bits) > 3:
        raise template.TemplateSyntaxError(
                            '%s tag takes at most three arguments' % tag_name)
    if len(bits) == 3:
        if bits[2].startswith('"') and bits[2].endswith('"'):
            bits[2] = bits[2][1:-1]
        else:
            raise template.TemplateSyntaxError(
                      'Third argument for %s tag must be a string' % tag_name)
    return BlockUserLinkNode(*bits)


def wizconnections(value):
    user = _get_user_from_value('wizconnections', value)
    return Wizcard.objects.wizconnections(user)


def wizconnection_requests(value):
    user = _get_user_from_value('wizconnections', value)
    return {
        'sent': WizConnectionRequest.objects.filter(from_user=user),
        'received': WizConnectionRequest.objects.filter(to_user=user),
    }


def is_blocked_by(value, arg):
    user = _get_user_from_value('isblockedby', value)
    target = _get_user_from_argument('isblockedby', arg)
    return UserBlocks.objects.filter(user=target, blocks=user).exists()


def is_wizconnections_with(value, arg):
    user = _get_user_from_value('iswizconnectionswith', value)
    target = _get_user_from_argument('iswizconnectionswith', arg)
    return Wizcard.objects.are_wizconnections(user, target)


def _get_user(value):
    if isinstance(value, User):
        return value
    elif hasattr(value, 'user') and isinstance(value.user, User):
        return value.user
    else:
        raise ValueError


def _get_user_from_argument(filter_name, arg):
    try:
        return _get_user(arg)
    except ValueError:
        message = '%s filter\'s argument must be a User or ' \
                  'an object with a `user` attribute.' % filter_name
        raise template.TemplateSyntaxError(message)


def _get_user_from_value(filter_name, value):
    try:
        return _get_user(value)
    except ValueError:
        message = '%s filter can only be applied to User\'s or ' \
                  'objects with a `user` attribute.' % filter_name
        raise template.TemplateSyntaxError(message)


register.filter('blocks', blocks)
register.filter('wizconnections', wizconnections)
register.filter('wizconnectionrequests', wizconnection_requests)
register.filter('isblockedby', is_blocked_by)
register.filter('iswizconnectionswith', is_wizconnections_with)
register.tag('addtowizconnections', add_to_wizconnections)
register.tag('blockuser', block_user)
