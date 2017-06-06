from Abbyy.AbbyyOnlineSdk import *
from celery import shared_task
from wizcard import err
from celery import exceptions
import pdb

class OCR:

    def __init__(self):
        self.result = dict()

    def process(self, _file):
        runproc = RunOCR()
        args = {'file':_file, "lang":"English", "format":"xml"}
        res = run_ocr.delay(runproc, **args)
        try:
            ocr_result = res.get(timeout=25)
        except exceptions.TimeoutError:
            self.result.update(err.LIB_OCR_CELERY_TIMEOUT)
            return self.result
        except:
            self.result.update(err.LIB_OCR_ERROR)
            return self.result

        status = ocr_result[0]
        result = ocr_result[1]

        if not result:
            self.result.update(err.LIB_OCR_ERROR)
            self.result['str'] = status
            return self.result

        self.ocr_result(**result)
        return self.result

    def ocr_result(self, **kwargs):
        self.result['first_name'] = ""
        self.result['last_name'] = ""
        self.result['title'] = ""
        self.result['company'] = ""
        self.result['phone'] = ""
        if kwargs.has_key('name'):
            part = kwargs.get('name').partition(" ")
            self.result['first_name'] = part[0]
            self.result['last_name'] = part[2]
        if kwargs.has_key('phone'):
            self.result['phone'] = kwargs.get('phone')
        if kwargs.has_key('email'):
            self.result['email'] = kwargs.get('email')
        if kwargs.has_key('company'):
            self.result['company'] = kwargs.get('company')
        if kwargs.has_key('web'):
            self.result['web'] = kwargs.get('web')
        if kwargs.has_key('job'):
            self.result['title'] = kwargs.get('job')


@shared_task
def run_ocr(inst, **kwargs):
    _file = kwargs.get('file')
    _lang = kwargs.get('lang', "English")
    _format = kwargs.get('format', "xml")
    return inst.RunProc(_file, _lang, _format)
