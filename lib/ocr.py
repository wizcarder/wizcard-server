from Abbyy.AbbyyOnlineSdk import *
import pdb

class OCR:

    def __init__(self):
        self.result = dict()

    def process(self, file):
	#call OCR lib and get result.
	runproc = RunOCR()
        ocr_result_dict = runproc.RunProc(
                              file,
                              "English","xml")

        self.ocr_result(**ocr_result_dict)
        return self.result

    def ocr_result(self, **kwargs):
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
        if kwargs.has_key('title'):
            self.result['title'] = kwargs.get('title')
