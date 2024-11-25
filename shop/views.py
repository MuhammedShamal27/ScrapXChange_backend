from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics,permissions
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from . serializer import *
from datetime import *
from user.serializers import ChatRoomSerializer,MessageSerializer
from django.db.models import Q
import socketio # type: ignore
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.


class ShopRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        serializer = ShopRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Shop registration request submitted successfully. Awaiting admin approval."},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class ShopLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        serializer = ShopLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ShopHomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user=request.user
        serializer = ShopHomeSerializer(user)
        return Response(serializer.data)

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_shop:
            raise PermissionDenied("You do not have permission to access this resource.")
        print('the user',self.request.user)
        return Category.objects.filter(user=self.request.user)


class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategoryCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        user = self.request.user
        if not user.shop.is_verified:
            raise PermissionDenied("Your shop is not verified.")
        serializer.save(user=user)

        
class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        category = super().get_object()
        print('category user',category,category.user,)
        if category.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this category.")
        return category
        
class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        
        category = self.get_object()
        print('category user',category,category.user,user)
        if category.user != user:
            raise PermissionDenied("You do not have permission to edit this category.")
        serializer.save()

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print(user)
        try:
            
            shop = Shop.objects.get(user=user)
            print('the user i get',user)
        except Shop.DoesNotExist:
            raise PermissionDenied("Shop associated with this user does not exist.")
        
        return Product.objects.filter(user=shop.user)
    

class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        try:
            shop = Shop.objects.get(user=user)
        except Shop.DoesNotExist:
            raise PermissionDenied("Shop associated with this user does not exist.")
        
        if not shop.is_verified==True:
            raise PermissionDenied("Only verified shops can create products.")
        
        serializer.save(user=user)

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        product = super().get_object()
        if product.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this product.")
        return product


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user

        try:
            shop = Shop.objects.get(user=user)
        except Shop.DoesNotExist:
            raise PermissionDenied("Shop associated with this user does not exist.")
        
        product = self.get_object()
        if product.user != user:
            raise PermissionDenied("You do not have permission to edit this product.")
        
        if not shop.is_verified:
            raise PermissionDenied("Only Verified shops can update products.")
        
        serializer.save()
        
class ScrapRequestListView(generics.ListAPIView):
    serializer_class = ScrapRequestListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        shop = self.request.user.shop
        if not shop:
            return CollectionRequest.objects.none()
        print('this is the shop name',shop)
        return CollectionRequest.objects.filter(shop=shop , is_accepted=False , is_rejected=False , is_scheduled=False)

    
        
class ScrapRequestDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class=ScrapRequestListSerializer
    lookup_field ='pk'
    
    def get(self,request,pk, *args, **kwargs):
        if not self.request.user.is_shop:
            raise PermissionDenied('Access to this page is only for the verified shop.')
        try:
            scrap_request = CollectionRequest.objects.get(pk=pk, shop=request.user.shop)
            serializer = self.serializer_class(scrap_request)
            return Response(serializer.data)
        except CollectionRequest.DoesNotExist:
            return Response({"error": "Scrap request not found."}, status=404)
        
        
class ScheduleRequestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SheduleSerializer
    
    def post(self,request,pk , *args, **kwargs):
        if not self.request.user.is_shop:
            raise PermissionDenied('Access to this page is only for the verified shop.')
        try:
            scrap_request= CollectionRequest.objects.get(pk=pk , shop=request.user.shop)
            serializer = self.serializer_class(scrap_request,data=request.data,context={'request':request})
            if not serializer.is_valid():
                print(serializer.errors)  
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            scrap_request.is_scheduled = True
            scrap_request.is_accepted = True
            scrap_request.scheduled_date = scrap_request.date_requested
            scrap_request.save()
            return Response({'message':'Request shedule succesfully'})
        except CollectionRequest.DoesNotExist:
            return Response({"error":"Scrap request not found."},status=status.HTTP_404_NOT_FOUND)        
            
class RescheduleRequestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RescheduleSerializer

    def post(self, request, pk, *args, **kwargs):
        if not self.request.user.is_shop:
            raise PermissionDenied('Access to this page is only for the verified shop.')

        try:
            scrap_request = CollectionRequest.objects.get(pk=pk, shop=request.user.shop)
        except CollectionRequest.DoesNotExist:
            return Response({"error": "Scrap request not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(scrap_request, data=request.data, context={'request': request})
        print('the serilaizer',serializer)
        if not serializer.is_valid():
            print('this is an error',serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        scrap_request.is_scheduled = True
        scrap_request.is_accepted = True
        serializer.save()
        return Response({'message': 'Request rescheduled successfully'})
    
    
class RejectRequestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ScrapRequestListSerializer
    
    def post(self,request,pk,*args, **kwargs):
        if not self.request.user.is_shop:
            raise PermissionDenied('Access to this page is only for the verified shop.')
        try:
            scrap_request = CollectionRequest.objects.get(pk=pk , shop=request.user.shop)
            scrap_request.is_rejected=True
            scrap_request.reject_message=request.data.get('reason','')
            scrap_request.save()
            return Response({'message':'Request has rejected.'})
        except CollectionRequest.DoesNotExist:
            return Response({'error':'Scrap request not found.'},status=status.HTTP_404_NOT_FOUND)
        
        
class TodayPendingRequestsView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = TodaySheduledSerializer

    def get_queryset(self):
        shop = self.request.user.shop
        if not shop:
            return CollectionRequest.objects.none()
        print('this is the shop name',shop)
        today = datetime.now().date()
        return CollectionRequest.objects.filter(shop=shop,scheduled_date__lte=today, is_accepted=True ,is_collected=False)
        
class PendingRequestsDetailsView(generics.RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = TodaySheduledSerializer
    lookup_field = 'id'

    def get_queryset(self):
        details=CollectionRequest.objects.filter( shop=self.request.user.shop)
        print('the deatils',details)
        return details
    
    
class ScrapCollectionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ScrapCollectionSerializer

    def post(self, request, *args, **kwargs):
        print('this is request ,',request.data)
        shop = self.request.user.shop  
        data = request.data

        collection_request_id = data.get('id')

        try:
            collection_request = CollectionRequest.objects.get(id=collection_request_id)
        except CollectionRequest.DoesNotExist:
            return Response({'error': 'Collection request not found.'}, status=status.HTTP_404_NOT_FOUND)

        if collection_request.shop != shop:
            return Response({'error': 'This collection request does not belong to your shop.'}, status=status.HTTP_403_FORBIDDEN)
        
        products = []
        for item in data.get('formData', []):
            product_data = {
                'product_id': item.get('id'),
                'quantity': item.get('quantity')
            }
            products.append(product_data)


        serializer_data = {
            'collection_request_id': collection_request_id,
            'transaction_products': products,
        }

        serializer = self.serializer_class(data=serializer_data)

        if serializer.is_valid():
            transaction = serializer.save()
            print('the details of the transactions',transaction)
            response_data = ScrapCollectionSerializer(transaction).data
            print('the response data',response_data)
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmCollectionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConfirmCollectionSerializer
    
    def get(self, request, id, *args, **kwargs):
        print(f"Request received for transaction id: {id}")
        try:
            transaction = Transaction.objects.get(id=id)
            print(f"Transaction found: {transaction}")
        except Transaction.DoesNotExist:
            print(f"Transaction with id {id} not found.")
            return Response({'error': 'Transaction not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class PaymentCashView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSuccessfullSerializer

    def post(self, request, id):
        print('the request comming ',self.request)
        try:
            transaction = Transaction.objects.get(id=id)
            transaction.payment_method = 'cash'
            collection_request = transaction.collection_request
            print('the collection_request comming to the backend',collection_request)
            collection_request.is_collected = True
            collection_request.save()
            transaction.save()
            serializer = self.serializer_class(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found.'}, status=status.HTTP_404_NOT_FOUND)


class InvoiceView(APIView):
    def get(self, request, id):
        print('the requesting data ',request)
        print('the requesting data ',id)
        transcation = Transaction.objects.get(id=id)
        print('the transcation  id is ',transcation)
        collection_request=CollectionRequest.objects.get(id=transcation)
        print('the collection request id is ',transcation)
        serializer = InvoiceSerializer(collection_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

class InvoiceView(APIView):
    def get(self, request, id):
        print('the requesting data ',id)

        try:
            transaction = Transaction.objects.get(id=id)
            print('the transcation  id is ',transaction)
            collection_request = transaction.collection_request
            print('the collection_request  id is ',collection_request)
            serializer = InvoiceSerializer(collection_request)
            # Return the serialized data
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found.'}, status=status.HTTP_404_NOT_FOUND)

        except CollectionRequest.DoesNotExist:
            return Response({'error': 'Collection Request not found.'}, status=status.HTTP_404_NOT_FOUND)


# -----------------------------------------------------------------------------------------------------------

class ShopCollectionRequestUsersView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        shop = self.request.user.shop
        queryset = CustomUser.objects.filter(collection_requests__shop=shop).distinct()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter( Q(username__icontains=search_query))

        return queryset


    
    
class ShopCreateOrFetchChatRoomView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopChatRoomSerializer
    
    def post(self, request, user_id):
        print('the requst comming',request)
        print('Received request for user_id:', user_id)
        try:
            user = CustomUser.objects.get(id=user_id)
            print('user found:', user)
        except CustomUser.DoesNotExist:
            print('user not found for id:', user_id)
            return Response({"error": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        
        shop_name = request.user.shop
        print('the shop id or shop',shop_name)
        username = shop_name.user
        print('the custom user name',username)
        shop = username.id
        print('the custom user',shop)
        chat_room, created = ChatRoom.objects.get_or_create(user=user,shop=shop)
        
        serializer = ShopChatRoomSerializer(chat_room)
        print('the serilizer data',serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    
class ShopChatRoomsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopChatRoomSerializer

    def get_queryset(self):

        user = self.request.user
        print('the user is ',user)
        chat_room = ChatRoom.objects.filter(shop__user=user)
        print('the chat rooms',chat_room)
        return chat_room

# Initialize Socket.IO server
sio = socketio.AsyncServer()
class ShopMessageView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, room_id):
        print('the coming request is in get ',request.data)
        room = get_object_or_404(ChatRoom, id=room_id)
        messages = room.messages.all()
        serializer = ShopMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, room_id):
        print('the coming request is in post ',request.data)
        try:
            room = get_object_or_404(ChatRoom, id=room_id)
            sender = request.user  # Assuming the user is authenticated
            print('the sender id ',sender)
            receiver_id = request.data.get('receiver_id')
            print('the reciever id ',receiver_id)
            message_text = request.data.get('message')
            
            file = request.data.get('file', None)  # Handle URL directly as it's a string
            print('The file:', file)
            image, video = None, None

            # Check if the file is a URL
            if file and isinstance(file, str):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                    print('This is an image URL')
                    image = file
                elif file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                    print('This is a video URL')
                    video = file

            message = Message.objects.create(
                room=room,
                sender=sender,
                receiver_id=receiver_id,
                message=message_text,
                image=image,
                video=video,
            )
            
            print ('the message details ',message)
            
                        # Emit message to WebSocket
            sio.emit('receive_message', {
                'message': message_text,
                'room_id': room_id,
                'sender_id': sender.id,
                'receiver_id': receiver_id,
                'image': message.image if message.image else None,
                'video': message.video if message.video else None,
                'timestamp': message.timestamp.isoformat(),
            }, room=room_id)


            return Response(ShopMessageSerializer(message).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class ShopProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        print ('the request comming',request.data)
        try:
            shop_profile = Shop.objects.get(user=request.user)
        except Shop.DoesNotExist:
            return Response({"error":"ShopProfile not found."},status=status.HTTP_404_NOT_FOUND)
        serializer =ShopProfileSerializer(shop_profile)
        return Response(serializer.data)
    
    
class ShopReportView(generics.CreateAPIView):
    serializer_class = ShopReportSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print('the request is arriving',request.data)
        receiver = request.data.get('receiver')
        print('reciver_id',receiver)
        reason = request.data.get('reason')
        print('the reason',reason)

        # Validate that receiver exists
        try:
            receiver = CustomUser.objects.get(id=receiver)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Receiver not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Create the report using the serializer
        serializer = self.get_serializer(data = request.data)
        if not serializer.is_valid():
            print('Serializer errors:', serializer.errors)  # Log errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(sender=request.user, receiver=receiver)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
class ShopGraphDataView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # Get transactions from the last 6 months
        today = now().date()
        six_months_ago = today - timedelta(days=180)

        transactions = (
            Transaction.objects.filter(date_picked__gte=six_months_ago)
            .values('date_picked__month')
            .annotate(total_spent=Sum('total_price'))
            .order_by('date_picked__month')
        )

        # Format response data
        months = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb']  # Example months
        total_spent = [t['total_spent'] for t in transactions]  # Total price sums

        data = {
            'months': months,
            'total_spent': total_spent,
            'total_spent_sum': sum(total_spent),
        }
        return Response(data)
    
class UpdateShopProfileView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # Add parsers for multipart data
    
    def put(self, request, *args, **kwargs):
        print('the request',request.data)
        user = request.user
        shop = get_object_or_404(Shop, user=user)
        print('the shop',shop)
        serializer = ShopProfileAndLocationSerializer(shop, data=request.data, partial=True)  

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print('the serilaizer error',serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ShopTransactionListView(generics.ListAPIView):
    serializer_class = TransactionsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the shop related to the current authenticated user
        shop = self.request.user.shop
        # Filter transactions related to the shop's collection requests
        return Transaction.objects.filter(collection_request__shop=shop)
    

class ShopDashboardView(APIView):
    def get(self, request):
        shop = request.user.shop  # Assuming the shop is the logged-in user
        today = now().date()

        # 1. Pending collections for today
        pending_collections = CollectionRequest.objects.filter(
            shop=shop, is_collected=False, is_scheduled=True
        )
        
        today_pending_collections = CollectionRequest.objects.filter(
            shop=shop, is_collected=False, is_scheduled=True, scheduled_date__lte=today
        )
                
        # 2. Users who completed transactions with the shop
        completed_transaction_users = CustomUser.objects.filter(
            collection_requests__transactions__collection_request__shop=shop
        ).distinct()

        # 3. Pending collection requests
        pending_requests = CollectionRequest.objects.filter(
            shop=shop, is_accepted=False, is_rejected=False,is_scheduled=False
        )

        # 4. All transactions related to the shop
        transactions = Transaction.objects.filter(collection_request__shop=shop)
        
        total_collected = transactions.aggregate(Sum('total_price'))['total_price__sum'] or 0


        data = {
            'pending_collections': pending_collections,
            'today_pending_collections':today_pending_collections,
            'completed_transaction_users': completed_transaction_users,
            'pending_requests': pending_requests,
            'transactions': transactions,
            'total_collected': total_collected
        }

        serializer = ShopDashboardSerializer(data)
        return Response(serializer.data)


class ShopNotificationCreateView(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = ShopNotificationCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
        
    
class ShopNotificationsView(generics.ListAPIView):
    serializer_class = ShopNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the current shop user from the request and filter notifications
        user = self.request.user
        if hasattr(user, 'shop'):
            # Filter notifications where the receiver is the current shop user
            return Notification.objects.filter(receiver=user)
        else:
            return Notification.objects.none()  # If the user is not a shop, return no notifications

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No notifications found."}, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class MarkNotificationAsReadView(generics.UpdateAPIView):
    serializer_class = ShopNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, notification_id):
        # Get the notification object by ID
        try:
            return Notification.objects.get(id=notification_id, receiver=self.request.user)
        except Notification.DoesNotExist:
            return None

    def put(self, request, notification_id, *args, **kwargs):
        notification = self.get_object(notification_id)
        if not notification:
            return Response({"error": "Notification not found or you do not have permission to access it."}, status=status.HTTP_404_NOT_FOUND)

        # Mark the notification as read
        notification.is_read = True
        notification.save()

        return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)