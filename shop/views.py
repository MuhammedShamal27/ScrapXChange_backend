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
import razorpay
from django.db.models import Q

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
        today = timezone.now().date()
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
        index = 0

        while True:
            product_id_key = f'formData[{index}][id]'
            quantity_key = f'formData[{index}][quantity]'
            if product_id_key in data and quantity_key in data:
                product_data = {
                    'product_id': data[product_id_key],
                    'quantity': data[quantity_key]
                }
                products.append(product_data)
                index += 1
            else:
                break

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

class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id): 
        print('the request data',request.data)
        # Accept the transaction ID as a parameter
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        try:
            transaction = Transaction.objects.get(id=id)
            amount = int(transaction.total_price * 100)  # Convert to paise

            razorpay_order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1"
            })
            transaction.razorpay_order_id = razorpay_order['id']
            transaction.save()
            
            collection_request = transaction.collection_request
            if collection_request:
                collection_request.is_collected = False
                collection_request.save()
                
            return Response({
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency']
            }, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        print('Received payment verification data:', request.data)
        params_dict = {
            'razorpay_order_id': request.data.get('razorpay_order_id'),
            'razorpay_payment_id': request.data.get('razorpay_payment_id'),
            'razorpay_signature': request.data.get('razorpay_signature')
        }

        try:
            # Verifying the signature
            client.utility.verify_payment_signature(params_dict)
            
            transaction = Transaction.objects.get(razorpay_order_id=request.data.get('razorpay_order_id'))
            transaction.payment_method = 'upi'
            transaction.razorpay_order_id = request.data.get('razorpay_order_id')
            transaction.payment_id = request.data.get('razorpay_payment_id')
            transaction.save()
            
            collection_request = transaction.collection_request
            if collection_request:
                collection_request.is_collected = True
                collection_request.save()

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except razorpay.errors.SignatureVerificationError:
            print('Signature verification failed.')
            return Response({'status': 'failure'}, status=status.HTTP_400_BAD_REQUEST)
        except Transaction.DoesNotExist:
            print('Transaction not found for order ID:', request.data.get('razorpay_order_id'))
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print('An error occurred:', str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

            return Response(ShopMessageSerializer(message).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)