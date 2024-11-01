from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from fcm_django.models import FCMDevice


# Create your views here.
class SaveFcmToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        token = request.data.get('token')
        
        if not token:
            return Response({"status": "error", "message": "Token not provided"}, status=400)
        
        # Use FCMDevice to store or update the token
        device, created = FCMDevice.objects.update_or_create(
            user=user,
            defaults={"registration_id": token, "type": "web"}
        )
        return Response({"status": "success", "message": "Token saved successfully"})
class NotifyShop(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            shop_id = request.data.get('shop_id')
            message_body = request.data.get('message', 'New Scrap Collection Request')
            
            # Debug information
            devices = FCMDevice.objects.filter(user_id=shop_id)
            for device in devices:
                print(f"""
                Device Details:
                - ID: {device.id}
                - Name: {device.name}
                - Registration ID: {device.registration_id}
                - Type: {device.type}
                - User ID: {device.user_id}
                - Active: {device.active}
                """)
            
            if not devices.exists():
                return Response({"status": "error", "message": "No device tokens found for this shop"}, status=404)
            
            # Send notification using the correct syntax
            result = devices.send_message(
                message={
                    "notification": {
                        "title": "New Notification",
                        "body": message_body,
                    }
                }
            )
            
            return Response({
                "status": "success", 
                "message": "Notification sent successfully",
                "device_count": devices.count(),
                "result": str(result)
            })
            
        except Exception as e:
            print(f"Error details: {str(e)}")
            return Response({"status": "error", "message": str(e)}, status=500)
# class SaveFcmToken(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         print('the sfcm token',request.data)
#         user = request.user
#         print('the user',user)
#         token = request.data.get('token')
#         if token:
#             FCMToken.objects.update_or_create(user=user, defaults={'token': token})
#             return Response({"status": "success", "message": "Token saved successfully"})
#         return Response({"status": "error", "message": "Token not provided"}, status=400)

# class NotifyShop(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def post(self, request):
#         print('the data coming as notification .',request.data)
#         shop_id = request.data.get('shop_id')  
#         message = request.data.get('message', 'New Scrap Collection Request')

#         # Retrieve shop's FCM tokens
#         devices = FCMToken.objects.filter(user_id=shop_id)
#         if not devices.exists():
#             return Response({"status": "error", "message": "No device tokens found for this shop"}, status=404)
        
#         # Send notification using Firebase
#         for device in devices:
#             device_instance = FCMDevice(token=device.token)
#             device_instance.send_message(title="New Notification", body=message)
        
#         return Response({"status": "Notification sent successfully"})
