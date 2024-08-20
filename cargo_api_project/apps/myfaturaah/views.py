# views.py

from rest_framework import status
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import xml.etree.ElementTree as ET
import json  # Import the json module

class PaymentView(APIView):

    def post(self, request):
        if request.method == 'POST':
            amount = int(request.data.get('amount'))
            
            # Prepare data for the payment request
            payment_data = {
                'Api_Key': "rLtt6JWvbUHDDhsZnfpAhpYk4dxYDQkbcPTyGaKp2TYqQgG7FGZ5Th_WD53Oq8Ebz6A53njUoo1w3pjU1D4vs_ZMqFiz_j0urb_BH9Oq9VZoKFoJEDAbRZepGcQanImyYrry7Kt6MnMdgfG5jn4HngWoRdKduNNyP4kzcp3mRv7x00ahkm9LAK7ZRieg7k1PDAnBIOG3EyVSJ5kK4WLMvYr7sCwHbHcu4A5WwelxYK0GMJy37bNAarSJDFQsJ2ZvJjvMDmfWwDVFEVe_5tOomfVNt6bOg9mexbGjMrnHBnKnZR1vQbBtQieDlQepzTZMuQrSuKn-t5XZM7V6fCW7oP-uXGX-sMOajeX65JOf6XVpk29DP6ro8WTAflCDANC193yof8-f5_EYY-3hXhJj7RBXmizDpneEQDSaSz5sFk0sV5qPcARJ9zGG73vuGFyenjPPmtDtXtpx35A-BVcOSBYVIWe9kndG3nclfefjKEuZ3m4jL9Gg1h2JBvmXSMYiZtp9MR5I6pvbvylU_PP5xJFSjVTIz7IQSjcVGO41npnwIxRXNRxFOdIUHn0tjQ-7LwvEcTXyPsHXcMD8WtgBh-wxR8aKX7WPSsT1O8d8reb2aR7K3rkV3K82K_0OgawImEpwSvp9MNKynEAJQS6ZHe_J_l77652xwPNxMRTMASk1ZsJL",
                'PaymentMethodId': 1,  # 1 represents KNET payment method, adjust as needed
                'Price': amount,
                # Add other payment data as needed
            }
            
            # Send the payment request to MyFatoorah to obtain the payment URL
            response = requests.post('https://apitest.myfatoorah.com', json=payment_data)

            if response.status_code == 200:
                try:
                    # Check if the response content is not empty
                    if response.text.strip():  # Check if there are non-whitespace characters
                        data = response.json()
                        return Response({"msg": "MyFatoorah Payment Gateway", 'code': response.status_code, 'url': data})
                        payment_url = data.get('Data', {}).get('PaymentURL')
                        
                        if payment_url:
                            return Response({"msg": "MyFatoorah Payment Gateway", 'code': response.status_code, 'url': payment_url})
                        else:
                            return Response({"error": "Payment URL not found in the response"})
                    else:
                        return Response({"error": "Empty response from the API"})
                except json.JSONDecodeError as e:
                    # Handle JSONDecodeError
                    return Response({"error": f"JSONDecodeError: {str(e)}"})
            else:
                # Handle other status codes and inspect the response content
                print(f"Response Content: {response.text}")
                return Response({"error": "Payment request failed"})
        else:
            pass
