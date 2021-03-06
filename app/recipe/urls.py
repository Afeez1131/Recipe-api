from django.urls import path, include
from recipe import views
from rest_framework.routers import DefaultRouter

app_name = 'recipe'
router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredient', views.IngredientViewSet)
router.register('recipe', views.RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]