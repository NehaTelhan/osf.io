from django.contrib import messages
from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.views.generic import FormView
from django.views.defaults import page_not_found

from admin.common_auth.models import MyUser
from admin.base.forms import GuidForm


@login_required
def home(request):
    context = {}
    return render(request, 'home.html', context)


def password_reset_done(request, **kwargs):
    messages.success(request, 'You have successfully reset your password and activated your admin account. Thank you')
    return redirect('auth:login')


def password_reset_confirm_custom(request, **kwargs):
    response = views.password_reset_confirm(request, **kwargs)
    # i.e. if the user successfully resets their password
    if response.status_code == 302:
        try:
            uid = urlsafe_base64_decode(kwargs['uidb64'])
            user = MyUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
            pass
        else:
            user.confirmed = True
            user.save()
    return response


class GuidFormView(FormView):
    form_class = GuidForm
    template_name = None
    object_type = None

    def get_guid_object(self):
        raise NotImplementedError

    def __init__(self):
        self.guid = None
        super(GuidFormView, self).__init__()

    def get(self, request, *args, **kwargs):
        try:
            return super(GuidFormView, self).get(request, args, kwargs)
        except AttributeError:
            return page_not_found(self.request)

    def get_context_data(self, **kwargs):
        self.guid = self.request.GET.get('guid', None)
        guid_object = None
        if self.guid is not None:
            try:
                guid_object = self.get_guid_object()
            except AttributeError:
                raise
        kwargs.setdefault('view', self)
        kwargs.setdefault('form', self.get_form())
        kwargs.setdefault('guid_object', guid_object)
        return kwargs

    def form_valid(self, form):
        self.guid = form.cleaned_data.get('guid').strip()
        return super(GuidFormView, self).form_valid(form)

    @property
    def success_url(self):
        raise NotImplementedError
