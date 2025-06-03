from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Custom pagination class for the API."""

    page_size = 6
    page_size_query_param = "limit"
    max_page_size = 100