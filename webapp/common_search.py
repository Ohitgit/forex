from copy import deepcopy
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from array import array
#from butype.serializers import BusinessUnitTypeSerializer
#from butype.models import BusinessUnitType
#http://127.0.0.1:8000/businessunittype?search=Navsoft&page=1&page_size=5&ordering=ID_BSN_UN_TYPE&BSN_UN_TYPE_STATUS=A,equals,boolean&CRT_DT=2023,contains,date&MDF_BY=amit,startswith,string

SEARCH_CONTAINS = "%s__icontains"
def get_total_count(obj_model):
    return obj_model.objects.all().count()

def get_all_data(obj_model, obj_serializer, default_order):
    '''get result'''
    
    serach_response = {}
    ordering = default_order[0]
    queryset = obj_model.objects.all().order_by(ordering)    
    response_data = obj_serializer(queryset, many=True)    
    serach_response["data"] = response_data.data
    serach_response["total"] = queryset.count()
    serach_response["page_size"] = 40
    serach_response["offset"] = 0    
    return serach_response

def get_page_no(get_request):
    page = 1 
    if 'page' in get_request and len(get_request['page']) > 0 and get_request['page'][0] is not None and get_request['page'][0] != '':
        page = get_request['page']        
    return page

def get_offset(get_request):
    offset = 0
    if 'offset' in get_request and len(get_request['offset']) > 0 and get_request['offset'][0] is not None and get_request['offset'][0] != '':
        offset = get_request['offset']        
    return offset

def get_page_size(get_request):
    page_size = 40    
    if 'page_size' in get_request and len(get_request['page_size']) > 0 and get_request['page_size'][0] is not None and get_request['page_size'][0] != '':
        page_size = get_request['page_size']
    return page_size

def get_single_row_page_info(response, get_request):
    response["total"] = 1
    response["page"] = 1
    response["offset"] = 0
    response["page_size"] = get_page_size(get_request)
    return response

def get_filter_operator_list():
    string_filter_list = ['contains', 'notcontains', 'startswith', 'endswith', 'equals', 'notequals']
    date_filter_list = ['contains', 'notcontains', 'equals', 'notequals', 'lessthan', 'greaterthan', 'greaterequal', 'lesserequal']
    number_filter_list = ['equals', 'notequals', 'lessthan', 'greaterthan', 'greaterequal', 'lesserequal']
    status_filter_list = ['equals', 'notequals']    
    return string_filter_list, date_filter_list, number_filter_list, status_filter_list

def get_filter_operator_replace_list():    
    string_filter_replace_list = ['__icontains', '__icontains', '__istartswith', '__iendswith', '__iexact', '__iexact']
    date_filter_replace_list = ['__icontains', '__icontains', '__date', '__date', '__date__lt', '__date__gte', '__date__gte', '__date__lte']
    number_filter_replace_list = ['__iexact', '__iexact', '__lt', '__gte', '__gte', 'date__lte']
    status_filter_replace_list = ['__iexact', '__iexact'] 
    return string_filter_replace_list, date_filter_replace_list, number_filter_replace_list, status_filter_replace_list    

def get_filter_request_data(request_data):
    copy_request_data = deepcopy(dict(request_data))     
    copy_request_data.pop('offset', None)
    copy_request_data.pop('page', None)    
    copy_request_data.pop('page_size', None)
    copy_request_data.pop('ordering', None)
    copy_request_data.pop('search', None)
    copy_request_data.pop('status', None)
    return copy_request_data

def get_search_filter_query(search_query, filter_query):
    search_filter_query = Q()
    flag = 0
    if search_query is not None:
        search_filter_query.add((search_query), Q.AND)
        flag = 1

    if filter_query is not None:
        search_filter_query.add((filter_query), Q.AND)
        flag = 1
    
    return search_filter_query, flag



def get_search_value(obj_model, obj_serializer, search_fields, status_fields, date_fields, other_fields, default_order, request_data):
    """searching"""    
    print("request_data") 
    print(request_data) 
    print("search_fields") 
    print(search_fields) 
    print("obj_model")
    
    ordering = default_order[0]
    flag = 0
    valid = 1
    order_list = 0
    serach_response = {} 
    search_query = None
    filter_query = None
    
    ordering_list_name = ['CRT_BY', 'MDF_BY']
    page = get_page_no(request_data)
    page_size = get_page_size(request_data)
    offset = get_offset(request_data)        

    search_query = get_search_query(request_data, search_fields, ordering_list_name, date_fields, status_fields, other_fields)
    ordering, order_list = get_search_order(request_data, search_fields, ordering_list_name, date_fields, status_fields, other_fields, ordering)
    print('search_query')    
    print(search_query)
    print("ordering") 
    print(ordering)  
    print("order_list") 
    print(order_list)
    print("valid") 
    print(valid)  

    copy_request_data = get_filter_request_data(request_data)    
    print('copy_request_data')
    print(copy_request_data)

    filter_query = get_filter_query(copy_request_data, search_fields, ordering_list_name, date_fields, status_fields, other_fields)       
    print('filter_query')    
    print(filter_query)

    '''search_filter_query''' 
    search_filter_query, flag = get_search_filter_query(search_query, filter_query)
        
    print('search_filter_query')
    print(search_filter_query)
    print("flag")
    print(flag)
    
    '''search result'''
    limit = int(page_size)
    page = int(page)
    offset = int(offset)    
    serach_response["page"] = page
    serach_response["page_size"] = page_size
    serach_response["offset"] = offset
    serach_response["data"] = []   
    print("1")

    '''without filter'''
    if flag == 0 and valid == 1:
        print("2")
        if order_list == 1:
            print("3")
            queryset = obj_model.objects.all().order_by(*ordering)[offset:offset+limit]
        else:
            print("4")
            queryset = obj_model.objects.all().order_by(ordering)[offset:offset+limit]
        
        '''get result'''
        serach_response["total"] = get_total_count(obj_model)
        response_data = obj_serializer(queryset, many=True)      
        serach_response["data"] = response_data.data        
    
    '''using filter'''   
    if flag == 1 and valid == 1:
        print("5")
        if order_list == 1:
            print("6")            
            queryset = obj_model.objects.filter(search_filter_query).order_by(*ordering)[offset:offset+limit]
        else:
            print("7")
            queryset = obj_model.objects.filter(search_filter_query).order_by(ordering)[offset:offset+limit]
        
        '''get result'''
        serach_response["total"] = obj_model.objects.filter(search_filter_query).count() 
        response_data = obj_serializer(queryset, many=True)    
        serach_response["data"] = response_data.data        
        print("8")
    '''send result'''
    
    return serach_response

def get_filter_search_value(obj_model, obj_serializer, search_fields, status_fields, date_fields, other_fields, default_order, request_data):
    ordering = default_order[0]
    flag = 0
    valid = 1
    order_list = 0
    serach_response = {} 
    search_query = None
    filter_query = None
    print("django_orm_query",request_data['django_orm_query'])
    ordering_list_name = ['CRT_BY', 'MDF_BY']
    page = get_page_no(request_data)
    page_size = get_page_size(request_data)
    offset = get_offset(request_data)
    limit = int(page_size)
    page = int(page)
    offset = int(offset)    
    serach_response["page"] = page
    serach_response["page_size"] = page_size
    serach_response["offset"] = offset
    serach_response["data"] = []
    queryset = obj_model.objects.filter(request_data['django_orm_query']).order_by(ordering)[offset:offset+limit]
    serach_response["total"] = obj_model.objects.filter(request_data['django_orm_query']).count() 
    response_data = obj_serializer(queryset, many=True)    
    serach_response["data"] = response_data.data
    return serach_response


def get_search_order(request_data, search_fields, ordering_list_name, date_fields, status_fields, other_fields, ordering):
    
    order_list = 0
        
    if 'ordering' in request_data and len(request_data['ordering']) > 0 and request_data['ordering'][0] is not None and request_data['ordering'][0] != '':
        search_order = request_data['ordering'] 
        order = search_order       
        if search_order[0] == '-':
            order = search_order[1:]
        
        if order in search_fields or order in date_fields or order in status_fields or order in other_fields:
            ordering = search_order                       
    
        if order in ordering_list_name:
            ordering1 = search_order+str('__first_name')
            ordering2 = search_order+str('__last_name')
            ordering = [ordering1, ordering2]
            order_list = 1

    return ordering, order_list

def get_search_fields_query_string(search_fields, search_query, search_lookup):
    for sfields in search_fields:            
        q = Q(**{SEARCH_CONTAINS % sfields: search_lookup })
        if search_query is not None:
            search_query = search_query | q
        else:
            search_query = q
    return search_query

def get_status_fields_query_string(search_fields, search_query, search_lookup):
    stat_lst = ["active", "inactive"]
    if search_lookup.lower() in stat_lst:
        search_lookup = search_lookup[0]
    for sfields in search_fields:            
        q = Q(**{SEARCH_CONTAINS % sfields: search_lookup })
        if search_query is not None:
            search_query = search_query | q
        else:
            search_query = q
    return search_query

def get_date_search_fields_query_string(date_fields, search_query, search_lookup):
    for dfields in date_fields:
        dfields1 = dfields+str('__date')
        q = Q(**{SEARCH_CONTAINS % dfields1: search_lookup })
        if search_query is not None:
            search_query = search_query | q
        else:
            search_query = q
    return search_query

def get_user_search_fields_query_string(ordering_list_name, search_query, search_lookup):
    for ufields in ordering_list_name:
        ufields1 = ufields+str('__first_name')
        q = Q(**{SEARCH_CONTAINS % ufields1: search_lookup }) 
        if search_query is not None:
            search_query = search_query | q
        else:
            search_query = q

        ufields2 = ufields+str('__last_name')
        q = Q(**{SEARCH_CONTAINS % ufields2: search_lookup }) 
        if search_query is not None:
            search_query = search_query | q
        else:
            search_query = q 
    return search_query

def get_search_query(request_data, search_fields, ordering_list_name, date_fields, status_fields, other_fields):
    '''get_search_query'''
    search_query = None
    search_lookup = None
    
    if 'search' in request_data and len(request_data['search']) > 0 and request_data['search'][0] is not None and request_data['search'][0] != '':
        search_lookup = request_data['search']        
        
        """search in module searchable fields"""
        search_query = get_search_fields_query_string(search_fields, search_query, search_lookup)        

        '''search in created and modified by user'''
        search_query = get_user_search_fields_query_string(ordering_list_name, search_query, search_lookup)

        '''search in date type fields'''
        search_query = get_date_search_fields_query_string(date_fields, search_query, search_lookup)
        
        '''search for status and boolean type fields''' 
        search_query = get_status_fields_query_string(status_fields, search_query, search_lookup)      
        
        '''search in other type fields'''
        search_query = get_search_fields_query_string(other_fields, search_query, search_lookup)
        
    print('search_query') 
    print(search_query)
    
    return search_query

def validate_data_filter_list(data_filter_list, string_filter_list, date_filter_list, number_filter_list, status_filter_list):
    flag = True
    filter_value = None
    filter_type = None
    field_type = None

    if len(data_filter_list) != 3:
        flag = False

    filter_value = data_filter_list[0]
    filter_type = data_filter_list[1]
    field_type = data_filter_list[2]

    if filter_value is None or filter_type is None or field_type is None:
        flag = False
    if field_type == 'string' and filter_type not in string_filter_list:
        flag = False
    if field_type == 'date' and filter_type not in date_filter_list:
        flag = False
    if field_type == 'number' and filter_type not in number_filter_list:
        flag = False
    if field_type == 'boolean' and filter_type not in status_filter_list:
        flag = False

    return flag, filter_value, filter_type, field_type

def get_filter_expression(field_type, filter_type, string_filter_list, date_filter_list, number_filter_list, status_filter_list, string_filter_replace_list, date_filter_replace_list, number_filter_replace_list, status_filter_replace_list):
    
    filter_expression = ''
    if field_type == 'string' :
        index = string_filter_list.index(filter_type)                
        filter_expression = string_filter_replace_list[index]
    
    if field_type == 'date' :
        index = date_filter_list.index(filter_type)                
        filter_expression = date_filter_replace_list[index]
    
    if field_type == 'number' :
        index = number_filter_list.index(filter_type)                
        filter_expression = number_filter_replace_list[index]

    if field_type == 'boolean' :
        index = status_filter_list.index(filter_type)                
        filter_expression = status_filter_replace_list[index]

    return filter_expression

def get_user_filter_query_set(field, filter_type, filter_value, filter_expression, filter_query, ordering_list_name):
    field_user = ''
    user_filter_query = None
    field_user = field
    field = field+str('__first_name')

    if filter_type.startswith('not'):
        qry1 = ~Q(**{str(field) + str(filter_expression): filter_value})
    else:
        qry1 = Q(**{str(field) + str(filter_expression): filter_value})
    
    user_filter_query = qry1

    '''user name filter'''
    if field_user != '' and field_user in ordering_list_name:
        field2 = field_user+str('__last_name')
        if filter_type.startswith('not'):
            qry2 = ~Q(**{str(field2) + str(filter_expression): filter_value})
        else:
            qry2 = Q(**{str(field2) + str(filter_expression): filter_value})                 
        
        user_filter_query = user_filter_query | qry2                        

    
    if filter_query is not None:
        filter_query = filter_query & user_filter_query
    else:
        filter_query = user_filter_query

    return filter_query

def get_filter_query(copy_request_data, search_fields, ordering_list_name, date_fields, status_fields, other_fields):
    
    filter_query = None

    if len(copy_request_data) == 0: 
        return filter_query
    
    string_filter_list, date_filter_list, number_filter_list, status_filter_list = get_filter_operator_list()
    string_filter_replace_list, date_filter_replace_list, number_filter_replace_list, status_filter_replace_list = get_filter_operator_replace_list()
       
    for field in copy_request_data:
                    
        if field not in search_fields and field not in ordering_list_name and field not in status_fields  and field not in date_fields and field not in other_fields:
            continue 
        
        data_filter_str = copy_request_data[field]            
        data_filter_str = data_filter_str[0]            
        data_filter_list = data_filter_str.split(',')
        valid = False

        valid, filter_value, filter_type, field_type = validate_data_filter_list(data_filter_list, string_filter_list, date_filter_list, number_filter_list, status_filter_list)
        
        if not valid:
            continue        
        
        '''filtering'''        
        filter_expression = ''        
        filter_expression = get_filter_expression(field_type, filter_type, string_filter_list, date_filter_list, number_filter_list, status_filter_list, string_filter_replace_list, date_filter_replace_list, number_filter_replace_list, status_filter_replace_list)       

        print('filter_expression')
        print(filter_expression)

        if filter_expression == '' or filter_expression is None: 
            continue
        
        if field in ordering_list_name:
            filter_query = get_user_filter_query_set(field, filter_type, filter_value, filter_expression, filter_query, ordering_list_name)            

        else:
            filter_query = get_general_filter_query_set(field, filter_type, filter_value, filter_expression, filter_query)            

    return filter_query

def get_general_filter_query_set(field, filter_type, filter_value, filter_expression, filter_query):
    if filter_type.startswith('not'):
        qry = ~Q(**{str(field) + str(filter_expression): filter_value})
    else:
        qry = Q(**{str(field) + str(filter_expression): filter_value})
    
    if filter_query is not None:
        filter_query = filter_query & qry
    else:
        filter_query = qry  

    return filter_query