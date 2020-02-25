from flaskcbv.url import Url, make_urls
from .views import categoriesListView, categoriesUpdateView

namespases = make_urls(
    Url('/categories/list/<string:parentid>/', categoriesListView(), name="categories_list"),
    Url('/categories/create/', categoriesUpdateView.as_view("create", delete=False), name="categories_create"),
    Url('/categories/update/<int:pk>/', categoriesUpdateView.as_view("update", delete=False), name="categories_update"),
    Url('/categories/delete/<int:pk>/', categoriesUpdateView.as_view("delete", delete=True), name="categories_delete"),
    Url('/categories/batch/update/<string:pk>/', categoriesUpdateView.as_view("update", delete=False, batch=True), name="categories_batch_update"),
    Url('/categories/batch/delete/<string:pk>/', categoriesUpdateView.as_view("delete", delete=True, batch=True), name="categories_batch_delete"),
)



