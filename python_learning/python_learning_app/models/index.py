from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin, UserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    #first_name = models.CharField(_("first name"), max_length=150, blank=True)
    #last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"))
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)



    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        #abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class IntroCourse(models.Model):
    TEXT_TYPES = (
        ('heading', '見出し'),
        ('text', 'テキスト'),
        ('red', '赤枠'),
        ('yellow', '黄枠'),
        ('blue', '青枠'),
        ('green', '緑枠'),
        ('img', '画像'))
    
    title = models.CharField(max_length=60,verbose_name="タイトル")
    section = models.PositiveIntegerField(verbose_name="区分")
    order = models.PositiveSmallIntegerField(verbose_name="順番")
    text_type = models.CharField(max_length=20, choices=TEXT_TYPES, verbose_name="タイプ", blank=True)
    content = models.TextField(blank=True, verbose_name="内容")

    def add_title(self):
        if self.text_type == 'heading':
            return str(self.order) + self.content
        elif self.text_type == 'red':
            return str(self.order) + "🟥"
        elif self.text_type == 'yellow':
            return str(self.order) + "🟨"
        elif self.text_type == 'blue':
            return str(self.order) + "🟦"
        elif self.text_type == 'green':
            return str(self.order) + "🟩"
        else:
            return str(self.order)
        
    def __str__(self):
        return self.title + self.add_title()