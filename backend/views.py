from rest_framework.decorators import api_view
from django.http import JsonResponse
import subprocess


@api_view(['POST'])
def update_server(request):
    if 'secret_key' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing secret key'})
    try:
        server_key = ''.join(open('.django_update_key').readlines()).strip()
        if server_key == request.data['secret_key'].strip():
            print("should match")
            subprocess.run(["git", "pull"])
            return JsonResponse({'success': True})
        else:
            print(server_key, request.data['secret_key'])
            return JsonResponse({'success': False, 'message': 'Keys don\'t match'})
    except IOError as e:
        print(e)
        return JsonResponse({'success': False, 'message': 'Couldn\'t get key in server'})
