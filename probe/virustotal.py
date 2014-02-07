import json
import urllib
import urllib2

url = "https://www.virustotal.com/vtapi/v2/file/report"

def get_scan_result(hashvalue):
    parameters = {"resource": hashvalue,
                  "apikey": "-=- YOUR KEY HERE -=-"}
    data = urllib.urlencode(parameters)
    req = urllib2.Request(url, data)
    res = urllib2.urlopen(req)
    res_json = res.read()
    try:
        vtres = json.loads(res_json)
        if vtres['response_code'] != 1:
            return "retcode %d" % vtres['response_code']
        else:
            return "%d/%d positives" % (vtres['positives'], vtres['total'])
    except:
        return "Error fetching online result"

def scan(sfile):
    res = {}
    res['result'] = get_scan_result(sfile.hashvalue)
    return res