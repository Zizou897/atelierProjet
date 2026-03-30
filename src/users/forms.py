from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from .models import Role, UserProfile

User = get_user_model()


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["code", "name", "description", "is_active"]

    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()


class PortalUserCreateForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    phone = forms.CharField(max_length=30, required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.filter(is_active=True), required=False)
    is_active = forms.BooleanField(required=False, initial=True)
    portal_active = forms.BooleanField(required=False, initial=True)
    password1 = forms.CharField(widget=forms.PasswordInput, min_length=8)
    password2 = forms.CharField(widget=forms.PasswordInput, min_length=8)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all().order_by("content_type__app_label", "codename"),
        required=False,
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur existe deja.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            self.add_error("password2", "Les mots de passe ne correspondent pas.")
        return cleaned_data


class PortalUserUpdateForm(forms.Form):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    phone = forms.CharField(max_length=30, required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.filter(is_active=True), required=False)
    is_active = forms.BooleanField(required=False)
    portal_active = forms.BooleanField(required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, min_length=8)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all().order_by("content_type__app_label", "codename"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop("user_instance")
        super().__init__(*args, **kwargs)

        profile, _ = UserProfile.objects.get_or_create(user=self.user_instance)
        self.fields["email"].initial = self.user_instance.email
        self.fields["first_name"].initial = self.user_instance.first_name
        self.fields["last_name"].initial = self.user_instance.last_name
        self.fields["phone"].initial = profile.phone
        self.fields["role"].initial = profile.role
        self.fields["is_active"].initial = self.user_instance.is_active
        self.fields["portal_active"].initial = profile.portal_active
        self.fields["groups"].initial = self.user_instance.groups.all()
        self.fields["user_permissions"].initial = self.user_instance.user_permissions.all()
