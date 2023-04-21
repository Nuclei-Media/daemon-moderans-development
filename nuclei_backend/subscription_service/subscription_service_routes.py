from .main import subscription_service
import stripe


@subscription_service.on_event("startup")
def init():
    stripe.api_key = "sk_test_51MZam8BBhtwo2YoBvQUqhfOs3DT8kLdeaeB1rQWlPqQ6YebE8q1xa7wJHnuukFdkigoFKswQxy1gMhdDiihI0vWY000JNOTrYa"
