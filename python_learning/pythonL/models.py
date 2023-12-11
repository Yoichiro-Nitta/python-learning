from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin, UserManager

# Create your models here.
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
    s_output = models.TextField(blank=True)
    s_answer = models.TextField(blank=True)
    s_explain = models.TextField(blank=True)
    c_number = models.PositiveSmallIntegerField(blank=True, null=True)
    a_number = models.PositiveSmallIntegerField(blank=True, null=True)


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


class Basis(models.Model):
    title = models.CharField(max_length=80, verbose_name="タイトル")
    name = models.CharField(max_length=60,verbose_name="問題名")
    section = models.PositiveIntegerField(verbose_name="区分")
    category = models.SmallIntegerField(verbose_name="分類")
    level = models.PositiveSmallIntegerField(verbose_name="難易度")
    question = models.TextField(verbose_name="問題文")
    pre_code = models.TextField(blank=True, verbose_name="指定入力（前）")
    pre_visual = models.TextField(blank=True, verbose_name="入力視像（前）")
    post_code = models.TextField(blank=True, verbose_name="指定入力（後）")
    post_visual = models.TextField(blank=True, verbose_name="入力視像（後）")
    i_range = models.TextField(blank=True, verbose_name="範囲")
    role_code = models.TextField(blank=True, verbose_name="演算コード")
    q_data = models.TextField(blank=True, verbose_name="出題データ/nct/bbcl/")
    c_output = models.TextField(blank=True, verbose_name="要求出力/nct/改")
    e_answer = models.TextField(blank=True, verbose_name="解答例/nct/mrcl/")
    explanation = models.TextField(blank=True, verbose_name="解説")

    def __str__(self):
        return self.title

class Quartet(models.Model):
    name = models.CharField(max_length=60,verbose_name="問題名")
    section = models.PositiveIntegerField(verbose_name="区分")
    level = models.PositiveSmallIntegerField(verbose_name="難易度")
    question = models.TextField(verbose_name="問題文")
    question_code = models.TextField(blank=True,verbose_name="使用コード")
    choices = models.TextField(verbose_name="選択肢")
    answer_idx = models.PositiveSmallIntegerField(verbose_name="解答番号")
    explanation = models.TextField(blank=True, verbose_name="解説")

    def __str__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=60,verbose_name="問題名")
    section = models.PositiveIntegerField(verbose_name="区分")
    level = models.PositiveSmallIntegerField(verbose_name="難易度")
    question = models.TextField(verbose_name="問題文")
    input_ex = models.TextField(verbose_name="入力例")
    output_ex = models.TextField(verbose_name="出力例")
    input_data = models.TextField(verbose_name="入力データ")
    output_data = models.TextField(verbose_name="出力データ")
    e_answer = models.TextField(blank=True, verbose_name="解答例")
    explanation = models.TextField(blank=True, verbose_name="解説")

    def __str__(self):
        return self.name
