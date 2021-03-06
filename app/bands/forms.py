from django import forms

from bands.models import Musician, City, Instrument, Style, Band


class MusicianProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control'}),
        help_text='YYYY-MM-DD', required=False)
    city = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False, queryset=City.objects.all())
    is_busy = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    instruments = forms.ModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text='May select multiple', required=False, queryset=Instrument.objects.all())
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    activated = forms.BooleanField(widget=forms.CheckboxInput(), required=False)

    class Meta:
        model = Musician
        fields = ('first_name', 'last_name', 'birth_date',
                  'city', 'is_busy', 'instruments', 'bio',
                  'activated')


class MusicianFilterForm(forms.Form):
    city = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'custom-select my-1 mr-sm-2'}),
        required=False, queryset=City.objects.all())
    instrument = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'custom-select my-1 mr-sm-2'}),
        required=False, queryset=Instrument.objects.all())


class BandFilterForm(forms.Form):
    city = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'custom-select my-1 mr-sm-2'}),
        required=False, queryset=City.objects.all())
    style = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'custom-select my-1 mr-sm-2'}),
        required=False, queryset=Style.objects.all())


class BandEditForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    musicians = forms.ModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text='May select multiple', required=False,
        queryset=Musician.activated_objects.all())
    styles = forms.ModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text='May select multiple', required=False, queryset=Style.objects.all())
    city = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False, queryset=City.objects.all())
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Band
        fields = ('name', 'musicians', 'styles', 'city', 'description')
