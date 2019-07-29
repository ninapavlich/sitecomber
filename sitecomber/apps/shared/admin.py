from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Q
from django.utils.decorators import method_decorator

from dal import autocomplete

User = get_user_model()


# class UserAdminAutocomplete(autocomplete.Select2QuerySetView):

#     def get_queryset(self):

#         if not self.request.user.is_authenticated:
#             return User.objects.none()
#         if not self.request.user.is_staff:
#             return User.objects.none()

#         qs = User.objects.all()

#         if self.q:
#             qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q) | Q(email__icontains=self.q) | Q(username__icontains=self.q))

#         return qs


class AdminModelSelect2(autocomplete.ModelSelect2):
    autocomplete_function = 'admin-autocomplete'


class AdminAutocomplete(autocomplete.Select2QuerySetView):

    autocomplete_class = None

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(AdminAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        model = 'auth.User'  # self.forwarded.get('model', None)
        if not model:
            return []

        limit_choices_to = self.forwarded.get('limit_choices_to', None)

        app_label = model.split('.')[0]
        model_name = model.split('.')[1]

        if not app_label or not model_name:
            return []

        # Determine which class we're working with
        self.autocomplete_class = apps.get_model(app_label, model_name)

        # Dynamically create query based on class's autocomplete_lookup_fields:
        qs = self.autocomplete_class.objects.all()

        if self.q:
            q = Q()
            if hasattr(self.autocomplete_class, 'autocomplete_search_fields'):
                autocomplete_fields = self.autocomplete_class.autocomplete_search_fields()
            else:
                if model == settings.AUTH_USER_MODEL:
                    # If using the default user model, use these query fields:
                    autocomplete_fields = ['first_name__icontains', 'last_name__icontains', 'email__icontains', 'username__icontains']
                else:
                    autocomplete_fields = ['pk']

            # print(autocomplete_fields)

            for autocomplete_field_query in autocomplete_fields:
                kwargs = {autocomplete_field_query: self.q}
                q = q | Q(**kwargs)

            qs = qs.filter(q)

        if limit_choices_to:
            if 'queries' in limit_choices_to:
                limit_query = Q()
                for query in limit_choices_to['queries']:
                    limit_query = limit_query | Q(**query)

                qs = qs.filter(limit_query)
            else:
                qs = qs.filter(**limit_choices_to)

        return qs[:20]

    def get_autocomplete_selected_text(self, item):
        if hasattr(self.autocomplete_class, 'autocomplete_selected_text'):
            return self.autocomplete_class.autocomplete_selected_text(item)
        return super(AdminAutocomplete, self).get_result_label(item)

    def get_autocomplete_text(self, item):
        if hasattr(self.autocomplete_class, 'autocomplete_text'):
            return self.autocomplete_class.autocomplete_text(item)
        return super(AdminAutocomplete, self).get_result_label(item)

    def get_results(self, context):
        """Return data for the 'results' key of the response."""
        return [
            {
                'id': self.get_result_value(result),
                'selected_text': self.get_autocomplete_selected_text(result),
                'text': self.get_autocomplete_text(result),
            } for result in context['object_list']
        ]
