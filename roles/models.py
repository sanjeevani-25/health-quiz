from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser, Group, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('The Password field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        print("create_user done",user)
        user.set_password(password)
        # print("create_user ",user.password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser,PermissionsMixin):
    ROLE_CHOICES = [
        ("Admin", "ADMIN"),
        ("Doctor", "DOCTOR"),
        ("User", "USER")
    ]
    class Types(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        USER = "USER","User"
        DOCTOR = "DOCTOR", "Doctor"

    type = models.CharField(choices=Types.choices, max_length=50)
    username= None
    uid = models.UUIDField(primary_key=True , default=uuid.uuid4 , editable=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256)
    # role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    archived = models.BooleanField(default=False)

    last_login = models.DateTimeField(auto_now=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD='email'
    REQUIRED_FIELDS = ['first_name','password', 'type']

    # groups=[]
    # permissions=[]

    objects = UserManager()

    class Meta:
        db_table = 'USER'

    def __str__(self):
        # return f"{self.first_name} {self.role}"
        # return str(self.uid)
        return str(self.email)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print(self.user_permissions)
        self.user_permissions.clear()
        print(self.user_permissions)
        self.assign_group()

    def assign_group(self):
        # Get or create the groups
        admin_group, created = Group.objects.get_or_create(name='Admin')
        doctor_group, created = Group.objects.get_or_create(name='Doctor')
        user_group, created = Group.objects.get_or_create(name='User')

        # Clear existing groups
        # self.groups.clear()

        # Assign the user to the correct group based on type
        if self.type == self.Types.ADMIN:
            self.groups.add(admin_group)
        elif self.type == self.Types.DOCTOR:
            self.groups.add(doctor_group)
        elif self.type == self.Types.USER:
            self.groups.add(user_group)
