from django import forms
from .models import Nomination, Prediction

class VoteForm(forms.Form):

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Nomination.get_nominations()

        predictions = (
            Prediction.objects
            .filter(event_id=1)
            .filter(user_id=user_id)
        )

        predictions_by_category = {p.category_id: p.entity_id for p in predictions}
        print(predictions_by_category)

        for category_id, category in categories.items():
            field_name = f"category_{category_id}"
            choices = [(e['id'], e['name']) for e in category['entities']]
            self.fields[field_name] = forms.ChoiceField(
                label=category['name'],
                choices=choices,
                widget=forms.RadioSelect,
                required=False,
                initial=predictions_by_category.get(category_id)
            )
