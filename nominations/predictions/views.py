from django.shortcuts import render
from django.core import serializers

from .models import Nomination, Prediction, Category
from .forms import VoteForm

from django.views.decorators.cache import cache_page
from django.template.defaulttags import register
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

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

@login_required
def my_predictions(request):
    predictions = Prediction.get_nominations(request.user.id)

    return render(
        request, "predictions/my-votes.html", {"predictions": predictions}
    )
