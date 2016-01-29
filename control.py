#!/usr/bin/env python
import requests
import json
import argparse
import os
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('')


api_key = None
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-j', '--job-id', type=int)
    ap.add_argument('-k', '--api-key', required=True)
    ap.add_argument('command')

    args = ap.parse_args()
    api_key = args.api_key

    if args.command == 'cancel-guessed': 
        assert(args.job_id)
        cancel_guessed(args.job_id)
    if args.command == 'cancel-non-guessed':
        assert(args.job_id)
        cancel_non_guessed(args.job_id)
        

def cancel_guessed(job_id):
    for unit_id, item in get_all_units(job_id).iteritems():
            if unit_guessed(item):
                res = cancel_unit(job_id, item_id)
                logger.info(res)

def cancel_non_guessed(job_id):
    for unit_id, item in get_all_units(job_id).iteritems():
            for judgment in get_all_judgments(job_id, unit_id):
                if not judgment_guessed(judgment):
                    res = cancel_unit(job_id, unit_id)
                    logger.info(res)

def reject_contributor(job_id, worker_id):
    url = "https://api.crowdflower.com/v1/jobs/{job_id}/workers/{worker_id}/reject.json"
    url = url.format(job_id=job_id, worker_id=worker_id)

    return call(url, 'put', {"key": api_key, "reject": "You are out!"})

def get_all_units(job_id):
    url = "https://api.crowdflower.com/v1/jobs/{job_id}/judgments.json"
    url = url.format(job_id=job_id)
    res = {}
    i = 1
    while True:
        logger.info("Getting judgments from job {0} (page {1})".format(job_id, i))
        res_i = call(url, 'get', { "key" : api_key, "page" : i})
        if not res_i:
            break
        res.update(res_i)
        i += 1
    return res

def get_all_judgments(job_id, unit_id):
    url = "https://api.crowdflower.com/v1/jobs/{job_id}/units/{unit_id}/judgments.json"
    url = url.format(job_id=job_id, unit_id=unit_id)
    return call(url, 'get', {"key": api_key})

def cancel_unit(job_id, unit_id):
    logger.info("Cancelling unit {0} of job {1}".format(unit_id, job_id))
    url = "https://api.crowdflower.com/v1/jobs/{job_id}/units/{unit_id}/cancel.json"
    #url = "https://api.crowdflower.com/v1/jobs/{job_id}/units/{unit_id}.json"
    url = url.format(job_id=job_id, unit_id=unit_id)
    #return call(url, 'put', {"key":api_key, 'unit[state]': 'canceled'})
    return call(url, 'post', {"key": api_key})

def unit_guessed(item):
    return item['answer'].lower() in map(lambda x: x.lower() if x else x,
        item['guess']+item['guess_2_optional']+item['guess_3_optional'])

def judgment_guessed(item):
    return item['unit_data']['answer'].lower() in map(lambda x: x.lower() if x else x,
        [item['data']['guess']]+[item['data'].get('guess_2_optional',None)]+[item['data'].get('guess_3_optional',
        None)])

def call(api_call,method, params):
    headers = {'content-type': 'application/json'}
    ret = requests.request(method, api_call, data=json.dumps(params),
    headers=headers)
    return json.loads(ret.text)




main()
