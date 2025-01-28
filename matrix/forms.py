from urllib.parse import urlparse

from django import forms

from matrix.models import PackageRequest, ContactMessage


class PackageRequestForm(forms.ModelForm):
    class Meta:
        model = PackageRequest
        fields = ['name', 'description', 'repository_url', 'documentation_url', 'latest_version', 'django_compatible_versions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter package name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description'}),
            'repository_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Only GitHub URLs are accepted'}),
            'documentation_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional, but highly desired'}),
            'latest_version': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Latest version in Major.Minor format (ex: 5.2)'}),
        }

    def clean_repository_url(self):
        repo_url = self.cleaned_data.get('repository_url')
        parsed_url = urlparse(repo_url)
        errors = []
        if parsed_url.netloc != "github.com":
            errors.append(forms.ValidationError("The domain must be 'github.com'."))
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) != 2:
            errors.append(forms.ValidationError("The URL must have exactly two components: owner/repo."))
        if errors:
            raise forms.ValidationError(errors)
        return repo_url


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']