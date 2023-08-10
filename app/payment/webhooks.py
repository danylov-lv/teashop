import stripe
from stripe.error import SignatureVerificationError
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from .tasks import payment_completed
from shop.recommender import Recommender


@csrf_exempt
def stripe_webhook(request: HttpRequest):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        return HttpResponse(status=400)
    except SignatureVerificationError:
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            order.paid = True
            order.stripe_id = session.payment_intent
            order.save()

            payment_completed.delay(order.id)

            r = Recommender()
            products = [item.product for item in order.items.all()]

            r.products_bought(products)

    return HttpResponse(status=200)
