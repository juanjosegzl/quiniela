from django.shortcuts import render
from django.core import serializers

from .models import Nomination, Prediction, Category
from .forms import VoteForm

from django.views.decorators.cache import cache_page
from django.template.defaulttags import register
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.http import Http404

import os

PROMOTED_EVENT_ID = 1


@register.filter
def get_item(dictionary, key):
    widget = dictionary[f"category_{key}"]
    html = """
    <div class="col-4"><div class="form-check">
    <input
      class="form-check-input"
      type="radio"
      name="{name}"
      id="{id}"
      {checked}
      value="{value}"
    >
    <label
       class="form-check-label"
       for="{id}"
    >
       {label}
    </label>
    </div></div>
    """
    print(widget.value(), widget[0].data['value'])
    return "".join([html.format(
            name=widget.html_name,
            id=choice.id_for_label,
            label=choice.choice_label,
            checked="checked=\"checked\"" if widget.value() == choice.data['value'] else "",
            value=choice.data['value']
        ) for choice in widget])

def index(request):
    categories = Nomination.get_nominations()

    if request.method == "POST":
        form = VoteForm(request.user.id, request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            for category, entity_id in form.cleaned_data.items():
                if not entity_id:
                    continue
                category_id = category.split("_")[-1]

                p = (
                    Prediction.objects.filter(event_id=PROMOTED_EVENT_ID)
                    .filter(user_id=request.user.id)
                    .filter(category_id=category_id)
                    .first()
                )

                if p is None:
                    # new vote
                    p = Prediction(
                        event_id=PROMOTED_EVENT_ID,
                        category_id=category_id,
                        user_id=request.user.id
                    )

                p.entity_id = entity_id

                p.save()
        else:
            print("SOEMTHING")

    form = VoteForm(request.user.id)

    return render(
        request, "predictions/main-area.html", {"categories": categories, "form": form}
    )

VOTING_IS_OVER = os.getenv('VOTING_IS_OVER', False)

@login_required
def my_predictions(request, username=None):
    if username is None or not VOTING_IS_OVER:
        username = request.user.username

    user = User.objects.filter(username=username)
    if len(user) == 0:
        raise Http404("That user does not exists.")

    predictions = Prediction.get_predictions_by_username(username)

    return render(
        request, "predictions/predictions.html", {
            "predictions": predictions,
            "username": username
        }
    )

def error_404(request, exception):
    return render(request,'predictions/error_404.html')

def error_500(request):
    return render(request,'predictions/error_404.html')
