from django.db.models import Q
from django.contrib.auth import get_user_model

from dal import autocomplete

User = get_user_model()


class UserAdminAutocomplete(autocomplete.Select2QuerySetView):
    # NOTE - a more generic approach would be better here

    def get_queryset(self):

        if not self.request.user.is_authenticated:
            return User.objects.none()
        if not self.request.user.is_staff:
            return User.objects.none()

        qs = User.objects.all()

        if self.q:
            qs = qs.filter(Q(firstName__icontains=self.q) | Q(lastName__icontains=self.q) | Q(email__icontains=self.q) | Q(username__icontains=self.q))

        return qs
