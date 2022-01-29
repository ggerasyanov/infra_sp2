from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User


class TitleAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "year", "description",
                    "category")
    search_fields = ("name", "description", "category")
    list_filter = ("category",)
    list_editable = ("category",)
    empty_value_display = "-пусто-"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")


class GenreAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")
    search_fields = ("name", "slug")


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "text", "author", "score", "pub_date")
    search_fields = ("text", "title",)
    list_filter = ("author", "title")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "author", "pub_date", "review")
    search_fields = ("text", "author")
    list_filter = ("author", "review")


admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User)
