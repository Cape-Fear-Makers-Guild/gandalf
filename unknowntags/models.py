from django.conf import settings
from django.db import models
import datetime

class Unknowntag(models.Model):
   tag = models.CharField(max_length=30) 
   last_used = models.DateTimeField(auto_now=True)

   def save(self, * args, ** kwargs):
      r = super(Unknowntag,self).save(*args, **kwargs)

      stale_tags = Unknowntag.objects.all().order_by('-last_used')[settings.UT_COUNT_CUTOFF:]

      for stale_tag in stale_tags:
          stale_tag.delete()

      return r

   def __str__(self):
         return "{} swiped on {}".format(self.tag, self.last_used.strftime("%Y-%m-%d %H:%M:%S"))

   def reassing_to_user(self, user, admin, activate = False):
      newtag = Tag.objects.create(tag=tag.tag, owner = user,
                 description="The card that was added on {} by {} ".format(datetime.date.today(), admin))
      newtag.changeReason = "Moved from the unknown tags list by {} to this user.".format(admin)
      newtag.save()

      self.changeReason = "Reassigned to user {} by {}".format(user,admin)
      self.delete()

      if activate:
             doors= PermitType.objects.get(pk=settings.DOORS)
             e,created = Entitlement.objects.get_or_create(active=True, permit = doors, holder = user, issuer = admin)
             if created:
                  e.changeReason = "Auto created during reasign of what was an unknown tag to {} by {}".format(user,admin)
                  e.save()

      return newtag
