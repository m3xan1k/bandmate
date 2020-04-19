from django import forms


class ProfileForm(forms.Form):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control'}))
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    instruments = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}))
