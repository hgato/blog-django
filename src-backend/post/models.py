from django.db import models
from django.utils import timezone

from authorization.models import User


class StatusMixIn:
    ACTIVE = 'AC'
    PENDING = 'PD'
    DELETED = 'DL'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (PENDING, 'Pending'),
        (DELETED, 'Deleted'),
    ]


class Post(models.Model, StatusMixIn):
    name = models.CharField(max_length=300)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=StatusMixIn.STATUS_CHOICES, default=StatusMixIn.PENDING)

    def _check_new_text(self) -> bool:
        return self.pk \
                and getattr(self, 'old_name', None) != self.name \
                and getattr(self, 'old_text', None) != self.text

    def _save_old_version(self):
        if self._check_cannot_create_old_version():
            raise Exception('Use "update" method to save existing model')

        old_post = OldPost(name=self.old_name,
                           text=self.old_text,
                           author=self.old_author,
                           date=self.old_date)
        old_post.save()

    def _check_cannot_create_old_version(self) -> bool:
        return not hasattr(self, 'old_name') or\
                not hasattr(self, 'old_text') or\
                not hasattr(self, 'old_author') or\
                not hasattr(self, 'old_date')

    def update(self, name: str, text: str):
        self.old_name = self.name
        self.old_text = self.text
        self.old_author = self.author
        self.old_date = self.date

        if name:
            self.name = name
        if text:
            self.text = text

        self.date = timezone.now()
        self.save()
        self._save_old_version()

    def make_delete(self):
        self.status = StatusMixIn.DELETED
        self.save()

    def serialize(self) -> dict:
        return {
            'id': self.pk,
            'text': self.text,
            'name': self.name,
            'author': {
                'first_name': self.author.first_name,
                'last_name': self.author.last_name,
                'id': self.author.id,
            },
            'date': self.date,
        }


class OldPost(models.Model):
    name = models.CharField(max_length=300)
    text = models.TextField()
    date = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
