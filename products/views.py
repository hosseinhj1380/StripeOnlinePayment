
import stripe
from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import  HttpResponse
from django.views import View
from .models import Product


from pymongo import MongoClient

client = MongoClient("127.0.0.1:27017")

db = client["datasets"]

# Access a collection
collection = db["stripe_users_subscription"]


YOUR_DOMAIN="127.0.0.1:8000"
stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductLandingPageView(TemplateView):
    template_name = "landing.html"

    # def get_context_data(self, **kwargs):
    #     product = Product.objects.get(name="test")
    #     context = super(ProductLandingPageView, self).get_context_data(**kwargs)
    #     context.update({
    #         "product": product,
    #         "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
    #     })
    #     return context


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        product = Product.objects.get(id=product_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        subscription = stripe.Subscription.create()
        


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)


    if event["type"] == "customer.subscription.updated":
        intent = event["data"]["object"]["id"]
        
        res={
            "id_user_subscription":intent
        }
        
        collection.insert_one(res)
        # print(intent)


    return HttpResponse(status=200)


# class StripeIntentView(View):
#     def post(self, request, *args, **kwargs):
#         try:
#             req_json = json.loads(request.body)
#             customer = stripe.Customer.create(email=req_json['email'])
#             product_id = self.kwargs["pk"]
#             product = Product.objects.get(id=product_id)
#             intent = stripe.PaymentIntent.create(
#                 amount=product.price,
#                 currency='usd',
#                 customer=customer['id'],
#                 metadata={
#                     "product_id": product.id
#                 }
#             )
#             return JsonResponse({
#                 'clientSecret': intent['client_secret']
#             })
#         except Exception as e:
#             return JsonResponse({ 'error': str(e) })