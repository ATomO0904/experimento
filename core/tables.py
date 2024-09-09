import django_tables2 as tables
from .models import TempUserAnswer

class TempUserAnswerTable(tables.Table):
    class Meta:
        model = TempUserAnswer
        template_name = "django_tables2/bootstrap5.html"
        fields = ("user.username", "answer", "group.name")