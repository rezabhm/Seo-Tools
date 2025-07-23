from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from apps.core.serializers import CustomUserSerializer, CollaboratorSerializer

# CustomUserAdminAPIView Decorators
admin_create_user_swagger = swagger_auto_schema(
    operation_summary='Create a New User (Admin)',
    operation_description=(
        'This endpoint allows administrators to create a new user. '
        'The request must include username, email, and other optional fields like first_name, last_name, and profile_image. '
        'The profile_image must be under 5MB. The response returns the created user’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    request_body=CustomUserSerializer,
    responses={
        201: CustomUserSerializer,
        400: 'Invalid input data (e.g., duplicate email or oversized profile image).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

admin_retrieve_user_swagger = swagger_auto_schema(
    operation_summary='Retrieve User Details (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve detailed information about a specific user by their ID. '
        'The response includes user details such as ID, username, email, and profile_image. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the user to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CustomUserSerializer,
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: User with the specified ID does not exist.'
    }
)

admin_update_user_swagger = swagger_auto_schema(
    operation_summary='Fully Update a User (Admin)',
    operation_description=(
        'This endpoint allows administrators to fully update the details of an existing user identified by their ID. '
        'The request body must include all required fields (e.g., username, email) even if some fields remain unchanged. '
        'The profile_image must be under 5MB. The response returns the updated user’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    request_body=CustomUserSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the user to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CustomUserSerializer,
        400: 'Invalid input data (e.g., duplicate email or oversized profile image).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: User with the specified ID does not exist.'
    }
)

admin_partial_update_user_swagger = swagger_auto_schema(
    operation_summary='Partially Update a User (Admin)',
    operation_description=(
        'This endpoint allows administrators to partially update the details of an existing user identified by their ID. '
        'Only the provided fields in the request body will be updated (e.g., updating only email or profile_image). '
        'The profile_image must be under 5MB. The response returns the updated user’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    request_body=CustomUserSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the user to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CustomUserSerializer,
        400: 'Invalid input data (e.g., duplicate email or oversized profile image).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: User with the specified ID does not exist.'
    }
)

admin_destroy_user_swagger = swagger_auto_schema(
    operation_summary='Delete a User (Admin)',
    operation_description=(
        'This endpoint allows administrators to delete a user by their ID. '
        'The operation permanently removes the user from the system. '
        'A successful deletion returns a 204 No Content response. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the user to delete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'User successfully deleted.',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: User with the specified ID does not exist.'
    }
)

admin_list_user_swagger = swagger_auto_schema(
    operation_summary='List All Users (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve a list of all user records in the system. '
        'The response includes details for each user, such as ID, username, email, and profile_image. '
        'Optional search functionality is available using the "search" query parameter to filter users by username or email. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Filter users by username or email (partial match).", type=openapi.TYPE_STRING)
    ],
    responses={
        200: CustomUserSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

# CustomUserPublicAPIView Decorators
public_create_user_swagger = swagger_auto_schema(
    operation_summary='Create a New User (Public)',
    operation_description=(
        'This endpoint allows unauthenticated users to create a new user account. '
        'The request must include username, email, and password, with optional fields like first_name, last_name, and profile_image. '
        'The profile_image must be under 5MB. The response returns the created user’s details. '
        'No authentication is required for this operation.'
    ),
    tags=['core.user'],
    request_body=CustomUserSerializer,
    responses={
        201: CustomUserSerializer,
        400: 'Invalid input data (e.g., duplicate email or oversized profile image).'
    }
)

# CustomUserAPIView Decorators
user_retrieve_user_swagger = swagger_auto_schema(
    operation_summary='Retrieve Own User Details',
    operation_description=(
        'This endpoint allows authenticated users to retrieve their own user information by their ID. '
        'The response includes details such as ID, username, email, and profile_image. '
        'The user ID must correspond to the authenticated user, and users cannot access other users’ data. '
        'This operation requires JWT authentication.'
    ),
    tags=['core.user'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the authenticated user.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CustomUserSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access their own data.',
        404: 'Not Found: User with the specified ID does not exist.'
    }
)

user_update_user_swagger = swagger_auto_schema(
    operation_summary='Fully Update Own User',
    operation_description=(
        'This endpoint allows authenticated users to fully update their own user data identified by their ID. '
        'The request body must include all required fields (e.g., username, email) even if some fields remain unchanged. '
        'The profile_image must be under 5MB. The response returns the updated user’s details. '
        'This operation requires JWT authentication.'
    ),
    tags=['core.user'],
    request_body=CustomUserSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the authenticated user to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CustomUserSerializer,
        400: 'Invalid input data (e.g., duplicate email or oversized profile image).',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only update their own data.',
        404: 'Not Found: User with the specified ID does not exist.'
    }
)

user_partial_update_user_swagger = swagger_auto_schema(
    operation_summary='Partially Update Own User',
    operation_description=(
        'This endpoint allows authenticated users to partially update their own user data identified by their ID. '
        'Only the provided fields in the request body will be updated (e.g., updating only email or profile_image). '
        'The profile_image must be under 5MB. The response returns the updated user’s details. '
        'This operation requires JWT authentication.'
    ),
    tags=['core.user'],
    request_body=CustomUserSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the authenticated user to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CustomUserSerializer,
        400: 'Invalid input data (e.g., duplicate email or oversized profile image).',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only update their own data.',
        404: 'Not Found: User with the specified ID does not exist.'
    }
)

# CollaboratorAdminAPIView Decorators
admin_create_collaborator_swagger = swagger_auto_schema(
    operation_summary='Create a New Collaborator (Admin)',
    operation_description=(
        'This endpoint allows administrators to create a new collaborator invitation. '
        'The request must include invitation_sender_id, invitation_receiver_id, and optional status (default is PENDING). '
        'The sender and receiver must be different users, and no duplicate pending invitations are allowed. '
        'The response returns the created collaborator details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.collaborator'],
    request_body=CollaboratorSerializer,
    responses={
        201: CollaboratorSerializer,
        400: 'Invalid input data (e.g., same sender and receiver or existing pending invitation).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

admin_retrieve_collaborator_swagger = swagger_auto_schema(
    operation_summary='Retrieve Collaborator Details (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve detailed information about a specific collaborator invitation by its ID. '
        'The response includes details such as ID, sender, receiver, and status. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.collaborator'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the collaborator invitation to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CollaboratorSerializer,
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Collaborator invitation with the specified ID does not exist.'
    }
)

admin_update_collaborator_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Collaborator (Admin)',
    operation_description=(
        'This endpoint allows administrators to fully update the details of an existing collaborator invitation identified by its ID. '
        'The request body must include all required fields (e.g., invitation_sender_id, invitation_receiver_id) even if some fields remain unchanged. '
        'The sender and receiver must be different users. The response returns the updated collaborator details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.collaborator'],
    request_body=CollaboratorSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the collaborator invitation to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CollaboratorSerializer,
        400: 'Invalid input data (e.g., same sender and receiver or invalid status).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Collaborator invitation with the specified ID does not exist.'
    }
)

admin_partial_update_collaborator_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Collaborator (Admin)',
    operation_description=(
        'This endpoint allows administrators to partially update the details of an existing collaborator invitation identified by its ID. '
        'Only the provided fields in the request body will be updated (e.g., updating only status). '
        'The response returns the updated collaborator details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.collaborator'],
    request_body=CollaboratorSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the collaborator invitation to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CollaboratorSerializer,
        400: 'Invalid input data (e.g., invalid status).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Collaborator invitation with the specified ID does not exist.'
    }
)

admin_destroy_collaborator_swagger = swagger_auto_schema(
    operation_summary='Delete a Collaborator (Admin)',
    operation_description=(
        'This endpoint allows administrators to delete a collaborator invitation by its ID. '
        'The operation permanently removes the collaborator from the system. '
        'A successful deletion returns a 204 No Content response. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.collaborator'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the collaborator invitation to delete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Collaborator invitation successfully deleted.',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Collaborator invitation with the specified ID does not exist.'
    }
)

admin_list_collaborator_swagger = swagger_auto_schema(
    operation_summary='List All Collaborators (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve a list of all collaborator invitations in the system. '
        'The response includes details for each invitation, such as ID, sender, receiver, and status. '
        'Optional search functionality is available using the "search" query parameter to filter by sender/receiver username or status. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.collaborator'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Filter collaborators by sender/receiver username or status (partial match).", type=openapi.TYPE_STRING)
    ],
    responses={
        200: CollaboratorSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

# CollaboratorAPIView Decorators
user_create_collaborator_swagger = swagger_auto_schema(
    operation_summary='Create a New Collaborator Invitation (User)',
    operation_description=(
        'This endpoint allows authenticated users to create a new collaborator invitation. '
        'The request must include invitation_receiver_id, and the invitation_sender_id is automatically set to the authenticated user. '
        'The sender and receiver must be different users, and no duplicate pending invitations are allowed. '
        'The response returns the created collaborator details. '
        'This operation requires JWT authentication.'
    ),
    tags=['core.collaborator'],
    request_body=CollaboratorSerializer,
    responses={
        201: CollaboratorSerializer,
        400: 'Invalid input data (e.g., same sender and receiver or existing pending invitation).',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: Sender must be the authenticated user.'
    }
)

user_retrieve_collaborator_swagger = swagger_auto_schema(
    operation_summary='Retrieve Own Collaborator Details',
    operation_description=(
        'This endpoint allows authenticated users to retrieve details of a collaborator invitation by its ID, '
        'where they are either the sender or receiver. '
        'The response includes details such as ID, sender, receiver, and status. '
        'This operation requires JWT authentication.'
    ),
    tags=['core.collaborator'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the collaborator invitation to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CollaboratorSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access their own collaboration records.',
        404: 'Not Found: Collaborator invitation with the specified ID does not exist.'
    }
)

user_update_collaborator_swagger = swagger_auto_schema(
    operation_summary='Fully Update Own Collaborator',
    operation_description=(
        'This endpoint allows authenticated users to fully update a collaborator invitation identified by its ID, '
        'where they are either the sender or receiver. '
        'The request body must include all required fields, though only status updates are allowed. '
        'Sender and receiver cannot be modified. The response returns the updated collaborator details. '
        'This operation requires JWT authentication.'
    ),
    tags=['core.collaborator'],
    request_body=CollaboratorSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the collaborator invitation to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CollaboratorSerializer,
        400: 'Invalid input data (e.g., attempting to modify sender or receiver).',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only update their own collaboration records.',
        404: 'Not Found: Collaborator invitation with the specified ID does not exist.'
    }
)

user_partial_update_collaborator_swagger = swagger_auto_schema(
    operation_summary='Partially Update Own Collaborator',
    operation_description=(
        'This endpoint allows authenticated users to partially update a collaborator invitation identified by its ID, '
        'where they are either the sender or receiver. '
        'Only the provided fields (e.g., status) will be updated. '
        'Sender and receiver cannot be modified. The response returns the updated collaborator details. '
        'This operation requires JWT authentication.'
    ),
    tags=['core.collaborator'],
    request_body=CollaboratorSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the collaborator invitation to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CollaboratorSerializer,
        400: 'Invalid input data (e.g., attempting to modify sender or receiver).',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only update their own collaboration records.',
        404: 'Not Found: Collaborator invitation with the specified ID does not exist.'
    }
)

user_destroy_collaborator_swagger = swagger_auto_schema(
    operation_summary='Delete Own Collaborator',
    operation_description=(
        'This endpoint allows authenticated users to delete a collaborator invitation by its ID, '
        'where they are either the sender or receiver. '
        'The operation permanently removes the collaborator from the system. '
        'A successful deletion returns a 204 No Content response. '
        'This operation requires JWT authentication.'
    ),
    tags=['core.collaborator'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the collaborator invitation to delete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Collaborator invitation successfully deleted.',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only delete their own collaboration records.',
        404: 'Not Found: Collaborator invitation with the specified ID does not exist.'
    }
)

user_list_collaborator_swagger = swagger_auto_schema(
    operation_summary='List Own Collaborators',
    operation_description=(
        'This endpoint allows authenticated users to retrieve a list of their collaborator invitations, '
        'where they are either the sender or receiver. '
        'The response includes details for each invitation, such as ID, sender, receiver, and status. '
        'This operation requires JWT authentication.'
    ),
    tags=['core.collaborator'],
    responses={
        200: CollaboratorSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access their own collaboration records.'
    }
)

user_list_received_invitations_swagger = swagger_auto_schema(
    operation_summary='List Received Collaboration Invitations',
    operation_description=(
        'This endpoint allows authenticated users to retrieve a list of pending collaboration invitations '
        'where they are the receiver. '
        'The response includes details for each invitation, such as ID, sender, receiver, and status. '
        'This operation requires JWT authentication.'
    ),
    tags=['core.collaborator'],
    responses={
        200: CollaboratorSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access their own received invitations.'
    }
)

user_handle_invitation_swagger = swagger_auto_schema(
    operation_summary='Handle Collaboration Invitation',
    operation_description=(
        'This endpoint allows authenticated users to accept or reject a collaboration invitation by its ID, '
        'where they are the receiver. The request body must include an "action" field with value "ACCEPT" or "REJECT". '
        'Only pending invitations can be handled. The response returns the updated collaborator details. '
        'This operation requires JWT authentication.'
    ),
    tags=['core.collaborator'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'action': openapi.Schema(type=openapi.TYPE_STRING, enum=['ACCEPT', 'REJECT'], description='Action to perform on the invitation')
        },
        required=['action']
    ),
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the collaborator invitation to handle.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: CollaboratorSerializer,
        400: 'Invalid input data (e.g., invalid action or invitation already handled).',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only handle invitations sent to them.',
        404: 'Not Found: Collaborator invitation with the specified ID does not exist.'
    }
)