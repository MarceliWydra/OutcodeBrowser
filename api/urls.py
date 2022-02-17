from django.urls import re_path

from .views import NexusView, OutcodeView

urlpatterns = [
    re_path("outcode/(?P<symbol>.+)/$", OutcodeView.as_view(), name="outcode"),
    re_path("nexus/(?P<symbol>.+)/$", NexusView.as_view(), name="nexus"),
]
