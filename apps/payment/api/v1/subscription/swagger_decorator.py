from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from apps.payment.serializers.subscription import SubscriptionPlanSerializer, PlanFeatureSerializer, UserSubscriptionSerializer
from apps.core.serializers import CustomUserSerializer

# SubscriptionPlanAdminAPIView Decorators
admin_create_subscription_plan_swagger = swagger_auto_schema(
    operation_summary='Create a New Subscription Plan (Admin)',
    operation_description=(
        'This endpoint allows administrators to create a new subscription plan. '
        'The request must include price, keyword_limit, and optional fields like is_labeling_enabled, is_chatgpt_enabled, and is_free_plan. '
        'The price and keyword_limit must be non-negative. '
        'The response returns the created subscription plan’s details, including associated features. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.subscription_plan'],
    request_body=SubscriptionPlanSerializer,
    responses={
        201: SubscriptionPlanSerializer,
        400: 'Invalid input data (e.g., negative price or keyword limit).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

admin_retrieve_subscription_plan_swagger = swagger_auto_schema(
    operation_summary='Retrieve Subscription Plan Details (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve detailed information about a specific subscription plan by its ID. '
        'The response includes details such as ID, price, keyword_limit, is_labeling_enabled, is_chatgpt_enabled, is_free_plan, and features. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.subscription_plan'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the subscription plan to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: SubscriptionPlanSerializer,
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Subscription plan with the specified ID does not exist.'
    }
)

admin_update_subscription_plan_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Subscription Plan (Admin)',
    operation_description=(
        'This endpoint allows administrators to fully update the details of an existing subscription plan identified by its ID. '
        'The request body must include all required fields (e.g., price, keyword_limit) even if some fields remain unchanged. '
        'The price and keyword_limit must be non-negative. '
        'The response returns the updated subscription plan’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.subscription_plan'],
    request_body=SubscriptionPlanSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the subscription plan to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: SubscriptionPlanSerializer,
        400: 'Invalid input data (e.g., negative price or keyword limit).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Subscription plan with the specified ID does not exist.'
    }
)

admin_partial_update_subscription_plan_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Subscription Plan (Admin)',
    operation_description=(
        'This endpoint allows administrators to partially update the details of an existing subscription plan identified by its ID. '
        'Only the provided fields (e.g., price, is_labeling_enabled) will be updated. '
        'The price and keyword_limit must be non-negative. '
        'The response returns the updated subscription plan’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.subscription_plan'],
    request_body=SubscriptionPlanSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the subscription plan to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: SubscriptionPlanSerializer,
        400: 'Invalid input data (e.g., negative price or keyword limit).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Subscription plan with the specified ID does not exist.'
    }
)

admin_destroy_subscription_plan_swagger = swagger_auto_schema(
    operation_summary='Delete a Subscription Plan (Admin)',
    operation_description=(
        'This endpoint allows administrators to delete a subscription plan by its ID. '
        'The operation permanently removes the subscription plan from the system. '
        'A successful deletion returns a 204 No Content response. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.subscription_plan'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the subscription plan to delete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Subscription plan successfully deleted.',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Subscription plan with the specified ID does not exist.'
    }
)

admin_list_subscription_plan_swagger = swagger_auto_schema(
    operation_summary='List All Subscription Plans (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve a list of all subscription plans in the system. '
        'The response includes details for each plan, such as ID, price, keyword_limit, is_labeling_enabled, is_chatgpt_enabled, is_free_plan, and features. '
        'Optional search functionality is available using the "search" query parameter to filter by price or keyword_limit. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.subscription_plan'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Filter plans by price or keyword_limit (partial match).", type=openapi.TYPE_STRING)
    ],
    responses={
        200: SubscriptionPlanSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

# PlanFeatureAdminAPIView Decorators
admin_create_plan_feature_swagger = swagger_auto_schema(
    operation_summary='Create a New Plan Feature (Admin)',
    operation_description=(
        'This endpoint allows administrators to create a new plan feature. '
        'The request must include subscription_plan_id and description. '
        'The description cannot be empty. '
        'The response returns the created plan feature’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.plan_feature'],
    request_body=PlanFeatureSerializer,
    responses={
        201: PlanFeatureSerializer,
        400: 'Invalid input data (e.g., empty description).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

admin_retrieve_plan_feature_swagger = swagger_auto_schema(
    operation_summary='Retrieve Plan Feature Details (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve detailed information about a specific plan feature by its ID. '
        'The response includes details such as ID, description, and associated subscription plan. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.plan_feature'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the plan feature to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: PlanFeatureSerializer,
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Plan feature with the specified ID does not exist.'
    }
)

admin_update_plan_feature_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Plan Feature (Admin)',
    operation_description=(
        'This endpoint allows administrators to fully update the details of an existing plan feature identified by its ID. '
        'The request body must include all required fields (e.g., subscription_plan_id, description) even if some fields remain unchanged. '
        'The description cannot be empty. '
        'The response returns the updated plan feature’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.plan_feature'],
    request_body=PlanFeatureSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the plan feature to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: PlanFeatureSerializer,
        400: 'Invalid input data (e.g., empty description).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Plan feature with the specified ID does not exist.'
    }
)

admin_partial_update_plan_feature_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Plan Feature (Admin)',
    operation_description=(
        'This endpoint allows administrators to partially update the details of an existing plan feature identified by its ID. '
        'Only the provided fields (e.g., description) will be updated. '
        'The description cannot be empty. '
        'The response returns the updated plan feature’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.plan_feature'],
    request_body=PlanFeatureSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the plan feature to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: PlanFeatureSerializer,
        400: 'Invalid input data (e.g., empty description).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Plan feature with the specified ID does not exist.'
    }
)

admin_destroy_plan_feature_swagger = swagger_auto_schema(
    operation_summary='Delete a Plan Feature (Admin)',
    operation_description=(
        'This endpoint allows administrators to delete a plan feature by its ID. '
        'The operation permanently removes the plan feature from the system. '
        'A successful deletion returns a 204 No Content response. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.plan_feature'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the plan feature to delete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Plan feature successfully deleted.',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Plan feature with the specified ID does not exist.'
    }
)

admin_list_plan_feature_swagger = swagger_auto_schema(
    operation_summary='List All Plan Features (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve a list of all plan features in the system. '
        'The response includes details for each feature, such as ID, description, and associated subscription plan. '
        'Optional search functionality is available using the "search" query parameter to filter by description or subscription plan price. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.plan_feature'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Filter features by description or subscription plan price (partial match).", type=openapi.TYPE_STRING)
    ],
    responses={
        200: PlanFeatureSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

# UserSubscriptionAdminAPIView Decorators
admin_create_user_subscription_swagger = swagger_auto_schema(
    operation_summary='Create a New User Subscription (Admin)',
    operation_description=(
        'This endpoint allows administrators to create a new user subscription. '
        'The request must include user_id, subscription_plan_id, and optional fields like expire_time, keywords_extracted, and keywords_extracted_percent. '
        'The expire_time must be in the future, and keywords_extracted_percent must be between 0 and 100. '
        'The response returns the created subscription’s details, including remaining days and active status. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.user_subscription'],
    request_body=UserSubscriptionSerializer,
    responses={
        201: UserSubscriptionSerializer,
        400: 'Invalid input data (e.g., past expire_time or invalid keywords_extracted_percent).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

admin_retrieve_user_subscription_swagger = swagger_auto_schema(
    operation_summary='Retrieve User Subscription Details (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve detailed information about a specific user subscription by its ID. '
        'The response includes details such as ID, user, subscription_plan, expire_time, keywords_extracted, keywords_extracted_percent, remaining_days, and is_active. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.user_subscription'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the user subscription to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: UserSubscriptionSerializer,
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: User subscription with the specified ID does not exist.'
    }
)

admin_update_user_subscription_swagger = swagger_auto_schema(
    operation_summary='Fully Update a User Subscription (Admin)',
    operation_description=(
        'This endpoint allows administrators to fully update the details of an existing user subscription identified by its ID. '
        'The request body must include all required fields (e.g., user_id, subscription_plan_id) even if some fields remain unchanged. '
        'The expire_time must be in the future, and keywords_extracted_percent must be between 0 and 100. '
        'The response returns the updated subscription’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.user_subscription'],
    request_body=UserSubscriptionSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the user subscription to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: UserSubscriptionSerializer,
        400: 'Invalid input data (e.g., past expire_time or invalid keywords_extracted_percent).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: User subscription with the specified ID does not exist.'
    }
)

admin_partial_update_user_subscription_swagger = swagger_auto_schema(
    operation_summary='Partially Update a User Subscription (Admin)',
    operation_description=(
        'This endpoint allows administrators to partially update the details of an existing user subscription identified by its ID. '
        'Only the provided fields (e.g., expire_time, keywords_extracted) will be updated. '
        'The expire_time must be in the future, and keywords_extracted_percent must be between 0 and 100. '
        'The response returns the updated subscription’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.user_subscription'],
    request_body=UserSubscriptionSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the user subscription to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: UserSubscriptionSerializer,
        400: 'Invalid input data (e.g., past expire_time or invalid keywords_extracted_percent).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: User subscription with the specified ID does not exist.'
    }
)

admin_destroy_user_subscription_swagger = swagger_auto_schema(
    operation_summary='Delete a User Subscription (Admin)',
    operation_description=(
        'This endpoint allows administrators to delete a user subscription by its ID. '
        'The operation permanently removes the subscription from the system. '
        'A successful deletion returns a 204 No Content response. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.user_subscription'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the user subscription to delete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'User subscription successfully deleted.',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: User subscription with the specified ID does not exist.'
    }
)

admin_list_user_subscription_swagger = swagger_auto_schema(
    operation_summary='List All User Subscriptions (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve a list of all user subscriptions in the system. '
        'The response includes details for each subscription, such as ID, user, subscription_plan, expire_time, keywords_extracted, and remaining_days. '
        'Optional search functionality is available using the "search" query parameter to filter by user username or subscription plan price. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.user_subscription'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Filter subscriptions by user username or subscription plan price (partial match).", type=openapi.TYPE_STRING)
    ],
    responses={
        200: UserSubscriptionSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

# SubscriptionPlanReadOnlyAPIView Decorators
user_list_subscription_plan_swagger = swagger_auto_schema(
    operation_summary='List All Subscription Plans',
    operation_description=(
        'This endpoint allows authenticated users to retrieve a list of all subscription plans in the system. '
        'The response includes details for each plan, such as ID, price, keyword_limit, is_labeling_enabled, is_chatgpt_enabled, is_free_plan, and associated features. '
        'Optional search functionality is available using the "search" query parameter to filter by price or keyword_limit. '
        'This operation requires JWT authentication.'
    ),
    tags=['payment.subscription_plan'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Filter plans by price or keyword_limit (partial match).", type=openapi.TYPE_STRING)
    ],
    responses={
        200: SubscriptionPlanSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.'
    }
)

# UserSubscriptionReadOnlyAPIView Decorators
user_retrieve_user_subscription_swagger = swagger_auto_schema(
    operation_summary='Retrieve Own User Subscription Details',
    operation_description=(
        'This endpoint allows authenticated users to retrieve details of their own user subscription by its ID. '
        'The response includes details such as ID, subscription_plan, expire_time, keywords_extracted, keywords_extracted_percent, remaining_days, and is_active. '
        'This operation requires JWT authentication.'
    ),
    tags=['payment.user_subscription'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the user subscription to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: UserSubscriptionSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access their own subscriptions.',
        404: 'Not Found: User subscription with the specified ID does not exist.'
    }
)

user_list_user_subscription_swagger = swagger_auto_schema(
    operation_summary='List Own User Subscriptions',
    operation_description=(
        'This endpoint allows authenticated users to retrieve a list of their own user subscriptions. '
        'The response includes details for each subscription, such as ID, subscription_plan, expire_time, keywords_extracted, keywords_extracted_percent, remaining_days, and is_active. '
        'This operation requires JWT authentication.'
    ),
    tags=['payment.user_subscription'],
    responses={
        200: UserSubscriptionSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access their own subscriptions.'
    }
)