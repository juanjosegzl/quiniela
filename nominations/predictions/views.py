from django.shortcuts import render
from django.core import serializers
from django.db.models import F

from .models import Nomination, Prediction, Category

from django.views.decorators.cache import cache_page

PROMOTED_EVENT_ID = 1

@cache_page(60 * 5)
def index(request):
    nominations = (
        Nomination.objects
        .filter(event_id=PROMOTED_EVENT_ID)
        .select_related("category")
        .select_related("entity")
        .annotate(
            category_name=F("category__name"),
            entity_name=F("entity__name"),
            youtube_video_id=F("entity__youtube_video_id"),
        )
        .values(
            "category_id",
            "category_name",
            "entity_id",
            "entity_name",
            "youtube_video_id",
        )
    )

    categories = {}

    for nomination in nominations:
        category_id = nomination['category_id']
        if category_id not in categories:
            categories[category_id] = {
                'name': nomination['category_name'],
                'entities': list()
            }

        categories[category_id]['entities'].append({
            'id': nomination['entity_id'],
            'name': nomination['entity_name'],
            'youtube_video_id': nomination['youtube_video_id'],
        })

    print(categories)
    return render(request, "predictions/main-area.html", {
        'categories': categories
    })
