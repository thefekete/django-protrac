from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from protrac.models import Job, ProductionLine


class PriorityForm(ModelForm):

    class Meta:
        model = Job
        fields = ['priority']
# PriorityFormSet = inlineformset_factory(ProductionLine, PriorityForm)
