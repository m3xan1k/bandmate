from django import forms


class SignUpForm(forms.Form):
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_password2(self):
        form_data = self.cleaned_data
        password = form_data.get('password')
        confirm_password = form_data.get('confirm_password')
        if not password or not confirm_password:
            raise forms.ValidationError('No password provided')
        if password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password


class LogInForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_password2(self):
        form_data = self.cleaned_data
        password = form_data.get('password')
        confirm_password = form_data.get('confirm_password')
        if not password or not confirm_password:
            raise forms.ValidationError('No password provided')
        if password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password
