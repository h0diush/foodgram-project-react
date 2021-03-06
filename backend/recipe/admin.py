from django.contrib import admin

from .models import (Favorite, Follow, IngredientRecord, Ingredient, Recipe,
                     ShopList, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'color', 'slug')
    list_display_links = ('id', 'name',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Follow)
admin.site.register(ShopList)
admin.site.register(Favorite)
admin.site.register(IngredientRecord)
