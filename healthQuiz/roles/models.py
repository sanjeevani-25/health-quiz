from django.db import models
import uuid
# Create your models here.


class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Role(models.Model):
    DOCTOR = 'Doctor'
    USER = 'User'
    ADMIN = 'Admin'
    
    ROLE_CHOICES = [
        (DOCTOR, 'Doctor'),
        (USER, 'User'),
        (ADMIN, 'Admin'),
    ]
    
    name = models.CharField(
        max_length=255,
        unique=True,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'roles'


class User(BaseModel):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def save(self):
        self.full_clean()
        super().save()