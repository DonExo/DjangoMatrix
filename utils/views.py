import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from matrix.models import Package
from utils.models import Report
from utils.utils import get_client_ip_address


def report_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            if data:
                report_type = data.pop('type', None)
                package_slug = data.pop('package_slug', None)
                if package_slug:
                    package = get_object_or_404(Package, slug=package_slug)
                allowed_keys = {'existing_version', 'compatible_django', 'package_version', 'details', 'package_slug'}
                filtered_data = {key: value for key, value in data.items() if key in allowed_keys}

                client_ip = get_client_ip_address(request)
                Report.objects.create(
                    package=package,
                    report_type=report_type,
                    data=filtered_data,
                    ip_address=client_ip,
                )

                return JsonResponse({'status': 'success', 'received_data': data})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)