import logging
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView

from djangoblog.utils import send_email, get_sha256, get_current_site, generate_code, delete_sidebar_cache
from . import utils
from .forms import RegisterForm, LoginForm, ForgetPasswordForm, ForgetPasswordCodeForm
from .models import BlogUser

logger = logging.getLogger(__name__)


# Create your views here.

class RegisterView(FormView):
    # 指定自定义注册表单
    form_class = RegisterForm
    # 指定注册页面的模板文件路径
    template_name = 'account/registration_form.html'

    # 使用csrf_protect装饰器来保护跨站请求伪造攻击
    # 然后调用父类的dispatch方法来处理请求
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(RegisterView, self).dispatch(*args, **kwargs)

    # form_valid方法在表单验证通过时被调用
    # 如果表单数据有效，它会执行以下操作
    def form_valid(self, form):
        if form.is_valid():
            # 创建一个未激活的用户对象
            user = form.save(False)
            user.is_active = False
            user.source = 'Register'
            # 保存用户对象到数据库
            user.save(True)
            # 当前站点的域名
            site = get_current_site().domain
            # 获取用户id和设置的密钥的字符串，对其进行两次SHA256加密，返回加密后的签名
            sign = get_sha256(get_sha256(settings.SECRET_KEY + str(user.id)))

            if settings.DEBUG:
                site = '127.0.0.1:8000'
            path = reverse('account:result')
            # 生成一个验证链接
            url = "http://{site}{path}?type=validation&id={id}&sign={sign}".format(
                site=site, path=path, id=user.id, sign=sign)

            content = """
                            <p>请点击下面链接验证您的邮箱</p>

                            <a href="{url}" rel="bookmark">{url}</a>

                            \n再次感谢您！
                            <br />
                            如果上面链接无法打开，请将此链接复制至浏览器。\n
                            {url}
                            """.format(url=url)
            send_email(
                emailto=[
                    user.email,
                ],
                title='验证您的电子邮箱',
                content=content)

            url = reverse('accounts:result') + \
                  '?type=register&id=' + str(user.id)
            return HttpResponseRedirect(url)
        else:
            return self.render_to_response({
                'form': form
            })


class LogoutView(RedirectView):
    url = '/login/'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(LogoutView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logout(request)
        delete_sidebar_cache()
        return super(LogoutView, self).get(request, *args, **kwargs)


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'account/login.html'
    success_url = '/'
    redirect_field_name = REDIRECT_FIELD_NAME
    login_ttl = 2626560  # 一个月的时间

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        redirect_to = self.request.GET.get(self.redirect_field_name)
        if redirect_to is None:
            redirect_to = '/'
        kwargs['redirect_to'] = redirect_to

        return super(LoginView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form = AuthenticationForm(data=self.request.POST, request=self.request)

        if form.is_valid():
            delete_sidebar_cache()
            logger.info(self.redirect_field_name)

            auth.login(self.request, form.get_user())
            if self.request.POST.get("remember"):
                self.request.session.set_expiry(self.login_ttl)
            return super(LoginView, self).form_valid(form)
            # return HttpResponseRedirect('/')
        else:
            return self.render_to_response({
                'form': form
            })

    def get_success_url(self):

        redirect_to = self.request.POST.get(self.redirect_field_name)
        if not url_has_allowed_host_and_scheme(
                url=redirect_to, allowed_hosts=[
                    self.request.get_host()]):
            redirect_to = self.success_url
        return redirect_to


def account_result(request):
    type = request.GET.get('type')
    id = request.GET.get('id')

    user = get_object_or_404(get_user_model(), id=id)
    logger.info(type)
    if user.is_active:
        return HttpResponseRedirect('/')
    if type and type in ['register', 'validation']:
        if type == 'register':
            content = '''
    恭喜您注册成功，一封验证邮件已经发送到您的邮箱，请验证您的邮箱后登录本站。
    '''
            title = '注册成功'
        else:
            c_sign = get_sha256(get_sha256(settings.SECRET_KEY + str(user.id)))
            sign = request.GET.get('sign')
            if sign != c_sign:
                return HttpResponseForbidden()
            user.is_active = True
            user.save()
            content = '''
            恭喜您已经成功的完成邮箱验证，您现在可以使用您的账号来登录本站。
            '''
            title = '验证成功'
        return render(request, 'account/result.html', {
            'title': title,
            'content': content
        })
    else:
        return HttpResponseRedirect('/')


class ForgetPasswordView(FormView):
    form_class = ForgetPasswordForm
    template_name = 'account/forget_password.html'

    def form_valid(self, form):
        if form.is_valid():
            print("cleaned_data: ", form.cleaned_data)
            blog_user = BlogUser.objects.filter(email=form.cleaned_data.get("email")).get()
            blog_user.password = make_password(form.cleaned_data["new_password2"])
            blog_user.save()
            return HttpResponseRedirect('/login/')
        else:
            return self.render_to_response({'form': form})


class ForgetPasswordEmailCode(View):

    def post(self, request: HttpRequest):
        form = ForgetPasswordCodeForm(request.POST)
        if not form.is_valid():
            return HttpResponse("当前站点数据库无此邮箱")
        to_email = form.cleaned_data["email"]

        code = generate_code()
        utils.send_verify_email(to_email, code)
        utils.set_code(to_email, code)

        return HttpResponse("ok")
