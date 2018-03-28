from ..models import Record
import threading
import time
from django.utils import timezone
import random


class History:
    @staticmethod
    def get_record(id, count=-1, reverse=True):
        record1 = Record.objects.filter(id1=id)
        record2 = Record.objects.filter(id2=id)
        #print('In History')
        #print(record1)
        #print(record2)
        records = []
        for r in record1:
            records.append(r)
        for r in record2:
            records.append(r)

        if len(record1) != 0 and len(record2) != 0:
            sorted(records, key=lambda x: x.count)

        if count == -1:
            return records
        elif reverse:
            return records[-count:]
        else:
            return records[0: count]
