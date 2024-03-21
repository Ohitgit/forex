from urllib import response
from django.conf import settings
from drf_yasg import openapi


def brand_create_schema():
    '''Generate butype Schema'''

    brand_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'ID_BRN': openapi.Schema(type=openapi.TYPE_STRING, description='Brand ID'),
            'NM_BRN': openapi.Schema(type=openapi.TYPE_STRING, description='Brand Name'),            
        }, required=['NM_BRN'])

    return brand_schema

brand_params = [
    openapi.Parameter("ID_BRN",
                      openapi.IN_PATH,
                      description="Brand ID",
                      type=openapi.TYPE_INTEGER
                      )
]
brandlist_response = openapi.Schema(
        type=openapi.TYPE_ARRAY, description='Array of Brand',
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ID_BRN': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='Brand ID'),
                'NM_BRN': openapi.Schema(type=openapi.TYPE_STRING,
                                         description='Brand Name'),
                'SC_BRN': openapi.Schema(type=openapi.TYPE_STRING,
                                              description='Brand type Status (A/I)'),
                'DE_BRN':openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Brand Description'),
                'CD_BRN_GRDG':openapi.Schema(type=openapi.TYPE_STRING,
                                             description="Brand Code"),
                'NM_MF':openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Manufacturer Name'),
                'ID_BR_PRNT':openapi.Schema(type=openapi.TYPE_STRING,
                                            description='Parent Brand'),                           
                'CRT_DT': openapi.Schema(type=openapi.TYPE_STRING,
                                         description='Created Date'),
                'CRT_BY': openapi.Schema(type=openapi.TYPE_STRING,
                                               description='Created By'),
                'MDF_DT': openapi.Schema(type=openapi.TYPE_STRING,
                                         description='Modified Date'),
                'MDF_BY': openapi.Schema(type=openapi.TYPE_STRING,
                                               description='Modified By'),                               
            }
        )
    )




status_request_schema = request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'ids': openapi.Schema(type=openapi.TYPE_ARRAY, description='Brand Id list',
                                items=openapi.Items(type=openapi.TYPE_INTEGER, description='Brand Id')),
        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Brand status (A/I)'),
    }, required=['ids', 'status']
)
delete_request_schema = request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'ids': openapi.Schema(type=openapi.TYPE_ARRAY, description='List of Ids', items=openapi.Items(type=openapi.TYPE_INTEGER, description='Brand ID list')),
    }, required=['ids']
)

multiple_status_update_response_schema = {
    "200": openapi.Response(
        description="Status Successfully Updated",
    ),
    "400": openapi.Response(
        description="Bad Request"
    )
}


multiple_delete_response_schema = {
    "200": openapi.Response(
        description="BusinessUnitType Successfully Deleted",
    ),
    "400": openapi.Response(
        description="Bad Request"
    )
}
