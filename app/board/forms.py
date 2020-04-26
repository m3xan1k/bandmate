from django import forms

from board.models import Category, Announcement


class AnnouncementEditForm(forms.ModelForm):

    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    category = forms.ChoiceField(widget=forms.Select(), choices=Category.choices)

    class Meta:
        model = Announcement
        fields = ('title', 'text', 'category')
