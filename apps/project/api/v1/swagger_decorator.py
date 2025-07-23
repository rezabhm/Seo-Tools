from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from apps.project.serializers import ProjectSerializer, ProcessSerializer

# ProjectAdminAPIView Decorators
admin_create_project_swagger = swagger_auto_schema(
    operation_summary='Create a New Project (Admin)',
    operation_description=(
        'This endpoint allows administrators to create a new project. '
        'The request must include name, description, service_url, owner_id, and optional fields like banner and collaborator_ids. '
        'The name must not exceed 50 characters, service_url must start with http:// or https://, and banner must be under 5MB. '
        'The response returns the created project’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.project'],
    request_body=ProjectSerializer,
    responses={
        201: ProjectSerializer,
        400: 'Invalid input data (e.g., empty name, invalid URL, or oversized banner).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

admin_retrieve_project_swagger = swagger_auto_schema(
    operation_summary='Retrieve Project Details (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve detailed information about a specific project by its ID. '
        'The response includes details such as ID, name, description, service_url, owner, and collaborators. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.project'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the project to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: ProjectSerializer,
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Project with the specified ID does not exist.'
    }
)

admin_update_project_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Project (Admin)',
    operation_description=(
        'This endpoint allows administrators to fully update the details of an existing project identified by its ID. '
        'The request body must include all required fields (e.g., name, description, service_url, owner_id) even if some fields remain unchanged. '
        'The name must not exceed 50 characters, service_url must start with http:// or https://, and banner must be under 5MB. '
        'The response returns the updated project’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.project'],
    request_body=ProjectSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the project to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: ProjectSerializer,
        400: 'Invalid input data (e.g., empty name, invalid URL, or oversized banner).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Project with the specified ID does not exist.'
    }
)

admin_partial_update_project_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Project (Admin)',
    operation_description=(
        'This endpoint allows administrators to partially update the details of an existing project identified by its ID. '
        'Only the provided fields in the request body will be updated (e.g., updating only description or banner). '
        'The name must not exceed 50 characters, service_url must start with http:// or https://, and banner must be under 5MB. '
        'The response returns the updated project’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.project'],
    request_body=ProjectSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the project to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: ProjectSerializer,
        400: 'Invalid input data (e.g., empty name or invalid URL).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Project with the specified ID does not exist.'
    }
)

admin_destroy_project_swagger = swagger_auto_schema(
    operation_summary='Delete a Project (Admin)',
    operation_description=(
        'This endpoint allows administrators to delete a project by its ID. '
        'The operation permanently removes the project from the system. '
        'A successful deletion returns a 204 No Content response. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.project'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the project to delete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Project successfully deleted.',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Project with the specified ID does not exist.'
    }
)

admin_list_project_swagger = swagger_auto_schema(
    operation_summary='List All Projects (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve a list of all project records in the system. '
        'The response includes details for each project, such as ID, name, description, service_url, owner, and collaborators. '
        'Optional search functionality is available using the "search" query parameter to filter by name or owner username. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.project'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Filter projects by name or owner username (partial match).", type=openapi.TYPE_STRING)
    ],
    responses={
        200: ProjectSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

# ProjectAPIView Decorators
user_create_project_swagger = swagger_auto_schema(
    operation_summary='Create a New Project (User)',
    operation_description=(
        'This endpoint allows authenticated users to create a new project. '
        'The request must include name, description, service_url, and optional fields like banner and collaborator_ids. '
        'The owner_id is automatically set to the authenticated user and cannot be modified. '
        'The name must not exceed 50 characters, service_url must start with http:// or https://, and banner must be under 5MB. '
        'The response returns the created project’s details. '
        'This operation requires JWT authentication.'
    ),
    tags=['project.project'],
    request_body=ProjectSerializer,
    responses={
        201: ProjectSerializer,
        400: 'Invalid input data (e.g., empty name, invalid URL, or oversized banner).',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: Owner must be the authenticated user.'
    }
)

user_retrieve_project_swagger = swagger_auto_schema(
    operation_summary='Retrieve Own Project Details',
    operation_description=(
        'This endpoint allows authenticated users to retrieve details of a project by its ID, '
        'where they are the owner or a collaborator. '
        'The response includes details such as ID, name, description, service_url, owner, and collaborators. '
        'This operation requires JWT authentication.'
    ),
    tags=['project.project'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the project to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: ProjectSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access their own projects or those they collaborate on.',
        404: 'Not Found: Project with the specified ID does not exist.'
    }
)

user_update_project_swagger = swagger_auto_schema(
    operation_summary='Fully Update Own Project',
    operation_description=(
        'This endpoint allows authenticated users to fully update a project identified by its ID, '
        'where they are the owner or a collaborator. '
        'The request body must include all required fields (e.g., name, description, service_url) even if some fields remain unchanged. '
        'The owner_id cannot be modified. The name must not exceed 50 characters, service_url must start with http:// or https://, '
        'and banner must be under 5MB. The response returns the updated project’s details. '
        'This operation requires JWT authentication.'
    ),
    tags=['project.project'],
    request_body=ProjectSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the project to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: ProjectSerializer,
        400: 'Invalid input data (e.g., empty name, invalid URL, or attempting to modify owner).',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only update their own projects or those they collaborate on.',
        404: 'Not Found: Project with the specified ID does not exist.'
    }
)

user_partial_update_project_swagger = swagger_auto_schema(
    operation_summary='Partially Update Own Project',
    operation_description=(
        'This endpoint allows authenticated users to partially update a project identified by its ID, '
        'where they are the owner or a collaborator. '
        'Only the provided fields in the request body will be updated (e.g., updating only description or banner). '
        'The owner_id cannot be modified. The name must not exceed 50 characters, service_url must start with http:// or https://, '
        'and banner must be under 5MB. The response returns the updated project’s details. '
        'This operation requires JWT authentication.'
    ),
    tags=['project.project'],
    request_body=ProjectSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the project to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: ProjectSerializer,
        400: 'Invalid input data (e.g., empty name or invalid URL).',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only update their own projects or those they collaborate on.',
        404: 'Not Found: Project with the specified ID does not exist.'
    }
)

user_destroy_project_swagger = swagger_auto_schema(
    operation_summary='Delete Own Project',
    operation_description=(
        'This endpoint allows authenticated users to delete a project by its ID, where they are the owner. '
        'The operation permanently removes the project from the system. '
        'A successful deletion returns a 204 No Content response. '
        'This operation requires JWT authentication.'
    ),
    tags=['project.project'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the project to delete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Project successfully deleted.',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only delete their own projects.',
        404: 'Not Found: Project with the specified ID does not exist.'
    }
)

user_list_project_swagger = swagger_auto_schema(
    operation_summary='List Own Projects',
    operation_description=(
        'This endpoint allows authenticated users to retrieve a list of projects where they are the owner or a collaborator. '
        'The response includes details for each project, such as ID, name, description, service_url, owner, and collaborators. '
        'This operation requires JWT authentication.'
    ),
    tags=['project.project'],
    responses={
        200: ProjectSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access their own projects or those they collaborate on.'
    }
)

# ProcessAdminAPIView Decorators
admin_create_process_swagger = swagger_auto_schema(
    operation_summary='Create a New Process (Admin)',
    operation_description=(
        'This endpoint allows administrators to create a new process. '
        'The request must include project_id, extraction_level, total_count, and optional fields like completed_count and status. '
        'The total_count must be at least 1, and completed_count must not exceed total_count. '
        'The response returns the created process’s details, including progress percentage. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.process'],
    request_body=ProcessSerializer,
    responses={
        201: ProcessSerializer,
        400: 'Invalid input data (e.g., negative counts or invalid status).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

admin_retrieve_process_swagger = swagger_auto_schema(
    operation_summary='Retrieve Process Details (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve detailed information about a specific process by its ID. '
        'The response includes details such as ID, extraction_level, total_count, completed_count, status, and associated project. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.process'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the process to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: ProcessSerializer,
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Process with the specified ID does not exist.'
    }
)

admin_update_process_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Process (Admin)',
    operation_description=(
        'This endpoint allows administrators to fully update the details of an existing process identified by its ID. '
        'The request body must include all required fields (e.g., project_id, extraction_level, total_count) even if some fields remain unchanged. '
        'The total_count must be at least 1, and completed_count must not exceed total_count. '
        'The response returns the updated process’s details, including progress percentage. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.process'],
    request_body=ProcessSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the process to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: ProcessSerializer,
        400: 'Invalid input data (e.g., negative counts or invalid status).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Process with the specified ID does not exist.'
    }
)

admin_partial_update_process_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Process (Admin)',
    operation_description=(
        'This endpoint allows administrators to partially update the details of an existing process identified by its ID. '
        'Only the provided fields in the request body will be updated (e.g., updating only status or completed_count). '
        'The total_count must be at least 1, and completed_count must not exceed total_count. '
        'The response returns the updated process’s details, including progress percentage. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.process'],
    request_body=ProcessSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the process to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: ProcessSerializer,
        400: 'Invalid input data (e.g., negative counts or invalid status).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Process with the specified ID does not exist.'
    }
)

admin_destroy_process_swagger = swagger_auto_schema(
    operation_summary='Delete a Process (Admin)',
    operation_description=(
        'This endpoint allows administrators to delete a process by its ID. '
        'The operation permanently removes the process from the system. '
        'A successful deletion returns a 204 No Content response. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.process'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the process to delete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Process successfully deleted.',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Process with the specified ID does not exist.'
    }
)

admin_list_process_swagger = swagger_auto_schema(
    operation_summary='List All Processes (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve a list of all process records in the system. '
        'The response includes details for each process, such as ID, extraction_level, total_count, completed_count, status, and associated project. '
        'Optional search functionality is available using the "search" query parameter to filter by project name or status. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.project.process'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Filter processes by project name or status (partial match).", type=openapi.TYPE_STRING)
    ],
    responses={
        200: ProcessSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

# ProcessAPIView Decorators
user_retrieve_process_swagger = swagger_auto_schema(
    operation_summary='Retrieve Own Process Details',
    operation_description=(
        'This endpoint allows authenticated users to retrieve details of a process by its ID, '
        'where the process is associated with a project they own or are a collaborator on, and the process is not finished. '
        'The response includes details such as ID, extraction_level, total_count, completed_count, status, and associated project. '
        'This operation requires JWT authentication.'
    ),
    tags=['project.process'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the process to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: ProcessSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access active processes for their own projects or collaborations.',
        404: 'Not Found: Process with the specified ID does not exist.'
    }
)

user_list_process_swagger = swagger_auto_schema(
    operation_summary='List Own Active Processes',
    operation_description=(
        'This endpoint allows authenticated users to retrieve a list of active (pending or started) processes '
        'associated with projects they own or are a collaborator on. '
        'The response includes details for each process, such as ID, extraction_level, total_count, completed_count, status, and associated project. '
        'This operation requires JWT authentication.'
    ),
    tags=['project.process'],
    responses={
        200: ProcessSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access active processes for their own projects or collaborations.'
    }
)

user_list_project_processes_swagger = swagger_auto_schema(
    operation_summary='List Active Processes for a Project',
    operation_description=(
        'This endpoint allows authenticated users to retrieve a list of active (pending or started) processes '
        'for a specific project identified by project_id, where they are the owner or a collaborator. '
        'The response includes details for each process, such as ID, extraction_level, total_count, completed_count, status, and associated project. '
        'This operation requires JWT authentication.'
    ),
    tags=['project.process'],
    manual_parameters=[
        openapi.Parameter('project_id', openapi.IN_PATH, description="The ID of the project to retrieve processes for.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: ProcessSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access processes for their own projects or collaborations.',
        400: 'Invalid input: Project with the specified ID does not exist.'
    }
)