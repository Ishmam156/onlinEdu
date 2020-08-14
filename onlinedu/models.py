from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from final.settings import EMAIL_HOST_USER

from multiselectfield import MultiSelectField

# Global categories for courses
CLASS_CHOICES = (('Programming', 'Programming'),
              ('UX', 'UX'),
              ('Finance', 'Finance'),
              ('Database', 'Database'),
              ('Art', 'Art'),
              ('Productivity', 'Productivity'))


# User class with choices, teacher field and courses chosen
class User(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    choices = MultiSelectField(choices=CLASS_CHOICES, blank=True)
    reference = models.URLField(max_length=200, blank=True)
    courses = models.ManyToManyField('Course', related_name='course_takers', blank=True) 

    # Representation
    def __str__(self):
        if self.is_teacher:
            return f'Teacher: {self.username}'
        else:
            return f'{self.username}'

    # Total course by an instructor
    def course_count(self):
        return Course.objects.filter(instructor=self).filter(is_active=True).count()         


# Course class with link to User class and method functions
class Course(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    title = models.TextField(blank=False, unique=True)
    description = models.TextField(blank=False)
    category = models.TextField(blank=False)
    rating = models.DecimalField(default=0, max_digits=3, decimal_places=2)
    raters = models.ManyToManyField(User, related_name='course_rated', blank=True)
    thumbnail = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    video = models.URLField(blank=True)
    completed = models.ManyToManyField(User, related_name='completed_courses', blank=True)

    # Representation
    def __str__(self):
        return f'{self.title}: Taught by, {self.instructor}'

    # Easy access of number of students in course
    def student_count(self):
        return User.objects.filter(courses=self.id).count()        

    # Easy access of number of raters of course
    def raters_count(self):
        return Course.objects.get(pk=self.id).raters.all().count()

    # YouTube Embed link
    def video_embed(self):
        new_link = self.video.replace('watch?v=', 'embed/')
        new_link += '?enablejsapi=1'
        return new_link

    # Get all reviews of course
    def reviews(self):
        all_reviews = Review.objects.filter(course=self).order_by('-pk')
        return all_reviews

    # Get all discussions of a course
    def discussions(self):
        return Discussion.objects.filter(course=self).order_by('-pk')


# Reviews class with link to user and course
class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Representation
    def __str__(self):
        return f'Review: {self.review} on Course: {self.course.title}'

    # Formatted time
    def time(self):
        return self.timestamp.strftime("%-I:%M %p, %b %-d %Y")


# Discussion Threads model
class Discussion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_discussion')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussions')
    comment = models.TextField(blank=False)
    like = models.IntegerField(blank=False, default=0)
    likers = models.ManyToManyField(User, related_name='discussion_likes', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Representation
    def __str__(self):
        return f'Discussion #{self.id} on {self.course.title} by: {self.creator.username}'

    # Formatted time
    def time(self):
        return self.timestamp.strftime("%-I:%M %p, %b %-d %Y")

    # Get all comments in a discussion
    def all_comments(self):
        return Comment.objects.filter(thread=self).all()


# Comment on Discussion model
class Comment(models.Model):
    thread = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(blank=False)
    like = models.IntegerField(blank=False, default=0)
    likers = models.ManyToManyField(User, related_name='comment_likes', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Representation
    def __str__(self):
        return f'Comment on Discussion #{self.thread.id} by: {self.creator.username}'

    # Formatted time
    def time(self):
        return self.timestamp.strftime("%-I:%M %p, %b %-d %Y")


# Send email to user when account has been activated for teacher
@receiver(signals.post_save, sender=User)
def update_active_status(sender, instance, created, **kwargs):
    # Check for only updated model
    if not created:
        update_fields = kwargs.get('update_fields') or set()
        # check if active status changed
        if 'is_active' in update_fields:
            if instance.is_teacher and instance.is_active:
                # Send confirmation message.
                subject = 'Your account has been activated!'
                message = f'Dear {instance.username},\n\nWelcome to OnlinEdu! We are glad to welcome you officially to the team and can not wait for the content you create!\n\nWith Love from OnlinEdu Team <3'
                send_mail(subject, message, EMAIL_HOST_USER, [instance.email], fail_silently = False)
            else:
                pass                
        else:
            pass