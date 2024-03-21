from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.contrib.auth.models import User
# from sqyapp import common_func

# def get_mongo_brand_search_query(request_data):
#     query = {}
#     if "ID_BRN" in request_data and request_data["ID_BRN"] is not None:
#         brand_id = request_data["ID_BRN"]
#         query = {"ID_BRN":int(brand_id)}    
#     return query

def valid_post(request):
    if validate_brand_name_entry(request) is not True:
        return validate_brand_name_entry(request)
        
    # if location.objects.filter(city=request.data["city"]).exists():
    #     return Response({'message': get_already_exist_msg()}, status=status.HTTP_400_BAD_REQUEST) 
    
    # return True

# def valid_put(request, obj_id):
#     if validate_brand_name_entry(request) is not True:
#         return validate_brand_name_entry(request)
    
#     if Brand.objects.filter(NM_BRN=request.data["NM_BRN"]).exclude(ID_BRN=obj_id).exists():
#         return Response({'message': get_already_exist_msg()}, status=status.HTTP_400_BAD_REQUEST) 
    
#     return True


def validate_brand_name_entry(request):
    if "business_name" not in request.data:
        return Response({'message': get_name_req_msg()}, status=status.HTTP_400_BAD_REQUEST)
    
    # if "map_url" not in request.data:
    #     return Response({'message': "map_url name is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # if "open_time" not in request.data:
    #     return Response({'message': "open_time name is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # if "close_time" not in request.data:
    #     return Response({'message': "close_time name is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # if "weekday_off" not in request.data:
    #     return Response({'message': "weekday_off name is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # if "pincode" not in request.data:
    #     return Response({'message': "pincode name is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # if "state" not in request.data:
    #     return Response({'message': "state name is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    return True


def get_not_found_msg():
    msg = "Location does not exists"
    return msg

def get_already_exist_msg():
    msg = "Location name already exists"
    return msg

def get_name_req_msg():
    msg = "business_name name is required"
    return msg

def get_email_req_msg():
    msg = "City is required"
    return msg
def get_invalid_id_msg():
    msg = "Invalid User ID Provided"
    return msg

def get_create_success_msg():
    msg = "Inquiry  created successfully"
    return msg

def get_update_success_msg():
    msg = "Inquiry updated successfully"
    return msg

def get_delete_success_msg():
    msg = "Inquiry deleted successfully"
    return msg

def get_status_update_success_msg():
    msg = "Inquiry Status updated successfully"
    return msg



