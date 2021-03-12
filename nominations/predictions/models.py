from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    """
    Represent an award ceremony
    """

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50)
    celebrated = models.DateField(db_index=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Category of an award, e.g. Best Movie
    """

    class Meta:
        verbose_name_plural = "categories"

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Entity(models.Model):
    class Meta:
        verbose_name_plural = "entities"

    PERSON = "P"
    MOVIE = "M"

    ENTITY_CHOICES = [(PERSON, "Person"), (MOVIE, "Movie")]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50)
    imdb_url = models.URLField(max_length=300)
    kind = models.CharField(max_length=1, choices=ENTITY_CHOICES)
    youtube_video_id = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name


class Nomination(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return " | ".join(
            [
                self.event.name,
                self.category.name,
                self.entity.name,
                "Winner" if self.is_winner else "",
            ]
        )

    def get_nominations():
        nominations = (
            Nomination.objects
            .filter(event_id=1)
            .select_related("category")
            .select_related("entity")
            .annotate(
                category_name=models.F("category__name"),
                entity_name=models.F("entity__name"),
                youtube_video_id=models.F("entity__youtube_video_id"),
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

        return categories



class Prediction(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} | {self.event.name} | {self.category.name} | {self.entity.name}"

    def get_predictions_by_username(username):
        nominations = (
            Prediction.objects
            .filter(event_id=1)
            .filter(user__username=username)
            .select_related("category")
            .select_related("entity")
            .annotate(
                category_name=models.F("category__name"),
                entity_name=models.F("entity__name"),
            )
            .values(
                "category_id",
                "category_name",
                "entity_id",
                "entity_name",
            )
        )

        predictions = [
            {
                'category': nomination['category_name'],
                'entity': nomination['entity_name']
            }
            for nomination
            in nominations
        ]
        return predictions
