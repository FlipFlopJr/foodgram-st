from rest_framework.pagination import PageNumberPagination


class PaginationSite(PageNumberPagination):
    """Класс Пагинации"""

    page_size = 8
    page_size_query_param = "limit"
    max_page_size = 50
