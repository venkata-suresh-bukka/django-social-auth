from django.shortcuts import render, redirect
from django.contrib.auth import logout
import os
from google.auth import default
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from google.cloud import compute_v1
from django.core.mail import send_mail
from django.http import HttpResponse
import requests
import hvac
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
# Initialize the Vault client
# Use the authenticated vault_client to access Vault resources


# Create your views here.
from django.http import HttpResponse
import hvac

vault_url = 'http://localhost:8200'

def authenticate_userpass(username, password):
    # Define the Vault URL
    vault_url = 'http://localhost:8200'

    # Define the user's credentials
    auth_data = {
        'password': password,
    }

    # Send a POST request to authenticate with Userpass
    response = requests.post(f'{vault_url}/v1/auth/userpass/login/{username}', json=auth_data)

    if response.status_code == 200:
        # Authentication successful; extract the Vault token
        auth_data = json.loads(response.text)
        vault_token = auth_data.get('auth', {}).get('client_token')

        if vault_token:
            return vault_token
        else:
            return None  # Token not found in the response
    else:
        return None  # Authentication failed

def get_gcp_instances(zone, vault_token):
    print('hi')
    try:
        # Initialize the Vault client with the obtained token
        vault_client = hvac.Client(url='http://localhost:8200', token=vault_token)

        # Define the path where the GCP service account key is stored in Vault
        vault_path = '/gcp_key'

        # Read the GCP service account key from Vault
        response = vault_client.secrets.kv.v2.read_secret_version(path=vault_path)
        service_account_key = response['data']['data']

        # print(service_account_key)
        # json_string_cleaned = service_account_key.replace('\n', '')
        # data = json.loads(json_string_cleaned)


        # print(data)

        # Initialize the Compute Engine client using the service account key
        print('hello')
        credentials = service_account.Credentials.from_service_account_info(service_account_key)
        compute = build('compute', 'v1', credentials=credentials)

        project = 'axial-module-393809'
        zone = 'us-west4-b'
        print(project)
        # List instances in the specified project and zone
        instances = compute.instances().list(project=project, zone=zone).execute()
        print("hi")
        # Extract relevant information from the instance list
        instance_details = []
        print(instance_details)
        instance_details = []
        for instance in instances.get('items', []):
           instance_details.append({
               'name': instance['name'],
               'status': instance['status'],
               'machine_type': instance['machineType'],
            # Add more fields as needed
           })

        return JsonResponse({'instances': instance_details})

        # Return the list of instance names as an HTTP response
    except hvac.exceptions.InvalidPath:
        # Handle the case where the path does not exist in Vault
        return HttpResponse("Service account key not found in Vault.")
    except Exception as e:
        # Handle other errors or exceptions that may occur when interacting with Vault or GCP
        return HttpResponse(f"Error: {str(e)}")

def home(request):
    try:
        # Define the username and password for authentication
        username = 'venkat'
        password = 'venkat'

        # Authenticate using Userpass and obtain a Vault token
        vault_token = authenticate_userpass(username, password)

        if vault_token:
            # Specify the GCP zone you want to fetch instances from
            gcp_zone = 'us-west4-b'

            # Fetch the list of GCP instances in the specified zone
            return get_gcp_instances(gcp_zone, vault_token)
        else:
            return HttpResponse("Authentication to Vault failed.")
    except Exception as e:
        # Handle other errors or exceptions that may occur
        return HttpResponse(f"Error: {str(e)}")

def logout_view(request):
    logout(request)
    return redirect("/")


@login_required
def get_instance_details(request):
    # Set up credentials
    creds, _ = default()

    # If credentials are not available or expired, request user's permission
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # If no valid credentials are found, redirect the user to the Google OAuth login
            # You can customize this URL to match your Django URL configuration
            return render(request, 'google_login.html')

    # Create a GCP Compute Engine service client
    compute = build('compute', 'v1', credentials=creds)

    # Specify your GCP project and zone
    project = 'vertical-hook-393809'
    zone = 'us-west4-b'

    # List instances in the specified project and zone
    instances = compute.instances().list(project=project, zone=zone).execute()
    # Extract relevant information from the instance list
    instance_details = []
    for instance in instances.get('items', []):
        instance_details.append({
            'name': instance['name'],
            'status': instance['status'],
            'machine_type': instance['machineType'],
            # Add more fields as needed
        })
    print(instance_details)

    return JsonResponse({'instances': instance_details})




