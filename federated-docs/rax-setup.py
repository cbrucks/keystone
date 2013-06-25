import urllib
import urllib2
import json

BASE_URL="http://localhost"

""" Make a request to keystone """
def keystoneRequest(endpoint, data = {}, method = "GET"):
    headers = {'X-Auth-Token': 'admin'}
    if method == "GET":        
        req = urllib2.Request(endpoint, headers = headers)
        response = urllib2.urlopen(req)
    elif method == "PUT":
        req = urllib2.Request(endpoint, headers = headers)        
        req.get_method = lambda: 'PUT'
        response = urllib2.urlopen(req)
        return
    elif method == "POST":
        data = json.dumps(data)
        headers['Content-Type'] = 'application/json'
        req = urllib2.Request(endpoint, data, headers)
        response = urllib2.urlopen(req)
    return json.loads(response.read())



print "Adding Identity Providers"
kentproxy = {"service":{"name":"Rax","description": "Rackspace Public Cloud", "type":"idp.rax"}}
serviceEndpoint = BASE_URL+":5000/v3/services"
proxy = keystoneRequest(serviceEndpoint, kentproxy, "POST")
print "OK"

print "Adding Endpoints"
kentendpoint = "https://identity.api.rackspacecloud.com/v2.0"
proxycertdata = "MIIDXDCCAsWgAwIBAgIJANHDiJSSuTu+MA0GCSqGSIb3DQEBBQUAMH0xCzAJBgNVBAYTAkdCMQ0wCwYDVQQIEwRLZW50MRMwEQYDVQQHEwpDYW50ZXJidXJ5MRswGQYDVQQKExJVbml2ZXJzaXR5IG9mIEtlbnQxCzAJBgNVBAsTAkNTMSAwHgYDVQQDExdpZHAuc2hpbnRhdTIua2VudC5hYy51azAeFw0xMDExMDgxMzI4MDVaFw0yMDExMDcxMzI4MDVaMH0xCzAJBgNVBAYTAkdCMQ0wCwYDVQQIEwRLZW50MRMwEQYDVQQHEwpDYW50ZXJidXJ5MRswGQYDVQQKExJVbml2ZXJzaXR5IG9mIEtlbnQxCzAJBgNVBAsTAkNTMSAwHgYDVQQDExdpZHAuc2hpbnRhdTIua2VudC5hYy51azCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEAqMJSgjGNS9f/T2jyU3ort+vzY29hEMXjJPgtQEvM2ms/QsaNEIMCkH32duA6zpw37EdpWj3Zkd23+1YNELFPkXA8AKP8LKKoVMeyvBmVwddsfAQsQVSBP6wD9rAGxsRX4+ZiMD7Pr/W9z2oH4VHLO+3dhKN/jKs0i0X+pqfmDe8CAwEAAaOB4zCB4DAdBgNVHQ4EFgQURPhSdGQW7H3QDKx4uyPxLEEc5J4wgbAGA1UdIwSBqDCBpYAURPhSdGQW7H3QDKx4uyPxLEEc5J6hgYGkfzB9MQswCQYDVQQGEwJHQjENMAsGA1UECBMES2VudDETMBEGA1UEBxMKQ2FudGVyYnVyeTEbMBkGA1UEChMSVW5pdmVyc2l0eSBvZiBLZW50MQswCQYDVQQLEwJDUzEgMB4GA1UEAxMXaWRwLnNoaW50YXUyLmtlbnQuYWMudWuCCQDRw4iUkrk7vjAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBBQUAA4GBAJJfj3BOWxtZGm/4tnIyRNMINBZfMAz9GS5/9np16mVYVsKHX+ZSxnZkXVNouzaZnQmsAy+L9yeccaETEOvo8tKmUkV9YTIKRABq7Sb95ELkf7BVXSX/8hCpTRz84edBwE9Zppu2S1t+1bfhfDak0enqXCJ5P6fKdTmrdjPn0eoo"

kentproxyendpoint = {"endpoint":{}}
kentproxyendpoint["endpoint"]["service_id"] = proxy["service"]["id"]
kentproxyendpoint["endpoint"]["publicurl"]=kentendpoint
kentproxyendpoint["endpoint"]["internalurl"]=kentendpoint
kentproxyendpoint["endpoint"]["adminurl"]=kentendpoint
kentproxyendpoint["endpoint"]["certdata"]=proxycertdata

endpointEndpoint = BASE_URL+":35357/v2.0/endpoints"

kpep = keystoneRequest(endpointEndpoint, kentproxyendpoint, "POST")
print "OK"

print "Adding Org Attributes"
orgattEndpoint = BASE_URL+":5000/v3/org_attributes"
# An example Project attribute
# is only triggered if the user has an attribute named project and a value of 785717
att1 = {"org_attribute":{}}
att1["org_attribute"]["type"] = "project"
att1["org_attribute"]["value"] = "785717"
orgatt1 = keystoneRequest(orgattEndpoint, att1, "POST")
print "OK"

print "Adding Authorised Issuers for Attributes"
#Proxy can issue org atts 6-7
keystoneRequest(orgattEndpoint+"/"+orgatt1["org_attribute"]["id"]+"/issuers/"+proxy["service"]["id"], method="PUT")
print "OK"

print "Organising Org Sets"
orgsetEndpoint = BASE_URL+":5000/v3/org_attribute_sets"
# Create the set
# A organization set contains as many attributes as you want to be related to that set
org_set1 = {"org_attribute_set":{}}
org_set1["org_attribute_set"]["name"] = "example_org_mapping_set"
org_set1 = keystoneRequest(orgsetEndpoint, org_set1, "POST")
# Add the attributes
keystoneRequest(orgsetEndpoint+"/"+org_set1["org_attribute_set"]["id"]+"/attributes/"+orgatt1["org_attribute"]["id"], method="PUT")
print "OK"

print "Adding roles"
roleEndPoint = BASE_URL+":5000/v3/roles"
# Add a role that the organization set of attributes can be mapped to
role1 = {"role":{}}
role1["role"]["name"] = "example_mapping_role"
role1 = keystoneRequest(roleEndPoint, role1, "POST")
print "OK"

print "Adding Projects"
projectEndPoint = BASE_URL+":5000/v3/projects"
# Add a project that the organization set of attributes can be mapped to
project1 = {"project":{}}
project1["project"]["name"] = "example_mapping_project"
project1["project"]["description"] = "Example Mapping Project"
project1 = keystoneRequest(projectEndPoint, project1, "POST")
print "OK"

print "Organising Os Sets"
ossetEndpoint = BASE_URL+":5000/v3/os_attribute_sets"
# Add an OpenStack set that specifies projects and roles that organization attribute sets can be mapped to
os_set1 = {"os_attribute_set":{}}
os_set1["os_attribute_set"]["name"] = "example_os_mapping_set"
os_set1 = keystoneRequest(ossetEndpoint, os_set1, "POST")
# Add the attributes
keystoneRequest(ossetEndpoint+"/"+os_set1["os_attribute_set"]["id"]+"/projects/"+project1["project"]["id"], method="PUT")
keystoneRequest(ossetEndpoint+"/"+os_set1["os_attribute_set"]["id"]+"/roles/"+role1["role"]["id"], method="PUT")
print "OK"

print "Mapping Sets"
amEndpoint = BASE_URL+":5000/v3/attribute_set_mappings"
basicMap = {"attribute_set_mapping":{"org_attribute_set_id":"", "os_attribute_set_id":""}}
# Add a mapping between the example organization attribute set and the OpenStack attribute set
attr_set_map1 = basicMap.copy()
attr_set_map1["attribute_set_mapping"]["org_attribute_set_id"] = org_set1["org_attribute_set"]["id"]
attr_set_map1["attribute_set_mapping"]["os_attribute_set_id"] = os_set1["os_attribute_set"]["id"]
keystoneRequest(amEndpoint, attr_set_map1, "POST")
print "OK"

print "Success, all entities created, demo ready"
