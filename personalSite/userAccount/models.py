from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.dispatch import receiver
from timezone_field import TimeZoneField
from django.conf import settings
# Create your models here.
import os
from uuid import uuid4
from PIL import Image


class UserModelManager(BaseUserManager):
	"""Model manager for UserModel
	"""
	use_in_migrations = True

	def create_user(self, email, first_name, last_name, password=None):
		if not email:
			raise ValueError("User must have an email")
		if not password:
			raise ValueError("User must have a password")
		if not first_name:
			raise ValueError("User must have a first name")
		if not last_name:
			raise ValueError("User must have a last name")

		user = self.model(
			email=self.normalize_email(email),
			first_name=first_name,
			last_name=last_name,
		)
		user.set_password(password)  # change password to hash
		user.is_admin = False
		user.is_staff = False
		user.save(using=self._db)
		return user

	def create_superuser(self, email, first_name, last_name, password=None):
		if not email:
			raise ValueError("User must have an email")
		if not password:
			raise ValueError("User must have a password")
		if not first_name:
			raise ValueError("User must have a first name")
		if not last_name:
			raise ValueError("User must have a last name")

		user = self.model(
			email=self.normalize_email(email),
			first_name=first_name,
			last_name=last_name
		)

		user.set_password(password)  # change password to hash
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user

	def create_staffuser(self, email, first_name, last_name, password=None):
		if not email:
			raise ValueError("User must have an email")
		if not password:
			raise ValueError("User must have a password")
		if not first_name:
			raise ValueError("User must have a first name")
		if not last_name:
			raise ValueError("User must have a last name")

		user = self.model(
			email=self.normalize_email(email),
			first_name=first_name,
			last_name=last_name,
		)
		user.set_password(password)  # change password to hash
		user.is_admin = False
		user.is_staff = True
		user.save(using=self._db)
		return user


class InternalUser(AbstractBaseUser, PermissionsMixin):
	class Meta:
		ordering = [
			'last_name',
			'first_name',
			'middle_name',
			'email'
		]

	GENDER_CHOICES = [
		('M', 'Male'),
		('F', 'Female'),
		('', 'Not Set'),
	]
	email = models.EmailField('email', null=False, blank=False, max_length=64,
	                          unique=True, db_index=True)
	first_name = models.CharField('first_name', null=False, blank=False, max_length=50)
	last_name = models.CharField('last_name', null=False, blank=False, max_length=50)

	middle_name = models.CharField('middle_name', null=False, blank=True, max_length=50)
	bio = models.CharField('bio', null=False, blank=True, max_length=500, default="")

	is_confirmed = models.BooleanField('is_confirmed', default=False)
	dob = models.DateField('dob', null=False, blank=True, default="1970-01-01")
	gender = models.CharField('gender', max_length=1, choices=GENDER_CHOICES, null=False,
	                          blank=True, default='')
	timezone = TimeZoneField('timezone', default='Europe/Moscow')
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)
	two_factor_auth = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	username = models.CharField(max_length=100, null=False, blank=True)
	EMAIL_FIELD = 'email'
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['first_name', 'last_name']

	objects = UserModelManager()

	@property
	def full_name(self) -> str:
		"""Constructs user's full name.
		"""
		name = f'{self.last_name} {self.first_name}'
		if self.middle_name:
			name += ' ' + self.middle_name
		return name

	def get_full_name(self) -> str:
		"""Constructs user's full name.
		"""
		name = f'{self.last_name} {self.first_name}'
		if self.middle_name:
			name += ' ' + self.middle_name
		return name

	@property
	def short_name(self) -> str:
		"""Constructs user's short name (without patronymic).
		"""
		return f'{self.last_name} {self.first_name}'

	def has_module_perms(self, app_label):
		return self.is_admin

	def has_perm(self, perm, obj=None):
		return self.is_admin

	def __str__(self):
		return "{}".format(self.email)


def path_and_rename(instance, filename):
	path = ''
	ext = filename.split('.')[-1]
	# get filename
	if instance.pk:
		filename = '{}.{}'.format(instance.pk, ext)
	else:
		# set filename as random string
		filename = '{}.{}'.format(uuid4().hex, ext)
	# return the whole path to the file
	return os.path.join(path, filename)


class UserImage(models.Model):
	class Meta:
		app_label = 'userAccount'

	account = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='account_images',
	                               on_delete=models.CASCADE)
	image = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
	is_deleted = models.BooleanField(default=False)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def save(self):
		super().save()

		image = Image.open(self.image.path)

		if image.height > 300 or image.width > 300:
			output_size = (300, 300)
			image.thumbnail(output_size)
			image.save(self.image.path)


@receiver(models.signals.post_delete, sender=UserImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
	"""
	Deletes file from filesystem
	when corresponding `MediaFile` object is deleted.
	"""
	instance.image.delete(save=False)