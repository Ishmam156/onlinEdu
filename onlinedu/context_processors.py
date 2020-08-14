from .models import CLASS_CHOICES

# Global categories for navbar dropdown
def get_category_choices(request):
    categories = [i[0] for i in CLASS_CHOICES]
    return {'categories' : categories }