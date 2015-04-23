import boto.rds2
from datetime import datetime

# Put your db_identifier here
db_identifier = ''

# Put your db_region here
db_region = ''

conn = boto.rds2.connect_to_region(db_region)
log_files = conn.describe_db_log_files(db_identifier, 'mysql-slowquery.log', file_size=1024)
log_files = log_files['DescribeDBLogFilesResponse']['DescribeDBLogFilesResult']['DescribeDBLogFiles']
log_files.sort(key=lambda r: r['LastWritten'], reverse=True)
time = datetime.today().strftime('%Y-%m-%dT%H%M%S')

for lf in log_files:
    log_local_fn = 'logs/' + time + '-' + lf['LogFileName'].split('/')[-1]

    mkr = u'0'
    f = open(log_local_fn, 'w')

    while mkr is not False:
        print 'mkr:{2} | {0}MB | {1}'.format(lf['Size'] / 1024 / 1024, lf['LogFileName'], mkr)
        fr = conn.download_db_log_file_portion(db_identifier, lf['LogFileName'], mkr)
        fpr = fr['DownloadDBLogFilePortionResponse']['DownloadDBLogFilePortionResult']

        if fpr['LogFileData'] is not None:
            f.write(fpr['LogFileData'].encode('utf8'))

        f.close()

        if fpr['AdditionalDataPending']:
            mkr = fpr['Marker']
            f = open(log_local_fn, 'a')
        else:
            mkr = False