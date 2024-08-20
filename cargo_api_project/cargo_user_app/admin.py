from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django_google_maps import widgets as map_widgets#map api modules
from django_google_maps import fields as map_fields
import json


class UserModelAdmin(BaseUserAdmin):
  # The fields to be used in displaying the User model.
  # These override the definitions on the base UserModelAdmin
  # that reference specific fields on auth.User.
  list_display = ('id', 'email', 'fullname', 'phone','country_code', 'is_admin','is_courier')
  list_filter = ('is_admin',)
  fieldsets = (
      ('User Credentials', {'fields': ('email', 'password')}),
      ('Personal info', {'fields': ('fullname', 'phone','country_code')}),
      ('Permissions', {'fields': ('is_admin','is_courier',)}),
  )
  # add_fieldsets is not a standard ModelAdmin attribute. UserModelAdmin
  # overrides get_fieldsets to use this attribute when creating a user.
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ('email', 'fullname', 'phone', 'country_code','password1', 'password2'),
      }),
  )
  search_fields = ('email',)
  ordering = ('email', 'id')
  filter_horizontal = ()




# Now register the new UserModelAdmin...
admin.site.register(User, UserModelAdmin)

# class PickupLocationAdmin(BaseUserAdmin):
#   # The fields to be used in displaying the User model.
#   # These override the definitions on the base UserModelAdmin
#   # that reference specific fields on auth.User.
#   list_display = ('id', 'address','latitude','longitude')

admin.site.register(PickupLocation)
#admin.site.register(Vehicle)
admin.site.register(Cargo_package)
admin.site.register(Time_Slot)
