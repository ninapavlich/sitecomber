from django import forms


class AdminAutocompleteFormMixin(forms.ModelForm):

    class Media:
        js = ('autocomplete_light/jquery.init.js',
              'admin/autocomplete/forward.js',
              'admin/autocomplete/select_admin_autocomplete.js')
