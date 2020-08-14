from django.contrib import admin
from .models import Comment, Course, Discussion, Review, User

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_teacher', 'is_active')

    # Detect if active status of user has changed
    def save_model(self, request, obj, form, change):
        update_fields = []

        if change: 
            if form.initial['is_active'] != form.cleaned_data['is_active']:
                update_fields.append('is_active')
                obj.save(update_fields=update_fields)
            else:
                obj.save()
        else:
            obj.save()

class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'instructor', 'rating')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'reviewer', 'timestamp')


class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'creator', 'like')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'creator', 'like')


admin.site.register(User, UserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Comment, CommentAdmin)