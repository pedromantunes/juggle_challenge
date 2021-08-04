from __future__ import annotations

from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

from juggle_challenge import utils


class LinkHeaderPagination(PageNumberPagination):
    """Inform the user of pagination links via response headers, similar to
    what's described in
    https://developer.github.com/v3/guides/traversing-with-pagination/
    """

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()
        first_url = self.get_first_link()
        last_url = self.get_last_link()

        links = []
        for url, label in (
            (first_url, "first"),
            (previous_url, "prev"),
            (next_url, "next"),
            (last_url, "last"),
        ):
            if url is not None:
                links.append('<{}>; rel="{}"'.format(url, label))

        headers = {"Link": ", ".join(links)} if links else {}

        return Response(data, headers=headers)

    def get_first_link(self):
        if not self.page.has_previous():
            return None
        else:
            url = utils.build_absolute_url(path=self.request.get_full_path())
            return remove_query_param(url, self.page_query_param)

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = utils.build_absolute_url(path=self.request.get_full_path())
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = utils.build_absolute_url(path=self.request.get_full_path())
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)

    def get_last_link(self):
        if not self.page.has_next():
            return None
        else:
            if getattr(settings, "SITE_BASE_URL", False):
                url = "{}{}".format(
                    settings.SITE_BASE_URL, self.request.get_full_path()
                )
            else:
                url = self.request.build_absolute_uri()
            return replace_query_param(
                url, self.page_query_param, self.page.paginator.num_pages
            )
