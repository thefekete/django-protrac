from django.forms import ModelForm
from django.forms.models import modelformset_factory

from protrac.models import Job, ProductionLine


class PriorityForm(ModelForm):

    class Meta:
        model = Job
        fields = ['priority']

PriorityFormSet = modelformset_factory(Job, PriorityForm, extra=0)
