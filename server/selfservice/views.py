import re

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.urls import reverse
from django.forms import widgets

from gandalf.decorators import (
    superuser_or_bearer_required,
    is_superuser_or_bearer,
)

from .forms import TabledCheckboxSelectMultiple

from django.conf import settings

import logging
import json
import sys

from members.models import User
from acl.models import Machine, Entitlement, PermitType
from selfservice.forms import (
    UserForm,
    SignalNotificationSettingsForm,
    EmailNotificationSettingsForm,
)


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.email)


email_check_token = AccountActivationTokenGenerator()
logger = logging.getLogger(__name__)


def index(request):
    context = {
        "has_permission": request.user.is_authenticated,
        "title": "Selfservice",
        "user": request.user,
    }
    if request.user.is_authenticated:
        context["is_logged_in"] = request.user.is_authenticated
        context["member"] = request.user

    return render(request, "index.html", context)


@login_required
def pending(request):
    pending = (
        Entitlement.objects.all().filter(active=False).filter(holder__is_active=True)
    )

    es = []
    for p in pending:
        es.append((p.id, p))

    form = forms.Form(request.POST)
    form.fields["entitlement"] = forms.MultipleChoiceField(
        label="Entitlements",
        choices=es,
        widget=widgets.SelectMultiple(attrs={"size": len(es)}),
    )
    context = {
        "title": "Pending entitlements",
        "user": request.user,
        "has_permission": request.user.is_authenticated,
        "pending": pending,
        "lst": es,
        "form": form,
    }
    if request.method == "POST" and form.is_valid():
        if not request.user.is_staff:
            return HttpResponse(
                "You are propably not an admin ?", status=403, content_type="text/plain"
            )

        for eid in form.cleaned_data["entitlement"]:
            e = Entitlement.objects.get(pk=eid)
            e.active = True
            e.changeReason = (
                "Activated through the self-service interface by {0}".format(
                    request.user
                )
            )
            e.save()
        context["saved"] = True

    return render(request, "pending.html", context)


@login_required
def recordinstructions(request):
    member = request.user

    # keep the option open to `do bulk adds
    members = User.objects.filter(is_active=True)
    machines = Machine.objects.all().exclude(requires_permit=None)

    # TODO: switch this to showing Permits rather than Machines

    # Only show machine we are entitled for ourselves.
    #
    if not request.user.is_privileged:
        machines = machines.filter(
            Q(requires_permit__permit=None)
            | Q(requires_permit__permit__isRequiredToOperate__holder=member)
        )
        members = members.exclude(id=member.id)  # .order_by('first_name')

    ps = []
    for m in members:
        ps.append((m.id, m.first_name + " " + m.last_name))

    ms = []
    for m in machines.order_by("name"):
        ms.append((m.id, m.name))

    form = forms.Form(request.POST)  # machines, members)
    form.fields["machine"] = forms.MultipleChoiceField(
        label="Machine",
        choices=ms,
        help_text="Select multiple if so desired",
        widget=TabledCheckboxSelectMultiple(),
    )
    form.fields["persons"] = forms.MultipleChoiceField(
        label="Person", choices=ps, help_text="Select multiple if so desired"
    )

    if request.user.is_privileged:
        form.fields["issuer"] = forms.ChoiceField(label="Issuer", choices=ps)

    context = {
        "machines": machines,
        "members": members,
        "title": "Selfservice - record instructions",
        "is_logged_in": request.user.is_authenticated,
        "user": request.user,
        "has_permission": True,
        "form": form,
        "lst": ms,
    }

    saved = False
    if request.method == "POST" and form.is_valid():
        context["machines"] = []
        context["holder"] = []

        for mid in form.cleaned_data["machine"]:
            try:
                m = Machine.objects.get(pk=mid)
                if request.user.is_privileged and form.cleaned_data["issuer"]:
                    i = User.objects.get(pk=form.cleaned_data["issuer"])
                else:
                    i = user = request.user

                pt = None
                if m.requires_permit:
                    pt = PermitType.objects.get(pk=m.requires_permit.id)

                if pt == None:
                    logger.error(f"{m} skipped - no permit - bug ?")
                    continue

                for pid in form.cleaned_data["persons"]:
                    p = User.objects.get(pk=pid)

                    # Note: We allow for 'refreshers' -- and rely on the history record.
                    #
                    created = False
                    try:
                        record = Entitlement.objects.get(permit=pt, holder=p)
                        record.issuer = i
                        record.changeReason = (
                            "Updated through the self-service interface by {0}".format(
                                i
                            )
                        )
                    except Entitlement.DoesNotExist:
                        record = Entitlement(permit=pt, holder=p, issuer=i)
                        created = True
                        record.changeReason = (
                            "Created in the self-service interface by {0}".format(i)
                        )
                    except Exception as e:
                        logger.error(
                            "Something else went wrong during create: {0}".format(e)
                        )
                        return HttpResponse(
                            "Something went wrong. Could not understand this update. Sorry.",
                            status=500,
                            content_type="text/plain",
                        )

                    record.active = not pt.require_ok_trustee
                    try:
                        record.save(request=request)
                        context["holder"].append(p)
                    except Exception as e:
                        logger.error("Updating of instructions failed: {0}".format(e))
                        return HttpResponse(
                            "Something went wrong. Could not record these instructions. Sorry.",
                            status=500,
                            content_type="text/plain",
                        )

                context["created"] = created
                context["machines"].append(m)
                context["issuer"] = i

                saved = True
            # except Exception as e:
            except Entitlement.DoesNotExist as e:
                exc_type, exc_obj, tb = sys.exc_info()
                f = tb.tb_frame
                lineno = tb.tb_lineno
                filename = f.f_code.co_filename

                logger.error(
                    "Unexpected error during save of intructions:: {} at {}:{}".format(
                        filename, lineno, e
                    )
                )
                return HttpResponse(
                    "Something went wrong. Could not undertand these instructions. Sorry.",
                    status=500,
                    content_type="text/plain",
                )

    context["saved"] = saved
    return render(request, "record.html", context)


@login_required
def confirmemail(request, uidb64, token, newemail):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if request.user != user:
            return HttpResponse(
                "You can only change your own records.",
                status=500,
                content_type="text/plain",
            )
        email = user.email
        user.email = newemail
        if email_check_token.check_token(user, token):
            user.email = newemail
            user.email_confirmed = True
            user.save()
        else:
            return HttpResponse(
                "Failed to confirm", status=500, content_type="text/plain"
            )

        logger.debug(
            "Change of email from '{}' to '{}' confirmed.".format(email, newemail)
        )
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        # We perhaps should not provide the end user with feedback -- e.g. prentent all
        # went well. As we do not want to function as an oracle.
        #
        logger.error("Something else went wrong in confirm email: {0}".format(e))
        HttpResponse(
            "Something went wrong. Sorry.", status=500, content_type="text/plain"
        )

    # return redirect('userdetails')
    return render(request, "email_verification_ok.html")


@login_required
def confirm_waiver(request, user_id=None):
    try:
        operator_user = request.user
    except User.DoesNotExist:
        return HttpResponse(
            "You are probably not a member-- admin perhaps?",
            status=400,
            content_type="text/plain",
        )

    try:
        member = User.objects.get(pk=user_id)
    except ObjectDoesNotExist as e:
        return HttpResponse("User not found", status=404, content_type="text/plain")

    if not operator_user.is_staff:
        return HttpResponse(
            "You must be staff to confirm a waiver",
            status=400,
            content_type="text/plain",
        )

    member.form_on_file = True
    member.save()

    return render(request, "waiver_confirmation.html", {"member": member})


@login_required
def userdetails(request):
    try:
        member = request.user
        old_email = "{}".format(member.email)
    except User.DoesNotExist:
        return HttpResponse(
            "You are probably not a member-- admin perhaps?",
            status=500,
            content_type="text/plain",
        )

    if request.method == "POST":
        try:
            user = UserForm(request.POST, request.FILES, instance=request.user)
            save_user = user.save(commit=False)
            if user.is_valid():
                new_email = "{}".format(user.cleaned_data["email"])

                save_user.email = old_email
                save_user.changeReason = (
                    "Updated through the self-service interface by {0}".format(
                        request.user
                    )
                )
                save_user.save()

                user = UserForm(request.POST, instance=save_user)
                for f in user.fields:
                    user.fields[f].disabled = True

                if old_email != new_email:
                    member.email_confirmed = False
                    member.changeReason = "Reset email validation, email changed."
                    member.save()
                    send_email_verification(request, save_user, new_email, old_email)
                    return render(request, "email_verification_email.html")

                return render(
                    request, "userdetails.html", {"form": user, "saved": True}
                )
        except Exception as e:
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename

            logger.error(
                "Unexpected error during save of user '{}' : {} at {}:{}".format(
                    request.user, filename, lineno, e
                )
            )
            return HttpResponse(
                "Unexpected error during save of userdetails (does the phone number start with a +<country code>?)",
                status=500,
                content_type="text/plain",
            )

    form = UserForm(instance=request.user)
    context = {
        "title": "Selfservice - update details",
        "is_logged_in": request.user.is_authenticated,
        "user": request.user,
        "form": form,
        "has_permission": True,
    }
    return render(request, "userdetails.html", context)


class AmnestyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        machines = kwargs.pop("machines")
        super(AmnestyForm, self).__init__(*args, **kwargs)
        for m in machines:
            self.fields["machine_%s" % m.id] = forms.BooleanField(
                label=m.name, required=False
            )


@login_required
def amnesty(request):
    machines = Machine.objects.exclude(requires_permit=None)
    machines_entitled = Machine.objects.all().filter(
        requires_permit__isRequiredToOperate__holder=request.user
    )

    context = {"title": "Amnesty", "saved": False}

    form = AmnestyForm(request.POST or None, machines=machines)
    if form.is_valid():
        permits = []
        for m in machines:
            if not form.cleaned_data["machine_%s" % m.id]:
                continue
            if m in machines_entitled:
                continue
            if not m.requires_permit or m.requires_permit in permits:
                continue
            permits.append(m.requires_permit)
        for p in permits:
            e, created = Entitlement.objects.get_or_create(
                holder=request.user, issuer=request.user, permit=p
            )
            if created:
                e.changeReason = (
                    "Added through the grant amnesty interface by {0}".format(
                        request.user
                    )
                )
                e.active = True
                e.save()
                context["saved"] = True
            # return redirect('userdetails')

    for m in machines_entitled:
        form.fields["machine_%s" % m.id].initial = True
        form.fields["machine_%s" % m.id].disabled = True
        form.fields[
            "machine_%s" % m.id
        ].help_text = "Already listed - cannot be edited."

    context["form"] = form

    return render(request, "amnesty.html", context)
