import json
def getRequestData(data,dataType = False):
    """
    Get request data from request object
    """
    if (dataType):
        formedData = {}
        for key in dataType:
            try:
                if (data[key] and data[key]['type'] and dataType[key]['type'] == data[key]['type']):
                    formedData[key] = data[key]['value']
                else:
                    raise Exception('Missing data type or value for ' + key + ' in ' + dataType[key]['type'] + ' format.')
            except:
                raise Exception('Missing data type or value for ' + key + ' in ' + dataType[key]['type'] + ' format.')
        
    return formedData