from .forms import ProductSearchForm

def common_context(request):
    search_form = ProductSearchForm(request.GET)
    genre = request.GET.get("genre")
    if genre:
        search_form = ProductSearchForm({"keyword":genre})
    context = {
        "search_form": search_form,
    }
    return context