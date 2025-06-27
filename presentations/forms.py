from django import forms
from .models import Presentation
from events.models import Event

class PresentationForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ['title', 'description', 'content_md', 'file_url', 'event']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea'}),
            'content_md': forms.Textarea(attrs={'rows': 8, 'class': 'form-textarea'}),
            'event': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': '발표 제목',
            'description': '발표 내용 설명',
            'content_md': '마크다운 내용',
            'file_url': '발표 자료 (PDF, PPT, PPTX, 최대 50MB)',
            'event': '이벤트',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event'].queryset = Event.objects.all().order_by('-event_date')
        self.fields['file_url'].required = False 