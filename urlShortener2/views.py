from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from urlShortener2.models import ShortenedURL
import string
import random
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import ShortenedURL

def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(7))
    return short_url

@csrf_exempt
def shorten_url(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            # Validate the URL
            url_validator = URLValidator()
            try:
                url_validator(url)
            except ValidationError:
                return HttpResponse("Invalid URL", status=400)
            
            # Generate a short URL
            short_url = generate_short_url()

            # Save the original and short URLs to the database
            shortened_url = ShortenedURL(original_url=url, short_url=short_url)
            shortened_url.save()

            response_data = {"shortUrl": f"http://localhost:3000/{short_url}"}
            return JsonResponse(response_data, status=201)
        return HttpResponse("URL not provided", status=400)
    return HttpResponse(status=405)

@api_view(['GET'])
def redirect_url(request, short_url):
    try:
        shortened_url = ShortenedURL.objects.get(short_url=short_url)
        return JsonResponse({"originalUrl": shortened_url.original_url})
    except ShortenedURL.DoesNotExist:
        return JsonResponse({"error": "Short URL not found."}, status=status.HTTP_404_NOT_FOUND)
