from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import BlogUser


class BlogUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_('password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Enter password again'), widget=forms.PasswordInput)

    class Meta:
        """
        在管理员为用户注册完成后，
        自动将创建的用户对象跳转至BlogUser模型中设置具体信息
        由于用户名以及密码已完成输入，其余皆为自动添加字段，依次仅需将Email字段加入fields即可
        """
        model = BlogUser
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("passwords do not match"))
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # print("save user before commit")
        # print("commit: ", commit)
        # if commit:
        #     print("save user after commit")
        #     user.source = 'adminsite'
        #     user.save()
        return user


class BlogUserChangeForm(UserChangeForm):
    class Meta:
        model = BlogUser
        fields = '__all__'
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BlogUserAdmin(UserAdmin):
    form = BlogUserChangeForm
    add_form = BlogUserCreationForm

    def save_model(self, request, obj, form, change):
        # 如果不是变更操作（即添加新对象）
        if not change:
            # 可以在这里设置额外的字段值
            obj.source = 'adminsite'
            # 调用父类的 save_model 方法来保存对象
        super().save_model(request, obj, form, change)
    list_display = (
        'id',
        'nickname',
        'username',
        'email',
        'last_login',
        'date_joined',
        'source')
    list_display_links = ('id', 'username')
    ordering = ('-id',)
