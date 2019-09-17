
import os
import time
import sys
sys.path.append(os.getenv('TICKALGOAGENT'))
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

from src.loghandler import log
from src.main.algo_agent_object import AlgoAgentObjects as algoObj

logger = log.setup_custom_logger('TickStream')


class FireBaseUtils(object):
    cred = None
    bucket = None

    def __init__(self):
        try:
            logger.info("Initiating connection to fire base")
            FireBaseUtils.cred = credentials.Certificate(algoObj.get_with_base_path("firebase", "firebase_key"))
            firebase_admin.initialize_app(FireBaseUtils.cred, {
                'storageBucket': algoObj.get_value('firebase', 'firebase_app_name')
            })
            logger.info("Connected to firebase bucket")
            FireBaseUtils.bucket = storage.bucket()
        except Exception as ex:
            logger.error(ex)


    def get_file_from_firebaseStorage(self, path):
        try:
            """Downloads a blob from the bucket."""
            blob = FireBaseUtils.bucket.blob(path)
            print('Blobs: {}'.format(blob.name))
            blob.download_to_filename(os.path.join("/","tmp",blob.name.split('/')[1]))
            logger.info('Blob {} downloaded to {}.'.format(
                path, "/tmp/"+ blob.name.split('/')[1]))
            return os.path.join("/","tmp",blob.name.split('/')[1])
        except Exception as ex:
            logger.error(ex)

    def get_blob_path(self, date, symbol, contract_type="STK"):
        if contract_type is "STK":
            return os.path.join(date,symbol+"_STK.csv")

    def upload_all_file_in_dir_to_firebaseStorage(self, dir_path, date):
        try:
            for r, d, f in os.walk(dir_path):
                for file in f:
                    if '.csv' in file:
                        print("Uploading file @" + os.path.join(r, file))
                        blob = FireBaseUtils.bucket.blob(date + "/" + file)
                        blob.upload_from_filename(os.path.join(r, file))
                        logger.info('File {} uploaded to {}.'.format(
                            os.path.join(r, file),
                            date + "/" + file))
        except Exception as ex:
            logger.error(ex)


if __name__ == '__main__':
    fbuObj = FireBaseUtils()
    fbuObj.upload_all_file_in_dir_to_firebaseStorage("/Users/sivaamur/Vuk-ai/GitRepos/TickStream/tickbank/20190830/",
                                                     "20190830")