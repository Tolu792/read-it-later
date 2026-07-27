from django import forms


class AddArticleForm(forms.Form):
    url = forms.URLField(max_length=2000)
