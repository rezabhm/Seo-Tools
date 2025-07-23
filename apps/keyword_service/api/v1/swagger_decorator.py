from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from apps.keyword_service.serializers import KeywordSerializer

# KeywordAdminAPIView Decorators
admin_create_keyword_swagger = swagger_auto_schema(
    operation_summary='Create a New Keyword (Admin)',
    operation_description=(
        'This endpoint allows administrators to create a new keyword. '
        'The request must include root_keyword, keyword, project_id, and optional fields like keyword_type, extra_word, '
        'search_volume_data, geo_search_volume_data, search_engine_results, and search_volume. '
        'The root_keyword must not exceed 128 characters, keyword must not exceed 256 characters, '
        'and extra_word must not exceed 32 characters. Search volume must be non-negative. '
        'The response returns the created keyword’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.keyword_service.keyword'],
    request_body=KeywordSerializer,
    responses={
        201: KeywordSerializer,
        400: 'Invalid input data (e.g., empty root_keyword, oversized fields, or negative search volume).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

admin_retrieve_keyword_swagger = swagger_auto_schema(
    operation_summary='Retrieve Keyword Details (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve detailed information about a specific keyword by its ID. '
        'The response includes details such as ID, root_keyword, keyword, keyword_type, and associated project. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.keyword_service.keyword'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the keyword to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: KeywordSerializer,
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Keyword with the specified ID does not exist.'
    }
)

admin_update_keyword_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Keyword (Admin)',
    operation_description=(
        'This endpoint allows administrators to fully update the details of an existing keyword identified by its ID. '
        'The request body must include all required fields (e.g., root_keyword, keyword, project_id) even if some fields remain unchanged. '
        'The root_keyword must not exceed 128 characters, keyword must not exceed 256 characters, '
        'and extra_word must not exceed 32 characters. Search volume must be non-negative. '
        'The response returns the updated keyword’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.keyword_service.keyword'],
    request_body=KeywordSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the keyword to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: KeywordSerializer,
        400: 'Invalid input data (e.g., empty root_keyword, oversized fields, or negative search volume).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Keyword with the specified ID does not exist.'
    }
)

admin_partial_update_keyword_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Keyword (Admin)',
    operation_description=(
        'This endpoint allows administrators to partially update the details of an existing keyword identified by its ID. '
        'Only the provided fields in the request body will be updated (e.g., updating only keyword_type or search_volume). '
        'The root_keyword must not exceed 128 characters, keyword must not exceed 256 characters, '
        'and extra_word must not exceed 32 characters. Search volume must be non-negative. '
        'The response returns the updated keyword’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.keyword_service.keyword'],
    request_body=KeywordSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the keyword to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: KeywordSerializer,
        400: 'Invalid input data (e.g., empty root_keyword or negative search volume).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Keyword with the specified ID does not exist.'
    }
)

admin_destroy_keyword_swagger = swagger_auto_schema(
    operation_summary='Delete a Keyword (Admin)',
    operation_description=(
        'This endpoint allows administrators to delete a keyword by its ID. '
        'The operation permanently removes the keyword from the system. '
        'A successful deletion returns a 204 No Content response. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.keyword_service.keyword'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the keyword to delete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Keyword successfully deleted.',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Keyword with the specified ID does not exist.'
    }
)

admin_list_keyword_swagger = swagger_auto_schema(
    operation_summary='List All Keywords (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve a list of all keyword records in the system. '
        'The response includes details for each keyword, such as ID, root_keyword, keyword, keyword_type, and associated project. '
        'Optional search functionality is available using the "search" query parameter to filter by root_keyword, keyword, or keyword_type. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.keyword_service.keyword'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Filter keywords by root_keyword, keyword, or keyword_type (partial match).", type=openapi.TYPE_STRING)
    ],
    responses={
        200: KeywordSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

# KeywordAPIView Decorators
user_retrieve_keyword_swagger = swagger_auto_schema(
    operation_summary='Retrieve Own Keyword Details',
    operation_description=(
        'This endpoint allows authenticated users to retrieve details of a keyword by its ID, '
        'where the keyword is associated with a project they own or are a collaborator on. '
        'The response includes details such as ID, root_keyword, keyword, keyword_type, and associated project. '
        'This operation requires JWT authentication.'
    ),
    tags=['keyword_service.keyword'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the keyword to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: KeywordSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access keywords for their own projects or collaborations.',
        404: 'Not Found: Keyword with the specified ID does not exist.'
    }
)

user_list_keyword_swagger = swagger_auto_schema(
    operation_summary='List Own Keywords',
    operation_description=(
        'This endpoint allows authenticated users to retrieve a list of keywords '
        'associated with projects they own or are a collaborator on. '
        'The response includes details for each keyword, such as ID, root_keyword, keyword, keyword_type, and associated project. '
        'This operation requires JWT authentication.'
    ),
    tags=['keyword_service.keyword'],
    responses={
        200: KeywordSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access keywords for their own projects or collaborations.'
    }
)