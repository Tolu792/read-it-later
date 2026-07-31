from django import forms


class AddArticleForm(forms.Form):
    url = forms.URLField(max_length=2000)
    tags = forms.CharField(required=False, help_text="Comma-separated tags, optional")
