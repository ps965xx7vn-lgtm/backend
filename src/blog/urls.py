"""
Blog URL Configuration

Маршруты для приложения блога:
- Главная страница и список статей
- Детальные страницы статей, категорий, тегов, серий
- Страницы авторов и фильтрация по сложности
- Подписка на newsletter
- AJAX API для реакций, комментариев, закладок
- Управление комментариями (редактирование, удаление)

Все маршруты используют класс-based views для удобства и переиспользования.
"""

from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    # Главная страница блога
    path("", views.BlogHomeView.as_view(), name="home"),
    # Статьи
    path("article/<slug:slug>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path("articles/", views.ArticleListView.as_view(), name="article_list"),
    path("articles/search/", views.ArticleSearchView.as_view(), name="article_search"),
    # Категории
    path("category/<str:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    # Теги
    path("tag/<path:slug>/", views.TagDetailView.as_view(), name="tag_detail"),
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    # Фильтрация по сложности
    path(
        "difficulty/<str:difficulty>/", views.DifficultyListView.as_view(), name="difficulty_list"
    ),
    # Серии статей
    path("series/<str:slug>/", views.SeriesDetailView.as_view(), name="series_detail"),
    path("series/", views.SeriesListView.as_view(), name="series_list"),
    # Авторы
    path("author/<str:slug>/", views.AuthorDetailView.as_view(), name="author_detail"),
    path("authors/", views.AuthorListView.as_view(), name="author_list"),
    # Рекомендуемые статьи
    path("featured/", views.FeaturedArticlesView.as_view(), name="featured"),
    # Подписка на рассылку
    path(
        "newsletter/subscribe/",
        views.NewsletterSubscribeView.as_view(),
        name="newsletter_subscribe",
    ),
    path(
        "newsletter/unsubscribe/",
        views.NewsletterUnsubscribeView.as_view(),
        name="newsletter_unsubscribe",
    ),
    # API для AJAX запросов
    path("api/article-reaction/", views.ArticleReactionView.as_view(), name="article_reaction"),
    path(
        "api/like-article/", views.LikeArticleView.as_view(), name="like_article"
    ),  # Алиас для обратной совместимости
    path("api/add-comment/", views.AddCommentView.as_view(), name="add_comment"),
    path(
        "api/load-more-articles/", views.LoadMoreArticlesView.as_view(), name="load_more_articles"
    ),
    path("api/toggle-bookmark/", views.ToggleBookmarkView.as_view(), name="toggle_bookmark"),
    path("api/report-article/", views.ReportArticleView.as_view(), name="report_article"),
    # Управление комментариями
    path("comment/<int:comment_id>/edit/", views.CommentEditView.as_view(), name="comment_edit"),
    path(
        "comment/<int:comment_id>/delete/", views.CommentDeleteView.as_view(), name="comment_delete"
    ),
]
