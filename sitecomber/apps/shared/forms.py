from django import forms

from dal import autocomplete


class BaseUserAutocompleteForm(forms.ModelForm):

    class Meta:
        js = ('admin/autocomplete/forward.js',
              'admin/autocomplete/select_admin_autocomplete.js')

        widgets = {
            'user': autocomplete.ModelSelect2(
                url='author-autocomplete',
                attrs={'data-html': True}
            )
        }
