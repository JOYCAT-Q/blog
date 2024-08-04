from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from djangoblog.utils import get_current_site


# Create your models here.

class BlogUser(AbstractUser):
    nickname = models.CharField(_('nick name'), max_length=100, blank=True)
    creation_time = models.DateTimeField(_('creation time'), default=now)
    last_modify_time = models.DateTimeField(_('last modify time'), default=now)
    source = models.CharField(_('create source'), max_length=100, blank=True)

    def get_absolute_url(self):
        return reverse(
            'blog:author_detail', kwargs={
                'author_name': self.username})

    def __str__(self):
        return self.email

    def get_full_url(self):
        # 当前的站点域名
        site = get_current_site().domain
        # print("site: %s" % site)
        url = "https://{site}{path}".format(site=site,
                                            path=self.get_absolute_url())
        # 当前访问的url路径
        # print("path: %s" % self.get_absolute_url())
        # 拼接的完整域名路径
        # print("URL: %s" % url)
        return url

    class Meta:
        ordering = ['-id']
        verbose_name = _('user')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
