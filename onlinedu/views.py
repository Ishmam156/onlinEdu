import decimal
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import FileResponse, JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from .forms import ChoiceForm, ImageUploadForm, TypeForm
from .models import CLASS_CHOICES, Comment, Course, Discussion, Review, User

# Index view
def index(request):
    # Get list of top 5 course
    courses = Course.objects.filter(is_active=True).order_by('-rating')[:5]
    return render(request, 'onlinedu/index.html', {'courses' : courses})


# Login view
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        print(user)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            # Check if there is next in the login submission
            if 'next' in request.POST and request.POST['next']:
                return redirect(request.POST['next'])
            else:
                # Login view with message
                courses = Course.objects.filter(is_active=True).order_by('-rating')[:5]
                message = f"You've been logged in successfully, {request.user}!" 
                return render(request, 'onlinedu/index.html', {'courses' : courses, 'message': message})
        else:
            return render(request, "onlinedu/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "onlinedu/login.html")

# Logout view
def logout_view(request):
    # Logout User
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# Register view
def register(request):
    # Initial registration page
    return render(request, 'onlinedu/register.html')

# Register with choice
def register_choice(request, choice):
    # Check for POST method
    if request.method == "POST":
        # Create form for providing in render if needed
        form = ChoiceForm()

        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            if choice == 'teacher':
                return render(request, "onlinedu/register_teacher.html", {
                    "message": "Passwords must match.",
                    'form' : form
                })
            else:
                return render(request, "onlinedu/register_student.html", {
                    "message": "Passwords must match.",
                    'form' : form
                })                                

        # Getting reference from user
        if choice == 'teacher':
            reference = request.POST["reference"]
            # Check if reference is blank
            if not reference and choice == 'teacher':
                return render(request, "onlinedu/register_teacher.html", {
                    "message": "Must provide a reference as a teacher.",
                    'form' : form
                })

        # Get course choices
        form_register = ChoiceForm(request.POST)
        if form_register.is_valid():
            options = form_register.cleaned_data["options"]

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.choices = options
            user.first_name = first_name
            user.last_name = last_name
            # Check if teacher
            if choice == 'teacher':
                user.is_teacher = True
                user.is_active = False
                user.reference = reference
            user.save()
        # If username already exists
        except IntegrityError:
            if choice == 'teacher':
                return render(request, "onlinedu/register_teacher.html", {
                    "message": "Username already taken.",
                    'form' : form
                })
            else:
                return render(request, "onlinedu/register_student.html", {
                    "message": "Username already taken.",
                    'form' : form
                })   
        # Show inactive message to teacher
        if choice == 'teacher':
            return render(request, "onlinedu/login.html", {'message' : "Thank you for registering! Your account is currently under review and you'll receive an email when activated."})
        # Login user
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    # Check if GET method
    elif request.method == 'GET':
        form = ChoiceForm()
        # Check which choice user has made
        if choice == 'student':
            return render(request, 'onlinedu/register_student.html', {'form': form })
        elif choice == 'teacher':
            return render(request, 'onlinedu/register_teacher.html', {'form': form })
        else:
            return render(request, 'onlinedu/error.html', { 'error' : f"Page named, {choice} doesn't exist in our website" })


# Create a course
@login_required
def create(request):
    # Check for POST methid
    if request.method == 'POST':
        # Get data from the form
        instructor = request.user
        title = request.POST['title']
        description = request.POST['description']

        # Get category option
        form = TypeForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['option']

        # Get thumbnail image
        thumbnail = request.POST['thumbnail']
        # file_form = ImageUploadForm(request.POST, request.FILES)
        # if file_form.is_valid():
        #     thumbnail = file_form.cleaned_data['thumbnail']

        # Get course video
        video = request.POST['video']

        # Check if YouTube video
        if 'www.youtube.com/watch?v=' not in video:
            return render(request, 'onlinedu/create.html', {'form' : TypeForm(), 'file_form' : ImageUploadForm(), 'message' : 'The link must be an YouTube video' })

        # Try to create new course:
        try:
            course = Course(instructor=instructor, title=title, description=description, category=category, thumbnail=thumbnail, video=video)
            course.save()
        # Check if course with title already exists
        except IntegrityError:
            return render(request, 'onlinedu/create.html', {'form' : TypeForm(), 'file_form' : ImageUploadForm(), 'message' : 'A course with that tile already exists!' })

        return HttpResponseRedirect(reverse('course', args=( course.id ,)))
        
    else:
        # Check if teacher or not
        if not request.user.is_teacher:
            return render(request, 'onlinedu/error.html', { 'error' : f"{request.user} is not an instructor in the website and cannot create courses." })

        # Generate required forms
        form = TypeForm()
        file_form = ImageUploadForm()
        return render(request, 'onlinedu/create.html', {'form' : form, 'file_form' : file_form })


# Category view of courses
def categories(request, category=''):
    # Check if all category is selected
    if not category:
        # Render all courses
        courses = Course.objects.filter(is_active=True).order_by('-rating')
        return render(request, 'onlinedu/categories.html', {'courses' : courses })
    else:
        # Check for specific category and render
        courses = Course.objects.filter(category=category).filter(is_active=True).order_by('-rating')
        return render(request, 'onlinedu/categories.html', {'courses' : courses , 'category_title' : category })


# Instructor view
def instructor(request, username):
    # Get user objects
    user = User.objects.get(username=username)

    # Check if url is not that of a teacher
    if not user.is_teacher:
        return render(request, 'onlinedu/error.html', { 'error' : f"{user} is not currently an instructor in the website." })

    # Get all courses by user
    courses = user.courses_taught.filter(is_active=True).order_by('-rating')
    return render(request, 'onlinedu/instructor.html', {'courses' : courses, 'instructor' : user })


# Student view
@login_required
def student(request, username):
    # Try to get user
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return render(request, 'onlinedu/error.html', { 'error' : f"{username} currently does not exist in the website." })
    # Check if url is not that of a teacher
    if user.is_teacher:
        return render(request, 'onlinedu/error.html', { 'error' : f"{user} is currently an instructor in the website." })

    # Get all courses attended by user
    courses = user.courses.filter(is_active=True).order_by('-rating')
    return render(request, 'onlinedu/student.html', {'courses' : courses, 'student' : user })


# Course Homepage view
def course(request, id):
    # Get the course details
    course_selected = Course.objects.get(pk=id)
    # Get all courses by logged in user
    try:
        courses = request.user.courses.all()
    except AttributeError:
        courses = []

    # Check if already enrolled in the course
    if course_selected in courses:
        enrolled = True
    else:
        enrolled = False

    return render(request, 'onlinedu/course.html', {'course' : course_selected, 'enrolled' : enrolled})


# Joining course view
@login_required
def join_course(request, id):
    # Get course object
    course = Course.objects.get(pk=id)

    # Adding course to users course list
    request.user.courses.add(course)

    return HttpResponseRedirect(reverse("course_view", args=(id,)))


# Course view
@login_required
def course_view(request, id):
    # Check for POST method
    if request.method == 'POST':
        # Getting course object
        course = Course.objects.get(pk=id)
        # Getting user discussion
        comment = request.POST['discussion']

        # Getting discussion object
        discussion = Discussion(course=course, creator=request.user, comment=comment)
        discussion.save()

        return HttpResponseRedirect(reverse('course_view', args=(id,)))
    else:        
        # Get courses of user
        courses = request.user.courses.all()
        # Get course object
        course = Course.objects.get(pk=id)

        # Check if user is teacher
        if course.instructor == request.user:
            return render(request, 'onlinedu/course_view.html', {'course' : course })    

        # Check is student is enrolled in course
        if course not in courses:
            return render(request, 'onlinedu/error.html', { 'error' : f"{request.user} is currently not enrolled in the course {course.title}." })

        return render(request, 'onlinedu/course_view.html', {'course' : course })


# Disabling course for teacher
@login_required
def disable_course(request, id):
    # Get course object
    course = Course.objects.get(pk=id)

    # Check if user is teacher of the course
    if course.instructor != request.user:
        return render(request, 'onlinedu/error.html', { 'error' : f"{request.user} is not the instructor of {course.title} and cannot disable the course." })

    # Disabling course
    course.is_active = False
    course.save()

    return HttpResponseRedirect(reverse("index"))


# Certificate generator
@login_required
def certificate(request, id):
    # Get courses of user
    courses = request.user.courses.all()
    # Get course object
    course = Course.objects.get(pk=id)

    # Check is student is enrolled in course
    if course not in courses:
        return render(request, 'onlinedu/error.html', { 'error' : f"{request.user} is currently not enrolled in the course, {course.title}." })

    # Check if student has completed the course
    if request.user not in course.completed.all():
         return render(request, 'onlinedu/error.html', { 'error' : f"{request.user} has not yet completed the course, {course.title}." })

    # Get the path ready for cert
    PATH = str(Path().absolute())
    ROUTE = '/media/course/cert/'
    TEMPLATE = 'template.png'
    NAME = request.user.get_full_name()
    
    # Basic font and color
    text_color = (0, 0, 0)
    font = ImageFont.truetype('Brush Script.ttf', 100)
    
    # Load template
    load_image = PATH + ROUTE + TEMPLATE
    png_image = Image.open(load_image)
    # Convert PNG to PDF ready format
    image = Image.new('RGB', png_image.size, (255, 255, 255))
    image.paste(png_image, mask=png_image.split()[3])     
    draw = ImageDraw.Draw(image)
    
    # Draw Name
    location = (105, 780)
    draw.text(location, NAME, fill = text_color, font = font)

    # Draw Course
    course_title = course.title
    location = (105, 1020)
    font = ImageFont.truetype('Brush Script.ttf', 40)
    draw.text(location, course_title, fill = text_color, font = font)

    # Draw Time
    now = datetime.now()
    current_time = now.strftime("%d %B %Y")
    location = (155, 1100)
    font = ImageFont.truetype('Brush Script.ttf', 32)
    draw.text(location, current_time, fill = text_color, font = font)

    # Check if user already has directory
    DIRECTORY = ROUTE + f'{request.user.username}/'
    if not os.path.exists(PATH + DIRECTORY):
        os.makedirs(PATH + DIRECTORY)

    # Base URL for saving
    image_web = DIRECTORY + course_title

    # Save image and PDF to media folder
    image.save(PATH + image_web + '.png')
    image.save(PATH + image_web + '.pdf', 'PDF', resoultion=100.0)

    # Path to image and PDF
    img_path = image_web + '.png'
    pdf_path = image_web + '.pdf'

    return render(request, 'onlinedu/certificate.html', {'image' : img_path, 'pdf' : pdf_path, 'course' : course })


# Review addition function
@login_required
def review(request, id):
    if request.method == 'POST':
        # Get course object
        course = Course.objects.get(pk=id)
        # Get user review
        user_review = request.POST['review']
        # Get rating
        rating = request.POST.get('rating2', '0')
        
        # Check if rating has been provided
        if rating != '0':
            # Get current rating and total raters
            current_rating = course.rating
            current_raters = course.raters_count()

            # Get new rating
            current_total = current_rating * current_raters
            new_total = current_total + decimal.Decimal(rating)
            new_rating = (new_total) / (current_raters + 1)

            # Add new rating and user to raters list
            course.rating = new_rating
            course.raters.add(request.user)
            course.save()

        # Create review object
        review = Review(course=course, reviewer=request.user, review=user_review)
        review.save()

        return HttpResponseRedirect(reverse('course', args=(id,)))
    else:
        return render(request, 'onlinedu/error.html', { 'error' : "Page not found" })


# Like modifier view
@csrf_exempt
@login_required
def like(request, id, content):

    # Check for the type of post
    if content == 'thread':
        post = Discussion.objects.get(pk=id)
    elif content == 'comment':
        post = Comment.objects.get(pk=id)
        
    # Check if post is the users
    if post.creator == request.user:
        return JsonResponse({'error': 'Can not like your own posts!'}, status=201)

    # Check if the post has already been liked by user
    if request.user in post.likers.all():
        return JsonResponse({'error': 'Can not like a post 2 times!'}, status=201)
    else:
        # Increase like count and save
        likecount = post.like + 1
        post.like = likecount
        post.likers.add(request.user)
        post.save()

        # Return sucess response
        return JsonResponse({'success': 'Post has now 1 more like!', 'likecount' : f'{likecount}'}, status=201)

# Comment view
@login_required
def comment(request, id):

    # Check request method
    if request.method == 'POST':
        # Get discussion object
        discussion = Discussion.objects.get(pk=id)
        # Get user comment
        user_comment = request.POST['comment']
        # Get course id
        course_id = discussion.course.id

        # Create comment object
        comment = Comment(thread=discussion, creator=request.user, comment=user_comment)
        comment.save()

        # Redirect to course view
        return HttpResponseRedirect(reverse('course_view', args=(course_id,)))

    else:
        # Show error message
        return render(request, 'onlinedu/error.html', { 'error' : "This page is not accessible." })


# Course completed view
@csrf_exempt
@login_required
def completed(request, id):

    # Check for request method
    if request.method == 'PUT':

        # Get course object
        course = Course.objects.get(pk=id)
        
        # Add user to completed user list
        course.completed.add(request.user)
        course.save()

        # Return completion response
        return HttpResponse(status=204)

    else:
        # Show error message
        return render(request, 'onlinedu/error.html', { 'error' : "This page is not accessible." })