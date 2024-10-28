from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status,permissions
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.exceptions import NotFound,PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from .serializers import *
from .generate_otp import *
import logging
from .tasks import generate_and_send_otp
import socketio # type: ignore

# Create your views here.

# -------- User Register -----------
# ----------------------------------

class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        user_serializer=UserRegistrationSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            generate_and_send_otp.delay(user.email)           
            return Response({'message':'User registered succesfully'},status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
# -------- OTP Verification --------
# ----------------------------------


class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user =serializer.save()
            refresh =RefreshToken.for_user(user)
            return Response({
                'message':'OTP Verified succesfully. User account activated',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },status=status.HTTP_200_OK)
        logger.warning(f'Invalid data :{serializer.errors}')
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



# -------- Resend OTP --------------
# ----------------------------------


class ResendOTPView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        print(self.request.data)
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user_profile = serializer.context['user_profile']
            user_profile.otp = ''
            user_profile.otp_generated_at = None
            user_profile.save()
            generate_and_send_otp.delay(email)
            return Response({'message':'OTP sent successfully.'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


# -------- Password Reset ----------
# ----------------------------------

class PasswordResetRequestView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer = PasswordRestRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
            generate_and_send_otp.delay(email)
            return Response({'message':'OTP sent for password reset.'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


# -------- Email Verification ------
# ----------------------------------

class EmailOTPVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self ,request):
        serializer = EmailOTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
            
            user_profile.otp =None
            user_profile.save()
            return Response({"message":"OTP verified successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
# -------- Password Reset ----------
# ----------------------------------


class PasswordResetView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Password reset successful.'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


# -------- User Login --------------
# ----------------------------------


logger = logging.getLogger(__name__)
class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        logger.info("userlogin",request.data)
        serializer = UserLoginSerializer(data=request.data)
        logger.info("the serilzier",serializer)
        if serializer.is_valid():
            return Response(serializer.validated_data,status=status.HTTP_200_OK)
        logger.warning(f"serializer errors:{serializer.errors}")
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


# -------- Home Page ---------------
# ----------------------------------


class HomePageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        logger.debug(f'Recieved data :{request.user}')
        user=request.user
        serializer = HomePageSerializer(user)
        logger.debug(f'Recieved data :{serializer.data}')
        return Response(serializer.data)

# -------- User Profile ------------
# ----------------------------------

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error":"UserProfile not found."},status=status.HTTP_404_NOT_FOUND)
        serializer =UserProfileSerializer(user_profile)
        return Response(serializer.data)

# -------- Edit Profile ------------
# ----------------------------------

class EditUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_profile =UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error":"UserProfile not found."},status=status.HTTP_400_BAD_REQUEST)
        serializer =EditUserProfileSerializer(user_profile)
        print('this is the get method',serializer)
        return Response(serializer.data)

    def put(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found."}, status=status.HTTP_404_NOT_FOUND)
        print(request.data.get('profile_picture'))
        if isinstance(request.data.get('profile_picture'), str):
            request_data = request.data.copy()
            request_data.pop('profile_picture', None)
            serializer = EditUserProfileSerializer(user_profile, data=request_data, partial=True)
        else:
            serializer = EditUserProfileSerializer(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------- Shop List ---------------
#According to the given State and District
# ----------------------------------    

class ShopListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopListSerializer

    def get_queryset(self):
        
        queryset = Shop.objects.filter(
            user__is_superuser=False, 
            user__is_shop=True, 
            is_blocked=False, 
            is_verified=True, 
            is_rejected=False
        )
        
        # Extract query parameters
        state = self.request.query_params.get('state', None)
        district = self.request.query_params.get('district', None)

        # Filter queryset based on state and district if provided
        if state:
            queryset = queryset.filter(state=state)
        if district:
            queryset = queryset.filter(district=district)

        return queryset


# -------- Shop Product List -------
# ---------------------------------- 


class ShopProductListView(ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        shop_id = self.kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            raise NotFound(detail="Shop not found")
        user = shop.user
        return Category.objects.filter(user=user).distinct()


# ----- Scrap Collection Request ---
# ----------------------------------
  
class CollectionRequestCreateView(APIView):
    def post(self, request, *args, **kwargs):
        print('the data', request.data)
        
        # Get the last request submitted by the user for the same shop
        last_request = CollectionRequest.objects.filter(user=request.user, shop=request.data.get('shop')).order_by('-created_at').first()
        
        # If there's a previous request, compare it with the current data
        if last_request:
            current_request_data = request.data.copy()
            last_request_data = {
                'shop': last_request.shop.id,
                'date_requested': last_request.date_requested,
                'name': last_request.name,
                'address': last_request.address,
                'landmark': last_request.landmark,
                'pincode': last_request.pincode,
                'phone': last_request.phone,
                'upi': last_request.upi,
                'products': list(last_request.products.values_list('id', flat=True)),
                'add_note': last_request.add_note,
            }

            # Convert the 'products' field to lists and compare
            current_request_products = request.data.getlist('products[]') if 'products[]' in request.data else []
            last_request_products = last_request_data['products']

            # Check if the current request data matches the last one
            if (
                current_request_data['shop'] == str(last_request_data['shop']) and
                current_request_data['date_requested'] == str(last_request_data['date_requested']) and
                current_request_data['name'] == last_request_data['name'] and
                current_request_data['address'] == last_request_data['address'] and
                current_request_data['landmark'] == last_request_data['landmark'] and
                current_request_data['pincode'] == last_request_data['pincode'] and
                current_request_data['phone'] == last_request_data['phone'] and
                current_request_data['upi'] == last_request_data['upi'] and
                sorted(current_request_products) == sorted(last_request_products) and
                current_request_data['add_note'] == last_request_data['add_note']
            ):
                return Response({"detail": "You have already submitted this request."}, status=status.HTTP_400_BAD_REQUEST)

        # If it's a new or different request, proceed with saving
        serializer = CollectionRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
        
        
# -------- Shop List For Message ---
# ---------------------------------- 


class MessageShopListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopListSerializer

    def get_queryset(self):
        queryset = CustomUser.objects.filter(is_superuser=False, is_shop=True, shop__is_verified=True)
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter( Q(shop__shop_name__icontains=search_query))
            print('the query set' , queryset)
        return queryset


# -------- ChatRoom Creation -----------
# --------------------------------------


class UserCreateOrFetchChatRoomView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, shop_id):
        print('the requst comming',request.data)
        print('Received request for shop_id:', shop_id)
        user = request.user
        try:
            shop = Shop.objects.get(id=shop_id)
            print('Shop found:', shop)
        except Shop.DoesNotExist:
            print('Shop not found for id:', shop_id)
            return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)

        chat_room, created = ChatRoom.objects.get_or_create(user=user, shop=shop)
        serializer = ChatRoomSerializer(chat_room)

        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    

class UserChatRoomsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(user=user)


 
# -------- User Message -----------
# ---------------------------------

# Initialize Socket.IO server
sio = socketio.AsyncServer()
class UserMessageView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, room_id):
        print('the coming request is in get ',request.data)
        room = get_object_or_404(ChatRoom, id=room_id)
        messages = room.messages.all()
        serializer = MessageSerializer(messages, many=True)
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
            
            # Check for files in the request
            file = request.FILES.get('file', None)
            print('the files',file)
            image, video = None, None
            audio = request.FILES.get('audio', None)

            if file:
                if file.content_type.startswith('image/'):
                    print('this is image')
                    image = file
                elif file.content_type.startswith('video/'):
                    print('this is video')
                    video = file

            message = Message.objects.create(
                room=room,
                sender=sender,
                receiver_id=receiver_id,
                message=message_text,
                image=image,
                video=video,
                audio=audio
            )
            
            print ('the message details ',message)
            
            # Emit message to WebSocket
            sio.emit('receive_message', {
                'message': message_text,
                'room_id': room_id,
                'sender_id': sender.id,
                'receiver_id': receiver_id,
                'image': message.image.url if message.image else None,
                'audio': message.audio.url if message.audio else None,
                'video': message.video.url if message.video else None,
                'timestamp': message.timestamp.isoformat(),
            }, room=room_id)

            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class UserReportView(generics.CreateAPIView):
    serializer_class = UserReportSerializer
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
        
        # Check if the user has already reported this receiver in the last week
        one_week_ago = timezone.now() - timedelta(weeks=1)
        if Report.objects.filter(sender=request.user, receiver=receiver, timestamp__gte=one_week_ago).exists():
            return Response({'message': 'You have already reported this shop you can not reported multiple times.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the report using the serializer
        serializer = self.get_serializer(data = request.data)
        if not serializer.is_valid():
            print('Serializer errors:', serializer.errors)  # Log errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(sender=request.user, receiver=receiver)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        
class CompletedTransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]  # Ensure that the user is authenticated

    def get_queryset(self):
        user = self.request.user  # Get the authenticated user
        # Filter transactions where the related CollectionRequest is marked as collected
        return Transaction.objects.filter(
            collection_request__user=user,
            collection_request__is_collected=True
        )
        
class UserNotificationView(generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(
            receiver=user
        ).order_by('-created_at')
        
class MarkNotificationAsReadView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, id):
        try:
            notification = Notification.objects.get(id=id, receiver=request.user)
            notification.is_read = True
            notification.save()
            return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        
class UserDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        transactions = Transaction.objects.filter(collection_request__user=user)
        pending_pickups = CollectionRequest.objects.filter(user=user, is_accepted=True, is_scheduled=True, is_collected=False)
        total_collections = CollectionRequest.objects.filter(user=user, is_collected=True)
        total_collected_value = total_collections.aggregate(total_price=models.Sum('transactions__total_price'))['total_price'] or 0
        today = date.today()
        today_pending_pickups = CollectionRequest.objects.filter(user=user, is_scheduled=True, scheduled_date__lte=today, is_collected=False)
        pending_requests = CollectionRequest.objects.filter(user=user, is_accepted=False, is_scheduled=False)

        dashboard_data = {
            'transactions': transactions,
            'pending_pickups': pending_pickups,
            'total_collections': total_collections,
            'total_collected_value': total_collected_value,
            'today_pending_pickups': today_pending_pickups,
            'pending_requests': pending_requests
        }

        serializer = DashboardSerializer(dashboard_data)
        return Response(serializer.data)