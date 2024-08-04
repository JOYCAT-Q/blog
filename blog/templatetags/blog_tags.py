import hashlib
import logging
import random
import urllib

from django import template
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe

from blog.models import Article, Category, Tag, Links, SideBar, LinkShowType
from comments.models import Comment
from djangoblog.utils import CommonMarkdown, sanitize_html
from djangoblog.utils import cache
from djangoblog.utils import get_current_site
from oauth.models import OAuthUser

logger = logging.getLogger(__name__)

register = template.Library()

# 注册一个简单标签，用于将时间对象格式化为指定的字符串格式
@register.simple_tag
def timeformat(data):
    """
    根据设置的TIME_FORMAT格式化时间对象。

    参数:
    - data: 时间对象，例如datetime.datetime实例。
    
    返回:
    格式化后的时间字符串。
    """
    try:
        return data.strftime(settings.TIME_FORMAT)
    except Exception as e:
        logger.error(e)
        return ""

# 注册一个简单标签，用于将日期时间对象格式化为指定的字符串格式
@register.simple_tag
def datetimeformat(data):
    """
    根据设置的DATE_TIME_FORMAT格式化日期时间对象。
    
    参数:
    - data: 日期时间对象，例如datetime.datetime实例。
    
    返回:
    格式化后的日期时间字符串。
    """
    try:
        return data.strftime(settings.DATE_TIME_FORMAT)
    except Exception as e:
        logger.error(e)
        return ""

# 注册一个自定义的markdown过滤器，用于将markdown内容转换为HTML并添加安全标记
@register.filter()
@stringfilter
def custom_markdown(content):
    """
    将markdown内容转换为HTML并添加安全标记。
    
    参数:
    - content: markdown字符串。
    
    返回:
    转换后的HTML字符串，被标记为安全的。
    """
    return mark_safe(CommonMarkdown.get_markdown(content))

# 注册一个简单标签，用于获取markdown内容的目录
@register.simple_tag
def get_markdown_toc(content):
    """
    获取markdown内容的目录。
    
    参数:
    - content: markdown字符串。
    
    返回:
    markdown目录的HTML字符串，被标记为安全的。
    """
    from djangoblog.utils import CommonMarkdown
    body, toc = CommonMarkdown.get_markdown_with_toc(content)
    return mark_safe(toc)

# 注册一个过滤器，用于将评论内容的markdown转换为HTML并进行消毒处理
@register.filter()
@stringfilter
def comment_markdown(content):
    """
    对评论内容的markdown进行转换和消毒处理。
    
    参数:
    - content: 评论的markdown字符串。
    
    返回:
    转换后的HTML字符串，被标记为安全的。
    """
    content = CommonMarkdown.get_markdown(content)
    return mark_safe(sanitize_html(content))

# 注册一个过滤器，用于截断文章内容的字符数
@register.filter(is_safe=True)
@stringfilter
def truncatechars_content(content):
    """
    截断文章内容的字符数，根据博客设置确定截断长度。
    
    参数:
    - content: 文章内容的HTML字符串。
    
    返回:
    截断后的内容，保留HTML标签。
    """
    from django.template.defaultfilters import truncatechars_html
    from djangoblog.utils import get_blog_setting
    blogsetting = get_blog_setting()
    return truncatechars_html(content, blogsetting.article_sub_length)

# 注册一个过滤器，用于截断内容的字符数，去除HTML标签
@register.filter(is_safe=True)
@stringfilter
def truncate(content):
    """
    截断内容的字符数，去除HTML标签。
    
    参数:
    - content: 待截断的内容。
    
    返回:
    截断后的字符串。
    """
    from django.utils.html import strip_tags
    return strip_tags(content)[:150]

# 注册一个包含标签，用于生成文章的面包屑导航
@register.inclusion_tag('blog/tags/breadcrumb.html')
def load_breadcrumb(article):
    """
    生成文章的面包屑导航。
    
    参数:
    - article: 文章对象。
    
    返回:
    包含面包屑导航的数据字典。
    """
    names = article.get_category_tree()
    from djangoblog.utils import get_blog_setting
    blogsetting = get_blog_setting()
    site = get_current_site().domain
    names.append((blogsetting.site_name, '/'))
    names = names[::-1]

    return {
        'names': names,
        'title': article.title,
        'count': len(names) + 1
    }

# 注册一个包含标签，用于加载文章的标签列表
@register.inclusion_tag('blog/tags/article_tag_list.html')
def load_articletags(article):
    """
    加载文章的标签列表。
    
    参数:
    - article: 文章对象。
    
    返回:
    包含文章标签列表的数据字典。
    """
    tags = article.tags.all()
    tags_list = []
    for tag in tags:
        url = tag.get_absolute_url()
        count = tag.get_article_count()
        tags_list.append((
            url, count, tag, random.choice(settings.BOOTSTRAP_COLOR_TYPES)
        ))
    return {
        'article_tags_list': tags_list
    }


# 加载侧边栏信息，缓存结果以提高性能
@register.inclusion_tag('blog/tags/sidebar.html')
def load_sidebar(user, linktype):
    """
    加载侧边栏。

    从缓存中获取侧边栏信息，如果不存在则从数据库中获取并存入缓存。
    这样做可以减少数据库的访问次数，提高网站的响应速度。

    :param user: 当前用户对象
    :param linktype: 链接类型，用于生成不同的侧边栏内容
    :return: 侧边栏的HTML内容
    """
    """
    加载侧边栏
    :return:
    """
    value = cache.get("sidebar" + linktype)
    if value:
        value['user'] = user
        return value
    else:
        logger.info('load sidebar')
        from djangoblog.utils import get_blog_setting
        blogsetting = get_blog_setting()
        recent_articles = Article.objects.filter(
            status='p')[:blogsetting.sidebar_article_count]
        sidebar_categorys = Category.objects.all()
        extra_sidebars = SideBar.objects.filter(
            is_enable=True).order_by('sequence')
        most_read_articles = Article.objects.filter(status='p').order_by(
            '-views')[:blogsetting.sidebar_article_count]
        dates = Article.objects.datetimes('creation_time', 'month', order='DESC')
        links = Links.objects.filter(is_enable=True).filter(
            Q(show_type=str(linktype)) | Q(show_type=LinkShowType.A))
        commment_list = Comment.objects.filter(is_enable=True).order_by(
            '-id')[:blogsetting.sidebar_comment_count]
        # 标签云 计算字体大小
        # 根据总数计算出平均值 大小为 (数目/平均值)*步长
        increment = 5
        tags = Tag.objects.all()
        sidebar_tags = None
        if tags and len(tags) > 0:
            s = [t for t in [(t, t.get_article_count()) for t in tags] if t[1]]
            count = sum([t[1] for t in s])
            dd = 1 if (count == 0 or not len(tags)) else count / len(tags)
            import random
            sidebar_tags = list(
                map(lambda x: (x[0], x[1], (x[1] / dd) * increment + 10), s))
            random.shuffle(sidebar_tags)

        value = {
            'recent_articles': recent_articles,
            'sidebar_categorys': sidebar_categorys,
            'most_read_articles': most_read_articles,
            'article_dates': dates,
            'sidebar_comments': commment_list,
            'sidabar_links': links,
            'show_google_adsense': blogsetting.show_google_adsense,
            'google_adsense_codes': blogsetting.google_adsense_codes,
            'open_site_comment': blogsetting.open_site_comment,
            'show_gongan_code': blogsetting.show_gongan_code,
            'sidebar_tags': sidebar_tags,
            'extra_sidebars': extra_sidebars
        }
        cache.set("sidebar" + linktype, value, 60 * 60 * 60 * 3)
        logger.info('set sidebar cache.key:{key}'.format(key="sidebar" + linktype))
        value['user'] = user
        return value

# 加载文章的元信息，如标题、作者等
@register.inclusion_tag('blog/tags/article_meta_info.html')
def load_article_metas(article, user):
    """
    获得文章meta信息。

    提供文章的元信息，如标题、作者、发表时间等，用于在文章详情页显示。

    :param article: 文章对象
    :param user: 当前用户对象
    :return: 包含文章元信息的字典
    """
    """
    获得文章meta信息
    :param article:
    :return:
    """
    return {
        'article': article,
        'user': user
    }

# 加载分页信息，用于文章列表的分页显示
@register.inclusion_tag('blog/tags/article_pagination.html')
def load_pagination_info(page_obj, page_type, tag_name):
    """
    加载分页信息。

    根据当前页面对象和页面类型，生成上一页和下一页的URL，用于文章列表的分页导航。

    :param page_obj: 当前页面对象
    :param page_type: 页面类型，用于确定生成URL的逻辑
    :param tag_name: 标签名，用于生成特定标签的分页URL
    :return: 包含上一页和下一页URL的字典
    """
    previous_url = ''
    next_url = ''
    if page_type == '':
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse('blog:index_page', kwargs={'page': next_number})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:index_page', kwargs={
                    'page': previous_number})
    if page_type == '分类标签归档':
        tag = get_object_or_404(Tag, name=tag_name)
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:tag_detail_page',
                kwargs={
                    'page': next_number,
                    'tag_name': tag.slug})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:tag_detail_page',
                kwargs={
                    'page': previous_number,
                    'tag_name': tag.slug})
    if page_type == '作者文章归档':
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:author_detail_page',
                kwargs={
                    'page': next_number,
                    'author_name': tag_name})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:author_detail_page',
                kwargs={
                    'page': previous_number,
                    'author_name': tag_name})

    if page_type == '分类目录归档':
        category = get_object_or_404(Category, name=tag_name)
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:category_detail_page',
                kwargs={
                    'page': next_number,
                    'category_name': category.slug})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:category_detail_page',
                kwargs={
                    'page': previous_number,
                    'category_name': category.slug})

    return {
        'previous_url': previous_url,
        'next_url': next_url,
        'page_obj': page_obj
    }

# 加载文章详情页的内容和相关信息
@register.inclusion_tag('blog/tags/article_info.html')
def load_article_detail(article, isindex, user):
    """
    加载文章详情。

    提供文章的详细内容以及相关的信息，如作者、发表时间等，用于在文章详情页显示。

    :param article: 文章对象
    :param isindex: 是否是列表页，用于决定是否显示摘要
    :param user: 当前用户对象
    :return: 包含文章详情和相关信息的字典
    """
    """
    加载文章详情
    :param article:
    :param isindex:是否列表页，若是列表页只显示摘要
    :return:
    """
    from djangoblog.utils import get_blog_setting
    blogsetting = get_blog_setting()

    return {
        'article': article,
        'isindex': isindex,
        'user': user,
        'open_site_comment': blogsetting.open_site_comment,
    }

# 生成Gravatar头像的URL
@register.filter
def gravatar_url(email, size=40):
    """
    根据电子邮件地址生成Gravatar头像的URL。

    使用Gravatar服务根据电子邮件地址生成头像URL。如果用户在Gravatar上有头像，它会返回该头像；否则，返回一个默认头像。

    :param email: 用户的电子邮件地址
    :param size: 头像的大小
    :return: 头像的URL
    """
    """获得gravatar头像"""
    cachekey = 'gravatat/' + email
    url = cache.get(cachekey)
    if url:
        return url
    else:
        usermodels = OAuthUser.objects.filter(email=email)
        if usermodels:
            o = list(filter(lambda x: x.picture is not None, usermodels))
            if o:
                return o[0].picture
        email = email.encode('utf-8')

        default = static('blog/img/avatar.png')

        url = "https://www.gravatar.com/avatar/%s?%s" % (hashlib.md5(
            email.lower()).hexdigest(), urllib.parse.urlencode({'d': default, 's': str(size)}))
        cache.set(cachekey, url, 60 * 60 * 10)
        logger.info('set gravatar cache.key:{key}'.format(key=cachekey))
        return url

# 显示Gravatar头像的HTML代码
@register.filter
def gravatar(email, size=40):
    """
    根据电子邮件地址生成Gravatar头像的HTML代码。

    使用Gravatar服务根据电子邮件地址生成头像URL，并返回包含该URL的HTML图像标签。

    :param email: 用户的电子邮件地址
    :param size: 头像的大小
    :return: 包含头像URL的HTML图像标签
    """
    """获得gravatar头像"""
    url = gravatar_url(email, size)
    return mark_safe(
        '<img src="%s" height="%d" width="%d">' %
        (url, size, size))

# 根据查询参数过滤查询集
@register.simple_tag
def query(qs, **kwargs):
    """
    根据提供的参数过滤查询集。

    这是一个模板标签，允许在模板中根据参数过滤查询集，用于动态生成查询结果。

    :param qs: 查询集对象
    :param kwargs: 过滤条件，以键值对形式提供
    :return: 过滤后的查询集
    """
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    return qs.filter(**kwargs)


@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)