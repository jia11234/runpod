from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.pop('is_superuser', None)
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser):
    objects = UserManager()
    
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    nickname = models.CharField(max_length=100)
    state = models.IntegerField(default=0)
    login_failed = models.IntegerField(default=0)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    img_url = models.ImageField(upload_to='profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'

    def __str__(self):
        return f"{self.nickname} ({self.email})"
    
    REQUIRED_FIELDS = []

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def __str__(self):
        return f"{self.nickname} ({self.email})"

    class Meta:
        db_table = 'users'

class EmailVerification(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    send_count = models.IntegerField(default=0)
    last_modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'email_verifications'