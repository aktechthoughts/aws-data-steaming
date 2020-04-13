import subprocess
import boto3
import select
import time
import json
import argparse

class KinesisInputStream:

    def __init__(self,in_stream_name,in_file_name):
        self.kinesis = boto3.client('kinesis')
        self.in_file = in_file_name
        self.in_stream = in_stream_name

    def put_records(self):
        fout = subprocess.Popen(['tail', '-f', self.in_file], \
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p = select.poll()
        p.register(fout.stdout)
        data = [];

        while True:
            rec_count = 0
            while rec_count <=2:
                if p.poll(1):

                    record = fout.stdout.readline()
                    time.sleep(1)
                    data.append(dict({'Data': record, 'PartitionKey': 'partition_key'}))
                    rec_count +=1
            res = self.kinesis.put_records(StreamName=self.in_stream, Records=data)
            time.sleep(0.1)
            print(str(rec_count-res['FailedRecordCount'])+' records pushed to '+self.in_stream+' stream successfully.')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Argument for Tweet Text')
    parser.add_argument('streamName', help="Stream to Pass the records.")
    parser.add_argument('fileName', help="Absolute path to filename where the records will be read.")    
    args = parser.parse_args()

    inp_stream = KinesisInputStream(args.streamName,args.fileName)
    inp_stream.put_records()


