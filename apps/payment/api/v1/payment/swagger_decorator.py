from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from apps.payment.serializers.payment import PaymentTransactionSerializer
from apps.payment.serializers.subscription import UserSubscriptionSerializer

# PaymentTransactionAdminAPIView Decorators
admin_create_payment_transaction_swagger = swagger_auto_schema(
    operation_summary='Create a New Payment Transaction (Admin)',
    operation_description=(
        'This endpoint allows administrators to create a new payment transaction. '
        'The request must include user_id, subscription_plan_id, paypal_transaction_id, amount, '
        'and optional fields like status, paypal_response, and redirect_url. '
        'The amount must match the subscription plan price and be positive. '
        'The paypal_transaction_id must be unique, and redirect_url must not exceed 500 characters. '
        'The response returns the created transaction’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.transaction'],
    request_body=PaymentTransactionSerializer,
    responses={
        201: PaymentTransactionSerializer,
        400: 'Invalid input data (e.g., non-positive amount, non-unique PayPal transaction ID, or mismatched amount).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

admin_retrieve_payment_transaction_swagger = swagger_auto_schema(
    operation_summary='Retrieve Payment Transaction Details (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve detailed information about a specific payment transaction by its ID. '
        'The response includes details such as ID, user, subscription_plan, paypal_transaction_id, amount, status, and subscription remaining days. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.transaction'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the payment transaction to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: PaymentTransactionSerializer,
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Payment transaction with the specified ID does not exist.'
    }
)

admin_update_payment_transaction_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Payment Transaction (Admin)',
    operation_description=(
        'This endpoint allows administrators to fully update the details of an existing payment transaction identified by its ID. '
        'Only status, paypal_response, and redirect_url can be updated. '
        'The response returns the updated transaction’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.transaction'],
    request_body=PaymentTransactionSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the payment transaction to update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: PaymentTransactionSerializer,
        400: 'Invalid input data (e.g., invalid status or oversized redirect_url).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Payment transaction with the specified ID does not exist.'
    }
)

admin_partial_update_payment_transaction_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Payment Transaction (Admin)',
    operation_description=(
        'This endpoint allows administrators to partially update the details of an existing payment transaction identified by its ID. '
        'Only the provided fields (e.g., status, paypal_response, or redirect_url) will be updated. '
        'The response returns the updated transaction’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.transaction'],
    request_body=PaymentTransactionSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the payment transaction to partially update.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: PaymentTransactionSerializer,
        400: 'Invalid input data (e.g., invalid status or oversized redirect_url).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Payment transaction with the specified ID does not exist.'
    }
)

admin_destroy_payment_transaction_swagger = swagger_auto_schema(
    operation_summary='Delete a Payment Transaction (Admin)',
    operation_description=(
        'This endpoint allows administrators to delete a payment transaction by its ID. '
        'The operation permanently removes the transaction from the system. '
        'A successful deletion returns a 204 No Content response. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.transaction'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The unique ID of the payment transaction to delete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Payment transaction successfully deleted.',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'Not Found: Payment transaction with the specified ID does not exist.'
    }
)

admin_list_payment_transaction_swagger = swagger_auto_schema(
    operation_summary='List All Payment Transactions (Admin)',
    operation_description=(
        'This endpoint allows administrators to retrieve a list of all payment transactions in the system. '
        'The response includes details for each transaction, such as ID, user, subscription_plan, paypal_transaction_id, amount, and status. '
        'Optional search functionality is available using the "search" query parameter to filter by paypal_transaction_id, user username, or status. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.payment.transaction'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Filter transactions by paypal_transaction_id, user username, or status (partial match).", type=openapi.TYPE_STRING)
    ],
    responses={
        200: PaymentTransactionSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

# PaymentTransactionAPIView Decorators
user_initiate_payment_swagger = swagger_auto_schema(
    operation_summary='Initiate a PayPal Payment (User)',
    operation_description=(
        'This endpoint allows authenticated users to initiate a new PayPal payment transaction. '
        'The request must include subscription_plan_id and amount, which must match the subscription plan price. '
        'The user_id is automatically set to the authenticated user. '
        'The response includes the created transaction details and a PayPal redirect URL for payment processing. '
        'This operation requires JWT authentication.'
    ),
    tags=['payment.transaction'],
    request_body=PaymentTransactionSerializer,
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'transaction': PaymentTransactionSerializer().to_schema(),
                'redirect_url': openapi.Schema(type=openapi.TYPE_STRING, description='PayPal redirect URL for payment')
            }
        ),
        400: 'Invalid input data (e.g., mismatched amount or non-unique PayPal transaction ID).',
        401: 'Unauthorized: Valid JWT token required.'
    }
)

user_complete_payment_swagger = swagger_auto_schema(
    operation_summary='Complete a PayPal Payment (User)',
    operation_description=(
        'This endpoint allows authenticated users to complete a pending payment transaction by its ID. '
        'The transaction must belong to the authenticated user. '
        'Upon successful completion, a UserSubscription is created, and the response includes the updated transaction and subscription details. '
        'This operation requires JWT authentication.'
    ),
    tags=['payment.transaction'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the payment transaction to complete.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Transaction ID'),
                'user': CustomUserSerializer().to_schema(),
                'subscription_plan': SubscriptionPlanSerializer().to_schema(),
                'paypal_transaction_id': openapi.Schema(type=openapi.TYPE_STRING, description='PayPal transaction ID'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, format='decimal', description='Transaction amount'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Transaction status'),
                'paypal_response': openapi.Schema(type=openapi.TYPE_OBJECT, description='PayPal API response'),
                'redirect_url': openapi.Schema(type=openapi.TYPE_STRING, description='PayPal redirect URL'),
                'subscription_remaining_days': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description='Remaining days for subscription'),
                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Transaction creation time'),
                'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Transaction update time'),
                'subscription': UserSubscriptionSerializer().to_schema()
            }
        ),
        400: 'Invalid input: Transaction is not pending or failed to complete.',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only complete their own transactions.',
        404: 'Not Found: Payment transaction with the specified ID does not exist.'
    }
)

user_cancel_payment_swagger = swagger_auto_schema(
    operation_summary='Cancel a Pending Payment Transaction (User)',
    operation_description=(
        'This endpoint allows authenticated users to cancel a pending payment transaction by its ID. '
        'The transaction must belong to the authenticated user and must be in pending status. '
        'The response returns the updated transaction details with status set to canceled. '
        'This operation requires JWT authentication.'
    ),
    tags=['payment.transaction'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the payment transaction to cancel.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: PaymentTransactionSerializer,
        400: 'Invalid input: Transaction is not pending or failed to cancel.',
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only cancel their own transactions.',
        404: 'Not Found: Payment transaction with the specified ID does not exist.'
    }
)

user_retrieve_payment_transaction_swagger = swagger_auto_schema(
    operation_summary='Retrieve Own Payment Transaction Details',
    operation_description=(
        'This endpoint allows authenticated users to retrieve details of a payment transaction by its ID, '
        'where the transaction belongs to the authenticated user. '
        'The response includes details such as ID, subscription_plan, paypal_transaction_id, amount, status, and subscription remaining days. '
        'This operation requires JWT authentication.'
    ),
    tags=['payment.transaction'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="The ID of the payment transaction to retrieve.", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: PaymentTransactionSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access their own transactions.',
        404: 'Not Found: Payment transaction with the specified ID does not exist.'
    }
)

user_list_payment_transaction_swagger = swagger_auto_schema(
    operation_summary='List Own Payment Transactions',
    operation_description=(
        'This endpoint allows authenticated users to retrieve a list of their own payment transactions. '
        'The response includes details for each transaction, such as ID, subscription_plan, paypal_transaction_id, amount, status, and subscription remaining days. '
        'This operation requires JWT authentication.'
    ),
    tags=['payment.transaction'],
    responses={
        200: PaymentTransactionSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.',
        403: 'Forbidden: User can only access their own transactions.'
    }
)